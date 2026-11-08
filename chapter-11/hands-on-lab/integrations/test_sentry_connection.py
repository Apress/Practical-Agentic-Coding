#!/usr/bin/env python3
"""
Test Sentry Connection

Quick verification script to ensure Sentry is properly configured.
Run this before starting Exercise 3 to verify your setup.

Usage:
    python integrations/test_sentry_connection.py

Expected output if configured correctly (abridged):
    [PASS] Environment variables loaded from .env
    [PASS] Sentry SDK installed
    [PASS] SENTRY_DSN configured
    [PASS] Sentry initialized successfully
    [PASS] Test event sent successfully
    Then check your Sentry dashboard: https://sentry.io/
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import from starter
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 70)
print("Sentry Connection Test")
print("=" * 70)
print()

# Step 1: Check environment variables
print("Step 1: Checking environment configuration...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[PASS] Environment variables loaded from .env")
except ImportError:
    print("[WARN] python-dotenv not installed, using system environment")
except Exception as e:
    print(f"[WARN] Error loading .env: {e}")

print()

# Step 2: Check Sentry SDK installation
print("Step 2: Checking Sentry SDK installation...")
try:
    import sentry_sdk
    print(f"[PASS] Sentry SDK installed (version: {sentry_sdk.VERSION})")
except ImportError:
    print("[FAIL] Sentry SDK not installed")
    print("   Run: pip install sentry-sdk")
    sys.exit(1)

print()

# Step 3: Check DSN configuration
print("Step 3: Checking DSN configuration...")
dsn = os.getenv("SENTRY_DSN", "")

if not dsn:
    print("[FAIL] SENTRY_DSN not set in environment")
    print("   Add to .env file:")
    print("   SENTRY_DSN=https://your-key@o123.ingest.sentry.io/456")
    print()
    print("   Get your DSN from: https://sentry.io/")
    print("   Settings > Projects > Your Project > Client Keys (DSN)")
    sys.exit(1)

if dsn == "PLACEHOLDER_DSN" or dsn.startswith("your-") or dsn.startswith("https://your-"):
    print("[WARN] SENTRY_DSN is still a placeholder")
    print(f"   Current value: {dsn}")
    print()
    print("   Replace with actual DSN from Sentry:")
    print("   1. Go to https://sentry.io/")
    print("   2. Select your project")
    print("   3. Go to Settings > Client Keys (DSN)")
    print("   4. Copy the DSN")
    print("   5. Add to .env file")
    print()
    print("   See integrations/sentry_setup.md for detailed instructions")
    sys.exit(1)

# Basic DSN format validation
if not dsn.startswith("https://") or "sentry.io" not in dsn:
    print(f"[WARN] DSN format looks incorrect: {dsn[:50]}...")
    print("   Expected format: https://[key]@o[org].ingest.sentry.io/[project]")
    print()
    print("   Double-check your DSN from Sentry dashboard")
else:
    # Mask most of the DSN for security in output
    masked_dsn = dsn[:30] + "..." + dsn[-10:]
    print(f"[PASS] SENTRY_DSN configured: {masked_dsn}")

print()

# Step 4: Initialize Sentry
print("Step 4: Initializing Sentry SDK...")
environment = os.getenv("SENTRY_ENVIRONMENT", "lab")
traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))

try:
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=traces_sample_rate,
        # Enable debug mode for this test
        debug=False,
        # Disable sending events in test mode if desired
        # sample_rate=0.0 would disable
    )
    print(f"[PASS] Sentry initialized successfully")
    print(f"  - Environment: {environment}")
    print(f"  - Traces sample rate: {traces_sample_rate}")
except Exception as e:
    print(f"[FAIL] Failed to initialize Sentry: {e}")
    print()
    print("   Common causes:")
    print("   - Invalid DSN format")
    print("   - Network connectivity issues")
    print("   - Firewall blocking sentry.io")
    sys.exit(1)

print()

# Step 5: Send test event
print("Step 5: Sending test event to Sentry...")
try:
    # Send a test message
    event_id = sentry_sdk.capture_message(
        "Test event from Zero-Downtime Deployer Lab",
        level="info"
    )

    print("[PASS] Test event sent successfully")
    print(f"  - Event ID: {event_id}")
    print()

    # Send a test event with context. new_scope() is the sentry-sdk 2.x API
    # (configure_scope() is deprecated); the tags apply to events captured
    # inside the block.
    with sentry_sdk.new_scope() as scope:
        scope.set_tag("test", "connection_test")
        scope.set_tag("source", "test_sentry_connection.py")
        scope.set_context("test_context", {
            "message": "This is a test event to verify Sentry integration",
            "lab": "chapter-11-hands-on-lab",
        })
        event_id_2 = sentry_sdk.capture_message(
            "Test event with context and tags",
            level="info"
        )
    print("[PASS] Test event with context sent")
    print(f"  - Event ID: {event_id_2}")

except Exception as e:
    print(f"[FAIL] Failed to send test event: {e}")
    print()
    print("   This might indicate:")
    print("   - Network issues connecting to Sentry")
    print("   - Invalid API credentials")
    print("   - Rate limiting (unlikely with free tier)")
    sys.exit(1)

print()
print("=" * 70)
print("All checks passed.")
print("=" * 70)
print()
print("Next Steps:")
print("1. Check your Sentry dashboard: https://sentry.io/")
print("2. Navigate to your project: zero-downtime-deployer-lab")
print("3. Click 'Issues' in the left sidebar")
print("4. You should see 2 test events")
print("5. Click on an event to see details, tags, and context")
print()
print("If you see the events in Sentry:")
print("- Sentry is fully configured and working")
print("- You're ready to start Exercise 3")
print("- Follow exercises/exercise-3-sentry.md")
print()
print("If you don't see the events:")
print("- Wait 30-60 seconds (Sentry has slight ingestion delay)")
print("- Check the Issues tab (not Alerts or other sections)")
print("- Verify time range in Sentry UI (should be 'Last 24 hours')")
print("- Try running this script again")
print()
print("For detailed setup help, see:")
print("- integrations/sentry_setup.md")
print("- integrations/observability_setup.md")
print("=" * 70)
