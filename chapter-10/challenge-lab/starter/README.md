# Starter scaffolds: intermittent checkout failures

Reference: Chapter 10, Section 10.8.

Your agent team investigates this codebase. It has:

- three small services
- a set of production logs from the incident
- a shared findings board to fill in

Everything here is Python standard library. You need no pip install, no
Docker, and no API keys. The services are small on purpose, so an agent (and
you) can read all of them.

## The scenario

You are on call. Checkout fails intermittently in production. The overall error
rate is in the low single digits. It spikes during flash sales.

What the support tickets say:

- Customers see "could not confirm the order" and an HTTP 500. Some of them
  were charged and then refunded within seconds. That generates its own angry
  ticket.
- A smaller group sees an HTTP 504 gateway timeout instead. Those customers
  were never charged.
- Twice, warehouse staff picked an order for a SKU the system said was in
  stock. They found an empty shelf.

What the previous on-call engineer wrote on the ticket:

> Cannot reproduce. Tried 50 checkouts in a row against staging, all passed.
> The 500 comes out of the gateway logs, so probably a gateway problem. Payment
> latency also looks bad in the same window, could be the processor. Reassigning.

The failing service appears to change between requests. Watch for this trap.
A single agent finds one plausible explanation, writes it up, and stops.

## What is here

```text
starter/
├── README.md                 # this file
├── findings.md               # shared investigation board, you fill it in
├── run_services.py           # starts all three services on one machine
├── reproduce_failure.py      # concurrency harness plus a reconciliation report
├── logs/
│   ├── gateway.log           # production traces from the 2026-07-18 incident
│   ├── inventory.log
│   └── payment.log
└── services/
    ├── _http.py              # shared JSON-over-HTTP helpers
    ├── gateway/app.py        # API gateway, owns the checkout flow and retries
    ├── inventory/app.py      # inventory HTTP surface
    ├── inventory/reservation.py  # the reservation ledger
    ├── inventory/NOTES.md    # inventory team notes and open tickets
    └── payment/app.py        # payment service, wraps a card processor
```

## How checkout works

The gateway orchestrates three calls:

1. `POST /reservations` on inventory, to place a soft hold on stock.
2. `POST /charges` on payment, to charge the card. Retried once on timeout,
   with an idempotency key.
3. `POST /reservations/commit` on inventory, to turn the hold into a real stock
   decrement.

If step 2 fails, the gateway releases the hold. If step 3 fails, it refunds the
charge. Both compensating actions are logged.

## Run it

Python 3.11 or newer. From this directory:

```bash
python run_services.py
```

This starts each service on its own thread:

- inventory on port 8081
- payment on 8082
- the gateway on 8080

Use `--check` to verify that all three answer `/health`, then exit. Override
any port with `INVENTORY_PORT`, `PAYMENT_PORT`, or `GATEWAY_PORT`.

Port collision: the bonus SDK lab's Redis Commander (`../../hands-on-lab/`)
also binds port 8081. If that Docker stack is still up, stop it
(`docker compose down` there) or set `INVENTORY_PORT` here.

A single successful checkout, in another terminal:

```bash
curl -s -X POST http://127.0.0.1:8080/checkout \
  -H 'Content-Type: application/json' \
  -H 'X-Request-Id: req_manual_001' \
  -d '{"order_id":"ord_1","sku":"HEADSET-77","quantity":1,"amount_cents":8900,"card_token":"tok_test_visa"}'
```

Inspect inventory state at any time:

```bash
curl -s http://127.0.0.1:8081/inventory/audit
curl -s http://127.0.0.1:8082/payment/stats
```

These `curl` lines use bash quoting. On Windows, run them in WSL or Git Bash.
`reproduce_failure.py` below drives the same endpoints from Python on any
platform.

## Reproduce the failure

One request at a time does not reproduce it. The previous engineer tried that.
Send concurrent requests at a low-stock SKU:

```bash
python reproduce_failure.py --embedded --concurrency 8
```

`--embedded` starts its own copies of the three services. You do not need
`run_services.py` running. The script prints:

- the status code mix
- the inventory audit
- a reconciliation summary that compares stock at the start against what the
  system actually handed out

`FLAGSHIP-001` starts with 3 units. Watch what happens when 8 people try to buy
it at once. Then try the same thing against `CABLE-9`, which starts with 500:

```bash
python reproduce_failure.py --embedded --concurrency 30 --sku CABLE-9
```

Compare those two runs. The difference is a large part of the investigation.

Try these three settings while you investigate:

| Variable | Default | Effect |
|----------|---------|--------|
| `INVENTORY_WRITE_LATENCY_MS` | 15 | Simulated inventory database write time |
| `PAYMENT_POOL_SIZE` | 3 | Card processor connections, lower means more queueing |
| `GATEWAY_PAYMENT_TIMEOUT_S` | 1.0 | How long the gateway waits on a charge |

## Your task

Create an agent team with three teammates, each carrying one hypothesis:

```text
Create an agent team to investigate checkout failures.
Spawn 3 teammates:
- Payment investigator (hypothesis: payment gateway timeout under load)
- Inventory investigator (hypothesis: race condition on stock check)
- Gateway investigator (hypothesis: request header corruption on retry)
Have them share findings and try to disprove each other's theories.
Update a shared findings.md with the consensus.
```

In each teammate's spawn prompt, tell it to read only its own service directory
plus `logs/`. Then no single agent can see the whole picture alone, and the
teammates must exchange findings.

Claude Code enforces which tools a teammate has. It does not enforce which
directories a teammate reads. The boundary holds only while the teammates
follow their instructions.

Two of these three hypotheses are wrong. All three have real supporting
evidence in the code and the logs. This is why a single agent stops early. The
hypothesis still standing after peer challenge is your root cause.

### What your team must produce

- `findings.md`, filled in by all three teammates. One teammate must not write
  it alone.
- At least two entries in the Challenges section. In each, one teammate
  presents evidence against another's hypothesis. The owner answers it, by
  conceding or by pushing back with counter-evidence. Ignoring a challenge is
  a fail.
- A conclusion that does three things:
  - names the root cause, down to the file and function
  - explains why the symptom appears in a different service than the defect
  - says how each rejected hypothesis was ruled out
- A proposed fix and a way to verify it. To verify, apply the fix and re-run
  `reproduce_failure.py`.

### Where to look

1. Start with `logs/`. Correlate the three files on `request_id`. Every
   interesting request appears in more than one file. The sequence across
   files tells you more than any single line.
2. Then read the code for the service the logs point at.

The `logs/*.log` files carry comment lines that start with `#`. The on-call
engineer added them during triage. Treat them as observations. They are not
verdicts.

## Bonus challenge

Spawn a fourth teammate whose whole job is devil's advocacy. It takes each
hypothesis on the board and looks for evidence against it. Give it Read and
Grep across all three services.

Compare the investigation quality against your first run:

- Count how many hypotheses got challenged.
- Note how early the wrong ones were dropped.

## When you are done

`../solution/ROOT-CAUSE.md` has:

- the answer key
- the reasoning your team should have reached
- a rubric for grading the conclusion and the coordination

Read it only after your team has written its conclusion.
