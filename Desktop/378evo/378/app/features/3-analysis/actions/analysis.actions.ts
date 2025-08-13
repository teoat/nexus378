
"use server";

import { Anomaly, BenfordAnalysisPoint, UnmatchedBankTransaction, Vendor, OperationMode } from "@/types/types";
import { v4 as uuidv4 } from "uuid";
import { summarizeBenfordAnalysis } from "../ai-flows/summarize-benford-analysis";
import { MapTransactionColumnsOutput } from '@/types/types';
import { generateAuditNarrativeFlow } from "../ai-flows/generate-audit-narrative";
import { sentimentAnalysis } from "../ai-flows/sentiment-analysis";
import { enrichTransactionDetails } from "../../2-reconciliation/ai-flows/enrich-transaction-details";
import { legalSynthesisFlow } from "../ai-flows/legal-synthesis";
import { runComplianceChecks } from "@/app/actions/compliance.actions";
import { sendWebhook } from "@/app/actions/webhook.actions";
import { getSession } from "@/app/actions/auth.actions";
import { GenerateAuditNarrativeInput, GenerateAuditNarrativeOutput, LegalSynthesisInput, LegalSynthesisOutput } from "@/types/types";


interface FullAnalysisInput {
    unmatchedExpenses: any[];
    unmatchedBankTxns: UnmatchedBankTransaction[];
    benfordChartData: BenfordAnalysisPoint[];
    columnAnalyses: MapTransactionColumnsOutput['columnAnalyses'];
    isDataIntegrityEnabled: boolean;
    isEnrichmentEnabled: boolean;
    mode: OperationMode;
    ownerId: string;
}

// A simple rule-based anomaly detector for internal transfers
function detectInternalTransfers(unmatchedExpenses: any[]): Anomaly[] {
    return unmatchedExpenses.filter(expense => 
        expense.description?.toLowerCase().includes("internal transfer") ||
        expense.description?.toLowerCase().includes("payment to account")
    ).map(expense => ({
        id: uuidv4(),
        date: expense.date,
        description: `Potential Internal Transfer: ${expense.description}`,
        amount: expense.debit,
        category: 'Internal',
        reason: 'Internal Transfer',
        riskScore: 5,
        confidenceScore: 90,
        status: 'Reviewed',
        original: expense,
        auditHistory: [],
    }));
}

// Placeholder for a more sophisticated anomaly detection engine
function runLocalAnomalyDetection(unmatchedExpenses: any[]): Anomaly[] {
    const anomalies: Anomaly[] = [];

    // Rule: Detect expenses without a match in the bank statement
    unmatchedExpenses.forEach(expense => {
        anomalies.push({
            id: uuidv4(),
            date: expense.date,
            description: `Expense without match: ${expense.description}`,
            amount: expense.debit,
            category: expense.category || 'Uncategorized',
            reason: "Unmatched Expense",
            riskScore: 60, // Moderate risk
            confidenceScore: 95,
            status: 'Unreviewed',
            original: expense,
            auditHistory: [],
        });
    });
    
    anomalies.push(...detectInternalTransfers(unmatchedExpenses));

    return anomalies;
}

// Helper function to extract unique vendors from transactions
function extractUniqueVendors(transactions: any[]): Vendor[] {
    const vendors = new Map<string, Vendor>();
    transactions.forEach(tx => {
        // Assuming the 'description' field contains the vendor name.
        // This might need to be adjusted based on the actual data structure.
        const vendorName = tx.description; 
        if (vendorName && !vendors.has(vendorName)) {
            vendors.set(vendorName, {
                id: uuidv4(),
                name: vendorName,
                transactions: [tx]
            });
        } else if (vendorName && vendors.has(vendorName)) {
            vendors.get(vendorName)?.transactions.push(tx);
        }
    });
    return Array.from(vendors.values());
}


