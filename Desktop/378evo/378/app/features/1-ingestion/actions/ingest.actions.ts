
'use server';

import { ingestFileFlow } from '../ai-flows/ingest-file';
import { csvToJson } from '@/lib/csv-to-json';

export async function ingestFile(fileType: 'source' | 'bank', fileContent: string) {
  const jsonContent = fileContent.trim().startsWith('[') ? fileContent : JSON.stringify(csvToJson(fileContent));
  
  const result = await ingestFileFlow(jsonContent);

  return {
      fileType,
      jsonContent: result.jsonContent,
      mapping: result.mapping,
      columnAnalyses: result.columnAnalyses,
      mappingConfidence: result.mappingConfidence,
  };
}
