/**
 * Genkit Flow Patterns
 * Chapter 6: Intent-First Development
 *
 * Common patterns for defining Genkit flows. Use these as templates for your
 * own AI-powered functionality.
 *
 * Reference file, not a runnable script: the prompts it calls
 * (`simple-qa`, `process-data`, and so on) are not included here. Copy the
 * pattern you need into your own project and point it at your own prompts.
 *
 * Note the instance rule: you call `genkit({...})` once and share the result.
 * `@genkit-ai/core` does not export a ready-made `ai` object, and a second
 * `genkit()` call creates a second registry whose flows the Developer UI
 * never sees. The MoneyMind lab keeps its instance in
 * hands-on-lab/moneymind/src/lib/ai.ts and imports it everywhere.
 */

import { genkit } from 'genkit';
import { googleAI } from '@genkit-ai/google-genai';
import { logger } from 'genkit/logging';
import { z } from 'zod';

// One configured instance, shared by every flow in this file.
const ai = genkit({
  plugins: [googleAI()],
  promptDir: './prompts',
});

// =============================================================================
// Pattern 1: Basic Flow with Typed Input/Output
// =============================================================================

/**
 * Simple flow with explicit schemas.
 * Always define input and output schemas for type safety and documentation.
 */
const SimpleInputSchema = z.object({
  query: z.string().describe('The user query to process'),
});

const SimpleOutputSchema = z.object({
  answer: z.string(),
  confidence: z.number().min(0).max(1),
});

export const simpleFlow = ai.defineFlow(
  {
    name: 'simpleFlow',
    inputSchema: SimpleInputSchema,
    outputSchema: SimpleOutputSchema,
  },
  async (input) => {
    // Flow logic here
    const prompt = ai.prompt('simple-qa');
    const response = await prompt({ query: input.query });

    return {
      answer: response.output.answer,
      confidence: response.output.confidence,
    };
  }
);

// =============================================================================
// Pattern 2: Flow with Error Handling
// =============================================================================

/**
 * Flow with proper error handling and fallbacks.
 * Always handle errors gracefully in production flows.
 */
export const resilientFlow = ai.defineFlow(
  {
    name: 'resilientFlow',
    inputSchema: z.object({ data: z.string() }),
    outputSchema: z.object({
      result: z.string(),
      success: z.boolean(),
      error: z.string().optional(),
    }),
  },
  async (input) => {
    try {
      const prompt = ai.prompt('process-data');
      const response = await prompt({ data: input.data });

      return {
        result: response.output.result,
        success: true,
      };
    } catch (error) {
      // Log error for debugging (visible in traces)
      logger.error('Flow failed', { error, input });

      // Return graceful failure
      return {
        result: '',
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }
);

// =============================================================================
// Pattern 3: Batch Processing Flow
// =============================================================================

/**
 * Flow that processes multiple items efficiently.
 * Uses Promise.all for parallel processing.
 */
const ItemSchema = z.object({
  id: z.string(),
  content: z.string(),
});

export const batchProcessFlow = ai.defineFlow(
  {
    name: 'batchProcessFlow',
    inputSchema: z.array(ItemSchema),
    outputSchema: z.array(
      ItemSchema.extend({
        processed: z.boolean(),
        result: z.string().optional(),
      })
    ),
  },
  async (items) => {
    // Process in parallel with error isolation
    const results = await Promise.all(
      items.map(async (item) => {
        try {
          const prompt = ai.prompt('process-item');
          const response = await prompt({ content: item.content });

          return {
            ...item,
            processed: true,
            result: response.output.result,
          };
        } catch (error) {
          logger.warn(`Failed to process item ${item.id}`, { error });
          return {
            ...item,
            processed: false,
          };
        }
      })
    );

    return results;
  }
);

// =============================================================================
// Pattern 4: Multi-Step Flow with Named Spans
// =============================================================================

/**
 * Complex flow with multiple steps, each creating a named span.
 * This makes debugging easier in the trace view.
 */
export const multiStepFlow = ai.defineFlow(
  {
    name: 'multiStepFlow',
    inputSchema: z.object({ documentId: z.string() }),
    outputSchema: z.object({
      summary: z.string(),
      entities: z.array(z.string()),
      sentiment: z.enum(['positive', 'negative', 'neutral']),
    }),
  },
  async (input) => {
    // Step 1: Fetch document (creates named span)
    const document = await ai.run('fetchDocument', async () => {
      // Simulated document fetch
      return { content: `Document content for ${input.documentId}` };
    });

    // Step 2: Extract entities
    const entities = await ai.run('extractEntities', async () => {
      const prompt = ai.prompt('extract-entities');
      const response = await prompt({ text: document.content });
      return response.output.entities;
    });

    // Step 3: Analyze sentiment
    const sentiment = await ai.run('analyzeSentiment', async () => {
      const prompt = ai.prompt('analyze-sentiment');
      const response = await prompt({ text: document.content });
      return response.output.sentiment;
    });

    // Step 4: Generate summary
    const summary = await ai.run('generateSummary', async () => {
      const prompt = ai.prompt('summarize');
      const response = await prompt({
        text: document.content,
        entities,
        sentiment,
      });
      return response.output.summary;
    });

    return { summary, entities, sentiment };
  }
);

// =============================================================================
// Pattern 5: Flow with Streaming Output
// =============================================================================

/**
 * Flow that streams output for real-time UI updates.
 * Useful for long-running operations.
 *
 * The flow function's second argument is the side channel. Call `sendChunk`
 * to push a partial result to the caller; the return value is still the
 * complete output.
 */
export const streamingFlow = ai.defineFlow(
  {
    name: 'streamingFlow',
    inputSchema: z.object({ topic: z.string() }),
    outputSchema: z.string(),
    // Declaring streamSchema is what makes the flow streamable.
    streamSchema: z.string(),
  },
  async (input, { sendChunk }) => {
    const storyPrompt = ai.prompt('generate-story');

    // .stream() returns an async iterable of chunks plus the final response.
    const { stream, response } = storyPrompt.stream({ topic: input.topic });

    for await (const chunk of stream) {
      sendChunk(chunk.text);
    }

    return (await response).text;
  }
);

// =============================================================================
// Pattern 6: Conditional Flow Logic
// =============================================================================

/**
 * Flow with conditional branching based on input.
 * Each branch creates its own span for visibility.
 */
export const conditionalFlow = ai.defineFlow(
  {
    name: 'conditionalFlow',
    inputSchema: z.object({
      type: z.enum(['summary', 'analysis', 'translation']),
      content: z.string(),
      targetLanguage: z.string().optional(),
    }),
    outputSchema: z.object({ result: z.string() }),
  },
  async (input) => {
    let result: string;

    switch (input.type) {
      case 'summary':
        result = await ai.run('summarize', async () => {
          const prompt = ai.prompt('summarize');
          const response = await prompt({ text: input.content });
          return response.output.summary;
        });
        break;

      case 'analysis':
        result = await ai.run('analyze', async () => {
          const prompt = ai.prompt('analyze');
          const response = await prompt({ text: input.content });
          return response.output.analysis;
        });
        break;

      case 'translation':
        result = await ai.run('translate', async () => {
          const prompt = ai.prompt('translate');
          const response = await prompt({
            text: input.content,
            targetLanguage: input.targetLanguage || 'en',
          });
          return response.output.translation;
        });
        break;

      default:
        throw new Error(`Unknown type: ${input.type}`);
    }

    return { result };
  }
);

// =============================================================================
// Pattern 7: Flow with Retry Logic
// =============================================================================

/**
 * Flow with built-in retry for transient failures.
 */
async function withRetry<T>(
  operation: () => Promise<T>,
  maxRetries = 3,
  delayMs = 1000
): Promise<T> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      if (attempt === maxRetries) throw error;
      logger.warn(`Retry ${attempt}/${maxRetries} after error`, { error });
      await new Promise((resolve) => setTimeout(resolve, delayMs * attempt));
    }
  }
  throw new Error('Retry exhausted');
}

