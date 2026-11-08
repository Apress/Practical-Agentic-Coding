/**
 * MoneyMind Genkit Server Entry Point
 *
 * The Genkit Developer UI needs a process that has already imported every
 * flow definition. That is all this file does: import the flows so they
 * register on the shared `ai` instance from src/lib/ai.ts, then report what
 * loaded.
 *
 * Run with: npx genkit start -- npx tsx --env-file=.env genkit-server.ts
 * (or the shortcut: npm run genkit)
 *
 * Genkit Developer UI: http://localhost:4000
 */

import { ai } from './src/lib/ai';
import { flows } from './src/lib/genkit';

// Fail fast with a readable message instead of a plugin error buried in a trace.
// The googleAI plugin reads GEMINI_API_KEY (GOOGLE_API_KEY also works). The
// placeholder from .env.example counts as unset, because copying the template
// without editing it is the most common way to end up with no key.
const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
if (!apiKey || apiKey === 'your_gemini_api_key_here') {
  console.error('ERROR: GEMINI_API_KEY is not set.');
  console.error('Copy .env.example to .env, add your key, then re-run.');
  console.error('Get a key at https://aistudio.google.com/apikey');
  process.exit(1);
}

console.log('Registered MoneyMind flows:');
for (const name of Object.keys(flows)) {
  console.log(`- ${name}`);
}

console.log('\nGenkit server ready. Developer UI: http://localhost:4000');

// Re-exported so API routes and tests can import from a single place.
export { ai, flows };
