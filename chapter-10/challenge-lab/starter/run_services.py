"""Start inventory, payment, and gateway in one process.

Each service runs on its own thread with its own port, so you get the same
three-service topology without three terminals.

    python run_services.py

Press Ctrl+C to stop. Use --check to verify all three answer /health and exit.
"""

from __future__ import annotations

import argparse
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from services._http import (  # noqa: E402
    GATEWAY_PORT,
    GATEWAY_URL,
    INVENTORY_PORT,
    INVENTORY_URL,
    PAYMENT_PORT,
    PAYMENT_URL,
    get_logger,
    serve,
)
from services.gateway.app import GatewayHandler  # noqa: E402
from services.inventory.app import InventoryHandler  # noqa: E402
from services.payment.app import PaymentHandler  # noqa: E402

LOG = get_logger("runner")

SERVICES = [
    ("inventory", InventoryHandler, INVENTORY_PORT, INVENTORY_URL),
    ("payment", PaymentHandler, PAYMENT_PORT, PAYMENT_URL),
    ("gateway", GatewayHandler, GATEWAY_PORT, GATEWAY_URL),
]


def start_all() -> None:
    for name, handler, port, _url in SERVICES:
        thread = threading.Thread(
            target=serve,
            args=(handler, port, get_logger(name)),
            name=f"{name}-server",
            daemon=True,
        )
        thread.start()
    time.sleep(0.4)


def health_check() -> bool:
    healthy = True
    for name, _handler, _port, url in SERVICES:
        try:
            with urllib.request.urlopen(f"{url}/health", timeout=2) as response:
                LOG.info("%s health %s", name, response.status)
        except (urllib.error.URLError, TimeoutError) as exc:
            LOG.error("%s health failed: %s", name, exc)
            healthy = False
    return healthy


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="start the services, hit /health on each, then exit",
    )
    args = parser.parse_args()

    start_all()
    ok = health_check()
    if args.check:
        return 0 if ok else 1

    LOG.info("gateway checkout endpoint: %s/checkout", GATEWAY_URL)
    LOG.info("press Ctrl+C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        LOG.info("stopping")
    return 0


if __name__ == "__main__":
    sys.exit(main())
