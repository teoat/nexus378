
'use server';

import { ai } from '@/ai/genkit';
import { z } from 'zod';
import { SentimentAnalysisInputSchema, SentimentAnalysisOutputSchema } from '@/types/types';

export const sentimentAnalysis = ai.defineFlow(
  {
    name: 'sentimentAnalysis',
    inputSchema: SentimentAnalysisInputSchema,
    outputSchema: SentimentAnalysisOutputSchema,
  },
  async ({ text }) => {
    const prompt = ai.definePrompt({
      name: 'sentimentAnalysisPrompt',
      input: {
        schema: z.object({
          text: z.string(),
        }),
      },
      output: {
        schema: SentimentAnalysisOutputSchema,
      },
      prompt: `Analyze the sentiment of the following text and classify it as positive, neutral, or negative. Provide a confidence score for your classification.

      Text: {{{text}}}
      `,
    });

    const { output } = await prompt({ text });

    if (!output) {
      return {
        sentiment: 'neutral',
        confidence: 0,
      };
    }

    return output;
  }
);
