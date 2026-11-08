#!/usr/bin/env python3
"""
Setup verification script for DevMemory hands-on lab.
Verifies all prerequisites before starting exercises.
"""

import sys
import subprocess
from pathlib import Path
from typing import Tuple


def print_status(check: str, passed: bool, message: str = "") -> None:
    label = "PASS" if passed else "FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{label}{reset} {check}")
    if message:
        print(f"  {message}")


def check_python_version() -> Tuple[bool, str]:
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor} (requires 3.11+)"


def check_docker() -> Tuple[bool, str]:
    try:
        result = subprocess.run(
            ["docker", "ps"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return True, "Docker is running"
        return False, "Docker is not running"
    except FileNotFoundError:
        return False, "Docker is not installed"
    except Exception as e:
        return False, str(e)


def chromadb_address() -> Tuple[str, int]:
    """Host and port the tests and demo.py connect to.

    They build DevMemoryConfig with its defaults, so read those defaults from
    starter/config.py instead of hard-coding them here. Falls back to
    localhost:8000 when config.py cannot be loaded (packages not installed).
    """
    import importlib.util

    try:
        spec = importlib.util.spec_from_file_location(
            "devmemory_config", Path("starter") / "config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        defaults = module.DevMemoryConfig()
        return defaults.chromadb_host, defaults.chromadb_port
    except Exception:
        return "localhost", 8000


def check_chromadb_service() -> Tuple[bool, str]:
    """Ping the Chroma heartbeat endpoint.

    Chroma 1.x serves /api/v2/... and answers the older /api/v1/... paths with
    HTTP 410 Gone, so try v2 first and fall back to v1 for older servers.
    """
    from urllib.request import urlopen
    from urllib.error import HTTPError, URLError

    host, port = chromadb_address()
    for path in ("/api/v2/heartbeat", "/api/v1/heartbeat"):
        try:
            response = urlopen(f"http://{host}:{port}{path}", timeout=5)
            if response.status == 200:
                return True, f"ChromaDB accessible at {host}:{port} ({path})"
        except HTTPError:
            # Wrong API version for this server: try the next path.
            continue
        except (URLError, OSError):
            return False, (
                f"ChromaDB not reachable at {host}:{port} "
                "(run: docker compose up -d)"
            )

    return False, (
        f"ChromaDB answered at {host}:{port} but not on /api/v2/heartbeat or "
        "/api/v1/heartbeat. Check the container image version."
    )


def check_dependencies() -> Tuple[bool, str]:
    required = ["mem0", "chromadb", "pydantic", "dotenv", "pytest"]
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if not missing:
        return True, "All required packages installed"
    return False, f"Missing: {', '.join(missing)}"


def check_env_file() -> Tuple[bool, str]:
    if Path(".env").exists():
        return True, ".env file found"
    if Path(".env.example").exists():
        return False, ".env not found (run: cp .env.example .env)"
    return False, ".env.example not found"


PLACEHOLDER_KEY = "your_openai_api_key_here"


def ollama_provider_count() -> int:
    """How many Mem0 config blocks in starter/memory_core.py name Ollama.

    Two (llm and embedder) is the fully local setup from the README's
    Prerequisites section; zero is the OpenAI default.
    """
    import re

    try:
        source = (Path("starter") / "memory_core.py").read_text(encoding="utf-8")
    except OSError:
        return 0
    return len(re.findall(r"""["']provider["']\s*:\s*["']ollama["']""", source))


def ollama_reachable() -> Tuple[bool, str]:
    """Ask the local Ollama server for its model list (no model call)."""
    import os
    from urllib.request import urlopen

    base = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    if not base.startswith("http"):
        base = f"http://{base}"
    try:
        urlopen(f"{base}/api/tags", timeout=5)
        return True, base
    except OSError:
        return False, base


def check_model_access() -> Tuple[bool, str]:
    """Check that Mem0 has a model to call: an OpenAI key, or Ollama.

    Mem0's default LLM and embedder are OpenAI, so DevMemory needs a key unless
    you switch to Ollama (see the README). The key check deliberately reads only
    the environment, not .env, because Mem0 reads the key from the environment
    too: a key that sits in .env but was never exported still fails at runtime.
    No model request is made here, so this check costs nothing.
    """
    import os

    key = os.getenv("OPENAI_API_KEY", "").strip()
    has_key = bool(key) and key != PLACEHOLDER_KEY

    ollama_blocks = ollama_provider_count()
    if ollama_blocks:
        reachable, where = ollama_reachable()
        if not reachable:
            return False, (
                f"starter/memory_core.py points Mem0 at Ollama, but nothing "
                f"answers at {where}. Start it with: ollama serve"
            )
        if ollama_blocks >= 2:
            return True, f"Mem0 uses Ollama for the LLM and embedder ({where})"
        if has_key:
            return True, (
                f"Ollama answers at {where}; OPENAI_API_KEY covers the block "
                "that still uses OpenAI"
            )
        return False, (
            "Only one of the llm and embedder blocks points at Ollama, so the "
            "other still uses OpenAI. Export OPENAI_API_KEY or switch both"
        )

    if has_key:
        return True, "OPENAI_API_KEY is set in the environment"

    detail = (
        "OPENAI_API_KEY not exported. Run: export OPENAI_API_KEY=<your key>, "
        "or switch Mem0 to Ollama (see README, Prerequisites)"
    )
    if key == PLACEHOLDER_KEY:
        detail = (
            "OPENAI_API_KEY is still the .env.example placeholder. Replace it "
            "with your real key and export it"
        )
    return False, detail


def check_starter_files() -> Tuple[bool, str]:
    required = [
        "starter/__init__.py",
        "starter/config.py",
        "starter/memory_core.py",
        "starter/capture.py",
        "starter/scopes.py",
        "starter/trust.py",
    ]
    missing = [f for f in required if not Path(f).exists()]
    if not missing:
        return True, "All starter files present"
    return False, f"Missing: {', '.join(missing)}"


def main() -> int:
    print("=" * 60)
    print("DevMemory Lab Setup Verification")
    print("=" * 60)
    print()

    checks = [
        ("Python version", check_python_version),
        ("Docker running", check_docker),
        ("Starter files", check_starter_files),
        ("Python dependencies", check_dependencies),
        ("Environment file", check_env_file),
        ("Model access (OpenAI key or Ollama)", check_model_access),
        ("ChromaDB service", check_chromadb_service),
    ]

    results = []
    for name, check_func in checks:
        passed, message = check_func()
        print_status(name, passed, message)
        results.append(passed)

    print()
    print("=" * 60)

    if all(results):
        print("\033[92mAll checks passed! Ready to start.\033[0m")
        print()
        print("Next: Open exercises/exercise-1-memory-core.md")
        return 0
    else:
        print("\033[91mSome checks failed. Fix the issues above.\033[0m")
        print()
        print("Common fixes:")
        print("  pip install -r requirements.txt")
        print("  docker compose up -d")
        print("  cp .env.example .env")
        print("  export OPENAI_API_KEY=<your key>")
        return 1


if __name__ == "__main__":
    sys.exit(main())
