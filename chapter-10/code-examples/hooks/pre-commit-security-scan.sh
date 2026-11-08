#!/bin/bash
# .claude/hooks/pre-commit-security-scan.sh
# Blocks `git commit` when the security scan reports high-severity findings.
# Wired as the PreToolUse hook on Bash(git commit*) in quality-gates-settings.json.
# Reference: Chapter 10, Section 10.6.
#
# Needs `jq` and `bandit` on PATH. Bandit alone is fast enough to run on every
# commit. To run the full ASH suite instead (slower; needs the ASH CLI), check
# for `ash` instead of `bandit` in the tool loop and replace everything from the
# REPORT line through its if block with an exit-code check, because ASH does not
# print Bandit's JSON. ASH exits 2 when it finds issues at or above
# --min-severity; any other non-zero code means the scan reached no verdict:
#   ash --mode local --source-dir . --min-severity high >/dev/null 2>&1; rc=$?
#   [ "$rc" -eq 2 ] && { echo "Blocked: ASH found high-severity issues. Run 'ash report' for details." >&2; exit 2; }
#   [ "$rc" -ne 0 ] && echo "pre-commit-security-scan: ASH exited $rc without a verdict; not blocking" >&2

# Read the hook payload (JSON on stdin): the Bash command is in
# .tool_input.command.
INPUT=$(cat)

for tool in bandit jq; do
  if ! command -v "$tool" > /dev/null 2>&1; then
    # Warn instead of blocking every commit in a project without the tooling.
    # Install it (pip install bandit / your package manager for jq) to enforce
    # the gate; until then the scan is skipped, not silently passed.
    echo "pre-commit-security-scan: $tool not found on PATH; skipping scan" >&2
    exit 0
  fi
done

# Scan only for git commit. The "if": "Bash(git commit*)" filter in the
# settings file is best-effort: Claude Code runs the hook anyway when it cannot
# tell which commands a Bash call runs. Checking here as well means any other
# command passes through untouched.
COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
if ! printf '%s' "$COMMAND" | grep -qE '(^|[;&|(]|[[:space:]])git[[:space:]]+commit'; then
  exit 0
fi

# Scan the repository. JSON output keeps severities machine-readable.
REPORT=$(bandit -r . -x ./venv,./.venv,./node_modules -f json -q 2>/dev/null)

HIGH_COUNT=$(echo "$REPORT" | jq '[.results[] | select(.issue_severity == "HIGH")] | length')

if [ "${HIGH_COUNT:-0}" -gt 0 ] 2>/dev/null; then
  echo "Blocked: $HIGH_COUNT high-severity finding(s). Run 'bandit -r .' for details, fix, then commit." >&2
  exit 2
fi
exit 0
