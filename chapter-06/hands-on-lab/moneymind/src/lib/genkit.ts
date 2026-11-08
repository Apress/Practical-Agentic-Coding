/**
 * MoneyMind Genkit Flow Definitions
 *
 * This module defines observable AI flows for transaction processing.
 * All flows are instrumented with Genkit telemetry for debugging.
 *
 * The `ai` instance comes from src/lib/ai.ts. Import it; do not call
 * genkit() again here, or these flows register on a second registry that
 * the Developer UI never sees.
 */

import { z } from 'zod';
import { ai } from './ai';

// ============================================================================
// Schemas
// ============================================================================

/**
 * Plaid Transaction Schema
 * Based on .context/plaid_reference.md
 */
export const PlaidTransactionSchema = z.object({
  transaction_id: z.string(),
  account_id: z.string(),
  amount: z.number(),
  iso_currency_code: z.string(),
  date: z.string(),
  name: z.string(),
  merchant_name: z.string().optional(), // DEPRECATED - do not use
  counterparties: z
    .array(
      z.object({
        name: z.string(),
        type: z.enum(['merchant', 'financial_institution', 'payment_app', 'marketplace']),
        logo_url: z.string().optional(),
        website: z.string().optional(),
        entity_id: z.string().optional(),
        confidence_level: z.enum(['VERY_HIGH', 'HIGH', 'MEDIUM', 'LOW']),
      })
    )
    .default([]),
  merchant_entity_id: z.string().optional(),
  personal_finance_category: z
    .object({
      primary: z.string(),
      detailed: z.string(),
      confidence_level: z.string(),
    })
    .optional(),
  payment_channel: z.enum(['online', 'in store', 'other']).default('other'),
  pending: z.boolean().default(false),
});

export type PlaidTransaction = z.infer<typeof PlaidTransactionSchema>;

/**
 * Enrichment Input Schema
 * Maps Plaid fields to our prompt schema
 */
export const EnrichmentInputSchema = z.object({
  description: z.string(),
  amount: z.number(),
  currency: z.string(),
  merchant_hint: z.string().optional(),
});

export type EnrichmentInput = z.infer<typeof EnrichmentInputSchema>;

/**
 * Enrichment Output Schema
 * Matches the classify.prompt output schema
 */
export const EnrichmentOutputSchema = z.object({
  category: z.enum(['Groceries', 'Dining', 'Transport', 'Housing', 'Income', 'Subscription']),
  clean_merchant: z.string(),
  is_recurring: z.boolean(),
  // The book's Step 2.2 prompt defines only the three fields above.
  // `confidence` is a reference-project enhancement (see classify.prompt),
  // kept optional so a prompt written exactly per the book still parses.
  confidence: z.number().min(0).max(1).optional(),
});

export type EnrichmentOutput = z.infer<typeof EnrichmentOutputSchema>;

/**
 * Enriched Transaction Schema
 * Original transaction plus AI enrichment
 */
export const EnrichedTransactionSchema = PlaidTransactionSchema.extend({
  enrichment: EnrichmentOutputSchema.optional(),
});

export type EnrichedTransaction = z.infer<typeof EnrichedTransactionSchema>;

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Maps Plaid transaction to enrichment input
 * IMPORTANT: Uses counterparties array, NOT merchant_name
 */
export function mapPlaidToEnrichmentInput(transaction: PlaidTransaction): EnrichmentInput {
  // Extract merchant hint from counterparties (preferred)
  // Falls back to undefined if not available
  const merchantHint = transaction.counterparties?.[0]?.name;

  return {
    description: transaction.name,
    amount: transaction.amount,
    currency: transaction.iso_currency_code,
    merchant_hint: merchantHint,
  };
}

// ============================================================================
// Genkit Flows
// ============================================================================

/**
 * Classify Transaction Flow
 *
 * A thin flow over classify.prompt that takes the prompt's own input shape
 * ({description, amount, currency, merchant_hint?}) rather than a full Plaid
 * transaction. This is the flow to target for evaluation: the golden dataset
 * at code-examples/genkit/evaluation-dataset.json uses exactly this shape,
 * so `npx genkit eval:flow classifyTransactionFlow --input <dataset>` runs
 * every case. (enrichTransactionFlow requires a full Plaid transaction and
 * would reject the dataset's inputs at the Zod boundary.)
 */
