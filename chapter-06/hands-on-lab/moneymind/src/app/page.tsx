'use client';

/**
 * MoneyMind Dashboard
 *
 * Main dashboard page showing transaction overview and waste detection.
 *
 * This page is a Client Component because it hands onCancel and onDismiss
 * callbacks to WasteCard. A Server Component cannot pass functions to a
 * Client Component, and Next.js fails the render (and `next build`) with
 * "Event handlers cannot be passed to Client Component props".
 */

import TransactionList from '@/components/TransactionList';
import WasteCard from '@/components/WasteCard';

export default function DashboardPage() {
  // Placeholder waste items so the dashboard renders without a model call.
  // Replace with detectWasteFlow output, mapping its snake_case fields
  // (monthly_cost, days_since_use) onto the camelCase props below.
  const wasteItems = [
    {
      merchant: 'Planet Fitness',
      monthlyCost: 49.99,
      daysSinceUse: 45,
    },
    {
      merchant: 'Adobe Creative Cloud',
      monthlyCost: 54.99,
      daysSinceUse: 30,
    },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-white">MoneyMind</h1>
          <p className="text-gray-400 mt-1">
            AI-powered financial insights at your fingertips
          </p>
        </header>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content: Transaction List */}
          <div className="lg:col-span-2">
            <TransactionList limit={10} showEnrichment={true} />
          </div>

          {/* Sidebar: Waste Detection */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white">Waste Detected</h2>
            <p className="text-sm text-gray-400 mb-4">
              Subscriptions you may want to cancel
            </p>

            {wasteItems.map((item, index) => (
              <WasteCard
                key={index}
                merchant={item.merchant}
                monthlyCost={item.monthlyCost}
                daysSinceUse={item.daysSinceUse}
                onCancel={() => console.log(`Cancel ${item.merchant}`)}
                onDismiss={() => console.log(`Keep ${item.merchant}`)}
              />
            ))}

            {wasteItems.length === 0 && (
              <div className="bg-green-500/10 backdrop-blur-lg border border-green-500/20 rounded-2xl p-6 text-center">
                <span className="text-4xl">🎉</span>
                <p className="text-green-400 mt-2">No waste detected!</p>
                <p className="text-sm text-gray-400 mt-1">
                  All your subscriptions are being used
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Footer: Genkit Info */}
        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>
            Powered by{' '}
            <a
              href="http://localhost:4000"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:underline"
            >
              Genkit Developer UI
            </a>{' '}
            for observability
          </p>
          <p className="mt-1">
            Built with Intent-First Development using Google Antigravity
          </p>
        </footer>
      </div>
    </main>
  );
}
