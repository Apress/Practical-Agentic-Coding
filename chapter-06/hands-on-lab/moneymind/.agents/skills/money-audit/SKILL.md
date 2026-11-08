---
description: Audits MoneyMind for security compliance.
---

# MoneyMind Security Audit

Act as a senior security engineer performing a security audit. Scan the files
or directory the user names for security vulnerabilities.

## Audit Checklist

### 1. Hardcoded Plaid Secrets
- Check for hardcoded Plaid API keys (PLAID_CLIENT_ID, PLAID_SECRET)
- Check for hardcoded Gemini API keys (GEMINI_API_KEY)
- Check for any API keys, tokens, or passwords in source code
- Verify all secrets come from environment variables

### 2. Missing Environment Variables
- Verify .env is in .gitignore
- Check that .env.example exists with placeholder values
- Ensure no .env files are committed
- Validate required environment variables are documented

### 3. Improper Error Handling
- Check that errors don't expose internal details
- Verify API endpoints don't leak stack traces
- Ensure sensitive data isn't logged
- Check for proper try-catch blocks

## Output Format

Provide a structured report with:
1. **CRITICAL** - Issues requiring immediate attention
2. **WARNING** - Potential vulnerabilities
3. **PASS** - Security checks that passed
4. **RECOMMENDATIONS** - Suggested improvements

For each issue found, give the file path and line number, a description of
the vulnerability, and a suggested fix with a code example. After reporting,
offer a guided code fix for the critical issues.
