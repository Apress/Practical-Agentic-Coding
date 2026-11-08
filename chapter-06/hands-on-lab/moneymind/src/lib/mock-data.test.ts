/**
 * Tests for the mock transaction source.
 *
 * These run without a GEMINI_API_KEY and without calling a model, which is the
 * point: the deterministic parts of MoneyMind (filtering, Plaid field mapping)
 * should be testable on their own, so a failing test means your code broke
 * rather than the model changed its mind.
 *
 * Run with: npm test
 */

import { getMockTransactions, mockTransactions } from './mock-data';

describe('getMockTransactions', () => {
  it('returns every transaction when no options are given', () => {
    expect(getMockTransactions()).toHaveLength(mockTransactions.length);
  });

  it('honors the limit option', () => {
    expect(getMockTransactions({ limit: 3 })).toHaveLength(3);
  });

  it('filters by Plaid primary category', () => {
    const results = getMockTransactions({ category: 'ENTERTAINMENT' });

    expect(results.length).toBeGreaterThan(0);
    for (const transaction of results) {
      expect(transaction.personal_finance_category?.primary).toBe('ENTERTAINMENT');
    }
  });

  it('filters by date range inclusively', () => {
    const results = getMockTransactions({
      startDate: '2024-01-14',
      endDate: '2024-01-15',
    });

    expect(results.length).toBeGreaterThan(0);
    for (const transaction of results) {
      expect(transaction.date >= '2024-01-14').toBe(true);
      expect(transaction.date <= '2024-01-15').toBe(true);
    }
  });

  it('returns an empty array for an unknown category', () => {
    expect(getMockTransactions({ category: 'NOT_A_CATEGORY' })).toEqual([]);
  });
});

describe('mock transaction shape', () => {
  it('identifies merchants through counterparties, not the legacy field', () => {
    // .context/plaid_reference.md tells the agent to ignore merchant_name and
    // read counterparties instead. The mock data has to follow the same rule,
    // or the lab teaches one thing and tests another.
    for (const transaction of mockTransactions) {
      expect(transaction.counterparties.length).toBeGreaterThan(0);
      expect(transaction.counterparties[0].name).toBeTruthy();
      expect(transaction.merchant_name).toBeUndefined();
    }
  });

  it('gives every transaction a currency code the prompt can use', () => {
    for (const transaction of mockTransactions) {
      expect(transaction.iso_currency_code).toMatch(/^[A-Z]{3}$/);
    }
  });
});
