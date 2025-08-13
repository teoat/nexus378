
'use server';

import { ai } from '@/ai/genkit';
import { RuleSchema } from '@/types/types';
import { z } from 'zod';
import { FrenlySuggestionSchema } from '@/types/types';

const SelfLearningOrganizerInputSchema = z.object({
  appState: z.object({
    hasSourceFile: z.boolean(),
    hasAnalysisResult: z.boolean(),
    anomalyCount: z.number(),
    unreviewedCount: z.number(),
  }),
  existingRules: z.array(RuleSchema),
});

const systemPrompt = `You are "Frenly", an intelligent AI assistant for the IntelliAudit AI application. Your primary goal is to provide helpful, contextual suggestions to the user to guide them through the audit process. You should only suggest ONE action at a time. Be proactive and concise.

Analyze the current state of the application and suggest the most logical next step.

- If no data has been uploaded, you must return an action of 'none'.
- If data has been uploaded but not analyzed, the most logical next step is to 'run_analysis'.
- If the analysis is complete and there are many unreviewed anomalies (>10), suggest creating a rule ('suggest_rule').
- If the analysis is complete but there are potential data quality issues (e.g., many 'Uncategorized' items), suggest cleansing data ('cleanse_data').
- If the analysis is complete and there are few or no unreviewed anomalies, you should state that everything looks good and return action 'none'.`;

const selfLearningOrganizerFlow = ai.defineFlow(
  {
    name: 'selfLearningOrganizerFlow',
    inputSchema: SelfLearningOrganizerInputSchema,
    outputSchema: FrenlySuggestionSchema,
  },
  async ({ appState, existingRules }) => {

    if (!appState.hasSourceFile) {
        return { action: 'none', title: 'Welcome!', description: 'Upload a source file to get started.' };
    }

    if (!appState.hasAnalysisResult) {
        return {
            action: 'run_analysis',
            title: 'Ready to Analyze?',
            description: "I see you've loaded a data file. I can run the initial analysis to match transactions and identify potential anomalies.",
        };
    }
    
    // This is a simplified logic. A more advanced version could analyze the *content* of the anomalies.
    if (appState.unreviewedCount > 10) {
        return {
            action: 'suggest_rule',
            title: 'Feeling Overwhelmed?',
            description: `There are ${appState.unreviewedCount} unreviewed anomalies. I can help create a rule to auto-adjudicate similar items to speed up your workflow.`,
            details: { trigger: 'unreviewed_count' }
        };
    }
    
    // This part of the logic is currently disabled as the data cleansing flow is not fully implemented.
    // A future implementation would re-enable this.
    /*
    const uncategorizedCount = appState.analysisResult?.anomalies.filter(a => a.category === 'Uncategorized').length || 0;
    if (uncategorizedCount > 5) {
        return {
            action: 'cleanse_data',
            title: 'Data Quality Check',
            description: `I found ${uncategorizedCount} uncategorized items. I can suggest new categories to help organize your data better.`,
            details: { trigger: 'uncategorized_count' }
        }
    }
    */


    return {
        action: 'none',
        title: 'All Clear!',
        description: 'No immediate actions are needed. You can continue your review or explore the data.',
    };
  }
);

export { selfLearningOrganizerFlow as selfLearningOrganizer };
