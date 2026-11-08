#!/usr/bin/env python3
"""
Setup verification script for Chapter 10 hands-on lab.

Checks that all required components are properly configured:
- Docker services (Redis)
- Python dependencies
- Redis connectivity
- Environment variables
- Agent initialization
"""

import sys
import os
import asyncio
from typing import List, Tuple
import importlib.util


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header():
    """Print verification script header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}" + "=" * 60)
    print("Chapter 10 bonus SDK lab - Setup Verification")
    print("=" * 60 + Colors.RESET + "\n")


def print_check(message: str, passed: bool, details: str = ""):
    """Print check result."""
    status = f"{Colors.GREEN}PASS" if passed else f"{Colors.RED}FAIL"
    print(f"{message}... {status}{Colors.RESET}")
    if details:
        print(f"  {details}")


def check_docker_services() -> Tuple[bool, str]:
    """Check if Docker services are running.

    Tries Compose v2 (`docker compose`, what current Docker Desktop ships and
    what the README uses) first, then the legacy standalone `docker-compose`.
    """
    import subprocess

    result = None
    for command in (["docker", "compose", "ps"], ["docker-compose", "ps"]):
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            return False, "Docker command timed out. Is Docker running?"
        except Exception as e:
            return False, f"Error checking Docker: {str(e)}"
        if result.returncode == 0:
            break

    if result is None:
        return False, "Docker not found. Please install Docker Desktop"
    if result.returncode != 0:
        return False, "docker compose ps failed. Is Docker running?"

    output = result.stdout.lower()
    if "redis" in output and "up" in output:
        return True, "Redis container is running"
    return False, "Redis container not running. Run: docker compose up -d"


def check_python_version() -> Tuple[bool, str]:
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"Python 3.11+ required, found {version.major}.{version.minor}.{version.micro}"


def check_dependencies() -> Tuple[bool, str]:
    """Check if required Python packages are installed."""
    required_packages = [
        "anthropic",
        "redis",
        "pydantic",
        "pydantic_settings",
        "dotenv",
        "pytest",
        "pytest_asyncio",
    ]

    missing = []
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            # Report the pip-style name (dashes) rather than the module name
            missing.append(package.replace("_", "-"))

    if missing:
        return False, f"Missing packages: {', '.join(missing)}. Run: pip install -r requirements.txt"
    else:
        return True, f"All {len(required_packages)} required packages installed"


def check_env_file() -> Tuple[bool, str]:
    """Check if .env file exists and has required variables."""
    if not os.path.exists(".env"):
        return False, ".env file not found. Copy .env.example to .env and configure"

    # Read .env file
    required_vars = ["ANTHROPIC_API_KEY"]
    found_vars = {}

    try:
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        found_vars[key.strip()] = value.strip()

        missing = [var for var in required_vars if var not in found_vars or not found_vars[var]]

        if missing:
            return False, f"Missing or empty variables: {', '.join(missing)}"

        # Check if API key looks valid (starts with expected prefix)
        api_key = found_vars.get("ANTHROPIC_API_KEY", "")
        if api_key == "your_key_here" or len(api_key) < 20:
            return False, "ANTHROPIC_API_KEY not configured. Add your actual API key"

        return True, "Environment variables configured"

    except Exception as e:
        return False, f"Error reading .env: {str(e)}"


async def check_redis_connection() -> Tuple[bool, str]:
    """Check Redis connectivity."""
    try:
        from redis import asyncio as aioredis

        # Load config
        from dotenv import load_dotenv
        load_dotenv()

        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))

        # Try to connect
        redis = aioredis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )

        # Test connection
        await redis.ping()
        await redis.aclose()

        return True, f"Connected to Redis at {redis_host}:{redis_port}"

    except ImportError:
        return False, "redis package not installed"
    except ConnectionRefusedError:
        return False, "Cannot connect to Redis. Is it running? (docker compose up -d)"
    except Exception as e:
        return False, f"Redis connection error: {str(e)}"


async def check_message_bus() -> Tuple[bool, str]:
    """Check message bus functionality."""
    try:
        from starter.message_bus import MessageBus
        from dotenv import load_dotenv
        load_dotenv()

        config = {
            "redis_host": os.getenv("REDIS_HOST", "localhost"),
            "redis_port": int(os.getenv("REDIS_PORT", "6379")),
        }

        bus = MessageBus(config)
        await bus.connect()

        # Test publish
        await bus.publish("test_agent", None, "test", {"data": "verification"})

        await bus.disconnect()

        return True, "Message bus operational"

    except Exception as e:
        return False, f"Message bus error: {str(e)}"


async def check_blackboard() -> Tuple[bool, str]:
    """Check blackboard functionality."""
    try:
        from starter.blackboard import Blackboard, TaskState
        from dotenv import load_dotenv
        load_dotenv()

        config = {
            "redis_host": os.getenv("REDIS_HOST", "localhost"),
            "redis_port": int(os.getenv("REDIS_PORT", "6379")),
        }

        blackboard = Blackboard(config)
        await blackboard.initialize()

        # Test post and retrieve
        test_task = TaskState("verify_test", "Test task", status="pending")
        await blackboard.post_task(test_task)

        retrieved = await blackboard.get_task("verify_test")

        # Cleanup
        await blackboard.clear()
        await blackboard.close()

        if retrieved and retrieved.task_id == "verify_test":
            return True, "Blackboard operational"
        else:
            return False, "Blackboard test failed"

    except Exception as e:
        return False, f"Blackboard error: {str(e)}"


async def check_agents() -> Tuple[bool, str]:
    """Check that agents can be initialized."""
    try:
        from starter.dev_agent import DevAgent
        from starter.qa_agent import QAAgent
        from starter.scrum_agent import ScrumAgent
        from dotenv import load_dotenv
        load_dotenv()

        config = {
            "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
            "redis_host": os.getenv("REDIS_HOST", "localhost"),
            "redis_port": int(os.getenv("REDIS_PORT", "6379")),
        }

        # Initialize agents
        dev = DevAgent(config)
        qa = QAAgent(config)
        scrum = ScrumAgent(config)

        # Verify they have correct IDs
        assert dev.agent_id == "dev"
        assert qa.agent_id == "qa"
        assert scrum.agent_id == "scrum"

        return True, "All agents initialized successfully"

    except Exception as e:
        return False, f"Agent initialization error: {str(e)}"


def check_starter_code() -> Tuple[bool, str]:
    """Check that starter code files exist."""
    required_files = [
        "starter/__init__.py",
        "starter/swarm_coordinator.py",
        "starter/base_agent.py",
        "starter/dev_agent.py",
        "starter/qa_agent.py",
        "starter/scrum_agent.py",
        "starter/message_bus.py",
        "starter/blackboard.py",
        "starter/config.py",
    ]

    missing = [f for f in required_files if not os.path.exists(f)]

    if missing:
        return False, f"Missing files: {', '.join(missing)}"
    else:
        return True, f"All {len(required_files)} starter files present"


async def run_all_checks():
    """Run all verification checks."""
    print_header()

    checks = [
        ("Python Version", check_python_version),
        ("Starter Code Files", check_starter_code),
        ("Python Dependencies", check_dependencies),
        ("Environment Variables", check_env_file),
        ("Docker Services", check_docker_services),
    ]

    async_checks = [
        ("Redis Connection", check_redis_connection),
        ("Message Bus", check_message_bus),
        ("Blackboard", check_blackboard),
        ("Agent Initialization", check_agents),
    ]

    results = []

    # Run synchronous checks
    print(f"{Colors.BOLD}Running Setup Checks...{Colors.RESET}\n")
    for name, check_func in checks:
        passed, details = check_func()
        print_check(name, passed, details)
        results.append(passed)

    # Run async checks
    print(f"\n{Colors.BOLD}Running Integration Checks...{Colors.RESET}\n")
    for name, check_func in async_checks:
        passed, details = await check_func()
        print_check(name, passed, details)
        results.append(passed)

    # Summary
    print(f"\n{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    passed_count = sum(results)
    total_count = len(results)

    if all(results):
        print(f"{Colors.GREEN}{Colors.BOLD}All checks passed! ({passed_count}/{total_count}){Colors.RESET}")
        print(f"\n{Colors.GREEN}Setup complete! You're ready to start the exercises.{Colors.RESET}")
        print(f"\nNext steps:")
        print(f"  1. Read starter/README.md for implementation guidance")
        print(f"  2. Implement coordinate_task_manager_pattern() (Exercise 1)")
        print(f"  3. Run tests: pytest starter/tests/test_swarm_coordinator.py::TestManagerPattern -v")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}Some checks failed ({passed_count}/{total_count} passed){Colors.RESET}")
        print(f"\n{Colors.YELLOW}Please fix the issues above before continuing.{Colors.RESET}")
        print(f"\nCommon fixes:")
        print(f"  - Start Docker: docker compose up -d")
        print(f"  - Install dependencies: pip install -r requirements.txt")
        print(f"  - Configure .env: cp .env.example .env (then edit)")
        return 1


def main():
    """Main entry point."""
    try:
        exit_code = asyncio.run(run_all_checks())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Verification cancelled.{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {str(e)}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
