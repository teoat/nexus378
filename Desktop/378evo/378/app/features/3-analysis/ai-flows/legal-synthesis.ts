
'use server';

import { ai } from '@/ai/genkit';
import { z } from 'zod';
import { LegalSynthesisInputSchema, LegalSynthesisOutputSchema } from '@/types/types';

export const legalSynthesisFlow = ai.defineFlow(
  {
    name: 'legalSynthesisFlow',
    inputSchema: LegalSynthesisInputSchema,
    outputSchema: LegalSynthesisOutputSchema,
  },
  async ({ anomalies }) => {
    
    const prompt = ai.definePrompt({
        name: 'legalSynthesisPrompt',
        input: { schema: LegalSynthesisInputSchema },
        output: { schema: LegalSynthesisOutputSchema },
        prompt: `For the given list of financial anomalies, provide a legal synthesis for each. This should include legal risk tags, a case linkability score, and a narrative explaining the potential legal implications.
        
        Anomalies:
        {{{json anomalies}}}
        `
    });

    const { output } = await prompt({ anomalies });

    if(!output) {
        return { results: [] };
    }

    return output;
  }
);
