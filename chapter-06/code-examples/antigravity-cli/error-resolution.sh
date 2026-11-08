#!/bin/bash
# =============================================================================
# Antigravity CLI (agy) Error Resolution Examples
# Chapter 6: Intent-First Development
# =============================================================================
#
# HOW TO USE THIS FILE: read it, then copy the one prompt you want. Do not
# execute it. Every uncommented line below is a separate agent invocation, so
# running the whole file would fire all of them back to back.
#
# The Antigravity CLI is an interactive terminal agent, not a bag of
# subcommands. There is no "fix" subcommand. You either:
#
#   1. Launch `agy` in your project and ask it to diagnose a failure
#      (the agent runs the build itself and reads the output), or
#   2. Use `agy -p "..."` print mode for a one-shot answer you can
#      fold into scripts.
#
# The agent's strength is that your build output, git state, and files are
# already its context. You do not need to pipe logs into it; ask it to run
# the failing command and it observes the output directly.
#
# Print mode and shell commands: in `agy -p` runs the agent reads and writes
# workspace files without asking, but shell commands (the build, the tests,
# git) need approval and are soft-denied when nobody can give it; the run still
# exits 0. Allow what a prompt needs with permissions.allow rules in
# ~/.gemini/antigravity-cli/settings.json, such as "command(git)" or
# "command(regex:npm run (build|lint|test))", or use an interactive session.
# =============================================================================

# -----------------------------------------------------------------------------
# Build Error Resolution (the "Smart Fix" loop)
# -----------------------------------------------------------------------------

# One-shot: diagnose a failing npm build and print the proposed fix
agy -p "Diagnose why npm run build fails and propose a fix"

# One-shot: TypeScript compile errors
agy -p "Run npx tsc --noEmit, read the errors, and propose fixes file by file"

# Interactive equivalent: launch agy in the project, then type:
#   > The npm build is failing. Read the error output, find the root
#   > cause, and propose a fix.

# -----------------------------------------------------------------------------
# Test Failure Resolution
# -----------------------------------------------------------------------------

# Diagnose failing Jest tests
agy -p "Run npm test, identify the failing tests, and explain the root cause of each failure"

# Focus on a single test file
agy -p "Run npm test -- src/lib/mock-data.test.ts and fix whatever is failing"

# accept-edits auto-approves file edits; running npm test still needs a
# permissions.allow rule in print mode
agy --mode accept-edits -p "Run npm test and fix the failing tests"

# -----------------------------------------------------------------------------
# Lint and Format Errors
# -----------------------------------------------------------------------------

# ESLint cleanup
agy -p "Run npm run lint and fix every reported violation"

# Prettier check
agy -p "Run npx prettier --check . and reformat the files that fail"

# -----------------------------------------------------------------------------
# Runtime and Infrastructure Errors
# -----------------------------------------------------------------------------

# Analyze a server log already on disk
agy -p "Read server.log, identify the errors, and propose fixes"

# Docker build failure
agy -p "Run docker build . and diagnose why the build fails"

# CI failure triage (gh CLI must be authenticated)
agy -p "Run 'gh run view --log-failed' and summarize the root cause of the CI failure"

# -----------------------------------------------------------------------------
# Pattern: Plan First, Then Fix
# -----------------------------------------------------------------------------

# Plan mode lets you approve the approach before any edits happen
agy --mode plan -p "npm run build is failing. Plan the fix, listing every file you would change and why."

# Then run for real. In print mode the edits apply without review, so commit
# first; run it interactively instead if you want to approve each diff
agy -p "Fix the npm build. Re-run the build after each change until it passes, with at most 3 attempts."

# -----------------------------------------------------------------------------
# Pattern: Error Classification Before Fixing
# -----------------------------------------------------------------------------

agy -p "Run npm run build. Classify the errors by severity (critical, warning,
info), type (syntax, type, import, runtime), and priority. Then propose fixes
for the critical issues first."

# -----------------------------------------------------------------------------
# Pattern: Root Cause Analysis Across Commits
# -----------------------------------------------------------------------------

agy -p "Look at the last 10 commits. Identify which commits most likely
introduced bugs, common patterns in the error-prone code, and recommendations
to prevent similar issues."

# -----------------------------------------------------------------------------
# Pattern: Save Findings to a File
# -----------------------------------------------------------------------------

# Print mode writes to stdout, so ordinary shell redirection works
agy -p "Diagnose why npm run build fails and propose a fix" > "fixes-$(date +%Y%m%d).md"
