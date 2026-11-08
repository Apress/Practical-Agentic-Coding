#!/bin/bash
# post-edit-tests.sh
# PostToolUse hook to automatically run tests after code changes
#
# This hook runs the appropriate test suite after files are modified,
# ensuring that changes don't break existing functionality.
#
# Exit codes:
#   0 - Tests passed or not applicable
#   2 - Tests failed. A PostToolUse hook cannot undo the edit (the tool
#       already ran), but exit 2 shows this script's stderr, the failing
#       test output, to Claude so it can fix the code.
#
# Each runner's output is captured in full before it is trimmed for
# display: in `runner | head -50`, the pipeline's exit status is head's,
# so a failing run would be reported as a pass.
#
# Usage:
#   Configure in .claude/settings.json as a PostToolUse hook with the
#   matcher "Edit|Write".

set -e

# Read tool input from stdin (JSON format)
INPUT=$(cat)

# Extract the file path from the tool input
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# If no file path, nothing to test
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

echo "Checking if tests needed for: $FILE_PATH" >&2

# =============================================================================
# PYTHON FILES
# =============================================================================

if [[ "$FILE_PATH" == *.py ]]; then
    echo "Python file modified - running pytest..." >&2

    # Check if pytest is available
    if ! command -v pytest &> /dev/null; then
        echo "WARNING: pytest not found, skipping tests" >&2
        exit 0
    fi

    # Check if tests directory exists
    if [ ! -d "tests" ]; then
        echo "WARNING: No tests directory found, skipping" >&2
        exit 0
    fi

    # -x: stop on first failure; --tb=short: shorter traceback
    TEST_STATUS=0
    TEST_OUTPUT=$(pytest tests/ -x --tb=short 2>&1) || TEST_STATUS=$?

    if [ "$TEST_STATUS" -eq 0 ]; then
        echo "All Python tests passed!" >&2
        exit 0
    fi
    echo "$TEST_OUTPUT" | head -50 >&2
    echo "Python tests failed after editing $FILE_PATH; fix them before moving on." >&2
    exit 2
fi

# =============================================================================
# JAVASCRIPT/TYPESCRIPT FILES
# =============================================================================

if [[ "$FILE_PATH" == *.js ]] || [[ "$FILE_PATH" == *.ts ]] || [[ "$FILE_PATH" == *.tsx ]]; then
    echo "JavaScript/TypeScript file modified - running tests..." >&2

    # Check for package.json test script
    if [ ! -f "package.json" ]; then
        echo "WARNING: No package.json found, skipping tests" >&2
        exit 0
    fi

    # Check if test script exists
    if ! grep -q '"test"' package.json; then
        echo "WARNING: No test script in package.json, skipping" >&2
        exit 0
    fi

    # Determine package manager
    if [ -f "pnpm-lock.yaml" ]; then
        PKG_MGR="pnpm"
    elif [ -f "yarn.lock" ]; then
        PKG_MGR="yarn"
    else
        PKG_MGR="npm"
    fi

    echo "Using $PKG_MGR to run tests..." >&2

    TEST_STATUS=0
    TEST_OUTPUT=$($PKG_MGR test -- --passWithNoTests 2>&1) || TEST_STATUS=$?

    if [ "$TEST_STATUS" -eq 0 ]; then
        echo "All JavaScript/TypeScript tests passed!" >&2
        exit 0
    fi
    echo "$TEST_OUTPUT" | head -50 >&2
    echo "Tests failed after editing $FILE_PATH; fix them before moving on." >&2
    exit 2
fi

# =============================================================================
# RUST FILES
# =============================================================================

if [[ "$FILE_PATH" == *.rs ]]; then
    echo "Rust file modified - running cargo test..." >&2

    if ! command -v cargo &> /dev/null; then
        echo "WARNING: cargo not found, skipping tests" >&2
        exit 0
    fi

    TEST_STATUS=0
    TEST_OUTPUT=$(cargo test 2>&1) || TEST_STATUS=$?

    if [ "$TEST_STATUS" -eq 0 ]; then
        echo "All Rust tests passed!" >&2
        exit 0
    fi
    echo "$TEST_OUTPUT" | head -50 >&2
    echo "Rust tests failed after editing $FILE_PATH; fix them before moving on." >&2
    exit 2
fi

# =============================================================================
# GO FILES
# =============================================================================

if [[ "$FILE_PATH" == *.go ]]; then
    echo "Go file modified - running go test..." >&2

    if ! command -v go &> /dev/null; then
        echo "WARNING: go not found, skipping tests" >&2
        exit 0
    fi

    TEST_STATUS=0
    TEST_OUTPUT=$(go test ./... 2>&1) || TEST_STATUS=$?

    if [ "$TEST_STATUS" -eq 0 ]; then
        echo "All Go tests passed!" >&2
        exit 0
    fi
    echo "$TEST_OUTPUT" | head -50 >&2
    echo "Go tests failed after editing $FILE_PATH; fix them before moving on." >&2
    exit 2
fi

# =============================================================================
# DEFAULT - No specific test runner
# =============================================================================

echo "No specific test runner for file type: $FILE_PATH" >&2
exit 0