export async function runFullForensicAnalysis(input: FullAnalysisInput) {
    const { unmatchedExpenses, unmatchedBankTxns, benfordChartData, columnAnalyses, isDataIntegrityEnabled, isEnrichmentEnabled, mode, ownerId } = input;

    // 1. Run local, rule-based anomaly detection
    let anomalies = runLocalAnomalyDetection(unmatchedExpenses);

    // 2. Extract unique vendors and run compliance checks in parallel
    const uniqueVendors = extractUniqueVendors(unmatchedExpenses);
    const compliancePromise = runComplianceChecks(unmatchedExpenses, uniqueVendors).catch(() => []);


    // 3. Run parallel AI enhancements on the initial set of anomalies, if applicable
    if (mode !== 'cost-optimized') {
        const enhancementPromises = anomalies.map(async (anomaly) => {
            const promises = [];

            // Sentiment Analysis is skipped in cost-optimized mode
            if (anomaly.description) {
                promises.push(
                    sentimentAnalysis({ text: anomaly.description })
                        .then(result => ({ sentiment: result.sentiment }))
                        .catch(() => ({})) // Ignore errors for individual enhancements
                );
            }

            // Data Enrichment
            if (isEnrichmentEnabled && anomaly.description) {
                promises.push(
                    enrichTransactionDetails({ description: anomaly.description })
                        .then(enriched => ({ enrichedData: enriched }))
                        .catch(() => ({}))
                );
            }
            
            const results = await Promise.all(promises);
            return results.reduce((acc, result) => ({ ...acc, ...result }), {});
        });
        
        const legalAnalysisPromise = legalSynthesisFlow({ anomalies }).catch(() => null);

        const [enhancedData, legalResults, complianceAnomalies] = await Promise.all([
             Promise.all(enhancementPromises),
             legalAnalysisPromise,
             compliancePromise
        ]);

        // 4. Merge enhancement and compliance results back into anomalies
        anomalies = anomalies.map((anomaly, index) => {
            const { sentiment, enrichedData } = enhancedData[index] as any;
            let updatedAnomaly = { ...anomaly };
            if (sentiment) {
                updatedAnomaly.sentiment = sentiment;
                if(sentiment === 'negative') updatedAnomaly.riskScore = Math.min(100, updatedAnomaly.riskScore + 10);
            }
            if (enrichedData) {
                // Logic to merge enriched data can be added here
                // For example, add notes or adjust risk based on entityType
            }
            
            // Merge legal analysis results
            const legalData = legalResults?.results.find(r => r.id === anomaly.id);
            if (legalData) {
                updatedAnomaly.legalRiskTags = legalData.legalRiskTags;
                updatedAnomaly.caseLinkabilityScore = legalData.caseLinkabilityScore;
                updatedAnomaly.legalRiskNarrative = legalData.legalRiskNarrative;
            }

            return updatedAnomaly;
        });

        // Add compliance anomalies to the list
        anomalies.push(...complianceAnomalies);

    } else {
        // In cost-optimized mode, just wait for compliance checks
        const complianceAnomalies = await compliancePromise;
        anomalies.push(...complianceAnomalies);
    }


    // 5. Generate AI summaries and narratives
    let analysisSummary = "Analysis complete. No AI summary was generated.";
    const summaryPromises = [];

    if (isDataIntegrityEnabled && benfordChartData.length > 0) {
       summaryPromises.push(
            summarizeBenfordAnalysis({ analysisResults: JSON.stringify(benfordChartData) })
                .then(result => `Benford's Law Summary: ${result.summary}`)
                .catch(() => "Benford's Law analysis failed.")
       );
    }
    
    if (anomalies.length > 0) {
        summaryPromises.push(
            generateAuditNarrativeFlow({ anomalies, analysisSummary: "See detailed findings below.", isCostOptimized: mode === 'cost-optimized' })
                .then(result => result.narrative)
                .catch(() => "Failed to generate audit narrative.")
        );
    }

    const summaryResults = await Promise.all(summaryPromises);
    analysisSummary = summaryResults.join('\n\n');
    
    // 6. Trigger webhooks for high-risk anomalies
    const highRiskAnomalies = anomalies.filter(a => a.riskScore > 80);
    if(highRiskAnomalies.length > 0 && ownerId) {
        for(const anomaly of highRiskAnomalies) {
            await sendWebhook(ownerId, 'high_risk_anomaly_detected', anomaly);
        }
    }


    return {
        anomalies,
        aiUnmatchedBankTxns: unmatchedBankTxns, // Placeholder for future AI bank matching
        analysisSummary,
    };
}


export async function generateAuditNarrative(input: GenerateAuditNarrativeInput): Promise<GenerateAuditNarrativeOutput> {
    return await generateAuditNarrativeFlow(input);
}


export async function runLegalSynthesis(input: LegalSynthesisInput): Promise<LegalSynthesisOutput> {
    return await legalSynthesisFlow(input);
}
