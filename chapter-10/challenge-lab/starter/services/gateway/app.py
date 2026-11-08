"""API gateway. Owns the checkout flow across inventory and payment.

Checkout is three calls:

    1. reserve stock in inventory
    2. charge the card in payment
    3. commit the reservation in inventory

If the charge fails or times out, the gateway releases the hold and returns an
error. If the commit fails, the gateway refunds the charge. Payment calls are
retried once, because the processor is known to be slow under load.

Run it on its own (inventory and payment must already be up):

    python -m services.gateway.app
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from services._http import (  # noqa: E402
    GATEWAY_PORT,
    INVENTORY_URL,
    PAYMENT_URL,
    JsonHandler,
    ServiceError,
    UpstreamError,
    UpstreamTimeout,
    get_logger,
    post_json,
    serve,
)

LOG = get_logger("gateway")

PAYMENT_TIMEOUT_S = float(os.environ.get("GATEWAY_PAYMENT_TIMEOUT_S", "1.0"))
INVENTORY_TIMEOUT_S = float(os.environ.get("GATEWAY_INVENTORY_TIMEOUT_S", "2.0"))
PAYMENT_RETRIES = int(os.environ.get("GATEWAY_PAYMENT_RETRIES", "1"))

# Inbound headers longer than this get truncated before the gateway logs or
# echoes them, so a client cannot push an unbounded string through the edge.
MAX_HEADER_LENGTH = int(os.environ.get("GATEWAY_MAX_HEADER_LENGTH", "128"))

# Headers the gateway is allowed to pass to an internal service. Anything else
# stops at the edge. Note what this means for the outbound calls below: they
# carry only values the gateway generates itself.
FORWARDABLE_HEADERS = ("X-Request-Id",)


def sanitize_inbound_headers(headers: dict, request_id: str) -> dict:
    """Truncate oversized inbound headers and keep only forwardable ones."""
    kept = {}
    for name, value in headers.items():
        if len(value) > MAX_HEADER_LENGTH:
            LOG.warning(
                "header truncated request_id=%s header=%s original_length=%d "
                "kept_length=%d",
                request_id,
                name,
                len(value),
                MAX_HEADER_LENGTH,
            )
            value = value[:MAX_HEADER_LENGTH]
        if name in FORWARDABLE_HEADERS:
            kept[name] = value
    return kept


def _trace_headers(request_id: str) -> dict:
    """Headers for an internal call. Generated here, never client supplied."""
    return {"X-Request-Id": request_id, "X-Forwarded-Service": "gateway"}


def _charge_with_retry(payload: dict, request_id: str) -> dict:
    """Charge the card, retrying once on timeout.

    The retry sends the same idempotency key so the processor collapses
    duplicates rather than charging twice.
    """
    attempts = PAYMENT_RETRIES + 1
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return post_json(
                f"{PAYMENT_URL}/charges",
                payload,
                timeout=PAYMENT_TIMEOUT_S,
                headers={
                    **_trace_headers(request_id),
                    "Idempotency-Key": payload["idempotency_key"],
                    "X-Retry-Attempt": str(attempt),
                },
            )
        except UpstreamTimeout as exc:
            last_error = exc
            LOG.warning(
                "payment timeout request_id=%s order=%s attempt=%d/%d "
                "timeout_s=%.1f",
                request_id,
                payload.get("order_id"),
                attempt,
                attempts,
                PAYMENT_TIMEOUT_S,
            )
    raise ServiceError(
        504, "payment_timeout", f"payment did not answer in {PAYMENT_TIMEOUT_S}s"
    ) from last_error


def handle_checkout(payload: dict, headers: dict) -> dict:
    request_id = headers.get("X-Request-Id") or f"req_{uuid.uuid4().hex[:10]}"
    inbound = sanitize_inbound_headers(headers, request_id)
    request_id = inbound.get("X-Request-Id", request_id)
    order_id = payload.get("order_id") or f"ord_{uuid.uuid4().hex[:8]}"
    sku = payload.get("sku", "")
    quantity = int(payload.get("quantity", 1))
    amount_cents = int(payload.get("amount_cents", 0))
    card_token = payload.get("card_token", "tok_test")

    LOG.info(
        "checkout start request_id=%s order=%s sku=%s qty=%d",
        request_id,
        order_id,
        sku,
        quantity,
    )

    # Step 1: hold the stock.
    try:
        reservation = post_json(
            f"{INVENTORY_URL}/reservations",
            {"sku": sku, "quantity": quantity, "order_id": order_id},
            timeout=INVENTORY_TIMEOUT_S,
            headers=_trace_headers(request_id),
        )
    except UpstreamError as exc:
        if exc.status == 409:
            LOG.info(
                "checkout rejected request_id=%s order=%s reason=out_of_stock",
                request_id,
                order_id,
            )
            raise ServiceError(409, "out_of_stock", "item is sold out") from exc
        raise ServiceError(502, "inventory_error", str(exc.body)) from exc
    except UpstreamTimeout as exc:
        raise ServiceError(504, "inventory_timeout", "inventory did not answer") from exc

    reservation_id = reservation["reservation_id"]

    # Step 2: charge the card.
    try:
        charge = _charge_with_retry(
            {
                "order_id": order_id,
                "amount_cents": amount_cents,
                "card_token": card_token,
                "idempotency_key": f"{order_id}:{reservation_id}",
            },
            request_id,
        )
    except (ServiceError, UpstreamError) as exc:
        _release(reservation_id, request_id)
        if isinstance(exc, UpstreamError):
            raise ServiceError(402, "payment_declined", str(exc.body)) from exc
        raise

    # Step 3: turn the hold into a real decrement.
    try:
        post_json(
            f"{INVENTORY_URL}/reservations/commit",
            {"reservation_id": reservation_id},
            timeout=INVENTORY_TIMEOUT_S,
            headers=_trace_headers(request_id),
        )
    except UpstreamError as exc:
        LOG.error(
            "checkout failed request_id=%s order=%s reservation=%s "
            "stage=commit upstream_error=%s",
            request_id,
            order_id,
            reservation_id,
            exc.body.get("error"),
        )
        _refund(charge["charge_id"], request_id)
        raise ServiceError(
            500, "checkout_failed", "could not confirm the order, payment refunded"
        ) from exc
    except UpstreamTimeout as exc:
        _refund(charge["charge_id"], request_id)
        raise ServiceError(504, "inventory_timeout", "commit did not answer") from exc

    LOG.info(
        "checkout ok request_id=%s order=%s charge=%s reservation=%s",
        request_id,
        order_id,
        charge["charge_id"],
        reservation_id,
    )
    return {
        "status": "confirmed",
        "order_id": order_id,
        "request_id": request_id,
        "charge_id": charge["charge_id"],
        "reservation_id": reservation_id,
    }


def _release(reservation_id: str, request_id: str) -> None:
    try:
        post_json(
            f"{INVENTORY_URL}/reservations/release",
            {"reservation_id": reservation_id},
            timeout=INVENTORY_TIMEOUT_S,
            headers=_trace_headers(request_id),
        )
        LOG.info(
            "compensation ok request_id=%s action=release reservation=%s",
            request_id,
            reservation_id,
        )
    except (UpstreamError, UpstreamTimeout):
        LOG.error(
            "compensation failed request_id=%s action=release reservation=%s",
            request_id,
            reservation_id,
        )


def _refund(charge_id: str, request_id: str) -> None:
    try:
        post_json(
            f"{PAYMENT_URL}/refunds",
            {"charge_id": charge_id},
            timeout=PAYMENT_TIMEOUT_S,
            headers=_trace_headers(request_id),
        )
        LOG.info(
            "compensation ok request_id=%s action=refund charge=%s",
            request_id,
            charge_id,
        )
    except (UpstreamError, UpstreamTimeout):
        LOG.error(
            "compensation failed request_id=%s action=refund charge=%s",
            request_id,
            charge_id,
        )


class GatewayHandler(JsonHandler):
    routes = {
        "/checkout": handle_checkout,
        "/health": lambda payload, headers: {"status": "ok", "service": "gateway"},
    }


if __name__ == "__main__":
    serve(GatewayHandler, GATEWAY_PORT, LOG)
