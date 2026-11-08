'use client';

/**
 * WasteCard Component
 *
 * Displays an unused subscription or wasteful spending item.
 * Uses Glassmorphism theme with high-contrast warning colors.
 *
 * Design follows .context/design_tokens.md specifications.
 */

interface WasteCardProps {
  /** Normalized merchant name */
  merchant: string;
  /** Monthly cost of the subscription */
  monthlyCost: number;
  /** Number of days since last use */
  daysSinceUse: number;
  /** Optional merchant logo URL */
  logoUrl?: string;
  /** Callback when cancel button is clicked */
  onCancel?: () => void;
  /** Callback when dismiss/keep button is clicked */
  onDismiss?: () => void;
}

/**
 * Get emoji based on merchant name for fallback logo
 */
function getMerchantEmoji(merchant: string): string {
  const emojiMap: Record<string, string> = {
    netflix: '🎬',
    spotify: '🎵',
    'planet fitness': '🏋️',
    gym: '🏋️',
    'apple music': '🎵',
    hulu: '📺',
    disney: '🏰',
    adobe: '🎨',
    dropbox: '📦',
    icloud: '☁️',
    default: '💳',
  };

  const key = Object.keys(emojiMap).find((k) =>
    merchant.toLowerCase().includes(k)
  );
  return emojiMap[key || 'default'];
}

/**
 * Format currency for display
 */
function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

/**
 * Get urgency level based on days since use
 */
function getUrgencyLevel(days: number): 'critical' | 'warning' | 'info' {
  if (days >= 60) return 'critical';
  if (days >= 30) return 'warning';
  return 'info';
}

export default function WasteCard({
  merchant,
  monthlyCost,
  daysSinceUse,
  logoUrl,
  onCancel,
  onDismiss,
}: WasteCardProps) {
  const urgency = getUrgencyLevel(daysSinceUse);

  const urgencyStyles = {
    critical: {
      container: 'bg-red-500/10 border-red-500/30',
      badge: 'bg-red-500',
      text: 'text-red-400',
    },
    warning: {
      container: 'bg-amber-500/10 border-amber-500/30',
      badge: 'bg-amber-500',
      text: 'text-amber-400',
    },
    info: {
      container: 'bg-blue-500/10 border-blue-500/30',
      badge: 'bg-blue-500',
      text: 'text-blue-400',
    },
  };

  const styles = urgencyStyles[urgency];

  return (
    <div
      className={`backdrop-blur-lg border rounded-2xl p-6 space-y-4 ${styles.container}`}
    >
      {/* Header: Logo and Cost Badge */}
      <div className="flex justify-between items-start">
        {/* Merchant Logo */}
        <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center overflow-hidden">
          {logoUrl ? (
            <img
              src={logoUrl}
              alt={merchant}
              className="w-full h-full object-cover"
            />
          ) : (
            <span className="text-2xl">{getMerchantEmoji(merchant)}</span>
          )}
        </div>

        {/* Monthly Cost Badge */}
        <span
          className={`${styles.badge} text-white px-3 py-1 rounded-full text-sm font-bold`}
        >
          {formatCurrency(monthlyCost)}/mo
        </span>
      </div>

      {/* Merchant Name */}
      <h3 className="text-lg font-semibold">{merchant}</h3>

      {/* Usage Warning */}
      <p className={`text-sm ${styles.text}`}>
        Usage: {daysSinceUse} days since last use
      </p>

      {/* Potential Savings */}
      <p className="text-sm text-gray-400">
        Cancel to save {formatCurrency(monthlyCost * 12)}/year
      </p>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={onCancel}
          className={`flex-1 ${styles.badge} hover:opacity-90 text-white
                     py-2 px-4 rounded-lg transition-opacity font-medium`}
        >
          Cancel Subscription
        </button>
        <button
          onClick={onDismiss}
          className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20
                     text-gray-300 transition-colors"
        >
          Keep
        </button>
      </div>
    </div>
  );
}
