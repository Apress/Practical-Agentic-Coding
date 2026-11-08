# Inventory service notes

Owner: inventory team. Escalation: #inv-oncall.

## What this service guarantees

One invariant, and everything downstream depends on it:

    committed units + held units <= units on hand

Fulfilment, the warehouse pick list, and the "order confirmed" email all assume
it holds. If it breaks, we promise stock we do not have.

## Reservation lifecycle

    reserve  -> state=held      (soft hold, does not move stock)
    commit   -> state=committed (decrements units on hand)
    release  -> state=released  (drops the hold, stock returns to available)

`commit` is idempotent. `commit` on a released reservation is an error. The
gateway owns the ordering: reserve, charge, commit, and it releases or refunds
when a step fails.

## Open tickets

**INV-2291: `available` can read negative under burst traffic.** Reported after
the 2026-07-18 flash sale. The 60-second audit cron reconciles by the time
anyone looks, because failed checkouts release their holds. Added
`_min_available` (a low-water mark) and `oversold_commits` to the audit payload
so the damage is still visible after the fact. Not root caused. Status: open.

**INV-2294: `oversold_inventory` on commit is reported as a gateway 500.** The
customer sees "could not confirm the order" and the error surfaces in the
gateway's logs, which sends every investigation to the gateway team first.
Status: open, needs an error-taxonomy decision with the gateway team.

**INV-2301: reserve does not log a rejection reason on the happy path.** We log
`reserve ok` for every accepted hold but there is no counter for how many holds
exist versus how much stock backs them at the moment of the decision. Makes
after-the-fact analysis harder than it should be. Status: open.

## Load characteristics

`INVENTORY_WRITE_LATENCY_MS` (default 15) stands in for the hold-row write:
connection checkout, INSERT, commit. Production p50 is close to this. Under a
flash sale, dozens of requests for one SKU land inside that window.

Reproduce load with `reproduce_failure.py` at the repo root of this lab. Single
requests behave correctly, which is worth knowing before you spend an hour
testing one request at a time.
