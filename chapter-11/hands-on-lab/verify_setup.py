#!/usr/bin/env python3
"""
Setup verification script for Zero-Downtime Deployer lab.

Checks the prerequisites before you start the exercises. Two kinds of check:

- Required: without these the exercises will not run.
- Optional: only needed if you go beyond the default mock setup (a real
  Kubernetes cluster, or an Anthropic API key for your own agent extensions).
  These print a note, not a failure.

Exit code is 0 when every required check passes.
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Tuple

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_check(message: str, passed: bool, details: str = ""):
    """Print check result with color coding."""
    symbol = f"[{GREEN}PASS{RESET}]" if passed else f"[{RED}FAIL{RESET}]"
    print(f"{symbol} {message}")
    if details:
        print(f"  {details}")
    return passed


def print_optional(message: str, present: bool, details: str = ""):
    """Print an optional check. Never counts as a failure."""
    symbol = f"[{GREEN}PASS{RESET}]" if present else f"[{YELLOW}SKIP{RESET}]"
    print(f"{symbol} {message}")
    if details:
        print(f"  {details}")
    return True


def check_docker() -> bool:
    """Check if Docker is running. Optional: only the extras need it."""
    note = (
        "Only needed for the optional Prometheus and Grafana services. "
        "The exercises run without it."
    )
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=10
        )
        running = result.returncode == 0
        return print_optional(
            "Docker running (optional)", running, "" if running else note
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return print_optional("Docker running (optional)", False, note)


def check_kubernetes() -> bool:
    """Check if a Kubernetes cluster is accessible. Optional for this lab."""
    note = (
        "Not needed with USE_MOCK_INFRASTRUCTURE=true (the default). "
        "Enable Kubernetes in Docker Desktop only if you set it to false."
    )
    try:
        result = subprocess.run(
            ["kubectl", "cluster-info"],
            capture_output=True,
            timeout=5
        )
        reachable = result.returncode == 0
        return print_optional(
            "Kubernetes cluster reachable (optional)",
            reachable,
            "" if reachable else note
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return print_optional(
            "Kubernetes cluster reachable (optional)", False, note
        )


def check_python_version() -> bool:
    """Check Python version is 3.11+."""
    version = sys.version_info
    success = version >= (3, 11)
    details = ""
    if not success:
        details = f"Python {version.major}.{version.minor} found, need 3.11+"
    return print_check("Python 3.11+ installed", success, details)


def check_dependencies() -> bool:
    """Check if the packages the exercises import are installed."""
    required_packages = [
        "pytest",
        "pytest_asyncio",
        "dotenv"
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    success = len(missing) == 0
    details = ""
    if not success:
        details = f"Missing {', '.join(missing)}. Run: pip install -r requirements.txt"
    return print_check("Python dependencies installed", success, details)


def check_environment_file() -> bool:
    """Check if .env file exists."""
    env_file = Path(".env")
    success = env_file.exists()
    details = ""
    if not success:
        details = "Run: cp .env.example .env"
    return print_check("Environment file (.env) exists", success, details)


def check_anthropic_key() -> bool:
    """
    Report whether an Anthropic API key is present. Optional for this lab.

    The exercises run entirely against mock infrastructure and never call the
    API. A key only matters if you extend the deployer with your own LLM calls.
    No request is made here, so nothing is billed.
    """
    # python-dotenv may not be installed yet; the dependency check above
    # already reports that, so read the environment without it.
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    api_key = os.getenv("ANTHROPIC_API_KEY")
    present = bool(api_key) and api_key != "your_anthropic_api_key_here"
    return print_optional(
        "Anthropic API key set (optional)",
        present,
        "" if present else "Not needed for the exercises; add it only if you "
                           "extend the deployer with your own model calls."
    )


def _compose_command() -> list:
    """Pick whichever Compose CLI is available: the plugin or the old binary."""
    for candidate in (["docker", "compose"], ["docker-compose"]):
        try:
            result = subprocess.run(
                candidate + ["version"], capture_output=True, timeout=10
            )
            if result.returncode == 0:
                return candidate
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    return []


def check_docker_services() -> bool:
    """Check if the Compose services are running. Optional for the exercises."""
    note = (
        "Only needed for the optional Prometheus and Grafana views. "
        "Start with: docker compose up -d"
    )
    compose = _compose_command()
    if not compose:
        return print_optional("Lab services running (optional)", False, note)

    try:
        result = subprocess.run(
            compose + ["ps", "-q"], capture_output=True, timeout=10
        )
        container_ids = [
            line for line in result.stdout.decode().strip().split("\n") if line
        ]
        running = len(container_ids) > 0
        return print_optional(
            "Lab services running (optional)", running, "" if running else note
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return print_optional("Lab services running (optional)", False, note)


def check_starter_files() -> bool:
    """Check if starter files exist."""
    required_files = [
        "starter/deployer.py",
        "starter/infrastructure_client.py",
        "starter/health_monitor.py",
    ]

    missing = [f for f in required_files if not Path(f).exists()]
    success = len(missing) == 0
    details = ""
    if not success:
        details = f"Missing files: {', '.join(missing)}"

    return print_check("Starter files present", success, details)


def main():
    """Run all checks."""
    print("=" * 60)
    print("Zero-Downtime Deployer - Setup Verification")
    print("=" * 60)
    print()

    checks = [
        ("Required for the exercises", [
            check_python_version,
            check_dependencies,
            check_environment_file,
            check_starter_files,
        ]),
        ("Optional extras", [
            check_docker,
            check_docker_services,
            check_kubernetes,
            check_anthropic_key,
        ]),
    ]

    all_passed = True

    for section_name, section_checks in checks:
        print(f"\n{section_name}:")
        print("-" * 40)

        for check in section_checks:
            if not check():
                all_passed = False

    print()
    print("=" * 60)

    if all_passed:
        print(f"{GREEN}Setup complete. Ready to start the exercises.{RESET}")
        print()
        print("Next steps:")
        print("  1. Read exercises/exercise-1-canary.md")
        print("  2. Implement validate_canary() in starter/deployer.py")
        print("  3. Run tests: pytest starter/tests/ -v -k canary")
        return 0
    else:
        print(f"{RED}Setup incomplete. Fix the failed checks above.{RESET}")
        print()
        print("Common fixes:")
        print("  - Create the .env file: cp .env.example .env")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Run from the hands-on-lab directory, not a subdirectory")
        return 1


if __name__ == "__main__":
    sys.exit(main())
