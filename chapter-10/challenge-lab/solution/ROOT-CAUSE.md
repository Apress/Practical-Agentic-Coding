# Answer key: the seeded root cause

> **Spoiler.** This file documents the defect the challenge lab is built
> around. Stop here and go investigate. Come back after your agent team has
> written its conclusion into `starter/findings.md`. Then use this file to
> grade it.

## The seeded defect

`ReservationLedger.reserve()` in
`starter/services/inventory/reservation.py` is a check-then-act sequence. No
lock spans the steps:

1. `available = self.available(sku)` takes the lock, computes availability,
   releases the lock.
2. `time.sleep(WRITE_LATENCY_MS / 1000.0)` stands in for the database round
   trip that writes the hold row.
3. A second `with self._lock:` block inserts the hold.

Each step is locked correctly on its own. The sequence is not locked. There is
a window between the read in step 1 and the write in step 3. It lasts 15ms by
default, the length of a real database write. During that window, every other
in-flight request sees the same stale availability.

For example, six concurrent requests for a three-unit SKU all read
`available=3`. All six decide they can proceed, and all six insert a hold.
The ledger has now granted more holds than it has stock. This breaks the
system-wide invariant:

    committed units + held units <= units on hand

## Why the symptom looks like three different bugs

The oversell is silent at reserve time. It only shows up later, at commit. The
request that fails is not the request that caused the problem:

- The **gateway** reports the failure, because `commit` is a gateway-issued
  call. The 500 is logged with `[gateway]` in front of it. The gateway looks
  guilty.
- The **payment** service sits in the middle of the trace with rising latency.
  The burst that triggers the race also saturates the processor pool. Payment
  looks guilty.
- The **inventory** service logs `reserve ok` for every request, including the
  ones it should have rejected. Inventory looks innocent.

Two more things hide it:

- Failed checkouts release their holds, so the next audit reconciles. After the
  fact, the damage is invisible unless you keep a low-water mark.
  `_min_available` in the ledger shows this.
- Under light load, the race does not fire at all. Each request's write
  completes before the next one reads. Single-request reproduction attempts
  come back clean. This is why "cannot reproduce" ends up on the ticket.

## The two decoys, and how to disprove each

**Payment gateway timeout under load.**

- Real evidence: The processor pool holds three connections. Latency climbs
  with queue depth. `payment.log` has genuine `charge slow` and 2-second
  entries.
- Disproof: Timeouts produce HTTP 504 `payment_timeout`, with the hold
  released and no order created. The failures under investigation are HTTP 500
  `checkout_failed` on charges that succeeded and then got refunded. The code
  path and the trace shape differ.
- Also check `payment.log` in the 14:32:00Z window. Every charge succeeded.
  None timed out.

**Request header corruption on retry.**

- Real evidence: `sanitize_inbound_headers()` in the gateway truncates
  oversized inbound headers and logs a warning. The warnings are in
  `gateway.log`.
- Disproof: Only `X-Request-Id` is forwardable. `_trace_headers()` inside the
  gateway generates every header on an internal call. No header is copied from
  the client. Truncation cannot reach inventory or payment.
- The warnings also fire all day, in windows with zero failures. They do not
  correlate with the incident.

## The fix

Hold one lock across the availability check and the hold write. The two steps
become a single atomic operation. In `starter/services/inventory/reservation.py`:

```python
def reserve(self, sku: str, quantity: int, order_id: str) -> Reservation:
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    with self._lock:
        if sku not in self._on_hand:
            raise OutOfStock(f"unknown sku {sku}")
        available = self._available_locked(sku)
        if available < quantity:
            raise OutOfStock(
                f"sku={sku} requested={quantity} available={available}"
            )
        reservation = Reservation(
            reservation_id=f"rsv_{uuid.uuid4().hex[:10]}",
            sku=sku,
            quantity=quantity,
            order_id=order_id,
        )
        self._reservations[reservation.reservation_id] = reservation
        self._record_watermark_locked(sku)
    return reservation
```

The simulated write latency (`time.sleep`) is gone from the method. The
availability read and the hold write are now one step. There are no longer two
round trips with a gap between them.

In a service backed by a real database, the equivalent fixes are:

- a `SELECT ... FOR UPDATE` on the stock row, inside the same transaction that
  inserts the hold
- an atomic conditional update
  (`UPDATE stock SET held = held + :qty WHERE sku = :sku AND on_hand - held >= :qty`),
  checked by affected row count
- a database-level constraint that makes the oversold state unrepresentable

After applying the fix, from `starter/`, run:

```bash
python reproduce_failure.py --embedded --concurrency 12
```

Expected result at `--concurrency 12`:

- exactly 3 confirmed orders on `FLAGSHIP-001`
- 9 rejected with HTTP 409 `out_of_stock`
- zero 500s
- `oversold_commits` at 0
- `holds_granted_total` at or below 3
- `min_available_seen` at or above 0

If you still see 500s after you apply the fix, delete stale bytecode first
(`find . -name __pycache__ -type d -exec rm -rf {} +`). Then run it again. An
agent can edit the file while a `__pycache__` from the pre-fix import still
exists. That agent then concludes the fix did not work.

## Grading the reader's findings.md

A finished investigation has all five of these. Partial credit is the normal
outcome on a first attempt.

1. **Names the check-then-act window.** "Inventory has a bug" is not enough.
   The conclusion points at the gap between the read and the write in
   `reserve()`. It explains why the two locked blocks are not enough.
2. **Cites the log evidence**: six `reserve ok` lines inside 13ms on a
   three-unit SKU, with no `reserve rejected` line in the same window.
3. **Explains the misdirection**: why the gateway logs the 500 when the defect
   is in inventory.
4. **Disproves both decoys with evidence.** Assertion is not enough. The
   payment hypothesis fails on the 504-versus-500 distinction. The header
   hypothesis fails on `FORWARDABLE_HEADERS` plus the lack of correlation.
5. **Proposes an atomic fix** and states how to verify it.

The report may skip item 4 and simply declare inventory the winner. Then the
team missed the coordination goal, even though the answer is right. The
exercise grades agents challenging each other. A correct guess alone does not
pass.

## Grading the coordination

Grade the answer and the transcript separately. In the transcript, check these
points:

- Check whether teammates messaged each other directly or routed everything
  through the lead. Direct exchange is the goal.
- Check how the payment investigator responded to the 504-versus-500
  evidence. Conceding passes. Defending with counter-evidence passes. Ignoring
  the message fails.
- Check whether each teammate wrote into `findings.md`, or one agent wrote the
  whole file. Concurrent writes to a shared file are a coordination problem
  too. Note the parallel with the bug you are chasing.
