/**
 * MoneyMind Mock Transaction Data
 *
 * Realistic Plaid-format transactions for development and testing.
 * Uses counterparties array (NOT deprecated merchant_name).
 */

import type { PlaidTransaction } from './genkit';

export const mockTransactions: PlaidTransaction[] = [
  // Subscription - Netflix
  {
    transaction_id: 'txn_netflix_001',
    account_id: 'acc_checking_001',
    amount: 15.99,
    iso_currency_code: 'USD',
    date: '2024-01-15',
    name: 'NETFLIX.COM 866-579-7172 CA',
    counterparties: [
      {
        name: 'Netflix',
        type: 'merchant',
        logo_url: 'https://plaid-counterparty-logos.plaid.com/netflix_logo.png',
        website: 'netflix.com',
        entity_id: 'ent_netflix',
        confidence_level: 'VERY_HIGH',
      },
    ],
    merchant_entity_id: 'ent_netflix',
    personal_finance_category: {
      primary: 'ENTERTAINMENT',
      detailed: 'ENTERTAINMENT_TV_AND_MOVIES',
      confidence_level: 'VERY_HIGH',
    },
    payment_channel: 'online',
    pending: false,
  },

  // Subscription - Spotify
  {
    transaction_id: 'txn_spotify_001',
    account_id: 'acc_checking_001',
    amount: 9.99,
    iso_currency_code: 'USD',
    date: '2024-01-14',
    name: 'SPOTIFY USA 877-778-8469',
    counterparties: [
      {
        name: 'Spotify',
        type: 'merchant',
        logo_url: 'https://plaid-counterparty-logos.plaid.com/spotify_logo.png',
        website: 'spotify.com',
        entity_id: 'ent_spotify',
        confidence_level: 'VERY_HIGH',
      },
    ],
    merchant_entity_id: 'ent_spotify',
    personal_finance_category: {
      primary: 'ENTERTAINMENT',
      detailed: 'ENTERTAINMENT_MUSIC_AND_AUDIO',
      confidence_level: 'VERY_HIGH',
    },
    payment_channel: 'online',
    pending: false,
  },

  // Dining - Starbucks
  {
    transaction_id: 'txn_starbucks_001',
    account_id: 'acc_checking_001',
    amount: 6.45,
    iso_currency_code: 'USD',
    date: '2024-01-15',
    name: 'STARBUCKS #12345 SEATTLE WA',
    counterparties: [
      {
        name: 'Starbucks',
        type: 'merchant',
        logo_url: 'https://plaid-counterparty-logos.plaid.com/starbucks_logo.png',
        website: 'starbucks.com',
        entity_id: 'ent_starbucks',
        confidence_level: 'VERY_HIGH',
      },
    ],
    merchant_entity_id: 'ent_starbucks',
    personal_finance_category: {
      primary: 'FOOD_AND_DRINK',
      detailed: 'FOOD_AND_DRINK_COFFEE',
      confidence_level: 'VERY_HIGH',
    },
    payment_channel: 'in store',
    pending: false,
  },

  // Transport - Uber
  {
    transaction_id: 'txn_uber_001',
    account_id: 'acc_checking_001',
    amount: 24.5,
    iso_currency_code: 'USD',
    date: '2024-01-14',
    name: 'UBER *TRIP HELP.UBER.COM',
    counterparties: [
      {
        name: 'Uber',
        type: 'merchant',
        logo_url: 'https://plaid-counterparty-logos.plaid.com/uber_logo.png',
        website: 'uber.com',
        entity_id: 'ent_uber',
        confidence_level: 'VERY_HIGH',
      },
    ],
    merchant_entity_id: 'ent_uber',
    personal_finance_category: {
      primary: 'TRANSPORTATION',
      detailed: 'TRANSPORTATION_TAXIS_AND_RIDE_SHARES',
      confidence_level: 'VERY_HIGH',
    },
    payment_channel: 'online',
    pending: false,
  },

  // Groceries - Whole Foods
  {
    transaction_id: 'txn_wholefoods_001',
    account_id: 'acc_checking_001',
    amount: 87.34,
    iso_currency_code: 'USD',
    date: '2024-01-13',
    name: 'WHOLE FOODS MARKET #10234',
    counterparties: [
      {
        name: 'Whole Foods Market',
        type: 'merchant',
        logo_url: 'https://plaid-counterparty-logos.plaid.com/wholefoods_logo.png',
        website: 'wholefoodsmarket.com',
        entity_id: 'ent_wholefoods',
        confidence_level: 'VERY_HIGH',
      },
    ],
    merchant_entity_id: 'ent_wholefoods',
    personal_finance_category: {
      primary: 'FOOD_AND_DRINK',
      detailed: 'FOOD_AND_DRINK_GROCERIES',
      confidence_level: 'VERY_HIGH',
    },
    payment_channel: 'in store',
    pending: false,
  },

  // Housing - Electric Bill
  {
    transaction_id: 'txn_electric_001',
    account_id: 'acc_checking_001',
    amount: 145.67,
    iso_currency_code: 'USD',
    date: '2024-01-10',
    name: 'SEATTLE CITY LIGHT AUTOPAY',
    counterparties: [
      {
        name: 'Seattle City Light',
        type: 'merchant',
        entity_id: 'ent_scl',
        confidence_level: 'HIGH',
      },
    ],
    merchant_entity_id: 'ent_scl',
    personal_finance_category: {
      primary: 'RENT_AND_UTILITIES',
      detailed: 'RENT_AND_UTILITIES_ELECTRIC',
      confidence_level: 'VERY_HIGH',
    },
    payment_channel: 'online',
    pending: false,
  },

  // Income - Payroll
  {
    transaction_id: 'txn_payroll_001',
    account_id: 'acc_checking_001',
    amount: -3500.0, // Negative = credit/income
    iso_currency_code: 'USD',
    date: '2024-01-01',
    name: 'ACME CORP PAYROLL DIR DEP',
    counterparties: [
      {
        name: 'ACME Corporation',
        type: 'financial_institution',
        entity_id: 'ent_acme',
        confidence_level: 'HIGH',
      },
    ],
    personal_finance_category: {
      primary: 'INCOME',
      detailed: 'INCOME_WAGES',
      confidence_level: 'VERY_HIGH',
    },
    payment_channel: 'other',
    pending: false,
  },

  // Subscription - Unused Gym (Waste Candidate)
  {
    transaction_id: 'txn_gym_001',
    account_id: 'acc_checking_001',
    amount: 49.99,
    iso_currency_code: 'USD',
    date: '2024-01-05',
    name: 'PLANET FITNESS 24HR',
    counterparties: [
      {
        name: 'Planet Fitness',
        type: 'merchant',
        logo_url: 'https://plaid-counterparty-logos.plaid.com/planetfitness_logo.png',
        website: 'planetfitness.com',
        entity_id: 'ent_planetfitness',
        confidence_level: 'VERY_HIGH',
      },
    ],
    merchant_entity_id: 'ent_planetfitness',
    personal_finance_category: {
      primary: 'GENERAL_SERVICES',
      detailed: 'GENERAL_SERVICES_GYMS_AND_FITNESS_CENTERS',
      confidence_level: 'VERY_HIGH',
    },
    payment_channel: 'online',
    pending: false,
  },

  // Dining - DoorDash
  {
    transaction_id: 'txn_doordash_001',
    account_id: 'acc_checking_001',
    amount: 32.47,
    iso_currency_code: 'USD',
    date: '2024-01-14',
    name: 'DOORDASH*CHIPOTLE',
    counterparties: [
      {
        name: 'DoorDash',
        type: 'marketplace',
        logo_url: 'https://plaid-counterparty-logos.plaid.com/doordash_logo.png',
        website: 'doordash.com',
        entity_id: 'ent_doordash',
        confidence_level: 'VERY_HIGH',
      },
    ],
    merchant_entity_id: 'ent_doordash',
    personal_finance_category: {
      primary: 'FOOD_AND_DRINK',
      detailed: 'FOOD_AND_DRINK_RESTAURANT',
      confidence_level: 'HIGH',
    },
    payment_channel: 'online',
    pending: false,
  },

  // Transport - Gas Station
  {
    transaction_id: 'txn_shell_001',
    account_id: 'acc_checking_001',
    amount: 52.18,
    iso_currency_code: 'USD',
    date: '2024-01-12',
    name: 'SHELL OIL 57442632001',
    counterparties: [
      {
        name: 'Shell',
        type: 'merchant',
        logo_url: 'https://plaid-counterparty-logos.plaid.com/shell_logo.png',
        website: 'shell.com',
        entity_id: 'ent_shell',
        confidence_level: 'VERY_HIGH',
      },
    ],
    merchant_entity_id: 'ent_shell',
    personal_finance_category: {
      primary: 'TRANSPORTATION',
      detailed: 'TRANSPORTATION_GAS',
      confidence_level: 'VERY_HIGH',
    },
    payment_channel: 'in store',
    pending: false,
  },
];

/**
 * Get mock transactions with optional filtering
 */
export function getMockTransactions(options?: {
  limit?: number;
  category?: string;
  startDate?: string;
  endDate?: string;
}): PlaidTransaction[] {
  let filtered = [...mockTransactions];

  if (options?.category) {
    filtered = filtered.filter(
      (t) => t.personal_finance_category?.primary === options.category
    );
  }

  if (options?.startDate) {
    filtered = filtered.filter((t) => t.date >= options.startDate!);
  }

  if (options?.endDate) {
    filtered = filtered.filter((t) => t.date <= options.endDate!);
  }

  if (options?.limit) {
    filtered = filtered.slice(0, options.limit);
  }

  return filtered;
}
