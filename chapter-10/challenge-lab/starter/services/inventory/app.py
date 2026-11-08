"""Inventory service. Holds stock, issues reservations, commits them.

Run it on its own:

    python -m services.inventory.app
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from services._http import (  # noqa: E402
    INVENTORY_PORT,
    JsonHandler,
    ServiceError,
    get_logger,
    serve,
)
from services.inventory.reservation import (  # noqa: E402
    OutOfStock,
    OversoldInventory,
    ReservationLedger,
    UnknownReservation,
)

LOG = get_logger("inventory")

# Warehouse stock at the start of the flash sale.
CATALOG = {
    "FLAGSHIP-001": 3,
    "HEADSET-77": 25,
    "CABLE-9": 500,
}

LEDGER = ReservationLedger(CATALOG)


def _request_id(headers: dict) -> str:
    return headers.get("X-Request-Id", "-")


def handle_reserve(payload: dict, headers: dict) -> dict:
    sku = payload.get("sku", "")
    quantity = int(payload.get("quantity", 1))
    order_id = payload.get("order_id", "-")
    try:
        reservation = LEDGER.reserve(sku, quantity, order_id)
    except OutOfStock as exc:
        LOG.warning(
            "reserve rejected request_id=%s order=%s %s",
            _request_id(headers),
            order_id,
            exc,
        )
        raise ServiceError(409, "out_of_stock", str(exc)) from exc
    except ValueError as exc:
        raise ServiceError(400, "invalid_quantity", str(exc)) from exc

    LOG.info(
        "reserve ok request_id=%s order=%s sku=%s qty=%d reservation=%s",
        _request_id(headers),
        order_id,
        sku,
        quantity,
        reservation.reservation_id,
    )
    return {"status": "held", **reservation.as_dict()}


def handle_commit(payload: dict, headers: dict) -> dict:
    reservation_id = payload.get("reservation_id", "")
    try:
        reservation = LEDGER.commit(reservation_id)
    except OversoldInventory as exc:
        LOG.error(
            "commit failed request_id=%s reason=oversold_inventory %s",
            _request_id(headers),
            exc,
        )
        raise ServiceError(500, "oversold_inventory", str(exc)) from exc
    except UnknownReservation as exc:
        raise ServiceError(404, "unknown_reservation", str(exc)) from exc

    LOG.info(
        "commit ok request_id=%s order=%s sku=%s reservation=%s",
        _request_id(headers),
        reservation.order_id,
        reservation.sku,
        reservation_id,
    )
    return {"status": "committed", **reservation.as_dict()}


def handle_release(payload: dict, headers: dict) -> dict:
    reservation_id = payload.get("reservation_id", "")
    try:
        reservation = LEDGER.release(reservation_id)
    except UnknownReservation as exc:
        raise ServiceError(404, "unknown_reservation", str(exc)) from exc
    LOG.info(
        "release ok request_id=%s reservation=%s",
        _request_id(headers),
        reservation_id,
    )
    return {"status": reservation.state, **reservation.as_dict()}


def handle_audit(_payload: dict, _headers: dict) -> dict:
    report = LEDGER.snapshot()
    for sku, row in report.items():
        # A negative availability, now or at any point in the run, means holds
        # were granted against stock that was not there.
        if min(row["available"], row["min_available_seen"]) < 0:
            LOG.warning("audit invariant broken sku=%s %s", sku, row)
    return {"stock": report, "oversold_commits": LEDGER.oversold_commits()}


class InventoryHandler(JsonHandler):
    routes = {
        "/reservations": handle_reserve,
        "/reservations/commit": handle_commit,
        "/reservations/release": handle_release,
        "/inventory/audit": handle_audit,
        "/health": lambda payload, headers: {"status": "ok", "service": "inventory"},
    }


if __name__ == "__main__":
    serve(InventoryHandler, INVENTORY_PORT, LOG)
