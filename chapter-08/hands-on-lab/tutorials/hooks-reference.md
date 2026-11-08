# Hooks: quick reference

Use this file to write, register, and test a hook. It gives one runnable script for each of four common events.

Why hooks enforce what CLAUDE.md can only ask for, and which events to use: Chapter 8, Section 8.3 (Table 8.4).

This is not the full event list. The [official hooks documentation](https://code.claude.com/docs) has the full set, more than thirty events. Check it for the latest.

## Overview

A hook is a script that Claude Code runs at a fixed point in a session.

## Hook Events in Detail

### SessionStart

**When**: Claude Code session begins

A SessionStart hook's stdout is added to Claude's context. Print what Claude should know:

```bash
#!/bin/bash
# session-start.sh

echo "Session started at $(date)"

# Check environment
if [ -z "$DATABASE_URL" ]; then
    echo "WARNING: DATABASE_URL is not set in this environment"
fi

# Load project context
if [ -f "CLAUDE.md" ]; then
    echo "Project constitution: CLAUDE.md is present"
fi

exit 0
```

### PreToolUse

**When**: Before any tool executes

```bash
#!/bin/bash
# pre-tool-use.sh

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

case "$TOOL_NAME" in
    "Bash")
        # Validate bash commands
        if echo "$COMMAND" | grep -qE "rm -rf /"; then
            echo "BLOCKED: Dangerous command" >&2
            exit 2
        fi
        ;;
    "Write"|"Edit")
        # Validate file writes; file_path is always an absolute path,
        # so compare the file's base name
        FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
        case "$(basename "$FILE")" in
            .env|.env.*)
                echo "BLOCKED: Cannot write to .env files" >&2
                exit 2
                ;;
        esac
        ;;
esac

exit 0
```

Register it with the matcher `"Bash|Edit|Write"`. Each branch then receives its calls.

### PostToolUse

**When**: After tool executes successfully

```bash
#!/bin/bash
# post-tool-use.sh

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

case "$TOOL_NAME" in
    "Write"|"Edit")
        # Run tests after code changes
        if [[ "$FILE_PATH" == *.py ]]; then
            if ! OUTPUT=$(pytest tests/ -x --tb=short 2>&1); then
                echo "$OUTPUT" | head -30 >&2
                exit 2  # cannot undo the edit; exit 2 shows stderr to Claude
            fi
        fi
        ;;
esac

exit 0
```

### Stop

**When**: Claude finishes responding

On exit 0, Claude Code reads JSON from stdout. It shows a `systemMessage` field to you as a warning. Exit 2 keeps Claude working instead, with stderr as the reason.

```bash
#!/bin/bash
# stop.sh

# Check for uncommitted changes
if git status --porcelain | grep -q .; then
    echo '{"systemMessage": "Note: you have uncommitted changes"}'
fi

exit 0
```

## Hook Configuration

### Basic Configuration

Reference scripts through `$CLAUDE_PROJECT_DIR`, the project root. Do not use a relative path.

Hooks run in the session's current directory. That directory moves when Claude runs `cd`. If a relative path stops resolving, the hook fails open: the shell exits 127, a non-blocking error.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validate-bash.sh"
          }
        ]
      }
    ]
  }
}
```

### Multiple Hooks

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/run-tests.sh"
          },
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/notify-team.sh"
          }
        ]
      }
    ]
  }
}
```

### Matcher Options

The matcher is a string that names the tool.

- If it holds only letters, digits, `_`, `-`, spaces, commas, and `|`, it is an exact name or an exact list. `"Edit|Write"` covers both tools.
- Any other character makes it a regular expression, such as `"mcp__.*"`.

Examples:

```json
{ "matcher": "Bash" }
```

```json
{ "matcher": "Edit|Write" }
```

Tool names you can match on:

- `Bash`, `Write`, `Edit`, `Read`, `Glob`, `Grep`, `WebFetch`, `WebSearch`
- `Agent`, the sub-agent tool. It was `Task` in releases before Claude Code 2.1.63.
- MCP tools, named `mcp__<server>__<tool>`

Notes:

- On macOS, Linux, and WSL, `Glob` and `Grep` are absent by default. Claude searches with `find` and `grep` through Bash. A `Glob` or `Grep` matcher fires only where those tools are loaded.
- To match everything, omit `matcher` or use `"*"`.
- Some events take no matcher, such as `UserPromptSubmit` and `Stop`.
- For `SessionStart`, the matcher is the start type: `startup`, `resume`, `clear`, or `compact`.

