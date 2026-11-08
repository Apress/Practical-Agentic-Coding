'use client';

/**
 * TransactionList Component
 *
 * Displays a list of transactions with enrichment data.
 * Follows Glassmorphism design from .context/design_tokens.md
 */

import { useState, useEffect } from 'react';
import type { EnrichedTransaction } from '@/lib/genkit';

interface TransactionListProps {
  /** Maximum number of transactions to display */
  limit?: number;
  /** Show enrichment data (category, recurring status) */
  showEnrichment?: boolean;
}

/**
 * Format currency with proper sign and locale
 */
function formatCurrency(amount: number, currency: string = 'USD'): string {
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  });

  // Positive = expense (money out), Negative = income (money in)
  const formattedAmount = formatter.format(Math.abs(amount));
  return amount > 0 ? `-${formattedAmount}` : `+${formattedAmount}`;
}

/**
 * Format date for display
 */
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Get category badge color
 */
function getCategoryColor(category: string): string {
  const colors: Record<string, string> = {
    Groceries: 'bg-green-500/20 text-green-400',
    Dining: 'bg-orange-500/20 text-orange-400',
    Transport: 'bg-blue-500/20 text-blue-400',
    Housing: 'bg-purple-500/20 text-purple-400',
    Income: 'bg-emerald-500/20 text-emerald-400',
    Subscription: 'bg-pink-500/20 text-pink-400',
  };
  return colors[category] || 'bg-gray-500/20 text-gray-400';
}

export default function TransactionList({
  limit = 10,
  showEnrichment = true,
}: TransactionListProps) {
  const [transactions, setTransactions] = useState<EnrichedTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [enriching, setEnriching] = useState(false);

  // Fetch transactions on mount
  useEffect(() => {
    async function fetchTransactions() {
      try {
        const response = await fetch(`/api/transactions?limit=${limit}`);
        const data = await response.json();

        if (data.success) {
          setTransactions(data.data);
        } else {
          setError(data.error || 'Failed to fetch transactions');
        }
      } catch (err) {
        setError('Network error');
        console.error('[TransactionList] Fetch error:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchTransactions();
  }, [limit]);

  // Enrich transactions with AI
  async function handleEnrich() {
    if (transactions.length === 0) return;

    setEnriching(true);
    try {
      const response = await fetch('/api/enrich', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transactions }),
      });

      const data = await response.json();

      if (data.success) {
        setTransactions(data.data);
      } else {
        setError(data.error || 'Enrichment failed');
      }
    } catch (err) {
      setError('Enrichment network error');
      console.error('[TransactionList] Enrich error:', err);
    } finally {
      setEnriching(false);
    }
  }

  if (loading) {
    return (
      <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-6">
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-white/5 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 backdrop-blur-lg border border-red-500/20 rounded-2xl p-6">
        <p className="text-red-400">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-6 space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Recent Transactions</h2>
        {showEnrichment && (
          <button
            onClick={handleEnrich}
            disabled={enriching}
            className="bg-primary-500 hover:bg-primary-600 disabled:bg-gray-500
                       text-white px-4 py-2 rounded-lg text-sm font-medium
                       transition-colors"
          >
            {enriching ? 'Enriching...' : 'Enrich with AI'}
          </button>
        )}
      </div>

      {/* Transaction List */}
      <div className="space-y-3">
        {transactions.map((transaction) => (
          <div
            key={transaction.transaction_id}
            className="bg-white/5 hover:bg-white/10 rounded-xl p-4
                       flex items-center gap-4 transition-colors"
          >
            {/* Merchant Logo Placeholder */}
            <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0">
              <span className="text-lg">
                {transaction.counterparties?.[0]?.name?.[0] || '?'}
              </span>
            </div>

            {/* Transaction Details */}
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">
                {transaction.enrichment?.clean_merchant ||
                  transaction.counterparties?.[0]?.name ||
                  transaction.name}
              </p>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <span>{formatDate(transaction.date)}</span>
                {showEnrichment && transaction.enrichment && (
                  <>
                    <span>-</span>
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs ${getCategoryColor(
                        transaction.enrichment.category
                      )}`}
                    >
                      {transaction.enrichment.category}
                    </span>
                    {transaction.enrichment.is_recurring && (
                      <span className="px-2 py-0.5 rounded-full text-xs bg-purple-500/20 text-purple-400">
                        Recurring
                      </span>
                    )}
                  </>
                )}
              </div>
            </div>

            {/* Amount */}
            <span
              className={`font-semibold ${
                transaction.amount > 0 ? 'text-red-400' : 'text-green-400'
              }`}
            >
              {formatCurrency(transaction.amount, transaction.iso_currency_code)}
            </span>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {transactions.length === 0 && (
        <p className="text-center text-gray-400 py-8">No transactions found</p>
      )}
    </div>
  );
}
