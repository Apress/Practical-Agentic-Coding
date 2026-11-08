/**
 * MoneyMind Transaction Enrichment API Route
 *
 * POST /api/enrich - Enrich transactions with AI categorization
 *
 * This endpoint uses Genkit flows to process transactions.
 * Results are observable in the Genkit Developer UI.
 */

import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import {
  PlaidTransactionSchema,
  enrichTransactionFlow,
  batchEnrichFlow,
} from '@/lib/genkit';

// Request body schema for single transaction
const SingleEnrichRequestSchema = z.object({
  transaction: PlaidTransactionSchema,
});

// Request body schema for batch enrichment
const BatchEnrichRequestSchema = z.object({
  transactions: z.array(PlaidTransactionSchema),
});

/**
 * POST /api/enrich
 *
 * Enriches transactions with AI-powered categorization.
 *
 * Request Body (single):
 * {
 *   "transaction": { ... PlaidTransaction }
 * }
 *
 * Request Body (batch):
 * {
 *   "transactions": [ ... PlaidTransaction[] ]
 * }
 *
 * Response:
 * {
 *   "success": true,
 *   "data": EnrichedTransaction | EnrichedTransaction[],
 *   "meta": { "processingTime": number }
 * }
 */
export async function POST(request: NextRequest) {
  const startTime = Date.now();

  try {
    const body = await request.json();

    // Determine if single or batch request
    const isBatch = 'transactions' in body && Array.isArray(body.transactions);

    if (isBatch) {
      // Batch enrichment
      const { transactions } = BatchEnrichRequestSchema.parse(body);

      const enrichedTransactions = await batchEnrichFlow(transactions);

      return NextResponse.json({
        success: true,
        data: enrichedTransactions,
        meta: {
          processed: enrichedTransactions.length,
          processingTime: Date.now() - startTime,
        },
      });
    } else {
      // Single transaction enrichment
      const { transaction } = SingleEnrichRequestSchema.parse(body);

      const enrichedTransaction = await enrichTransactionFlow(transaction);

      return NextResponse.json({
        success: true,
        data: enrichedTransaction,
        meta: {
          processingTime: Date.now() - startTime,
        },
      });
    }
  } catch (error) {
    // Handle Zod validation errors
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          success: false,
          error: 'Invalid request body',
          details: error.errors,
        },
        { status: 400 }
      );
    }

    // Handle Genkit/AI errors
    if (error instanceof Error && error.message.includes('GEMINI_API_KEY')) {
      return NextResponse.json(
        {
          success: false,
          error: 'AI service not configured',
          message: 'Please set GEMINI_API_KEY environment variable',
        },
        { status: 500 }
      );
    }

    // Log unexpected errors without exposing internals
    console.error('[/api/enrich] Unexpected error:', error);

    return NextResponse.json(
      {
        success: false,
        error: 'Enrichment failed',
        message: 'An error occurred while processing the transaction',
      },
      { status: 500 }
    );
  }
}