export const retryableFlow = ai.defineFlow(
  {
    name: 'retryableFlow',
    inputSchema: z.object({ input: z.string() }),
    outputSchema: z.object({ output: z.string() }),
  },
  async (input) => {
    const result = await withRetry(async () => {
      const prompt = ai.prompt('process');
      const response = await prompt({ input: input.input });
      return response.output as { output: string };
    });

    return { output: result.output };
  }
);

// =============================================================================
// Pattern 8: Flow Composition
// =============================================================================

/**
 * Flow that calls other flows for modular architecture.
 */
export const composedFlow = ai.defineFlow(
  {
    name: 'composedFlow',
    inputSchema: z.object({ documentId: z.string() }),
    outputSchema: z.object({
      summary: z.string(),
      classification: z.string(),
      actions: z.array(z.string()),
    }),
  },
  async (input) => {
    // Call sub-flows
    const [summary, classification, actions] = await Promise.all([
      summarizeFlow({ documentId: input.documentId }),
      classifyFlow({ documentId: input.documentId }),
      extractActionsFlow({ documentId: input.documentId }),
    ]);

    return {
      summary: summary.text,
      classification: classification.category,
      actions: actions.items,
    };
  }
);

// Sub-flows (simplified for example)
const summarizeFlow = ai.defineFlow(
  {
    name: 'summarizeSubFlow',
    inputSchema: z.object({ documentId: z.string() }),
    outputSchema: z.object({ text: z.string() }),
  },
  async () => ({ text: 'Summary placeholder' })
);

const classifyFlow = ai.defineFlow(
  {
    name: 'classifySubFlow',
    inputSchema: z.object({ documentId: z.string() }),
    outputSchema: z.object({ category: z.string() }),
  },
  async () => ({ category: 'Category placeholder' })
);

const extractActionsFlow = ai.defineFlow(
  {
    name: 'extractActionsSubFlow',
    inputSchema: z.object({ documentId: z.string() }),
    outputSchema: z.object({ items: z.array(z.string()) }),
  },
  async () => ({ items: ['Action 1', 'Action 2'] })
);

// =============================================================================
// Export All Flows for Registration
// =============================================================================

export const allFlows = {
  simpleFlow,
  resilientFlow,
  batchProcessFlow,
  multiStepFlow,
  streamingFlow,
  conditionalFlow,
  retryableFlow,
  composedFlow,
};
