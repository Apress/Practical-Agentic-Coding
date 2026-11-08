# Exercise 2: Creating Effective Steering Files

> This practice exercise has model answers. See the [Sample Solutions](#sample-solutions) at the end of this file. The four open-ended chapter exercises are in [`../../challenge-lab/`](../../challenge-lab/README.md). They give success criteria instead of answer keys.

## Overview

In this exercise, you write the three foundational steering files for a project: `product.md`, `tech.md`, and `structure.md`.

## Learning Objectives

- State the purpose of each steering file
- Write steering content
- Configure inclusion modes
- Create steering files for different project types

## Background: Steering File Fundamentals

### Three Foundational Files

| File | Purpose | Key Contents |
|------|---------|--------------|
| `product.md` | Define what you're building | Purpose, audience, features, business objectives |
| `tech.md` | Define how to build it | Frameworks, libraries, constraints, coding standards |
| `structure.md` | Define where things go | Directory layout, naming conventions, import patterns |

### Inclusion Modes

```yaml
---
inclusion: always      # Included in every interaction
---
```

```yaml
---
inclusion: fileMatch
fileMatchPattern: "components/**/*.tsx"
---
```

```yaml
---
inclusion: manual     # Referenced with #steering-file-name
---
```

```yaml
---
inclusion: auto       # Included when the request matches the description
name: api-error-conventions
description: Error response formats and status-code rules for the REST API
---
```

## Exercise Tasks

### Task 1: Analyze Existing Steering Files (15 minutes)

Read the three steering files in [`../daily-briefing-agent/.kiro/steering/`](../daily-briefing-agent/.kiro/steering/). Answer these questions:

**product.md Analysis:**

1. What is the primary purpose of the application?

   _____________________________________________

2. Who is the target audience?

   _____________________________________________

3. What persona does the application maintain?

   _____________________________________________

**tech.md Analysis:**

1. What are the non-negotiable code style requirements?

   _____________________________________________

2. How are tests organized?

   _____________________________________________

3. What AWS services are specified?

   _____________________________________________

**structure.md Analysis:**

1. What is the directory structure for source code?

   _____________________________________________

2. What naming conventions are used?

   _____________________________________________

3. What anti-patterns should be avoided?

   _____________________________________________

---

### Task 2: Create Steering Files for E-Commerce API (30 minutes)

Create steering files for a fictional e-commerce API project. Start from the templates below.

#### product.md Template

```markdown
---
inclusion: always
---

# Product Overview

## [Product Name]

[One paragraph description of what the product is and why it exists]

## Core Features

- **[Feature 1]**: [Description]
- **[Feature 2]**: [Description]
- **[Feature 3]**: [Description]

## Target Users

- [User type 1]
- [User type 2]

## Business Objectives

- [Objective 1]
- [Objective 2]
```

**Your product.md for E-Commerce API:**

```markdown
---
inclusion: always
---

# Product Overview

## E-Commerce API

[YOUR CONTENT HERE]

## Core Features

[YOUR CONTENT HERE]

## Target Users

[YOUR CONTENT HERE]

## Business Objectives

[YOUR CONTENT HERE]
```

---

#### tech.md Template

```markdown
---
inclusion: always
---

# Technology Stack & Development Guidelines

## Architecture Patterns (MANDATORY)

### Code Organization
- [Pattern 1]
- [Pattern 2]

### Error Handling Standards
- [Standard 1]
- [Standard 2]

## Technology Stack Rules

### [Language] Requirements
- [Framework]: [Purpose]
- [Library]: [Purpose]

### [Cloud Provider] Services Usage
- [Service 1]: [Purpose]
- [Service 2]: [Purpose]

## Code Style (NON-NEGOTIABLE)

### Naming Conventions
- **Files**: [convention]
- **Classes**: [convention]
- **Functions**: [convention]

## Testing Strategy (REQUIRED)

### Test Categories & Markers
- [Category 1]: [Description]
- [Category 2]: [Description]

### Coverage Requirements
- [Requirement]
```

**Your tech.md for E-Commerce API:**

```markdown
---
inclusion: always
---

# E-Commerce API Development Guidelines

## Architecture Patterns (MANDATORY)

[YOUR CONTENT HERE]

## Technology Stack Rules

[YOUR CONTENT HERE]

## Code Style (NON-NEGOTIABLE)

[YOUR CONTENT HERE]

## Testing Strategy (REQUIRED)

[YOUR CONTENT HERE]
```

---

#### structure.md Template

~~~markdown
# Project Structure & Organization

## Directory Layout

```text
project-name/
├── src/
│   ├── [module]/
│   └── [module]/
├── tests/
└── infrastructure/
```

## Source Code Organization

### [Module Name] (`src/[module]/`)
- [Description of contents]

## File Naming Conventions

### [File Type]
- [Convention]

## Import Conventions

### [Import Type]
```[language]
[Example]
```

## Anti-Patterns to Avoid

### [Category]
- [Anti-pattern 1]
- [Anti-pattern 2]
~~~

**Your structure.md for E-Commerce API:**

```markdown
# E-Commerce API Project Structure

## Directory Layout

[YOUR CONTENT HERE]

## Source Code Organization

[YOUR CONTENT HERE]

## File Naming Conventions

[YOUR CONTENT HERE]

## Anti-Patterns to Avoid

[YOUR CONTENT HERE]
```

---

### Task 3: Create Specialized Steering Files (20 minutes)

Create two more steering files, one with conditional inclusion and one with manual inclusion.

#### API Standards File (fileMatch inclusion)

Create `api-standards.md`. It loads only when you work on API files:

```markdown
---
inclusion: fileMatch
fileMatchPattern: "**/api/**/*.py"
---

# API Development Standards

## REST Conventions

[YOUR CONTENT HERE]

## Error Response Format

[YOUR CONTENT HERE]

## Authentication Requirements

[YOUR CONTENT HERE]
```

#### Migration Guide (manual inclusion)

Create `migration-guide.md`. You reference it on demand:

```markdown
---
inclusion: manual
---

# Database Migration Guide

## When to Create Migrations

[YOUR CONTENT HERE]

## Migration Naming Convention

[YOUR CONTENT HERE]

## Rollback Procedures

[YOUR CONTENT HERE]
```

---

### Task 4: Steering Files Best Practices Quiz (10 minutes)

Answer these questions:

1. **Why should steering files be kept focused on a single domain?**

   _____________________________________________

2. **What types of content should NEVER be in steering files?**

   _____________________________________________

3. **How can you reference live workspace files in steering documentation?**

   _____________________________________________

4. **What happens when workspace and global steering files conflict?**

   _____________________________________________

5. **When should you use manual inclusion vs. always inclusion?**

   _____________________________________________

---

## Sample Solutions

### Task 2: E-Commerce API Steering Files

#### Sample product.md

```markdown
---
inclusion: always
---

# Product Overview

## E-Commerce API

A RESTful API service that powers online retail operations, enabling merchants
to manage products, process orders, and handle customer transactions securely
and efficiently.

## Core Features

- **Product Catalog Management**: Create, update, and organize products with
  variants, pricing, and inventory tracking
- **Order Processing**: Handle cart operations, checkout flow, and order
  lifecycle management
- **Customer Management**: User registration, authentication, and profile
  management
- **Payment Integration**: Secure payment processing with multiple gateway
  support

## Target Users

- Frontend developers building e-commerce web and mobile applications
- Third-party integrators connecting marketplace platforms
- Internal tools and admin dashboard developers

## Business Objectives

- Provide reliable, scalable API infrastructure for retail operations
- Enable rapid frontend development with complete documentation
- Support multiple sales channels through unified API interface
- Maintain PCI compliance for payment data handling
```

There is no single right `tech.md` or `structure.md` for a fictional project. Compare yours with the templates in [`../../code-examples/steering-files/`](../../code-examples/steering-files/) and the lab starter's own files in [`../daily-briefing-agent/.kiro/steering/`](../daily-briefing-agent/.kiro/steering/).

Check your Task 3 files for:

- Valid front matter
- A pattern that matches the intended files
- Content about a single domain

### Task 4: Quiz Answers

1. **Why should steering files be kept focused on a single domain?**
   - Focused files are easier to maintain and update
   - Reduces cognitive load when reading
   - Allows selective inclusion based on context
   - Prevents conflicting guidance in single file

2. **What types of content should NEVER be in steering files?**
   - Credentials, API keys, or secrets
   - Customer data or PII
   - Temporary debugging instructions
   - Highly volatile information that changes frequently

3. **How can you reference live workspace files in steering documentation?**
   - Use the syntax: `#[[file:<relative_file_name>]]`
   - Example: `#[[file:api/openapi.yaml]]`

4. **What happens when workspace and global steering files conflict?**
   - Workspace steering takes precedence over global steering
   - This allows project-specific overrides of global conventions

5. **When should you use manual inclusion vs. always inclusion?**
   - **Always**: Core standards, security policies, universal conventions
   - **Manual**: Heavy documentation, specialized workflows, troubleshooting guides, migration procedures

## Summary

Check that your steering files:

- Give clear, actionable guidance
- Are organized by domain or concern
- Use the right inclusion mode
- Include examples where helpful
- Explain the "why" behind decisions
- Are reviewed and updated regularly
