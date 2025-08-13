
'use server';

import { ai } from '@/ai/genkit';
import { GenerateNoteSuggestionInputSchema, GenerateNoteSuggestionOutputSchema, AnomalySchema } from '@/types/types';
import { z } from 'zod';

const systemPrompt = `You are an expert forensic accountant. Your task is to generate a concise and relevant note for a given financial anomaly. The note should be a good starting point for a human auditor.

Based on the anomaly's data (description, category, reason, risk score), suggest a brief, professional note. For example, if the reason is "Unmatched Expense," a good note might be "Investigate receipt and confirm business purpose. Check for potential personal expense."`;

const generateNoteSuggestionFlow = ai.defineFlow(
  {
    name: 'generateNoteSuggestionFlow',
    inputSchema: GenerateNoteSuggestionInputSchema,
    outputSchema: GenerateNoteSuggestionOutputSchema,
  },
  async ({ anomaly }) => {
    
    const prompt = ai.definePrompt({
        name: 'generateNoteSuggestionPrompt',
        input: {
            schema: AnomalySchema
        },
        output: { schema: GenerateNoteSuggestionOutputSchema },
        prompt: `Generate a note for this anomaly:
        
        {{{json this}}}
        `,
        config: {
            system: systemPrompt,
        },
    });

    const { output } = await prompt(anomaly);

    if (!output) {
      throw new Error('AI failed to generate a note suggestion.');
    }

    return output;
  }
);

export { generateNoteSuggestionFlow as generateNoteSuggestion };
