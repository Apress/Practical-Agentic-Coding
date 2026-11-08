"""Reservation ledger for the inventory service.

A reservation is a soft hold on stock. Checkout reserves units first, charges
the card next, then commits the reservation once payment clears. Holds that are
never committed get released.

Invariant the rest of the system depends on:

    committed units + held units <= units on hand

Everything downstream (fulfilment, the warehouse pick list, the customer's
"order confirmed" email) assumes that invariant holds.
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from dataclasses import dataclass, field

# Time spent inside the write path. It stands in for the round trip to the
# inventory database (connection checkout, INSERT, commit) and is configurable
# so the lab behaves the same on fast and slow machines.
WRITE_LATENCY_MS = float(os.environ.get("INVENTORY_WRITE_LATENCY_MS", "15"))


class OutOfStock(Exception):
    """Not enough available units to satisfy the request."""


class OversoldInventory(Exception):
    """A committed reservation would drive units on hand below zero."""


class UnknownReservation(Exception):
    """No live reservation with that id."""


@dataclass
class Reservation:
    reservation_id: str
    sku: str
    quantity: int
    order_id: str
    state: str = "held"  # held -> committed | released
    created_at: float = field(default_factory=time.time)

    def as_dict(self) -> dict:
        return {
            "reservation_id": self.reservation_id,
            "sku": self.sku,
            "quantity": self.quantity,
            "order_id": self.order_id,
            "state": self.state,
        }


class ReservationLedger:
    """In-memory stand-in for the inventory tables.

    ``_on_hand`` is the stock table, ``_reservations`` is the holds table, and
    ``_lock`` is the transaction boundary: whatever runs inside a ``with
    self._lock`` block is what the real service would run inside one database
    transaction.
    """

    def __init__(self, stock: dict[str, int]) -> None:
        self._initial: dict[str, int] = dict(stock)
        self._on_hand: dict[str, int] = dict(stock)
        self._reservations: dict[str, Reservation] = {}
        self._lock = threading.Lock()
        # Lowest availability ever observed per SKU. Holds get released after a
        # failed checkout, which hides the damage from a later audit, so the
        # ledger keeps a watermark.
        self._min_available: dict[str, int] = dict(stock)
        self._oversold_commits = 0

    # ---------------------------------------------------------------- reads

    def _available_locked(self, sku: str) -> int:
        held = sum(
            r.quantity
            for r in self._reservations.values()
            if r.sku == sku and r.state == "held"
        )
        return self._on_hand.get(sku, 0) - held

    def _record_watermark_locked(self, sku: str) -> None:
        available = self._available_locked(sku)
        previous = self._min_available.get(sku, available)
        self._min_available[sku] = min(previous, available)

    def available(self, sku: str) -> int:
        """Units a new order could still claim."""
        with self._lock:
            return self._available_locked(sku)

    def snapshot(self) -> dict:
        """Audit view per SKU: stock, holds, commits, and units ever handed out."""
        with self._lock:
            report = {}
            for sku, on_hand in self._on_hand.items():
                held = sum(
                    r.quantity
                    for r in self._reservations.values()
                    if r.sku == sku and r.state == "held"
                )
                committed = sum(
                    r.quantity
                    for r in self._reservations.values()
                    if r.sku == sku and r.state == "committed"
                )
                granted = sum(
                    r.quantity for r in self._reservations.values() if r.sku == sku
                )
                report[sku] = {
                    "initial_on_hand": self._initial.get(sku, 0),
                    "on_hand": on_hand,
                    "held": held,
                    "committed": committed,
                    "available": on_hand - held,
                    "min_available_seen": self._min_available.get(sku, 0),
                    "holds_granted_total": granted,
                }
            return report

    def oversold_commits(self) -> int:
        """How many commits were rejected because stock had already run out."""
        with self._lock:
            return self._oversold_commits

    def get(self, reservation_id: str) -> Reservation:
        with self._lock:
            reservation = self._reservations.get(reservation_id)
            if reservation is None:
                raise UnknownReservation(reservation_id)
            return reservation

    # --------------------------------------------------------------- writes

    def reserve(self, sku: str, quantity: int, order_id: str) -> Reservation:
        """Place a hold on ``quantity`` units of ``sku``.

        The availability check and the hold write are two separate database
        round trips. Between them sits the write latency below.
        """
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if sku not in self._on_hand:
            raise OutOfStock(f"unknown sku {sku}")

        # Read the current availability.
        available = self.available(sku)
        if available < quantity:
            raise OutOfStock(
                f"sku={sku} requested={quantity} available={available}"
            )

        # Round trip to the inventory database to write the hold row.
        time.sleep(WRITE_LATENCY_MS / 1000.0)

        reservation = Reservation(
            reservation_id=f"rsv_{uuid.uuid4().hex[:10]}",
            sku=sku,
            quantity=quantity,
            order_id=order_id,
        )
        with self._lock:
            self._reservations[reservation.reservation_id] = reservation
            self._record_watermark_locked(sku)
        return reservation

    def commit(self, reservation_id: str) -> Reservation:
        """Convert a hold into a real stock decrement.

        Raises ``OversoldInventory`` when the decrement would push units on
        hand below zero, which means the invariant was already broken before
        this call arrived.
        """
        with self._lock:
            reservation = self._reservations.get(reservation_id)
            if reservation is None:
                raise UnknownReservation(reservation_id)
            if reservation.state == "committed":
                return reservation  # commit is idempotent
            if reservation.state == "released":
                raise UnknownReservation(f"{reservation_id} was released")

            on_hand = self._on_hand.get(reservation.sku, 0)
            if on_hand < reservation.quantity:
                self._oversold_commits += 1
                raise OversoldInventory(
                    f"sku={reservation.sku} on_hand={on_hand} "
                    f"requested={reservation.quantity} "
                    f"reservation={reservation_id} order={reservation.order_id}"
                )
            self._on_hand[reservation.sku] = on_hand - reservation.quantity
            reservation.state = "committed"
            return reservation

    def release(self, reservation_id: str) -> Reservation:
        """Drop a hold that will never be committed."""
        with self._lock:
            reservation = self._reservations.get(reservation_id)
            if reservation is None:
                raise UnknownReservation(reservation_id)
            if reservation.state == "held":
                reservation.state = "released"
            return reservation
