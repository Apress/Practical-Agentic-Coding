# Exercise 2: Implementing Lifecycle Hooks

## Objective

Create and configure lifecycle hooks that enforce your rules during Claude Code sessions.

## Duration

45-60 minutes

## Background

Hooks are scripts that Claude Code runs at lifecycle events. A CLAUDE.md instruction such as "Always run tests after editing" is advisory. A PostToolUse hook that runs the tests is enforced.

Why this difference matters: Chapter 8, Section 8.3. This exercise builds the hooks.

## Part 1: Understanding Hook Events

| Event | When It Fires | Common Use Cases |
|-------|---------------|------------------|
| SessionStart | Session begins | Load context, set environment |
| PreToolUse | Before tool execution | Validate operations, block danger |
| PostToolUse | After tool succeeds | Run tests, log actions, notify |
| Stop | Claude finishes responding | Quality checks, cleanup |

### Hook Exit Codes

| Exit Code | Behavior |
|-----------|----------|
| 0 | Allow. The tool call goes ahead. Claude never sees stderr |
| 2 | Block. A PreToolUse call is cancelled and stderr is fed back to Claude. A PostToolUse hook cannot cancel because the tool already ran. Its stderr still reaches Claude |
| Other | Non-blocking error. The operation still runs and the transcript shows a hook error notice |

## Part 2: Hook Configuration

Configure hooks in `.claude/settings.json`. Reference each script through `$CLAUDE_PROJECT_DIR`, the project root.

Do not use a relative path. Hooks run in the session's current directory, and that directory moves when Claude runs `cd`. If a relative path stops resolving, the hook fails open: the shell exits 127, a non-blocking error.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validate-bash.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/post-edit-tests.sh"
          }
        ]
      }
    ]
  }
}
```

### Matcher Options

- `matcher` names the tool the hook applies to, such as `Bash`, `Write`, `Edit`, or `Read`.
- `"Edit|Write"` matches either tool exactly.
- A matcher with other characters, such as `"mcp__.*"`, is a regular expression.
- To match every tool, omit `matcher` or use `"*"`.

## Part 3: Hands-On Exercises

### Exercise 2A: Prevent Dangerous Bash Commands

Build a PreToolUse hook that stops destructive commands before they run.

**Step 1**: Create the hook script

```bash
mkdir -p .claude/hooks
```

Create `.claude/hooks/validate-bash.sh`:

```bash
#!/bin/bash
# PreToolUse hook to block dangerous Bash commands

# Read tool input from stdin (JSON format)
INPUT=$(cat)

# Extract the command from Bash tool input
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# If no command, allow (not a Bash operation)
if [ -z "$COMMAND" ]; then
    exit 0
fi

# Define dangerous patterns. grep -E reads these as extended regular
# expressions, so escape * and | when you mean the literal characters;
# unescaped, "rm -rf *" matches every rm -rf and "curl.*|.*sh" matches any
# command containing "sh" (git push, bash, ssh).
BLOCKED_PATTERNS=(
    "rm -rf /[[:space:]]*$"
    "rm -rf ~"
    "rm -rf \*"
    "git push --force"
    "git reset --hard"
    "chmod 777"
    "curl.*\|[[:space:]]*(ba)?sh"
)

# Check each pattern
for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qE "$pattern"; then
        echo "BLOCKED: Command matches dangerous pattern: $pattern" >&2
        exit 2
    fi
done

echo "Command validated successfully" >&2
exit 0
```

**Step 2**: Make it executable

```bash
chmod +x .claude/hooks/validate-bash.sh
```

**Step 3**: Configure in settings.json

Create `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validate-bash.sh",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**Step 4**: Test the hook

```bash
# Test with a safe command (manual test)
echo '{"tool_input": {"command": "ls -la"}}' | .claude/hooks/validate-bash.sh
# Should exit 0

# Test with a dangerous command
echo '{"tool_input": {"command": "rm -rf /"}}' | .claude/hooks/validate-bash.sh
# Should exit 2 with BLOCKED message

# Test that ordinary commands are not caught by the patterns
echo '{"tool_input": {"command": "git push origin main"}}' | .claude/hooks/validate-bash.sh
# Should exit 0
```

### Exercise 2B: Auto-Run Tests After Code Changes

Create a PostToolUse hook that runs tests after Python files change. A PostToolUse hook cannot undo the edit. When it exits 2, Claude sees its stderr. That is how Claude gets the test failures.

**Step 1**: Create `.claude/hooks/post-edit-tests.sh`:

```bash
#!/bin/bash
# PostToolUse hook to run tests after code changes

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only run for Python files
if [[ "$FILE_PATH" == *.py ]]; then
    # Capture the full output first: in "pytest | head", the pipeline's
    # exit status would be head's, not pytest's
    if ! OUTPUT=$(pytest tests/ -x --tb=short 2>&1); then
        echo "$OUTPUT" | head -30 >&2
        echo "Tests failed after editing $FILE_PATH" >&2
        exit 2  # stderr goes to Claude
    fi
fi

exit 0
```

**Step 2**: Update settings.json to add the hook (the `PostToolUse` entry in Part 2, with matcher `"Edit|Write"`)

### Exercise 2C: Validate Customer Responses

For SupportFlow, create a hook that checks that customer-facing responses are marked as drafts. Register it as a PostToolUse hook with matcher `"Edit|Write"`. When it exits 2, Claude learns the file broke the rule and fixes it.

**Step 1**: Create `.claude/hooks/validate-customer-response.sh`:

