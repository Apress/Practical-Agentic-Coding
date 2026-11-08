# Chapter 6 Exercises

These three exercises practice the habits Chapter 6 teaches. Each one works on the MoneyMind project.

## Prerequisites

- At least Phase 1 of the [MoneyMind lab](../README.md) complete, or the finished project installed
- Google Antigravity IDE installed and signed in
- The Antigravity CLI installed (`curl -fsSL https://antigravity.google/cli/install.sh | bash`, then `agy install`. On Windows, see the [CLI guide](../../tutorials/antigravity-cli-guide.md#installation).)
- `GEMINI_API_KEY` set in `moneymind/.env` (for the Genkit parts)

## Exercise List

| Exercise | Focus | Book section | Time | Level |
|----------|-------|--------------|------|-------|
| [Exercise 1](./exercise-1-intent-first.md) | Intent-first development | Section 6.1 | 30-45 min | Beginner |
| [Exercise 2](./exercise-2-antigravity-cli.md) | Antigravity CLI mastery | Section 6.4 | 35-45 min | Intermediate |
| [Exercise 3](./exercise-3-artifacts.md) | Artifacts and Knowledge Items | Section 6.3 | 30-40 min | Intermediate |

## Learning Path

### Recommended Order

1. **Exercise 1: Intent-First Development**
   - Drive the Perceive-Plan-Act-Verify loop
   - Write intent-focused prompts
   - Review artifacts and give feedback on them

2. **Exercise 2: Antigravity CLI Mastery**
   - Work with the terminal agent
   - Use prompts for diagnosis, review, and scaffolding
   - Create Agent Skills

3. **Exercise 3: Artifacts & Knowledge Items**
   - Generate and review artifacts
   - Create Knowledge Items that persist across sessions
   - Share artifacts and Knowledge Items with a team

## Quick Start

```bash
cd chapter-06/hands-on-lab/moneymind
npm ci                    # installs the exact versions in package-lock.json
cp .env.example .env      # then add your GEMINI_API_KEY (Windows: copy .env.example .env)
npm test                  # confirms the clone is sound, no API key needed
npm run dev               # http://localhost:3000
```

## Key Concepts Covered

### Exercise 1: Intent-First Development
- Perceive-Plan-Act-Verify loop
- Fast Mode vs Plan Mode
- Artifact review and feedback

### Exercise 2: Antigravity CLI
- Driving the terminal agent (prompts, slash commands, shell mode)
- Diagnosis and review prompts
- Skill creation (.agents/skills/)
- CI/CD integration (headless print mode)

### Exercise 3: Artifacts & Knowledge Items
- Artifact types and purposes
- Knowledge Item creation and management
- Cross-session memory
- Documentation patterns

## Self-Assessment

After completing all exercises, you should be able to:

- [ ] Express development intent without specifying implementation details
- [ ] Use Plan Mode for complex architectural tasks
- [ ] Review and provide feedback on Implementation Plan Artifacts
- [ ] Use the Antigravity CLI for error resolution (the "Smart Fix" loop)
- [ ] Run review prompts before pushing (the "Auto-Review" loop)
- [ ] Build Agent Skills invoked as plain slash commands
- [ ] Generate and review different artifact types
- [ ] Create Knowledge Items for persistent context
- [ ] Use the browser subagent for visual verification

## Troubleshooting

**`agy` not found**
```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
agy install
```

**Genkit API key errors**
Set `GEMINI_API_KEY` in `moneymind/.env`. Start the server with `npm run genkit` (which passes `--env-file=.env`).

**The Genkit Developer UI shows no flows**
Either you ran a bare `npx genkit start` with no entry point, or something called `genkit({...})` twice. Use `npm run genkit`. Keep the one instance in `src/lib/ai.ts`.

**Antigravity extension not found**
Antigravity's extension source is the Open VSX Registry. If an extension is missing from it, install it from a VSIX file (Extensions view "..." menu, **Install from VSIX**).

For more fixes, see the troubleshooting section of the [lab README](../README.md#troubleshooting).

## Additional Resources

- [Antigravity Documentation](https://antigravity.google/docs)
- [Antigravity CLI Reference](https://antigravity.google/docs/cli/reference)
- [Genkit Documentation](https://genkit.dev/docs/get-started/)

---

## Navigation

- [Back to Hands-On Lab](../README.md)
- [Code Examples](../../code-examples/)
- [Tutorials](../../tutorials/)
- [Chapter 6 Overview](../../README.md)
