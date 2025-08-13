
'use server';

import { ai } from '@/ai/genkit';
import { z } from 'zod';
import { SuggestDataCleansingInputSchema, SuggestDataCleansingOutputSchema } from '@/types/types';

export const suggestDataCleansing = ai.defineFlow(
  {
    name: 'suggestDataCleansing',
    inputSchema: SuggestDataCleansingInputSchema,
    outputSchema: SuggestDataCleansingOutputSchema,
  },
  async ({ dataSample, columnToCleanse }) => {

    const prompt = ai.definePrompt({
        name: 'suggestDataCleansingPrompt',
        input: { schema: SuggestDataCleansingInputSchema },
        output: { schema: SuggestDataCleansingOutputSchema },
        prompt: `Given the data sample and the column "${columnToCleanse}", suggest data cleansing operations to standardize the values. Provide the original value, the suggested new value, the reason for the change, and the number of times the original value appears.

        Data Sample:
        {{{json dataSample}}}
        `
    });
    
    const { output } = await prompt({ dataSample, columnToCleanse });

    if (!output) {
        return { suggestions: [] };
    }

    return output;
  }
);
