# Implementation Plan Artifact

**Feature**: Spending Summary Dashboard Card
**Agent**: Antigravity (Pro-class model, Plan mode)
**Status**: Pending Review

---

## Overview

This plan outlines the implementation of a Spending Summary card component that displays aggregated spending by category with visual representations.

## Objectives

1. Create a reusable SpendingSummary component
2. Implement category aggregation logic
3. Add visual progress bars for each category
4. Integrate with existing transaction data flow

---

## Phase 1: Data Layer

### Task 1.1: Create Aggregation Utility

**File**: `src/lib/spending-utils.ts`

**Purpose**: Utility functions for aggregating transactions by category.

**Interface**:
```typescript
interface CategorySummary {
  category: string;
  total: number;
  percentage: number;
  count: number;
}

function aggregateByCategory(transactions: EnrichedTransaction[]): CategorySummary[];
```

**Dependencies**:
- `src/lib/genkit.ts` - EnrichedTransaction type

**Estimated Complexity**: Low

### Task 1.2: Add API Endpoint

**File**: `src/app/api/spending-summary/route.ts`

**Purpose**: API endpoint that returns aggregated spending data.

**Response Schema**:
```typescript
{
  success: boolean;
  data: {
    categories: CategorySummary[];
    total: number;
    period: string;
  }
}
```

**Dependencies**:
- `src/lib/spending-utils.ts`
- `src/app/api/transactions/route.ts` - for data source

---

## Phase 2: UI Components

### Task 2.1: Create CategoryBar Component

**File**: `src/components/CategoryBar.tsx`

**Purpose**: Individual progress bar for a spending category.

**Props**:
```typescript
interface CategoryBarProps {
  category: string;
  amount: number;
  percentage: number;
  color: string;
}
```

**Design Notes**:
- Use Tailwind `bg-gradient-to-r` for progress effect
- Follow Glassmorphism theme from design tokens
- Include hover state showing exact amount

### Task 2.2: Create SpendingSummary Component

**File**: `src/components/SpendingSummary.tsx`

**Purpose**: Container component displaying all category bars.

**Props**:
```typescript
interface SpendingSummaryProps {
  period?: 'week' | 'month' | 'year';
  showTotal?: boolean;
}
```

**Features**:
- Loading skeleton state
- Error state with retry
- Empty state message
- Total spending badge

---

## Phase 3: Integration

### Task 3.1: Update Dashboard Page

**File**: `src/app/page.tsx`

**Changes**:
- Add SpendingSummary to dashboard grid
- Position in sidebar or main area (TBD based on layout)

### Task 3.2: Add Tests

**File**: `src/components/SpendingSummary.test.tsx`

**Coverage**:
- Rendering with mock data
- Loading state
- Error handling
- Category click interactions

---

## Technical Decisions

### Decision 1: Client vs Server Rendering

**Choice**: Client-side rendering with SWR
**Rationale**: Allows real-time updates when transactions change

### Decision 2: Chart Library

**Choice**: Custom Tailwind implementation
**Rationale**: Follows project rules (no external charting libraries)

### Decision 3: Color Scheme

**Choice**: Category-based colors from design tokens
**Rationale**: Consistency with existing category badges

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Large dataset performance | Medium | High | Implement pagination/virtualization |
| Color accessibility | Low | Medium | Use design tokens with AA contrast |
| API latency | Low | Medium | Add loading states, consider caching |

---

## File Change Summary

| Action | Path | Description |
|--------|------|-------------|
| CREATE | `src/lib/spending-utils.ts` | Aggregation utilities |
| CREATE | `src/app/api/spending-summary/route.ts` | Summary API |
| CREATE | `src/components/CategoryBar.tsx` | Progress bar component |
| CREATE | `src/components/SpendingSummary.tsx` | Summary container |
| CREATE | `src/components/SpendingSummary.test.tsx` | Component tests |
| MODIFY | `src/app/page.tsx` | Dashboard integration |

---

## Estimated Effort

| Phase | Tasks | Time Estimate |
|-------|-------|---------------|
| Phase 1: Data Layer | 2 | 30 minutes |
| Phase 2: UI Components | 2 | 45 minutes |
| Phase 3: Integration | 2 | 20 minutes |
| **Total** | **6** | **~95 minutes** |

---

## Review Questions

1. Should the summary update in real-time or on manual refresh?
2. What time period should be the default (week/month)?
3. Should categories be clickable to show transactions?

---

**Awaiting Approval**

Please review this plan and provide feedback before implementation begins.