```bash
#!/bin/bash
# PostToolUse hook to validate customer response files

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Check if this is a customer-facing response
if [[ "$FILE_PATH" == *"responses"* ]]; then
    # Ensure it's marked as draft
    if ! grep -q "STATUS: DRAFT" "$FILE_PATH" 2>/dev/null; then
        if ! grep -q '"status": "draft"' "$FILE_PATH" 2>/dev/null; then
            echo "ERROR: Customer responses must be marked as DRAFT" >&2
            echo "File: $FILE_PATH" >&2
            exit 2
        fi
    fi
    echo "Response validation passed: marked as draft" >&2
fi

exit 0
```

### Exercise 2D: Create a SessionStart Hook

Create a hook that sets up the environment when a Claude Code session begins. A SessionStart hook's stdout is added to Claude's context. The script prints its findings to stdout, and Claude reads them at the start of the session.

**Step 1**: Create `.claude/hooks/session-setup.sh`:

```bash
#!/bin/bash
# SessionStart hook to initialize the development environment

echo "=== SupportFlow Development Session ==="
echo "Timestamp: $(date -Iseconds)"

# Check for required environment variables
REQUIRED_VARS=("DATABASE_URL" "API_KEY")
MISSING=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING+=("$var")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "WARNING: Missing environment variables:"
    printf '  - %s\n' "${MISSING[@]}"
    echo "Some features may not work correctly."
fi

# Display project status
if [ -f "CLAUDE.md" ]; then
    echo "Project constitution: CLAUDE.md found"
else
    echo "WARNING: No CLAUDE.md found - consider running /init"
fi

# Check for pending changes
if git status --porcelain 2>/dev/null | grep -q .; then
    echo "Note: Uncommitted changes detected"
fi

echo "Session initialized successfully"
exit 0
```

**Step 2**: Configure in settings.json:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/session-setup.sh"
          }
        ]
      }
    ]
  }
}
```

## Part 4: Advanced Hook Patterns

### Pattern 1: Conditional Blocking

Block operations only under certain conditions:

```bash
#!/bin/bash
# Block writes to production config during business hours

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

HOUR=$(date +%H)

if [[ "$FILE_PATH" == *"production"* ]] && [ "$HOUR" -ge 9 ] && [ "$HOUR" -lt 17 ]; then
    echo "BLOCKED: Production config changes not allowed 9am-5pm" >&2
    exit 2
fi

exit 0
```

### Pattern 2: Logging and Audit

Log all operations for compliance:

```bash
#!/bin/bash
# Log all tool operations to audit file

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // "unknown"')
TIMESTAMP=$(date -Iseconds)

echo "[$TIMESTAMP] Tool: $TOOL" >> .claude/audit.log
echo "$INPUT" | jq -c >> .claude/audit.log

exit 0
```

### Pattern 3: Notification Integration

Send notifications for important events:

```bash
#!/bin/bash
# Notify team on significant operations

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Notify on security-related file changes
if [[ "$FILE_PATH" == *"auth"* ]] || [[ "$FILE_PATH" == *"security"* ]]; then
    curl -s -X POST "https://hooks.slack.com/..." \
         -H "Content-Type: application/json" \
         -d "{\"text\": \"Security file modified: $FILE_PATH\"}"
fi

exit 0
```

## Part 5: Testing Your Hooks

Create a test script for your hooks:

```bash
#!/bin/bash
# test-hooks.sh - Test all hooks

echo "Testing validate-bash.sh..."

# Test 1: Safe command should pass
echo '{"tool_input": {"command": "ls -la"}}' | .claude/hooks/validate-bash.sh
if [ $? -eq 0 ]; then
    echo "  PASS: Safe command allowed"
else
    echo "  FAIL: Safe command blocked"
fi

# Test 2: Dangerous command should be blocked
echo '{"tool_input": {"command": "rm -rf /"}}' | .claude/hooks/validate-bash.sh
if [ $? -eq 2 ]; then
    echo "  PASS: Dangerous command blocked"
else
    echo "  FAIL: Dangerous command not blocked"
fi

# Test 3: Force push should be blocked
echo '{"tool_input": {"command": "git push --force origin main"}}' | .claude/hooks/validate-bash.sh
if [ $? -eq 2 ]; then
    echo "  PASS: Force push blocked"
else
    echo "  FAIL: Force push not blocked"
fi

echo "All tests completed!"
```

## Deliverables

1. Four hook scripts:
   - `validate-bash.sh` (PreToolUse)
   - `post-edit-tests.sh` (PostToolUse)
   - `validate-customer-response.sh` (PostToolUse)
   - `session-setup.sh` (SessionStart)

2. A complete `.claude/settings.json` configuring all hooks

3. A `test-hooks.sh` script that validates your hooks work

4. Documentation of what each hook does and why

## Self-Assessment

- [ ] All hooks are executable (`chmod +x`)
- [ ] Hooks use correct exit codes (0, 2, other)
- [ ] settings.json correctly configures all hooks
- [ ] Test script verifies hook behavior
- [ ] Hooks handle edge cases (empty input, missing fields)

## Common Mistakes

1. **Forgetting to make hooks executable**
   ```bash
   chmod +x .claude/hooks/*.sh
   ```

2. **Using wrong exit codes**
   - Exit 0 = success
   - Exit 2 = blocking error
   - Other = warning

3. **Not handling missing jq fields**
   ```bash
   # Good: Handle missing field
   COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
   ```

4. **Infinite loops** - Don't trigger Claude operations from hooks

## Solution Reference

Compare your solution with the examples in [`../../code-examples/hooks/`](../../code-examples/hooks/).

That directory ships `validate-bash.sh`, `post-edit-tests.sh`, and `validate-customer-response.sh`. It has no `session-setup.sh`. Use Exercise 2D above as the reference for that one.

## Next Steps

Continue to [Exercise 3: MCP Integration](exercise-3-mcp.md). It connects Claude Code to external systems.
