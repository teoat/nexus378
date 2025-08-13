
'use server';

import { ai } from '@/ai/genkit';
import { z } from 'zod';
import { SummarizeBenfordAnalysisInputSchema, SummarizeBenfordAnalysisOutputSchema } from '@/types/types';


const systemPrompt = `You are a forensic accountant. Your task is to analyze the provided results of a Benford's Law analysis and provide a concise summary. The user will provide a JSON object containing the actual vs. expected distribution of leading digits.

Identify any digits that show a significant deviation from the expected Benford distribution. Explain the potential implications of these deviations in simple terms (e.g., "The over-representation of the digit '1' could suggest manipulated or fabricated numbers, while the under-representation of '9' might indicate an avoidance of transaction limits.")

Your output must be a single JSON object with a "summary" field.`;

export const summarizeBenfordAnalysis = ai.defineFlow(
  {
    name: 'summarizeBenfordAnalysis',
    inputSchema: SummarizeBenfordAnalysisInputSchema,
    outputSchema: SummarizeBenfordAnalysisOutputSchema,
  },
  async ({ analysisResults }) => {
    const prompt = ai.definePrompt({
        name: 'summarizeBenfordAnalysisPrompt',
        input: { schema: SummarizeBenfordAnalysisInputSchema },
        output: { schema: SummarizeBenfordAnalysisOutputSchema },
        prompt: `Please summarize the following Benford's Law analysis results:

        {{{analysisResults}}}
        `,
        config: {
            system: systemPrompt,
        },
    });

    const { output } = await prompt({ analysisResults });

    if (!output) {
      throw new Error('AI failed to generate the Benford analysis summary.');
    }

    return output;
  }
);
