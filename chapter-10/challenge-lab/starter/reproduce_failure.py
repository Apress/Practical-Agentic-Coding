"""Reproduce the intermittent checkout failure.

Fires N concurrent checkouts at one low-stock SKU and reports what came back,
plus the inventory audit afterwards. Run it against services you started with
run_services.py, or let it start its own copies with --embedded.

    python reproduce_failure.py --embedded --concurrency 8

What to look at in the output:

  * the status code mix (some 200s, some 409s, sometimes a 500 or a 504)
  * the final audit: does "confirmed orders x units" match the stock that left
    the warehouse, and is "available" ever negative?

Run it a few times. The failure is intermittent by nature, that is the point.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from services._http import GATEWAY_URL, INVENTORY_URL  # noqa: E402


def checkout(index: int, sku: str, quantity: int) -> tuple[int, dict]:
    body = json.dumps(
        {
            "order_id": f"ord_load_{index:03d}",
            "sku": sku,
            "quantity": quantity,
            "amount_cents": 129900,
            "card_token": "tok_test_visa",
        }
    ).encode()
    request = urllib.request.Request(f"{GATEWAY_URL}/checkout", data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("X-Request-Id", f"req_load_{index:03d}")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, json.loads(exc.read() or b"{}")
        except json.JSONDecodeError:
            return exc.code, {"error": "unreadable_body"}
    except (urllib.error.URLError, TimeoutError) as exc:
        return 0, {"error": "client_error", "message": str(exc)}


def audit() -> dict:
    with urllib.request.urlopen(f"{INVENTORY_URL}/inventory/audit", timeout=5) as response:
        return json.loads(response.read() or b"{}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sku", default="FLAGSHIP-001", help="SKU to hammer")
    parser.add_argument("--quantity", type=int, default=1, help="units per order")
    parser.add_argument(
        "--concurrency", type=int, default=8, help="simultaneous checkout requests"
    )
    parser.add_argument(
        "--embedded",
        action="store_true",
        help="start the three services in this process first",
    )
    args = parser.parse_args()

    if args.embedded:
        from run_services import start_all

        start_all()

    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        results = list(
            pool.map(
                lambda i: checkout(i, args.sku, args.quantity),
                range(args.concurrency),
            )
        )

    statuses = Counter(status for status, _ in results)
    confirmed = [body for status, body in results if status == 200]

    print("\n=== checkout results ===")
    for status in sorted(statuses):
        label = {
            200: "confirmed",
            409: "rejected (out of stock)",
            402: "payment declined",
            500: "server error",
            504: "gateway timeout",
            0: "no response",
        }.get(status, "other")
        print(f"  HTTP {status:>3}  x{statuses[status]:<3} {label}")

    for status, body in results:
        if status not in (200, 409):
            print(f"  detail: HTTP {status} {body}")

    report = audit()
    print("\n=== inventory audit ===")
    print(json.dumps(report, indent=2))

    row = report["stock"].get(args.sku, {})
    units_promised = len(confirmed) * args.quantity
    stock_at_start = row.get("initial_on_hand", 0)
    print("\n=== reconciliation ===")
    print(f"  SKU under test:        {args.sku}")
    print(f"  stock at start:        {stock_at_start}")
    print(f"  confirmed orders:      {len(confirmed)} ({units_promised} units promised)")
    print(f"  units committed:       {row.get('committed')}")
    print(f"  units still on hand:   {row.get('on_hand')}")
    print(f"  holds granted (total): {row.get('holds_granted_total')}")
    print(f"  availability now:      {row.get('available')}")
    print(f"  lowest availability:   {row.get('min_available_seen')}")
    print(f"  commits refused as oversold: {report.get('oversold_commits')}")

    trouble = []
    lowest = min(row.get("available", 0), row.get("min_available_seen", 0))
    if lowest < 0:
        trouble.append(
            f"availability went negative (low water mark {lowest}): holds were "
            "granted against stock that was not there"
        )
    if row.get("holds_granted_total", 0) > stock_at_start:
        trouble.append(
            f"inventory handed out {row.get('holds_granted_total')} holds on a "
            f"{stock_at_start}-unit SKU"
        )
    if report.get("oversold_commits"):
        trouble.append(
            f"{report['oversold_commits']} commit(s) refused because stock had "
            "already run out"
        )
    if statuses.get(500):
        trouble.append("at least one checkout returned a 500")
    if statuses.get(504):
        trouble.append("at least one checkout timed out")

    if trouble:
        print("\n  FAILURE REPRODUCED:")
        for item in trouble:
            print(f"    - {item}")
    else:
        print(
            "\n  Clean run. The failure is load dependent: raise --concurrency, "
            "or run again."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
