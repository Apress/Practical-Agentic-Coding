/**
 * MoneyMind Genkit Instance
 *
 * One configured Genkit instance for the whole project. Flows, prompts, and
 * API routes all import `ai` from here.
 *
 * Why this file exists: `@genkit-ai/core` does not export a ready-made `ai`
 * object. You call `genkit({...})` once and share the result. If two modules
 * each call `genkit()`, they get separate registries, and flows defined on one
 * are invisible to the other (the Developer UI shows an empty flow list).
 *
 * `promptDir` defaults to `./prompts`, which is where this project keeps its
 * Dotprompt files, so `ai.prompt('classify')` resolves to prompts/classify.prompt.
 */

import { genkit } from 'genkit';
import { googleAI } from '@genkit-ai/google-genai';

export const ai = genkit({
  plugins: [googleAI()],
  promptDir: './prompts',
});
