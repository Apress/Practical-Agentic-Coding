#!/bin/bash
# =============================================================================
# Antigravity CLI (agy) Code Review Examples
# Chapter 6: Intent-First Development
# =============================================================================
#
# HOW TO USE THIS FILE: read it, then copy the one prompt you want. Do not
# execute it. Every uncommented line below is a separate agent invocation, so
# running the whole file would fire all of them back to back.
#
# There is no "review" subcommand. Reviews are prompts: the agent lives in
# your repository, so it can read diffs, commits, and files itself. You do
# not pipe `git diff` into it; you name the range and the agent runs git.
#
# Interactive (bare `agy`) suits back-and-forth review discussion.
# Print mode (`agy -p`) suits scripts, hooks, and CI.
#
# Print mode and shell commands: in `agy -p` runs the agent reads and writes
# workspace files without asking, but shell commands (the build, the tests,
# git) need approval and are soft-denied when nobody can give it; the run still
# exits 0. Allow what a prompt needs with permissions.allow rules in
# ~/.gemini/antigravity-cli/settings.json, such as "command(git)" or
# "command(regex:npm run (build|lint|test))", or use an interactive session.
# =============================================================================

# -----------------------------------------------------------------------------
# Basic Reviews (the "Auto-Review" loop)
# -----------------------------------------------------------------------------

# Review the most recent commit. Interactive version, inside agy:
#   > Review the diff of my most recent commit. Be strict: flag style
#   > violations, missing error handling, and anything that breaks our
#   > project rules.

# One-shot versions:
agy -p "Review the diff of my most recent commit. Be strict: flag style violations, missing error handling, and anything that breaks our project rules."

agy -p "Review my staged changes (git diff --cached) before I commit"

agy -p "Review my uncommitted changes and give a brief summary of risks"

# -----------------------------------------------------------------------------
# PR Review Workflows
# -----------------------------------------------------------------------------

# Review a branch against main
agy -p "Review the diff between this branch and main. Flag security issues, missing error handling, and style violations."

# Review a specific commit range
agy -p "Review the changes between commits abc123 and def456"

# Review changes since the last release tag
agy -p "Review everything that changed between tag v1.0.0 and HEAD, grouped by risk"

# -----------------------------------------------------------------------------
# Focused Reviews
# -----------------------------------------------------------------------------

# Security focus
agy -p "Review my latest commit for security only: hardcoded secrets, SQL
injection, XSS, missing input validation, and authentication issues."

# Performance focus
agy -p "Review my latest commit for performance only: N+1 queries, memory
leaks, unnecessary re-renders, large bundle imports, and missing caching."

# Accessibility focus
agy -p "Review the changed React components for accessibility: ARIA labels,
keyboard navigation, color contrast, and screen reader compatibility."

# Scope by path
agy -p "Review only the changes under src/app/api in my current branch"

# -----------------------------------------------------------------------------
# Review Outputs You Can Reuse
# -----------------------------------------------------------------------------

# Generate a PR description
agy -p "Look at the diff between this branch and main and write a PR
description: summary of changes, key modifications, testing notes, and any
breaking changes." > pr-description.md

# Generate a review checklist
agy -p "Create a review checklist for my staged changes as markdown checkboxes" > review-checklist.md

# -----------------------------------------------------------------------------
# Pre-commit Gate (scripted print mode)
# -----------------------------------------------------------------------------

review_and_commit() {
    review=$(agy -p "Review my staged changes. If you find critical or
security issues, start your reply with the word CRITICAL.")

    if echo "$review" | grep -qi "^CRITICAL"; then
        echo "Review found critical issues:"
        echo "$review"
        return 1
    fi

    echo "$review"
    read -p "Proceed with commit? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git commit "$@"
    fi
}

# Usage: review_and_commit -m "feat: add waste detection"

# -----------------------------------------------------------------------------
# Integration with GitHub (gh CLI)
# -----------------------------------------------------------------------------

# Post a review comment on the open PR for this branch
agy -p "Review the diff between this branch and main and output the findings as markdown" > /tmp/review.md
gh pr comment --body-file /tmp/review.md
