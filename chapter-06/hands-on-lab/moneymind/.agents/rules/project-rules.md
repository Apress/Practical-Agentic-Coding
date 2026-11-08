---
trigger: always_on
---
# MoneyMind Workspace Rules
# Global constraints for all agent-generated code

## Language & Framework Rules

- ALL code MUST be written in TypeScript with strict mode enabled
- Use Next.js 15 with App Router architecture (NO pages directory)
- Use React 18+ with functional components and hooks
- Prefer async/await over Promise chains

## Styling Rules

- ALL styling MUST use Tailwind CSS utility classes
- DO NOT use raw CSS, CSS modules, or styled-components
- Follow the design tokens defined in .context/design_tokens.md
- Use Glassmorphism theme for card components

## Testing Rules

- ALL tests MUST use Jest as the test runner
- Write tests in TypeScript with proper type definitions
- Achieve minimum 80% code coverage for new code
- Include unit tests for all Genkit flows

## API & Data Rules

- Use the Plaid schema as defined in .context/plaid_reference.md
- IGNORE the legacy `merchant_name` field from Plaid
- Use `counterparties` array and `merchant_entity_id` for merchants
- All API routes must validate input with Zod schemas

## Security Rules

- NEVER hardcode API keys or secrets
- ALL sensitive values MUST come from environment variables
- Respect .gitignore for sensitive files
- Use proper error handling without exposing internals

## Genkit Rules

- Define all AI flows using Genkit's defineFlow
- Use Dotprompt (.prompt files) for all prompts
- Use Picoschema for token-efficient schema definitions
- Ensure all flows are observable and traceable

## Code Organization Rules

- Place React components in src/components/
- Place utility functions in src/lib/
- Place Genkit flows in src/lib/genkit.ts
- Place API routes in src/app/api/

## Output Rules

- Generate Implementation Plan Artifacts for complex tasks
- Create Walkthrough Artifacts after completing multi-file changes
- Include inline comments for complex logic
- Follow consistent naming conventions (camelCase for functions, PascalCase for components)
