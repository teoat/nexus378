
'use server';
/**
 * @fileOverview Orchestrates the entire analysis workflow, from matching to forensic analysis.
 */

import { ai } from '@/ai/genkit';
import { z } from 'zod';
import { initialMatchingFlow } from './initial-matching';
import { fullForensicAnalysisFlow } from './full-forensic-analysis';
import { getCase } from '@/lib/db-connector';
import { AnalysisResultSchema } from '@/types/types';

const RunAnalysisInputSchema = z.string().describe('The ID of the case to analyze.');

export const runAnalysisFlow = ai.defineFlow(
  {
    name: 'runAnalysisFlow',
    inputSchema: RunAnalysisInputSchema,
    outputSchema: AnalysisResultSchema,
  },
  async (caseId) => {
    const caseData = await getCase(caseId);
    if (!caseData) {
      throw new Error('Case not found.');
    }

    const matchingResult = await initialMatchingFlow.run({
      sourceData: JSON.parse(caseData.sourceFileContent),
      bankData: caseData.bankFileContent ? JSON.parse(caseData.bankFileContent) : [],
      sourceMap: caseData.columnMapping,
      bankMap: caseData.bankColumnMapping,
      tolerances: caseData.tolerances,
      thousandSeparator: caseData.thousandSeparator,
    });

    const analysisResult = await fullForensicAnalysisFlow.run({
      ...matchingResult,
      caseName: caseData.name,
    });
    
    // Here you would typically save the result to the database
    // await saveAnalysisResult(caseId, analysisResult);

    return analysisResult;
  }
);