export const classifyTransactionFlow = ai.defineFlow(
  {
    name: 'classifyTransactionFlow',
    inputSchema: EnrichmentInputSchema,
    outputSchema: EnrichmentOutputSchema,
  },
  async (input) => {
    const classifyPrompt = ai.prompt('classify');
    const response = await classifyPrompt(input);
    return EnrichmentOutputSchema.parse(response.output);
  }
);

/**
 * Enrich Transaction Flow
 *
 * Takes a raw Plaid transaction and enriches it with AI-powered
 * categorization and merchant normalization.
 *
 * Observable in Genkit Developer UI at http://localhost:4000
 */
export const enrichTransactionFlow = ai.defineFlow(
  {
    name: 'enrichTransactionFlow',
    inputSchema: PlaidTransactionSchema,
    outputSchema: EnrichedTransactionSchema,
  },
  async (transaction) => {
    // Map Plaid transaction to prompt input
    const enrichmentInput = mapPlaidToEnrichmentInput(transaction);

    // Load and run the classify prompt
    // This step is traced in Genkit
    const classifyPrompt = ai.prompt('classify');
    const response = await classifyPrompt(enrichmentInput);

    // Parse the model output
    const enrichment = EnrichmentOutputSchema.parse(response.output);

    // Return enriched transaction
    return {
      ...transaction,
      enrichment,
    };
  }
);

/**
 * Batch Enrich Transactions Flow
 *
 * Processes multiple transactions in parallel for efficiency.
 * Each individual enrichment is still traced separately.
 */
export const batchEnrichFlow = ai.defineFlow(
  {
    name: 'batchEnrichFlow',
    inputSchema: z.array(PlaidTransactionSchema),
    outputSchema: z.array(EnrichedTransactionSchema),
  },
  async (transactions) => {
    // Process in parallel with Promise.all
    const enrichedTransactions = await Promise.all(
      transactions.map(async (transaction) => {
        try {
          return await enrichTransactionFlow(transaction);
        } catch (error) {
          // Log error but don't fail entire batch
          console.error(`[batchEnrichFlow] Failed to enrich ${transaction.transaction_id}:`, error);
          return {
            ...transaction,
            enrichment: undefined,
          };
        }
      })
    );

    return enrichedTransactions;
  }
);

/**
 * Waste Report Schema
 *
 * Field names are snake_case because they mirror the output schema in
 * prompts/waste-detect.prompt. Keeping the two identical means the model's
 * reply parses without a translation layer.
 */
export const WasteReportSchema = z.object({
  waste_items: z.array(
    z.object({
      merchant: z.string(),
      monthly_cost: z.number(),
      last_used: z.string(),
      days_since_use: z.number(),
      waste_reason: z.string(),
      recommendation: z.string(),
      confidence: z.number(),
    })
  ),
  total_monthly_waste: z.number(),
  summary: z.string(),
});

export type WasteReport = z.infer<typeof WasteReportSchema>;

/**
 * Waste Detection Flow
 *
 * Analyzes transaction history to identify unused subscriptions
 * and wasteful spending patterns.
 */
export const detectWasteFlow = ai.defineFlow(
  {
    name: 'detectWasteFlow',
    inputSchema: z.object({
      transactions: z.array(EnrichedTransactionSchema),
      analysisPeriodDays: z.number().default(30),
    }),
    outputSchema: WasteReportSchema,
  },
  async ({ transactions, analysisPeriodDays }) => {
    // Filter to recurring transactions only
    const recurringTransactions = transactions.filter(
      (t) => t.enrichment?.is_recurring === true
    );

    // Prepare prompt input
    const promptInput = {
      transactions: recurringTransactions.map((t) => ({
        merchant: t.enrichment?.clean_merchant || t.name,
        amount: t.amount,
        date: t.date,
        category: t.enrichment?.category || 'Unknown',
        is_recurring: true,
      })),
      analysis_period_days: analysisPeriodDays,
    };

    // Run waste detection prompt
    const wastePrompt = ai.prompt('waste-detect');
    const response = await wastePrompt(promptInput);

    // Validate the model output against the schema before returning it.
    return WasteReportSchema.parse(response.output);
  }
);

// ============================================================================
// Export All Flows
// ============================================================================

export const flows = {
  classifyTransactionFlow,
  enrichTransactionFlow,
  batchEnrichFlow,
  detectWasteFlow,
};
