
import { DataParserPluginSchema } from '@/types/types';
import { csvToJson } from '@/lib/csv-to-json';

export const csvParser = {
  name: 'CSV Parser',
  version: '1.0.0',
  type: 'parser',
  supportedExtensions: ['.csv'],
  parse: async (file) => {
    const content = await file.text();
    return await csvToJson(content);
  },
};

  