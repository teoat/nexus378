
'use server';

import { ai } from '@/ai/genkit';
import { GenerateAuditNarrativeInputSchema, GenerateAuditNarrativeOutputSchema, AnomalySchema } from '@/types/types';
import { z } from 'zod';

// This function is temporarily stubbed for the client-side refactor.
export async function generateAuditNarrative_stub(
    input: z.infer<typeof GenerateAuditNarrativeInputSchema>
): Promise<z.infer<typeof GenerateAuditNarrativeOutputSchema>> {
    console.log("CLIENT-SIDE STUB: generateAuditNarrative called.");
    return { narrative: "### AI Narrative Generation Disabled\n\nThis feature is temporarily disabled during the client-side architectural pivot. A full AI-powered narrative will be available when server-side actions are re-integrated." };
}

const systemPrompt = `You are a world-class forensic accountant and auditor. Your task is to generate a comprehensive, well-structured audit narrative in Markdown format based on a provided list of anomalies. The narrative should be clear, concise, and suitable for an executive summary or a detailed audit report.

**Structure:**
1.  **Executive Summary:** A high-level overview of the findings.
2.  **Key Findings:** A bulleted list of the most significant anomalies or patterns.
3.  **Recommendations:** Actionable steps to mitigate risks.
4.  **Detailed Anomaly Breakdown:** A brief mention of the riskiest items.`;

const costOptimizedSystemPrompt = `You are an efficient assistant. Generate a brief summary of the audit findings in Markdown. List the top 3-5 anomalies by risk score and provide a short concluding sentence.`;


export const generateAuditNarrativeFlow = ai.defineFlow(
  {
    name: 'generateAuditNarrativeFlow',
    inputSchema: GenerateAuditNarrativeInputSchema,
    outputSchema: GenerateAuditNarrativeOutputSchema,
  },
  async (input) => {
    
    // Sort anomalies by risk score to highlight the most critical ones
    const sortedAnomalies = [...input.anomalies].sort((a, b) => b.riskScore - a.riskScore);
    const top5Anomalies = sortedAnomalies.slice(0, 5);

    const prompt = ai.definePrompt({
        name: 'generateAuditNarrativePrompt',
        input: {
            schema: z.object({
                anomalies: z.array(AnomalySchema),
                analysisSummary: z.string().optional(),
            }),
        },
        output: { schema: GenerateAuditNarrativeOutputSchema },
        prompt: `Based on the following data, generate the audit narrative.

        **Provided Analysis Summary:**
        {{analysisSummary}}
        
        **Top Anomalies (for detailed breakdown):**
        {{{json anomalies}}}
        `,
        config: {
            system: input.isCostOptimized ? costOptimizedSystemPrompt : systemPrompt,
        },
    });

    const { output } = await prompt({
        anomalies: top5Anomalies,
        analysisSummary: input.analysisSummary,
    });
    
    if (!output) {
      throw new Error('AI failed to generate the audit narrative.');
    }

    return output;
  }
);
