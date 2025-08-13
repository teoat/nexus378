
'use server';
/**
 * @fileOverview A unified flow to ingest a file, parse it, and map its columns.
 *
 * - ingestFileFlow - A function that handles the entire file ingestion process.
 */

import { ai } from '@/ai/genkit';
import { z } from 'zod';
import { ColumnMappingSchema, MapTransactionColumnsOutputSchema } from '@/types/types';
import { csvToJson, getJsonHeaders } from '@/lib/csv-to-json';

// The input is now the raw file content, not pre-parsed JSON.
const IngestFileInputSchema = z.string().describe('The full raw string content of the uploaded file.');

const IngestFileOutputSchema = z.object({
  jsonContent: z.string().describe('The file content as a JSON string.'),
  mapping: ColumnMappingSchema,
  columnAnalyses: MapTransactionColumnsOutputSchema.shape.columnAnalyses,
  mappingConfidence: MapTransactionColumnsOutputSchema.shape.mappingConfidence,
});


// This server-side flow is being temporarily bypassed.
// The logic has been moved to the useAuditStore as a client-side function `mapColumns`
// and will be re-integrated in a future step to restore server-side processing.
export const ingestFileFlow = ai.defineFlow(
  {
    name: 'ingestFileFlow',
    inputSchema: IngestFileInputSchema,
    outputSchema: IngestFileOutputSchema,
  },
  async (fileContent) => {
    const parsedData = csvToJson(fileContent);
    const headers = getJsonHeaders(parsedData);
    const jsonContent = JSON.stringify(parsedData);

    // Placeholder for column mapping logic.
    // In the future, this will be replaced with a call to the AI.
    const mapping: z.infer<typeof ColumnMappingSchema> = {
      date: headers.find(h => h.toLowerCase().includes('date')) || null,
      description: headers.find(h => h.toLowerCase().includes('description')) || null,
      debit: headers.find(h => h.toLowerCase().includes('debit')) || null,
      credit: headers.find(h => h.toLowerCase().includes('credit')) || null,
      bankAccount: headers.find(h => h.toLowerCase().includes('account')) || null,
      category: headers.find(h => h.toLowerCase().includes('category')) || null,
      timeline: null,
      numbering: null,
      comment: null,
    };

    return {
      jsonContent: jsonContent,
      mapping,
      columnAnalyses: [], // Placeholder
      mappingConfidence: [], // Placeholder
    };
  });
