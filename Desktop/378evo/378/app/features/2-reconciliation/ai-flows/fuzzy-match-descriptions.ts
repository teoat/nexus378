
'use server';

import { ai } from '@/ai/genkit';
import { FuzzyMatchDescriptionsInputSchema, FuzzyMatchDescriptionsOutputSchema, FuzzyMatchSchema } from '@/types/types';
import { z } from 'zod';

const systemPrompt = `You are an expert financial data analyst. Your task is to find potential matches between two lists of transactions: one from an expense ledger and one from a bank statement.

You will be given two JSON arrays of objects. Each object in the 'unmatchedExpenses' array has an 'expenseDescription' and an 'expenseIndex'. Each object in the 'unmatchedBankTxns' array has a 'description' and a 'bankTxIndex'.

Your goal is to identify pairs of descriptions that are semantically similar, even if they are not identical (e.g., "Starbucks Coffee" and "STARBUCKS #12345").

For each match you find, you must provide a confidence score (0-100) indicating how certain you are about the match. Only return matches with a confidence score of 70 or higher.
Your output must be a JSON object containing a 'matches' array. Each element in the array should be an object with 'expenseDescription', 'bankTxDescription', 'expenseIndex', and 'confidence'.`;


export const fuzzyMatchDescriptions = ai.defineFlow(
  {
    name: 'fuzzyMatchDescriptionsFlow',
    inputSchema: FuzzyMatchDescriptionsInputSchema,
    outputSchema: FuzzyMatchDescriptionsOutputSchema,
  },
  async ({ unmatchedExpenses, unmatchedBankTxns }) => {
    if (unmatchedExpenses.length === 0 || unmatchedBankTxns.length === 0) {
      return { matches: [] };
    }

    const prompt = ai.definePrompt({
      name: 'fuzzyMatchDescriptionsPrompt',
      input: {
        schema: z.object({
          expenseExamples: z.array(z.any()),
          bankExamples: z.array(z.any()),
        }),
      },
      output: { schema: FuzzyMatchDescriptionsOutputSchema },
      prompt: `Based on the following lists, find semantic matches.

      Expense Descriptions:
      {{{json expenseExamples}}}
      
      Bank Statement Descriptions:
      {{{json bankExamples}}}
      `,
      config: {
        system: systemPrompt,
      },
    });

    const { output } = await prompt({
      expenseExamples: unmatchedExpenses,
      bankExamples: unmatchedBankTxns,
    });

    if (!output) {
      return { matches: [] };
    }

    // Post-processing to ensure the AI hasn't hallucinated indices
    const validMatches = output.matches.filter(match => 
        unmatchedExpenses.some(e => e.expenseIndex === match.expenseIndex) &&
        unmatchedBankTxns.some(b => b.description === match.bankTxDescription)
    );

    return { matches: validMatches };
  }
);
