#!/bin/bash
# .claude/hooks/validate-bash-command.sh
#
# PreToolUse hook to block dangerous Bash commands before execution.
# Prevents accidental destructive operations during development.

set -e

# Read tool input from stdin
INPUT=$(cat)

# Fail closed if jq is unavailable. A security hook that cannot parse its input
# must block, not wave the command through: exit codes other than 0 and 2 are
# treated as non-blocking warnings, so returning jq's 127 would let a dangerous
# command run.
if ! command -v jq >/dev/null 2>&1; then
    echo "BLOCKED: this safety hook requires jq, which is not installed." >&2
    echo "Install it (apt install jq / brew install jq) or remove the hook from .claude/settings.json." >&2
    exit 2
fi

# Extract the command from Bash tool input
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# If no command, allow (not a Bash operation)
if [ -z "$COMMAND" ]; then
    exit 0
fi

# Dangerous patterns to block (POSIX ERE, matched case-insensitively).
# Each pattern has a reason for blocking.
#
# Regex metacharacters are escaped (\., \*, \|, \$) and destructive-target
# patterns are anchored to the end of the command, so project-scoped
# deletions such as "rm -rf ./build" or "rm -rf /tmp/test" fall through to
# the warning branch below instead of being blocked here.
declare -A DANGEROUS_PATTERNS=(
    ['rm -rf /\*?[[:space:]]*$']="Attempting to delete root filesystem"
    ['rm -rf ~']="Attempting to delete home directory"
    ['rm -rf \*']="Attempting to delete all files with wildcard"
    ['rm -rf \.[/.]?[[:space:]]*$']="Attempting to delete current directory recursively"
    ['rm -rf \.\*']="Attempting to delete all dotfiles with wildcard"
    ['rm -rf \$']="Attempting to delete with variable expansion"
    ['sudo rm']="Using sudo with rm (dangerous deletion)"
    ['sudo dd']="Using sudo with dd (can destroy data)"
    ['chmod -R 777']="Setting world-writable permissions recursively"
    ['chmod 777']="Setting world-writable permissions"
    ['curl.*\| *sh']="Piping curl output to shell (security risk)"
    ['curl.*\| *bash']="Piping curl output to bash (security risk)"
    ['wget.*\| *sh']="Piping wget output to shell (security risk)"
    ['wget.*\| *bash']="Piping wget output to bash (security risk)"
    ['> */dev/sd']="Writing to block device (data loss risk)"
    ['mkfs']="Formatting filesystem (data loss)"
    ['dd if=.*of=/dev']="Using dd to write to device (data loss)"
    [':\(\)\{.*\}.*:']="Fork bomb (system crash)"
    ['sudo.*passwd']="Changing passwords (security risk)"
    ['sudo.*userdel']="Deleting users (security risk)"
)

# Additional high-risk sudo commands
SUDO_COMMANDS=(
    "sudo shutdown"
    "sudo reboot"
    "sudo systemctl stop"
    "sudo systemctl disable"
    "sudo iptables -F"
    "sudo ufw disable"
)

echo " Validating Bash command: ${COMMAND:0:80}..." >&2

# Check against dangerous patterns
for pattern in "${!DANGEROUS_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        echo "" >&2
        echo " BLOCKED: Dangerous command detected!" >&2
        echo "   Reason: ${DANGEROUS_PATTERNS[$pattern]}" >&2
        echo "   Pattern: $pattern" >&2
        echo "" >&2
        echo "   Command: $COMMAND" >&2
        echo "" >&2
        echo "   This command has been blocked for safety." >&2
        echo "   If you need to run this command, please:" >&2
        echo "   1. Review the command carefully" >&2
        echo "   2. Run it manually in a terminal" >&2
        echo "   3. Consider using safer alternatives" >&2
        exit 2
    fi
done

# Check specific sudo commands
for sudo_cmd in "${SUDO_COMMANDS[@]}"; do
    if echo "$COMMAND" | grep -qF "$sudo_cmd"; then
        echo "" >&2
        echo " BLOCKED: Dangerous sudo command detected!" >&2
        echo "   Command: $sudo_cmd" >&2
        echo "" >&2
        echo "   Full command: $COMMAND" >&2
        echo "" >&2
        echo "   System-altering sudo commands are blocked." >&2
        echo "   Please run this manually if necessary." >&2
        exit 2
    fi
done

# Check for any rm with suspicious flags
if echo "$COMMAND" | grep -qE "rm.* (-rf|-fr|-r -f|-f -r)"; then
    # Check if it's targeting system directories, root, or wildcards.
    # Root is anchored to end of command so paths like /tmp/test stay allowed.
    if echo "$COMMAND" | grep -qE "(rm.* /\*?[[:space:]]*$|rm.* /usr|rm.* /var|rm.* /etc|rm.* /home|rm.* \*|rm.* ~)"; then
        echo "" >&2
        echo " BLOCKED: Recursive deletion of critical path detected!" >&2
        echo "   Command: $COMMAND" >&2
        echo "" >&2
        echo "   Blocking deletion of:" >&2
        echo "   - System directories (/usr, /var, /etc, /home)" >&2
        echo "   - Root directory (/)" >&2
        echo "   - Wildcards (*)" >&2
        echo "   - Home directory (~)" >&2
        exit 2
    fi
fi

# Warn about rm -rf in project directories (but allow)
if echo "$COMMAND" | grep -qE "rm -rf"; then
    echo "  WARNING: rm -rf detected in command" >&2
    echo "   Command will proceed, but be cautious!" >&2
    echo "   Target: $COMMAND" >&2
fi

# Warn about sudo usage (but allow if not in dangerous list)
if echo "$COMMAND" | grep -qE "^sudo "; then
    echo "  WARNING: sudo command detected" >&2
    echo "   Command will proceed, but requires elevated privileges" >&2
fi

echo " Command validation passed" >&2

# Allow the operation
exit 0
