# Claude Code Hooks - Examples and Reference

This directory holds example lifecycle hooks for Claude Code. Copy them into your project and adapt them.

## Overview

Hooks are scripts that Claude Code runs at lifecycle events. What hooks are for, and when to use each event: Chapter 8, Section 8.3.

## Hook Lifecycle Events

These examples use four events. Table 8.4 in Section 8.3 lists more. The Claude Code hooks reference has the full set.

| Event | When It Fires | Common Use Cases |
|-------|---------------|------------------|
| `SessionStart` | Session begins | Load context, check environment |
| `PreToolUse` | Before tool execution | Validate operations, block danger |
| `PostToolUse` | After tool succeeds | Run tests, log actions, notify |
| `Stop` | Claude finishes responding | Quality checks, cleanup |

## Exit Codes

| Exit Code | Behavior |
|-----------|----------|
| 0 | Success - operation proceeds. Claude never sees stderr from a hook that exits 0 |
| 2 | Blocking error - a PreToolUse call is stopped and stderr goes to Claude as the reason. A PostToolUse hook cannot block because the tool already ran. Exit 2 still shows stderr to Claude |
| Other | Non-blocking error - operation continues and the transcript shows a hook error notice |

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

Edit and Write calls carry `tool_input.file_path` (an absolute path) instead of `command`. PostToolUse input adds `tool_response`, the tool's result.

## Files in This Directory

### validate-bash.sh

**Type**: PreToolUse
**Purpose**: Block dangerous bash commands before execution

Prevents operations like:
- `rm -rf /` (root filesystem deletion)
- `git push --force` (force push)
- `chmod 777` (world-writable permissions)
- Piped curl/wget to shell

It blocks (exit 2) when `jq` is missing.

### post-edit-tests.sh

**Type**: PostToolUse
**Purpose**: Automatically run tests after code changes

Features:
- Detects file type (Python, JavaScript, etc.)
- Runs appropriate test suite
- Reports failures back to Claude (exit 2 with the failing output on stderr). Claude can then fix them

### validate-customer-response.sh

**Type**: PostToolUse
**Purpose**: Ensure customer-facing content is marked as draft

Used in SupportFlow to enforce human review requirements.

### session-setup.sh (not shipped here)

**Type**: SessionStart
**Purpose**: Set up the development environment:

- Check required environment variables
- Verify the project structure
- Display session context

You write this one yourself. [Exercise 2D](../../hands-on-lab/exercises/exercise-2-hooks.md) builds it step by step. The configuration below shows where it plugs in.

## Configuration

Add hooks to `.claude/settings.json`. Reference each script through `$CLAUDE_PROJECT_DIR`, the project root.

Do not use a relative path. Hooks run in the session's current directory, and that directory moves when Claude runs `cd`. If a relative path no longer resolves, the hook fails open: the shell exits 127, a non-blocking error.

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
    ],
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

`"Edit|Write"` matches either tool name exactly. A matcher that contains other characters (such as `mcp__.*`) is treated as a regular expression.

## Installation

1. Copy the hook files to your project's `.claude/hooks/` directory.
2. Make them executable:
   ```bash
   chmod +x .claude/hooks/*.sh
   ```
3. Add the configuration to `.claude/settings.json`.
4. Test the hooks by hand before you use them with Claude Code.

## Testing Hooks

Use the included test patterns:

```bash
# Test validate-bash.sh
echo '{"tool_input": {"command": "ls -la"}}' | ./validate-bash.sh
echo $?  # Should be 0

echo '{"tool_input": {"command": "rm -rf /"}}' | ./validate-bash.sh
echo $?  # Should be 2
```

## Troubleshooting

### Hook not executing
- Check file permissions (`chmod +x`)
- Check that the path in settings.json uses `"$CLAUDE_PROJECT_DIR"`
- Run `/hooks` in a session to list the hooks Claude Code loaded
- Check jq is installed

### Hook blocking unexpectedly
- Review pattern matching logic
- Check for overly broad regex patterns
- Test with actual input JSON

### Hook timeout
- Raise `timeout` in settings.json. The value is in seconds. A command hook may run up to 600 seconds by default
- Optimize hook script
- Consider async operations

## See Also

- [Exercise 2: Implementing Hooks](../../hands-on-lab/exercises/exercise-2-hooks.md)
- [Hooks Reference Tutorial](../../hands-on-lab/tutorials/hooks-reference.md)
- [Claude Code Documentation](https://code.claude.com/docs)
