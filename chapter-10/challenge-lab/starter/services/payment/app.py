"""Payment service. Wraps a third-party card processor.

The processor is slow under load: it holds a small pool of connections, and
queued charges wait for one. Under a burst you will see latency climb and some
charges exceed the gateway's deadline. That is real, it shows up in the logs,
and it is not the reason customers get orders that cannot be fulfilled.

Run it on its own:

    python -m services.payment.app
"""

from __future__ import annotations

import os
import random
import sys
import threading
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from services._http import (  # noqa: E402
    PAYMENT_PORT,
    JsonHandler,
    ServiceError,
    get_logger,
    serve,
)

LOG = get_logger("payment")

# The processor's connection pool. Charges beyond this wait their turn, so
# latency grows with the queue depth rather than at random.
POOL_SIZE = int(os.environ.get("PAYMENT_POOL_SIZE", "3"))
BASE_LATENCY_MS = float(os.environ.get("PAYMENT_BASE_LATENCY_MS", "120"))
JITTER_MS = float(os.environ.get("PAYMENT_JITTER_MS", "80"))

_pool = threading.Semaphore(POOL_SIZE)
_stats_lock = threading.Lock()
_stats = {
    "charges": 0,
    "declines": 0,
    "idempotent_replays": 0,
    "queue_peak": 0,
    "queued_now": 0,
}

# Idempotency keys already charged, mapped to the charge they produced. A
# retried request with the same key returns the original charge instead of
# billing the card twice.
_charged_keys: dict[str, str] = {}
_keys_lock = threading.Lock()


def _charge_processor(amount_cents: int) -> str:
    """Call the processor. Blocks while the pool is saturated."""
    with _stats_lock:
        _stats["queued_now"] += 1
        _stats["queue_peak"] = max(_stats["queue_peak"], _stats["queued_now"])
    try:
        with _pool:
            time.sleep((BASE_LATENCY_MS + random.random() * JITTER_MS) / 1000.0)
            if amount_cents <= 0:
                raise ValueError("amount must be positive")
            return f"ch_{uuid.uuid4().hex[:12]}"
    finally:
        with _stats_lock:
            _stats["queued_now"] -= 1


def handle_charge(payload: dict, headers: dict) -> dict:
    request_id = headers.get("X-Request-Id", "-")
    order_id = payload.get("order_id", "-")
    amount_cents = int(payload.get("amount_cents", 0))
    card_token = payload.get("card_token", "")
    idempotency_key = headers.get("Idempotency-Key") or payload.get(
        "idempotency_key", ""
    )

    if not card_token:
        raise ServiceError(400, "missing_card_token", "card_token is required")

    # A retry carries the same key. Return the original charge, do not re-bill.
    if idempotency_key:
        with _keys_lock:
            existing = _charged_keys.get(idempotency_key)
        if existing:
            with _stats_lock:
                _stats["idempotent_replays"] += 1
            LOG.info(
                "charge replay request_id=%s order=%s charge=%s "
                "idempotency_key=%s attempt=%s",
                request_id,
                order_id,
                existing,
                idempotency_key,
                headers.get("X-Retry-Attempt", "-"),
            )
            return {
                "status": "captured",
                "charge_id": existing,
                "amount_cents": amount_cents,
                "replayed": True,
            }

    started = time.time()
    try:
        charge_id = _charge_processor(amount_cents)
    except ValueError as exc:
        with _stats_lock:
            _stats["declines"] += 1
        raise ServiceError(402, "declined", str(exc)) from exc

    if idempotency_key:
        with _keys_lock:
            _charged_keys[idempotency_key] = charge_id

    elapsed_ms = (time.time() - started) * 1000
    with _stats_lock:
        _stats["charges"] += 1
        queue_depth = _stats["queued_now"]

    if elapsed_ms > 500:
        LOG.warning(
            "charge slow request_id=%s order=%s charge=%s elapsed_ms=%.0f "
            "processor_queue_depth=%d",
            request_id,
            order_id,
            charge_id,
            elapsed_ms,
            queue_depth,
        )
    else:
        LOG.info(
            "charge ok request_id=%s order=%s charge=%s elapsed_ms=%.0f",
            request_id,
            order_id,
            charge_id,
            elapsed_ms,
        )
    return {
        "status": "captured",
        "charge_id": charge_id,
        "amount_cents": amount_cents,
        "elapsed_ms": round(elapsed_ms, 1),
    }


def handle_refund(payload: dict, headers: dict) -> dict:
    request_id = headers.get("X-Request-Id", "-")
    charge_id = payload.get("charge_id", "")
    if not charge_id:
        raise ServiceError(400, "missing_charge_id", "charge_id is required")
    LOG.info("refund ok request_id=%s charge=%s", request_id, charge_id)
    return {"status": "refunded", "charge_id": charge_id}


def handle_stats(_payload: dict, _headers: dict) -> dict:
    with _stats_lock:
        return {"pool_size": POOL_SIZE, **_stats}


class PaymentHandler(JsonHandler):
    routes = {
        "/charges": handle_charge,
        "/refunds": handle_refund,
        "/payment/stats": handle_stats,
        "/health": lambda payload, headers: {"status": "ok", "service": "payment"},
    }


if __name__ == "__main__":
    serve(PaymentHandler, PAYMENT_PORT, LOG)
