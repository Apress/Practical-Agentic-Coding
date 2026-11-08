#!/usr/bin/env python3
"""
Setup verification script for Governance Pipeline lab (Chapter 12).
Checks that all prerequisites are met before starting exercises.
"""

# Keeps the annotations below from failing on an older Python, so the
# version check can report the problem instead of a TypeError.
from __future__ import annotations

import sys
from pathlib import Path

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def print_check(message: str, passed: bool, details: str = "") -> bool:
    """Print check result with color coding."""
    symbol = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
    print(f"  [{symbol}] {message}")
    if details:
        print(f"         {details}")
    return passed


def check_python_version() -> bool:
    """Check Python version is 3.11+."""
    version = sys.version_info
    success = version >= (3, 11)
    details = ""
    if not success:
        details = f"Found {version.major}.{version.minor}, need 3.11+"
    return print_check(
        f"Python 3.11+ (found {version.major}.{version.minor}.{version.micro})",
        success,
        details,
    )


def check_package(package_name: str, import_name: str | None = None) -> bool:
    """Check if a Python package is importable."""
    name = import_name or package_name
    try:
        __import__(name)
        return print_check(f"Package '{package_name}' installed", True)
    except ImportError:
        return print_check(
            f"Package '{package_name}' installed",
            False,
            "Run: pip install -r requirements.txt",
        )


MODULES = (
    "validators.py",
    "budget.py",
    "audit.py",
    "drift_monitor.py",
    "execution_rail.py",
)


def _check_lab_directory(name: str, label: str) -> bool:
    """Check that a lab directory has all six governance modules."""
    script_dir = Path(__file__).parent
    root = script_dir / name
    required_files = [root / "__init__.py", root / "governance" / "__init__.py"]
    required_files += [root / "governance" / module for module in MODULES]

    missing = [
        str(f.relative_to(script_dir)) for f in required_files if not f.exists()
    ]
    details = f"Missing: {', '.join(missing)}" if missing else ""
    return print_check(label, not missing, details)


def check_starter_directory() -> bool:
    """Check the starter directory you implement."""
    return _check_lab_directory("starter", "Starter files present (your work)")


def check_complete_directory() -> bool:
    """Check the reference solution directory."""
    return _check_lab_directory(
        "complete", "Reference solution present (complete/)"
    )


def main() -> int:
    """Run all verification checks."""
    print("=" * 60)
    print("Chapter 12: Governance Pipeline - Setup Verification")
    print("=" * 60)

    all_passed = True

    print("\nPython Environment:")
    print("-" * 40)
    if not check_python_version():
        all_passed = False

    packages = [
        ("numpy", "numpy"),
        ("scikit-learn", "sklearn"),
        ("pytest", "pytest"),
        ("pytest-asyncio", "pytest_asyncio"),
    ]
    for pkg_name, import_name in packages:
        if not check_package(pkg_name, import_name):
            all_passed = False

    print("\nLab Files:")
    print("-" * 40)
    if not check_starter_directory():
        all_passed = False
    if not check_complete_directory():
        all_passed = False

    print()
    print("=" * 60)
    if all_passed:
        print(f"{GREEN}Setup complete! Ready to start the lab.{RESET}")
        print()
        print("Next steps:")
        print("  1. Read the TODO comments in starter/governance/")
        print("  2. Implement each module following the docstrings")
        print("  3. Run tests: pytest tests/test_governance.py -v")
        print()
        print("Stuck? complete/ has a working version of every module:")
        print("  pytest complete/tests/test_governance.py -v")
        return 0
    else:
        print(f"{RED}Setup incomplete. Please fix issues above.{RESET}")
        print()
        print("Quick fix: pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
