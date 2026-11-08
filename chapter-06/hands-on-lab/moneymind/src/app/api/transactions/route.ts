/**
 * MoneyMind Transactions API Route
 *
 * GET /api/transactions - Fetch transactions (mock or real based on config)
 *
 * This endpoint is configurable via environment variables:
 * - USE_MOCK_DATA=true : Returns mock data (default for development)
 * - USE_MOCK_DATA=false : Connects to real Plaid API (requires credentials)
 */

import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { getMockTransactions } from '@/lib/mock-data';

// This route reads query parameters on every request, so it is never a static
// page. Saying so up front also keeps `next build` from attempting (and
// logging) a static render of it.
export const dynamic = 'force-dynamic';

// Request query parameters schema
const QueryParamsSchema = z.object({
  // A positive whole number up to 100; anything else is a 400, not a guess.
  limit: z.coerce.number().int().positive().max(100).optional(),
  category: z.string().optional(),
  startDate: z.string().optional(),
  endDate: z.string().optional(),
});

/**
 * GET /api/transactions
 *
 * Returns a list of transactions. Uses mock data by default.
 *
 * Query Parameters:
 * - limit: Maximum number of transactions to return
 * - category: Filter by Plaid primary category
 * - startDate: Filter transactions on or after this date (YYYY-MM-DD)
 * - endDate: Filter transactions on or before this date (YYYY-MM-DD)
 */
export async function GET(request: NextRequest) {
  try {
    // Parse query parameters
    const searchParams = Object.fromEntries(request.nextUrl.searchParams);
    const params = QueryParamsSchema.parse(searchParams);

    // Check if we should use mock data
    const useMockData = process.env.USE_MOCK_DATA !== 'false';

    if (useMockData) {
      // Return mock data for development
      const transactions = getMockTransactions({
        limit: params.limit,
        category: params.category,
        startDate: params.startDate,
        endDate: params.endDate,
      });

      return NextResponse.json({
        success: true,
        data: transactions,
        meta: {
          total: transactions.length,
          source: 'mock',
        },
      });
    }

    // Real Plaid integration (requires credentials)
    const plaidClientId = process.env.PLAID_CLIENT_ID;
    const plaidSecret = process.env.PLAID_SECRET;

    if (!plaidClientId || !plaidSecret) {
      return NextResponse.json(
        {
          success: false,
          error: 'Plaid credentials not configured',
          message:
            'Set USE_MOCK_DATA=true or provide PLAID_CLIENT_ID and PLAID_SECRET',
        },
        { status: 500 }
      );
    }

    // TODO: Implement real Plaid API integration
    // For now, return an error indicating real integration is not implemented
    return NextResponse.json(
      {
        success: false,
        error: 'Real Plaid integration not implemented',
        message: 'Set USE_MOCK_DATA=true to use mock data',
      },
      { status: 501 }
    );
  } catch (error) {
    // Handle Zod validation errors
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          success: false,
          error: 'Invalid query parameters',
          details: error.errors,
        },
        { status: 400 }
      );
    }

    // Log unexpected errors without exposing internals
    console.error('[/api/transactions] Unexpected error:', error);

    return NextResponse.json(
      {
        success: false,
        error: 'Internal server error',
      },
      { status: 500 }
    );
  }
}