### Hook Options

| Option | Description | Default |
|--------|-------------|---------|
| `type` | Handler type. `command` is the workhorse | Required |
| `command` | Script to execute (for `type: command`) | Required for `command` |
| `timeout` | Max execution time, in **seconds** | 600 for `command` handlers |

**Timeouts are in seconds.** `"timeout": 10` means ten seconds. `3000` means roughly fifty minutes.

Other values for `type`:

- `http`: send an HTTP request
- `mcp_tool`: call an MCP tool
- `prompt`: ask a model to judge the input
- `agent`: delegate the decision to a sub-agent (experimental)

Every example in this file uses `command`.

## Exit Codes

| Exit code | Meaning | Effect |
|-----------|---------|--------|
| 0 | Allow | Tool call goes ahead. Claude never sees stderr. Stdout is parsed as JSON output. For `SessionStart` and `UserPromptSubmit`, plain text becomes context |
| 2 | Block | A `PreToolUse` call is stopped. Stderr goes to Claude as the reason. `PostToolUse` cannot block because the tool already ran. Stderr still reaches Claude |
| Other | Warn | Call goes ahead; the transcript shows a hook error notice |

### Examples

```bash
# Success - allow operation
exit 0

# Block operation
echo "ERROR: Operation not allowed" >&2
exit 2

# Warning - allow but notify
echo "WARNING: Proceed with caution" >&2
exit 1
```

## Hook Input Format

Hooks receive JSON on stdin. This is a PreToolUse call to the Bash tool. The field names come from the Claude Code hooks reference.

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/session-transcript.jsonl",
  "cwd": "/home/you/my-project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test"
  },
  "tool_use_id": "toolu_01ABC"
}
```

Edit and Write calls carry `tool_input.file_path`, an absolute path. PostToolUse input adds `tool_response`.

### Parsing with jq

```bash
INPUT=$(cat)

# Get tool name
TOOL=$(echo "$INPUT" | jq -r '.tool_name')

# Get specific field with default
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Get file path
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
```

## More hook scripts

More working scripts are in [`code-examples/hooks/`](../../code-examples/hooks/). Which hooks to build for your team, and why: Chapter 8, Section 8.3.

## Testing Hooks

### Manual Testing

```bash
# Make hook executable
chmod +x .claude/hooks/my-hook.sh

# Test with sample input
echo '{"tool_name": "Bash", "tool_input": {"command": "ls -la"}}' | \
    .claude/hooks/my-hook.sh

# Check exit code
echo $?
```

### Test Script

```bash
#!/bin/bash
# test-hooks.sh

echo "Testing hooks..."

# Test 1: Safe command
echo '{"tool_input": {"command": "ls"}}' | .claude/hooks/validate-bash.sh
[ $? -eq 0 ] && echo "PASS: Safe command" || echo "FAIL: Safe command"

# Test 2: Dangerous command
echo '{"tool_input": {"command": "rm -rf /"}}' | .claude/hooks/validate-bash.sh
[ $? -eq 2 ] && echo "PASS: Blocked dangerous" || echo "FAIL: Blocked dangerous"

echo "Tests complete"
```

## Troubleshooting

### Hook Not Running

1. Make the file executable: `chmod +x .claude/hooks/script.sh`.
2. Check that the path in settings.json uses `"$CLAUDE_PROJECT_DIR"`.
3. Run `/hooks` in a session. It lists the hooks Claude Code loaded.
4. Check that jq is installed.
5. Test the hook by hand (see Manual Testing above).

### Hook Blocking Unexpectedly

1. Add debug output: `echo "Debug: $COMMAND" >&2`.
2. Check the pattern matching.
3. Test with real input JSON.

### Hook Timeout

1. Raise `timeout` in settings.json. The value is in seconds.
2. Remove slow operations from the script.
3. Try async operations.

Every hook runs on the critical path of a tool call. A command hook may run up to 600 seconds by default. Give quick hooks a short `timeout`.

## See Also

- [Hook Examples](../../code-examples/hooks/)
- [Exercise 2: Implementing Hooks](../exercises/exercise-2-hooks.md)
- [Claude Code Documentation](https://code.claude.com/docs)
