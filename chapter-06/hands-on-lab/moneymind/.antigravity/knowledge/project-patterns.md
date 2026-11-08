# MoneyMind Project Patterns

## Knowledge Item: Project Conventions

This document captures learned patterns and preferences for the MoneyMind project.

### Component Naming Patterns

- Dashboard components: `*Dashboard.tsx` (e.g., `TransactionDashboard.tsx`)
- Card components: `*Card.tsx` (e.g., `WasteCard.tsx`, `TransactionCard.tsx`)
- List components: `*List.tsx` (e.g., `TransactionList.tsx`)
- Form components: `*Form.tsx` (e.g., `FilterForm.tsx`)

### Genkit Flow Patterns

Flow names read `[action][Resource]Flow`. Every flow takes its config object first and its implementation second, and they all share the one `ai` instance from `src/lib/ai.ts`.

```typescript
import { ai } from './ai';

export const enrichTransactionFlow = ai.defineFlow(
  { name: 'enrichTransactionFlow', inputSchema, outputSchema },
  async (input) => { /* ... */ }
);
```

### Prompt File Organization

One `.prompt` file per task, named after the task, because `ai.prompt('classify')` resolves by filename:

```text
prompts/
├── classify.prompt      - Transaction classification
└── waste-detect.prompt  - Subscription waste detection
```

### Environment Variables

```bash
# Required
GEMINI_API_KEY=     # Genkit/Gemini API access

# Optional (for production)
PLAID_CLIENT_ID=          # Plaid integration
PLAID_SECRET=             # Plaid secret
USE_MOCK_DATA=true        # Toggle mock vs real API
```

### Error Handling Pattern

```typescript
try {
  const result = await someOperation();
  return { success: true, data: result };
} catch (error) {
  console.error('[Context]:', error);
  return { success: false, error: 'User-friendly message' };
}
```

### Testing Patterns

- Unit tests: `*.test.ts` alongside the source file, as in `src/lib/mock-data.test.ts`
- Jest runs with ts-jest in the node environment; component tests need the jsdom environment instead
- Keep deterministic logic testable without a model call, so a red test means the code broke rather than the model changed its mind

### API Route Patterns

```text
app/api/[resource]/route.ts       - collection endpoints (GET list, POST create)
app/api/[resource]/[id]/route.ts  - item endpoints (GET one, PUT update, DELETE)
```

---

*A Knowledge Item: the patterns this project has settled on, so a new session does not have to rediscover them. Antigravity extracts items like this from conversations, and you can also write them by hand.*
