# MoneyMind Design System Tokens

## Overview

This document defines the design tokens and UI patterns for MoneyMind. All components MUST adhere to these specifications.

## Theme: Glassmorphism

MoneyMind uses a modern Glassmorphism design language with:
- Frosted glass effects
- Subtle transparency
- Soft shadows
- Vibrant accent colors

## Color Palette

### Primary Colors

```css
--color-primary-50: #f0fdf4;
--color-primary-100: #dcfce7;
--color-primary-500: #22c55e;    /* Main brand green */
--color-primary-600: #16a34a;
--color-primary-700: #15803d;
```

### Semantic Colors

```css
--color-income: #22c55e;         /* Green - positive */
--color-expense: #ef4444;        /* Red - negative */
--color-warning: #f59e0b;        /* Amber - attention */
--color-info: #3b82f6;           /* Blue - informational */
```

### Glassmorphism Base

```css
--glass-bg: rgba(255, 255, 255, 0.1);
--glass-border: rgba(255, 255, 255, 0.2);
--glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
--glass-blur: blur(10px);
```

## Tailwind Utility Classes

### Card Component (Glassmorphism)

```html
<div class="bg-white/10 backdrop-blur-lg border border-white/20
            rounded-2xl shadow-lg p-6">
  <!-- Card content -->
</div>
```

### Waste Card (High Contrast Warning)

```html
<div class="bg-red-500/10 backdrop-blur-lg border border-red-500/30
            rounded-2xl shadow-lg p-6">
  <span class="bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
    $14.99/mo
  </span>
</div>
```

### Transaction Amount

```html
<!-- Expense (positive amount = money out) -->
<span class="text-red-500 font-semibold">-$4.99</span>

<!-- Income (negative amount = money in) -->
<span class="text-green-500 font-semibold">+$1,500.00</span>
```

## Typography

### Font Stack

```css
--font-sans: 'Inter', system-ui, -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### Text Sizes

| Element | Tailwind Class | Size |
|---------|---------------|------|
| Page Title | `text-3xl font-bold` | 30px |
| Section Header | `text-xl font-semibold` | 20px |
| Card Title | `text-lg font-medium` | 18px |
| Body Text | `text-base` | 16px |
| Small/Caption | `text-sm text-gray-500` | 14px |

## Component Patterns

### WasteCard

```tsx
// Required elements:
// 1. Merchant logo (normalized)
// 2. Monthly cost badge (high-contrast red)
// 3. Usage warning ("0 days" indicator)
// 4. Cancel action button

<div className="bg-red-500/10 backdrop-blur-lg border border-red-500/30
               rounded-2xl p-6 space-y-4">
  {/* Logo */}
  <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
    <span className="text-2xl">{merchantEmoji}</span>
  </div>

  {/* Merchant & Cost */}
  <div className="flex justify-between items-start">
    <h3 className="text-lg font-semibold">{merchantName}</h3>
    <span className="bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
      ${monthlyCost}/mo
    </span>
  </div>

  {/* Usage Warning */}
  <p className="text-red-400 text-sm">
    Usage: {daysUsed} days in the last 30 days
  </p>

  {/* Action Button */}
  <button className="w-full bg-red-500 hover:bg-red-600 text-white
                     py-2 px-4 rounded-lg transition-colors">
    Cancel Subscription
  </button>
</div>
```

### TransactionCard

```tsx
<div className="bg-white/10 backdrop-blur-lg border border-white/20
               rounded-xl p-4 flex items-center gap-4">
  {/* Merchant Logo */}
  <div className="w-10 h-10 rounded-full bg-white/20" />

  {/* Details */}
  <div className="flex-1">
    <p className="font-medium">{merchantName}</p>
    <p className="text-sm text-gray-400">{category} - {date}</p>
  </div>

  {/* Amount */}
  <span className={amount > 0 ? 'text-red-500' : 'text-green-500'}>
    {formatCurrency(amount)}
  </span>
</div>
```

## Spacing Scale

```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
```

## Border Radius

```css
--radius-sm: 0.375rem;   /* 6px - buttons */
--radius-md: 0.5rem;     /* 8px - inputs */
--radius-lg: 0.75rem;    /* 12px - small cards */
--radius-xl: 1rem;       /* 16px - large cards */
--radius-2xl: 1.5rem;    /* 24px - main cards */
--radius-full: 9999px;   /* badges, avatars */
```

## Animation

### Transitions

```css
--transition-fast: 150ms ease;
--transition-base: 200ms ease;
--transition-slow: 300ms ease;
```

### Hover States

```tsx
// Buttons
className="transition-colors hover:bg-primary-600"

// Cards
className="transition-transform hover:scale-[1.02]"

// Links
className="transition-colors hover:text-primary-500"
```

---

*Reference this document when creating or modifying UI components.*
