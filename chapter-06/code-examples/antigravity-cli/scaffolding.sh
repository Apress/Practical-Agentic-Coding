#!/bin/bash
# =============================================================================
# Antigravity CLI (agy) Scaffolding Examples
# Chapter 6: Intent-First Development
# =============================================================================
#
# HOW TO USE THIS FILE: read it, then copy the one prompt you want. Do not
# execute it. Every uncommented line below is a separate agent invocation, so
# running the whole file would fire all of them back to back.
#
# There is no "scaffold" subcommand. Scaffolding with agy is prompt-driven:
# you describe the project or module, and the agent generates a unique
# structure from your prompt rather than copying a template. It creates the
# package.json, folders, and configuration files from scratch.
#
# For anything that creates many files, prefer the interactive session
# (bare `agy`) with the default request-review preset so you can accept or
# reject each write. Print mode (`agy -p`) works for scripted runs, but pair
# it with --mode plan first when the change is large.
#
# Print mode and shell commands: in `agy -p` runs the agent reads and writes
# workspace files without asking, but shell commands (the build, the tests,
# git) need approval and are soft-denied when nobody can give it; the run still
# exits 0. Allow what a prompt needs with permissions.allow rules in
# ~/.gemini/antigravity-cli/settings.json, such as "command(git)" or
# "command(regex:npm run (build|lint|test))", or use an interactive session.
# =============================================================================

# -----------------------------------------------------------------------------
# Project Scaffolding (interactive, recommended)
# -----------------------------------------------------------------------------

# Launch agy in an empty directory, then type:
#   > Scaffold a Next.js dashboard with a Prisma backend. Follow "clean
#   > architecture": separate the domain, data, and presentation layers.

# The same request as a startup prompt (interactive session opens with it):
agy -i "Scaffold a Next.js dashboard with a Prisma backend. Follow 'clean architecture': separate the domain, data, and presentation layers."

# -----------------------------------------------------------------------------
# Feature Module Scaffolding
# -----------------------------------------------------------------------------

agy -p "Scaffold a budget management module for MoneyMind under
src/features/budget with: a budget schema with category limits, a Genkit flow
for budget analysis, and a React hook for budget state management."

# -----------------------------------------------------------------------------
# Component Scaffolding
# -----------------------------------------------------------------------------

agy -p "Create a data table component at src/components/DataTable with
sortable columns, pagination, a search filter, loading states, and TypeScript
interfaces."

# -----------------------------------------------------------------------------
# API Scaffolding
# -----------------------------------------------------------------------------

agy -p "Scaffold an Express.js REST API under src/api with user CRUD
operations, JWT authentication, Zod validation, and error handling
middleware."

# -----------------------------------------------------------------------------
# Test Scaffolding
# -----------------------------------------------------------------------------

agy -p "Set up a Jest test suite structure under tests/ with unit test
templates, integration test setup, mock utilities, and custom matchers."

# -----------------------------------------------------------------------------
# Infrastructure Scaffolding
# -----------------------------------------------------------------------------

agy -p "Create a Docker multi-stage build for this Node.js app: a development
image, a production image, docker-compose for local development, and health
checks. Put the files under docker/."

# -----------------------------------------------------------------------------
# Scaffolding with Context
# -----------------------------------------------------------------------------

# The agent already reads your workspace, so reference files by name instead
# of piping them in:

agy -p "Read src/components/ExistingCard.tsx and create a similar card
component at src/components/UserCard.tsx for displaying user profiles with
avatar, name, email, and action buttons."

agy -p "Read docs/architecture.md and create the folder structure and
boilerplate files it describes under src/."

# Multi-repo scaffolding: add a second directory to the workspace
agy --add-dir ../shared-lib -p "Scaffold a consumer module in this project
that uses the types exported from ../shared-lib."

# -----------------------------------------------------------------------------
# Large Scaffolds: Plan Before You Build
# -----------------------------------------------------------------------------

# Review the plan first, then re-run in default mode to execute it
agy --mode plan -p "Plan the scaffold for a Next.js 15 project named
'MoneyMind' with App Router and Tailwind. Include a components and lib
folder. Do NOT include a pages directory."
