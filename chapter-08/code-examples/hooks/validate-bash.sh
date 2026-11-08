#!/bin/bash
# validate-bash.sh
# PreToolUse hook to block dangerous Bash commands
#
# This hook intercepts Bash commands before execution and blocks
# operations that could damage the system or violate governance rules.
#
# Exit codes:
#   0 - Command is safe, proceed
#   2 - Command is blocked, show error to user
#
# Usage:
#   Configure in .claude/settings.json as a PreToolUse hook for Bash tool

set -e

# Read tool input from stdin (JSON format)
INPUT=$(cat)
# Fail closed if jq is unavailable. A blocking hook that cannot parse its input
# must block, not wave the operation through: exit codes other than 0 and 2 are
# treated as non-blocking warnings, so returning jq's 127 would let the
# operation run unchecked.
if ! command -v jq >/dev/null 2>&1; then
    echo "BLOCKED: this hook requires jq, which is not installed." >&2
    echo "Install it (apt install jq / brew install jq) or remove the hook from .claude/settings.json." >&2
    exit 2
fi


# Extract the command from Bash tool input
# Use // empty to handle missing field gracefully
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# If no command, allow (not a Bash operation)
if [ -z "$COMMAND" ]; then
    exit 0
fi

echo "Validating command: ${COMMAND:0:80}..." >&2

# =============================================================================
# DANGEROUS PATTERNS - These commands will be BLOCKED (exit 2)
# =============================================================================

# Pattern 1: Root filesystem deletion
if echo "$COMMAND" | grep -qE "rm\s+(-rf|-fr|-r\s+-f|-f\s+-r)\s+/\*?\s*$"; then
    echo "BLOCKED: Attempting to delete root filesystem" >&2
    exit 2
fi

# Pattern 2: Home directory deletion
if echo "$COMMAND" | grep -qE "rm\s+(-rf|-fr)\s+~"; then
    echo "BLOCKED: Attempting to delete home directory" >&2
    exit 2
fi

# Pattern 3: Wildcard deletion at dangerous paths
if echo "$COMMAND" | grep -qE "rm\s+(-rf|-fr)\s+(/usr|/var|/etc|/home|/opt)\s*$"; then
    echo "BLOCKED: Attempting to delete system directory" >&2
    exit 2
fi

# Pattern 4: Force push to git
if echo "$COMMAND" | grep -qE "git\s+push\s+.*--force"; then
    echo "BLOCKED: Force push is prohibited" >&2
    exit 2
fi

# Pattern 5: Hard reset
if echo "$COMMAND" | grep -qE "git\s+reset\s+--hard"; then
    echo "BLOCKED: Hard reset is prohibited" >&2
    exit 2
fi

# Pattern 6: World-writable permissions
if echo "$COMMAND" | grep -qE "chmod\s+(-R\s+)?777"; then
    echo "BLOCKED: Setting world-writable permissions (777) is prohibited" >&2
    exit 2
fi

# Pattern 7: Piped execution from internet
if echo "$COMMAND" | grep -qE "curl.*\|\s*(sh|bash)"; then
    echo "BLOCKED: Piping curl output to shell is prohibited" >&2
    exit 2
fi

if echo "$COMMAND" | grep -qE "wget.*\|\s*(sh|bash)"; then
    echo "BLOCKED: Piping wget output to shell is prohibited" >&2
    exit 2
fi

# Pattern 8: Writing to block devices
if echo "$COMMAND" | grep -qE ">\s*/dev/sd"; then
    echo "BLOCKED: Writing to block device is prohibited" >&2
    exit 2
fi

if echo "$COMMAND" | grep -qE "dd.*of=/dev"; then
    echo "BLOCKED: Using dd to write to device is prohibited" >&2
    exit 2
fi

# Pattern 9: Filesystem formatting
if echo "$COMMAND" | grep -qE "mkfs"; then
    echo "BLOCKED: Filesystem formatting is prohibited" >&2
    exit 2
fi

# Pattern 10: Fork bombs
if echo "$COMMAND" | grep -qE ":\(\)\{.*\}.*:"; then
    echo "BLOCKED: Fork bomb detected" >&2
    exit 2
fi

# =============================================================================
# SUDO RESTRICTIONS - Block specific dangerous sudo commands
# =============================================================================

BLOCKED_SUDO=(
    "sudo rm"
    "sudo dd"
    "sudo shutdown"
    "sudo reboot"
    "sudo systemctl stop"
    "sudo systemctl disable"
    "sudo passwd"
    "sudo userdel"
    "sudo iptables -F"
    "sudo ufw disable"
)

for pattern in "${BLOCKED_SUDO[@]}"; do
    if echo "$COMMAND" | grep -qF "$pattern"; then
        echo "BLOCKED: Dangerous sudo command: $pattern" >&2
        exit 2
    fi
done

# =============================================================================
# WARNINGS - These will show a warning but allow the command
# =============================================================================

# Warn about rm -rf in general (but allow if not targeting system dirs)
if echo "$COMMAND" | grep -qE "rm\s+(-rf|-fr)"; then
    echo "WARNING: rm -rf detected - be cautious with this command" >&2
fi

# Warn about sudo usage
if echo "$COMMAND" | grep -qE "^sudo\s"; then
    echo "WARNING: sudo command - requires elevated privileges" >&2
fi

# =============================================================================
# ALLOW - Command passed all checks
# =============================================================================

echo "Command validated successfully" >&2
exit 0
