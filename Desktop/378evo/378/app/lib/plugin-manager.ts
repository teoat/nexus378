
import { z } from 'zod';
import { DataParserPluginSchema, AnalysisPluginSchema, PluginSchema } from '@/types/types';

class PluginManager {
  private parsers: z.infer<typeof DataParserPluginSchema>[] = [];
  private analyzers: z.infer<typeof AnalysisPluginSchema>[] = [];

  register(plugin: z.infer<typeof PluginSchema>) {
    if (DataParserPluginSchema.safeParse(plugin).success) {
      this.parsers.push(plugin as z.infer<typeof DataParserPluginSchema>);
    } else if (AnalysisPluginSchema.safeParse(plugin).success) {
      this.analyzers.push(plugin as z.infer<typeof AnalysisPluginSchema>);
    } else {
      throw new Error(`Invalid plugin type: ${plugin.type}`);
    }
  }

  getParser(extension: string) {
    return this.parsers.find(p => p.supportedExtensions.includes(extension));
  }

  getAnalyzers() {
    return this.analyzers;
  }
}

export const pluginManager = new PluginManager();

  