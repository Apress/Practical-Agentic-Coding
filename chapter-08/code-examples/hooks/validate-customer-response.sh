#!/bin/bash
# validate-customer-response.sh
# PostToolUse hook to enforce human review requirements for customer-facing content
#
# This hook ensures that any AI-generated customer-facing responses are
# properly marked as drafts requiring human review before sending.
#
# Part of SupportFlow's constitutional governance framework.
#
# Exit codes:
#   0 - Validation passed or not applicable
#   2 - Validation failed: the file is not marked as a draft. A PostToolUse
#       hook cannot undo the write (the tool already ran); exit 2 shows the
#       error on stderr to Claude so it corrects the file.
#
# Usage:
#   Configure in .claude/settings.json as a PostToolUse hook with the
#   matcher "Edit|Write".

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


# Extract the file path from the tool input
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# If no file path, nothing to validate
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# =============================================================================
# CHECK IF THIS IS A CUSTOMER-FACING RESPONSE FILE
# =============================================================================

# Patterns that indicate customer-facing content
CUSTOMER_PATTERNS=(
    "responses/"
    "customer_messages/"
    "email_templates/"
    "reply_drafts/"
)

IS_CUSTOMER_CONTENT=false
for pattern in "${CUSTOMER_PATTERNS[@]}"; do
    if [[ "$FILE_PATH" == *"$pattern"* ]]; then
        IS_CUSTOMER_CONTENT=true
        break
    fi
done

# Skip validation if not customer-facing
if [ "$IS_CUSTOMER_CONTENT" = false ]; then
    exit 0
fi

echo "Validating customer-facing content: $FILE_PATH" >&2

# =============================================================================
# VALIDATE DRAFT STATUS
# =============================================================================

# Check if file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "WARNING: File does not exist yet, skipping validation" >&2
    exit 0
fi

# Check for draft markers in various formats
DRAFT_MARKERS=(
    "STATUS: DRAFT"
    "status: draft"
    '"status": "draft"'
    '"status":"draft"'
    "requires_human_review: true"
    "requires_human_review=true"
    '"requires_human_review": true'
)

HAS_DRAFT_MARKER=false
for marker in "${DRAFT_MARKERS[@]}"; do
    if grep -qi "$marker" "$FILE_PATH" 2>/dev/null; then
        HAS_DRAFT_MARKER=true
        break
    fi
done

if [ "$HAS_DRAFT_MARKER" = false ]; then
    echo "" >&2
    echo "ERROR: Customer-facing content MUST be marked as DRAFT" >&2
    echo "" >&2
    echo "File: $FILE_PATH" >&2
    echo "" >&2
    echo "All AI-generated customer responses require human review" >&2
    echo "before being sent to customers." >&2
    echo "" >&2
    echo "Please add one of the following markers:" >&2
    echo "  - STATUS: DRAFT" >&2
    echo "  - \"status\": \"draft\"" >&2
    echo "  - requires_human_review: true" >&2
    echo "" >&2
    exit 2  # Claude sees the message above and fixes the file
fi

# =============================================================================
# VALIDATE NO INTERNAL DETAILS
# =============================================================================

# Patterns that indicate internal system details (should not be in customer content)
FORBIDDEN_PATTERNS=(
    "stack trace"
    "stacktrace"
    "Traceback"
    "Exception:"
    "Error:"
    "internal_id"
    "db_query"
    "SELECT.*FROM"
    "INSERT INTO"
    "/api/v[0-9]"
    "server_error"
    "debug_info"
)

echo "Checking for internal details..." >&2

for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
    if grep -qiE "$pattern" "$FILE_PATH" 2>/dev/null; then
        echo "" >&2
        echo "WARNING: Possible internal details detected in customer content" >&2
        echo "Pattern found: $pattern" >&2
        echo "File: $FILE_PATH" >&2
        echo "" >&2
        echo "Customer responses must not contain:" >&2
        echo "  - Stack traces or error details" >&2
        echo "  - Internal IDs or database queries" >&2
        echo "  - API endpoint paths" >&2
        echo "  - Debug information" >&2
        echo "" >&2
        # This is a warning, not a block - human reviewer should check
        break
    fi
done

# =============================================================================
# VALIDATION PASSED
# =============================================================================

echo "Customer response validation passed:" >&2
echo "  - Draft status marker: FOUND" >&2
echo "  - Ready for human review" >&2
exit 0
