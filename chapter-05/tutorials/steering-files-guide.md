# Steering files: quick reference

This page shows where Kiro steering files live, how to write their front matter, and how to check that Kiro reads them. Copy the templates in [`../code-examples/steering-files/`](../code-examples/steering-files/) into `.kiro/steering/` and adapt them.

What steering is for, when to use each inclusion mode, and steering best practices: Chapter 5, Section 5.4.

For the latest syntax, see the [Kiro documentation](https://kiro.dev/docs/).

## Where steering files live

| Scope | Location | Applies to |
|-------|----------|------------|
| Workspace | `.kiro/steering/` in the project root | That workspace |
| Global | `~/.kiro/steering/` in your home directory | Every workspace |

When the two conflict, workspace steering wins.

## The three foundational files

| File | Contents |
|------|----------|
| `product.md` | Product name and description, core features, target users and personas, business objectives and success metrics |
| `tech.md` | Languages and frameworks, third-party libraries, cloud services, coding standards, testing strategy, error handling patterns |
| `structure.md` | Directory layout, module organization, file naming conventions, import ordering, anti-patterns to avoid |

Templates: [`product-template.md`](../code-examples/steering-files/product-template.md), [`tech-template.md`](../code-examples/steering-files/tech-template.md), [`structure-template.md`](../code-examples/steering-files/structure-template.md).

### Minimal example

```markdown
---
inclusion: always
---

# Product Overview

## Tech News Aggregator

A web application that serves as a tech news aggregator with a distinctive
"Witty Tech Journalist" persona. The system curates technology stories from
various sources and presents them with sharp, concise, and slightly cynical
summaries that prioritize substance over hype.

## Core Features

- **Automated Story Collection**: Collects tech news from multiple sources
- **AI-Powered Summaries**: Uses Amazon Bedrock for witty commentary
- **Quality Curation**: Filters stories based on relevance and quality
```

## Inclusion modes

Set the mode in the YAML front matter at the top of the file.

### Always included (default)

```yaml
---
inclusion: always
---
```

Kiro loads the file in every interaction.

### Conditional inclusion (fileMatch)

```yaml
---
inclusion: fileMatch
fileMatchPattern: "components/**/*.tsx"
---
```

Kiro loads the file when the interaction involves files that match `fileMatchPattern`.

### Manual inclusion

```yaml
---
inclusion: manual
---
```

Reference the file in chat with `#steering-file-name`.

### Auto inclusion

```yaml
---
inclusion: auto
name: api-error-conventions
description: Error response formats and status-code rules for the REST API
---
```

1. Set `inclusion: auto`.
2. Add a `name` and a `description`.
3. Write the description as the topic a request would mention. Kiro compares requests against it when it decides whether to load the file.

To load the file on demand, run it as a slash command, the same way you run a manual file.

## Linking to live files

Reference a workspace file from a steering file with this syntax:

```markdown
## API Specification

See the current API specification:
#[[file:api/openapi.yaml]]

## Database Schema

Current schema definition:
#[[file:infrastructure/schema.sql]]
```

The reference follows the file as it changes.

## AGENTS.md

Kiro always includes `AGENTS.md`, whatever the inclusion mode settings. Put it in one of these places:

- Project root: `./AGENTS.md`
- Global steering: `~/.kiro/steering/AGENTS.md`
- A subdirectory, next to the code it describes, such as `services/api/AGENTS.md`

## Keep secrets out

Never put these in a steering file:

- API keys or secrets
- Passwords or credentials
- Connection strings with passwords
- Personal data or PII

Point to where the secret is stored instead:

```markdown
Database credentials are stored in AWS Secrets Manager.
Reference: `tech-news-aggregator/aurora-credentials`
```

## Troubleshooting

### Steering files not loading

1. **Check the location.** Files must be in `.kiro/steering/`.
2. **Check the front matter.** The YAML syntax must be valid.
3. **Check the file extension.** It must be `.md`.
4. **Restart Kiro.** Some changes need a restart.

### Conflicting guidance

1. **Find the source.** Identify the files that conflict.
2. **Apply precedence.** Workspace wins over global.
3. **Remove duplication.** Keep each rule in one place.
4. **Be explicit.** More specific guidance overrides general guidance.

### Steering not being applied

1. **Check the inclusion mode.** It must be `always`, `fileMatch`, `manual`, or `auto`.
2. **Check the patterns.** Make sure `fileMatchPattern` matches your files. For `auto`, make sure the `description` describes the requests that should trigger the file.
3. **Reference it manually.** Use `#file-name` in chat for manual files.
4. **Test in chat.** Ask Kiro "What do you know about [topic]?"

## Next Steps

1. Practice with [Exercise 2: Steering Files](../hands-on-lab/exercises/exercise-2-steering-files.md).
2. Review the [lab starter's steering files](../hands-on-lab/daily-briefing-agent/.kiro/steering/). Then compare them with the [reference set from the author's run](../daily-briefing-agent/.kiro/steering/).
3. Start the [hands-on lab](../hands-on-lab/README.md).

## Quick Reference

### Inclusion Mode Syntax

```yaml
# Always included
---
inclusion: always
---

# Conditional on file pattern
---
inclusion: fileMatch
fileMatchPattern: "**/*.py"
---

# Manual reference with #filename
---
inclusion: manual
---

# Auto-activated when the request matches the description
---
inclusion: auto
name: short-slash-command-name
description: What requests this guidance applies to
---
```

### File Linking Syntax

```markdown
#[[file:relative/path/to/file.yaml]]
```

### Standard File Names

| File | Purpose |
|------|---------|
| `product.md` | Product vision |
| `tech.md` | Technology stack |
| `structure.md` | Code organization |
| `AGENTS.md` | Agent directives (always included) |
| `api-standards.md` | REST conventions |
| `testing-standards.md` | Test patterns |
| `security-policies.md` | Security rules |
