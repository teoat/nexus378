
'use server';
/**
 * @fileOverview Performs the full forensic analysis on the matched and unmatched transactions.
 */

import { ai } from '@/ai/genkit';
import { z } from 'zod';
import { MatchedTransactionSchema, UnmatchedBankTransactionSchema, AnomalySchema, AnalysisResultSchema } from '@/types/types';
import { v4 as uuidv4 } from 'uuid';
import { sentimentAnalysis } from './sentiment-analysis';
import { enrichTransactionDetails } from './enrich-transaction-details';
import { legalSynthesisFlow } from './legal-synthesis';
import { redact } from '../../../../redact';

const AnalysisInputSchema = z.object({
  matchedExpenses: z.array(MatchedTransactionSchema),
  unmatchedExpenses: z.any(),
  unmatchedBankTxns: z.array(UnmatchedBankTransactionSchema),
  benfordChartData: z.any(),
  caseName: z.string(),
});

export const fullForensicAnalysisFlow = ai.defineFlow(
  {
    name: 'fullForensicAnalysisFlow',
    inputSchema: AnalysisInputSchema,
    outputSchema: AnalysisResultSchema,
  },
  async ({ matchedExpenses, unmatchedExpenses, unmatchedBankTxns, benfordChartData, caseName }) => {
    
    let anomalies: z.infer<typeof AnomalySchema>[] = [];
    unmatchedExpenses.forEach((expense: any) => {
        anomalies.push({ 
            id: uuidv4(), 
            date: expense.date, 
            description: `Expense without match: ${redact(expense.description)}`, 
            amount: expense.debit, 
            category: expense.category || 'Uncategorized', 
            reason: "Unmatched Expense", 
            riskScore: 60, 
            confidenceScore: 95, 
            status: 'Unreviewed', 
            original: expense, 
            auditHistory: [] 
        });
    });

    const enrichedAnomalies = await Promise.all(anomalies.map(async (anomaly) => {
        const sentimentResult = await sentimentAnalysis.run({ text: anomaly.description });
        const enrichedDetails = await enrichTransactionDetails.run({ description: anomaly.description });
        return { ...anomaly, ...sentimentResult, ...enrichedDetails };
    }));
    
    const legalSynthesis = await legalSynthesisFlow.run({ anomalies: enrichedAnomalies });

    const finalAnomalies = enrichedAnomalies.map(anomaly => {
        const legalData = legalSynthesis.results.find(r => r.id === anomaly.id);
        return { ...anomaly, ...legalData };
    });

    const analysisSummary = `Analysis complete. ${finalAnomalies.length} anomalies found.`;

    return {
        id: uuidv4(),
        caseName,
        versionHistory: [],
        matchedExpenses,
        toleranceMatches: [], // This can be populated if needed
        unmatchedExpenses,
        unmatchedBankTxns,
        anomalies: finalAnomalies,
        benfordChartData,
        analysisSummary,
    };
  }
);

  