
'use server';

import { ai } from '@/ai/genkit';
import { z } from 'zod';
import { EnrichTransactionDetailsInputSchema, EnrichTransactionDetailsOutputSchema } from '@/types/types';

export const enrichTransactionDetails = ai.defineFlow(
  {
    name: 'enrichTransactionDetails',
    inputSchema: EnrichTransactionDetailsInputSchema,
    outputSchema: EnrichTransactionDetailsOutputSchema,
  },
  async ({ description }) => {
    const prompt = ai.definePrompt({
        name: 'enrichTransactionDetailsPrompt',
        input: {
            schema: z.object({
                description: z.string(),
            }),
        },
        output: { schema: EnrichTransactionDetailsOutputSchema },
        prompt: `For the transaction description "{{description}}", provide enriched details such as location, entity type (individual, business, utility, internal, other), and a potential website if applicable. Only return a valid JSON object.`,
    });

    const { output } = await prompt({ description });

    if (!output) {
        return {};
    }

    return output;
  }
);
