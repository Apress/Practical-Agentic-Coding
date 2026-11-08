# Plaid Transaction Object Reference

## Overview

This document provides the authoritative schema reference for Plaid Transaction objects used in MoneyMind. Agents MUST use this reference when working with transaction data.

## Critical Field Mapping

> **IMPORTANT**: The agent MUST ignore the legacy `merchant_name` field. Instead, use the `counterparties` array and `merchant_entity_id` for identifying merchants.

### Preferred Fields

| Field | Purpose | Use Case |
|-------|---------|----------|
| `counterparties[].name` | Merchant name | Primary merchant identification |
| `counterparties[].entity_id` | Counterparty entity ID | Cross-referencing a specific counterparty |
| `merchant_entity_id` (top-level) | Unique merchant ID | Deduplication and categorization |
| `iso_currency_code` | Currency | Map to schema `currency` field |
| `amount` | Transaction amount | Positive = debit, Negative = credit |
| `date` | Transaction date | ISO 8601 format |

### Deprecated Fields (DO NOT USE)

| Field | Reason |
|-------|--------|
| `merchant_name` | Legacy field, unreliable |
| `name` | Raw description, not normalized |

## Transaction Schema

```typescript
interface PlaidTransaction {
  // Identification
  transaction_id: string;
  account_id: string;

  // Amount & Currency
  amount: number;                    // Positive = money out, Negative = money in
  iso_currency_code: string;         // "USD", "EUR", etc.
  unofficial_currency_code?: string;

  // Date
  date: string;                      // ISO 8601: "2024-01-15"
  datetime?: string;                 // ISO 8601 with time
  authorized_date?: string;

  // Description (legacy - use counterparties instead)
  name: string;                      // Raw merchant description
  merchant_name?: string;            // DEPRECATED - do not use

  // Modern Merchant Identification (PREFERRED)
  counterparties: Counterparty[];
  merchant_entity_id?: string;

  // Categorization
  category?: string[];               // Plaid categories
  category_id?: string;
  personal_finance_category?: {
    primary: string;
    detailed: string;
    confidence_level: string;
  };

  // Location
  location?: {
    address?: string;
    city?: string;
    region?: string;
    postal_code?: string;
    country?: string;
    lat?: number;
    lon?: number;
    store_number?: string;
  };

  // Payment Details
  payment_channel: 'online' | 'in store' | 'other';
  transaction_type?: string;

  // Status
  pending: boolean;
}

interface Counterparty {
  name: string;                      // Clean merchant name
  type: 'merchant' | 'financial_institution' | 'payment_app' | 'marketplace';
  logo_url?: string;
  website?: string;
  entity_id?: string;
  confidence_level: 'VERY_HIGH' | 'HIGH' | 'MEDIUM' | 'LOW';
}
```

## Example Transaction

```json
{
  "transaction_id": "txn_001abc",
  "account_id": "acc_xyz789",
  "amount": 4.99,
  "iso_currency_code": "USD",
  "date": "2024-01-15",
  "name": "STARBUCKS #12345 SEATTLE WA",
  "merchant_name": "Starbucks",
  "counterparties": [
    {
      "name": "Starbucks",
      "type": "merchant",
      "logo_url": "https://plaid-counterparty-logos.plaid.com/starbucks_logo.png",
      "website": "starbucks.com",
      "entity_id": "ent_starbucks",
      "confidence_level": "VERY_HIGH"
    }
  ],
  "merchant_entity_id": "ent_starbucks",
  "personal_finance_category": {
    "primary": "FOOD_AND_DRINK",
    "detailed": "FOOD_AND_DRINK_COFFEE",
    "confidence_level": "VERY_HIGH"
  },
  "location": {
    "city": "Seattle",
    "region": "WA",
    "country": "US"
  },
  "payment_channel": "in store",
  "pending": false
}
```

## Mapping to MoneyMind Schema

When processing Plaid transactions, map fields as follows:

```typescript
// MoneyMind enrichment input
const enrichmentInput = {
  description: transaction.name,                               // Raw description
  amount: transaction.amount,
  currency: transaction.iso_currency_code,
  merchant_hint: transaction.counterparties?.[0]?.name || undefined  // PREFERRED
};
```

## Subscription Detection Patterns

Transactions likely to be recurring subscriptions:

1. `personal_finance_category.detailed` contains "SUBSCRIPTION"
2. Same `merchant_entity_id` appears monthly
3. Amount is consistent across multiple transactions
4. Payment channel is "online"

## Common Categories for MoneyMind

| Plaid Primary Category | MoneyMind Category |
|----------------------|-------------------|
| FOOD_AND_DRINK | Groceries or Dining |
| TRANSPORTATION | Transport |
| RENT_AND_UTILITIES | Housing |
| INCOME | Income |
| ENTERTAINMENT | Subscription |
| GENERAL_SERVICES | Subscription |

---

*Use this reference for all transaction-related development in MoneyMind.*
