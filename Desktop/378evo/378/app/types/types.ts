

import { z } from 'zod';

// ############################################################################
// CORE DATA STRUCTURES
// ############################################################################

export const DataRowSchema = z.record(z.any());
export type DataRow = z.infer<typeof DataRowSchema>;

export const TransactionSchema = z.object({
  id: z.string(),
  date: z.string(),
  description: z.string(),
  amount: z.number(),
  category: z.string().optional(),
});
export type Transaction = z.infer<typeof TransactionSchema>;

export const MatchedTransactionSchema = z.object({
    id: z.string(),
    expenseOriginal: z.any(),
    bankTxOriginal: z.any(),
    expenseDate: z.string(),
    expenseDescription: z.string(),
    expenseAmount: z.number(),
    bankDate: z.string(),
    bankDescription: z.string(),
    bankAmount: z.number(),
    amountDifference: z.number(),
    dateDifference: z.number(),
    matchMethod: z.string(),
    confidence: z.number(),
});
export type MatchedTransaction = z.infer<typeof MatchedTransactionSchema>;


export const UnmatchedBankTransactionSchema = z.object({
  id: z.string(),
  date: z.string(),
  description: z.string(),
  amount: z.number(),
  original: z.any(),
  status: z.enum(['Unreviewed', 'Reviewed', 'Dismissed']),
});
export type UnmatchedBankTransaction = z.infer<typeof UnmatchedBankTransactionSchema>;


export const AuditLogSchema = z.object({
  timestamp: z.string(),
  user: z.string(),
  action: z.string(),
  details: z.string(),
});
export type AuditLog = z.infer<typeof AuditLogSchema>;

// ############################################################################
// ANOMALY & FRAUD DETECTION
// ############################################################################

export const AnomalyReason = [
  "Falsified Expenses", "Duplicate Claims", "Personal-to-Business", "Fictitious Vendors", "Split Transactions", "Collusion-Based Fraud",
  "PDF Bank Statement Forgery", "Synthetic Statement Generation", "Spreadsheet-Based Forgery", "Tampered CSV Uploads",
  "Reimbursable Timing Loops", "Circular Flows", "Micro-amount Leakages", "Bank Account Layering", "Missing Gaps/Partial Statements",
  "Expense Policy Gaming", "Unauthorized Account Use", "Ghost Employees/Vendors", "Kickbacks & Referral Loops",
  "High Risk Keywords", "Unusual Timing", "Out-of-Policy Expense", "Data Integrity Issue", "Unusual Pattern", "Internal Transfer",
] as const;


export const LegalRiskTagSchema = z.enum([
    'Fraud', 'Embezzlement', 'Misappropriation',
    'Breach of Contract', 'Civil Damages',
    'Regulatory Violation', 'Tax Evasion', 'AML Violation',
    'Corporate Governance Failure', 'Negligence',
    'Conflict of Interest', 'Nepotism'
]);
export type LegalRiskTag = z.infer<typeof LegalRiskTagSchema>;

const RiskFactorSchema = z.object({
    factor: z.string(),
    points: z.number(),
    reason: z.string(),
});
export type RiskFactor = z.infer<typeof RiskFactorSchema>;

export const AnomalyStatusSchema = z.enum(['Unreviewed', 'Reviewed', 'Flagged']);
export type AnomalyStatus = z.infer<typeof AnomalyStatusSchema>;


export const AnomalySchema = z.object({
  id: z.string(),
  date: z.string(),
  description: z.string(),
  amount: z.number(),
  category: z.string(),
  reason: z.string(),
  riskScore: z.number().min(0).max(100),
  confidenceScore: z.number().min(0).max(100).optional().default(0),
  riskFactors: z.array(RiskFactorSchema).optional(),
  status: AnomalyStatusSchema,
  notes: z.string().optional(),
  original: z.any(),
  auditHistory: z.array(AuditLogSchema),
  sentiment: z.enum(['positive', 'neutral', 'negative']).optional(),
  legalRiskTags: z.array(LegalRiskTagSchema).optional().describe("Tags identifying the specific nature of the legal risk."),
  caseLinkabilityScore: z.number().min(0).max(100).optional().describe("A score representing the strength of the evidence for a legal case."),
  legalRiskNarrative: z.string().optional().describe("An AI-generated narrative explaining the legal implications."),
});
export type Anomaly = z.infer<typeof AnomalySchema>;

export const RISK_FILTER_OPTIONS = ['all', 'High', 'Medium', 'Low'] as const;
export type RiskFilter = z.infer<typeof z.enum<typeof RISK_FILTER_OPTIONS>>;

// ############################################################################
// CONFIGURATION & MAPPING
// ############################################################################

export const OperationModeSchema = z.enum(['guided', 'automated', 'cost-optimized', 'smart']);
export type OperationMode = z.infer<typeof OperationModeSchema>;

export const ColumnMappingSchema = z.object({
  date: z.string().nullable(),
  description: z.string().nullable(),
  debit: z.string().nullable(),
  credit: z.string().nullable(),
  bankAccount: z.string().nullable(),
  category: z.string().nullable(),
  timeline: z.string().nullable(),
  numbering: z.string().nullable(),
  comment: z.string().nullable(),
});
export type ColumnMapping = z.infer<typeof ColumnMappingSchema>;


export const SavedMappingTemplateSchema = z.object({
    name: z.string(),
    ownerId: z.string(),
    mapping: ColumnMappingSchema
});
export type SavedMappingTemplate = z.infer<typeof SavedMappingTemplateSchema>;


// ############################################################################
// ANALYSIS & RESULTS
// ############################################################################

export const BenfordAnalysisPointSchema = z.object({
    digit: z.number(),
    actual: z.number(),
    expected: z.number(),
});
export type BenfordAnalysisPoint = z.infer<typeof BenfordAnalysisPointSchema>;


export const AnalysisResultSchema = z.object({
    id: z.string(),
    caseName: z.string(),
    versionHistory: z.array(z.any()), // Simplified to avoid circular dependency issues
    matchedExpenses: z.array(MatchedTransactionSchema),
    toleranceMatches: z.array(MatchedTransactionSchema),
    unmatchedExpenses: z.array(z.any()), // This can be any row structure
    unmatchedBankTxns: z.array(UnmatchedBankTransactionSchema),
    anomalies: z.array(AnomalySchema),
    benfordChartData: z.array(BenfordAnalysisPointSchema),
    analysisSummary: z.string(),
    aiUnmatchedBankTxns: z.array(UnmatchedBankTransactionSchema).optional(),
});
export type AnalysisResult = z.infer<typeof AnalysisResultSchema>;


export const JobStatusSchema = z.object({
  status: z.enum(['pending', 'processing', 'completed', 'failed']),
  stage: z.string().optional(),
  error: z.string().optional(),
  startedAt: z.string().optional(),
  completedAt: z.string().optional(),
});
export type JobStatus = z.infer<typeof JobStatusSchema>;


export const CaseSchema = z.object({
    id: z.string(),
    name: z.string(),
    ownerId: z.string(),
    savedAt: z.string(),
    currency: z.string(),
    thousandSeparator: z.enum([',', '.']),
    sourceFileContent: z.string(),
    bankFileContent: z.string(),
    sourceFileRowCount: z.number(),
    bankFileRowCount: z.number(),
    columnMapping: ColumnMappingSchema,
    bankColumnMapping: ColumnMappingSchema,
    analysisResult: AnalysisResultSchema.nullable(),
    jobStatus: JobStatusSchema.optional(),
    tolerances: z.object({
        date: z.number(),
        amount: z.number(),
    }),
    rules: z.array(z.lazy(() => RuleSchema)),
    versionHistory: z.array(z.any()),
    operationMode: OperationModeSchema.optional(),
});
export type Case = z.infer<typeof CaseSchema>;


export const CaseSummarySchema = z.object({
    id: z.string(),
    name: z.string(),
    savedAt: z.string(),
    sourceFileRowCount: z.number(),
    bankFileRowCount: z.number(),
});
export type CaseSummary = z.infer<typeof CaseSummarySchema>;

export const SavedFilterSetSchema = z.object({
    name: z.string(),
    filters: z.any()
});
export type SavedFilterSet = z.infer<typeof SavedFilterSetSchema>;


// ############################################################################
// RULE ENGINE & AUTOMATION
// ############################################################################

export const ConditionSchema = z.object({
  id: z.string(),
  field: z.enum(["category", "description", "reason", "amount", "riskScore"]),
  operator: z.enum(["equals", "not_equals", "contains", "greater_than", "less_than"]),
  value: z.union([z.string(), z.number()]),
});

export const ActionSchema = z.object({
    status: AnomalyStatusSchema.optional(),
    riskScore: z.number().optional(),
    category: z.string().optional(),
    note: z.string().optional(),
});

export const RuleSchema = z.object({
  id: z.string(),
  name: z.string(),
  conditions: z.array(ConditionSchema),
  action: ActionSchema,
  isEnabled: z.boolean(),
  versionHistory: z.array(z.any()), // Simplified for now
});
export type Rule = z.infer<typeof RuleSchema>;


// ############################################################################
// PLUGINS
// ############################################################################

export const PluginSchema = z.object({
  name: z.string(),
  version: z.string(),
  type: z.enum(['parser', 'analyzer']),
});
export type Plugin = z.infer<typeof PluginSchema>;

export const DataParserPluginSchema = PluginSchema.extend({
  type: z.literal('parser'),
  supportedExtensions: z.array(z.string()),
  parse: z.function().args(z.instanceof(File)).returns(z.promise(z.array(z.any()))),
});
export type DataParserPlugin = z.infer<typeof DataParserPluginSchema>;

export const AnalysisPluginSchema = PluginSchema.extend({
  type: z.literal('analyzer'),
  run: z.function().args(z.array(z.any())).returns(z.promise(z.array(AnomalySchema))),
});
export type AnalysisPlugin = z.infer<typeof AnalysisPluginSchema>;

// ############################################################################
// AI FLOW SCHEMAS
// ############################################################################

export const MapTransactionColumnsInputSchema = z.object({
    fileName: z.string(),
    headers: z.array(z.string()),
    sampleData: z.array(z.string()),
});
export type MapTransactionColumnsInput = z.infer<typeof MapTransactionColumnsInputSchema>;

export const MapTransactionColumnsOutputSchema = z.object({
    mapping: ColumnMappingSchema,
    columnAnalyses: z.array(z.object({
        columnName: z.string(),
        dataType: z.enum(['date', 'number', 'string', 'boolean', 'mixed', 'unknown']),
        valueDistribution: z.record(z.number()),
        nullPercentage: z.number(),
        recommendation: z.string().optional(),
    })),
     mappingConfidence: z.array(z.object({
        field: z.string(),
        confidence: z.number().min(0).max(100),
        reason: z.string(),
    })),
});
export type MapTransactionColumnsOutput = z.infer<typeof MapTransactionColumnsOutputSchema>;


export const BenfordsLawAnalysisInputSchema = z.object({
    debitTransactions: z.string().describe("A JSON string of transactions to be analyzed."),
    analysisDescription: z.string().describe("A brief description of the data being analyzed, e.g., 'Expense ledger debit transactions'."),
});
export type BenfordsLawAnalysisInput = z.infer<typeof BenfordsLawAnalysisInputSchema>;

export const BenfordsLawAnalysisOutputSchema = z.object({
    analysisResult: z.string().describe("A detailed, multi-paragraph analysis of the Benford's Law distribution, including any anomalies and their potential implications."),
});
export type BenfordsLawAnalysisOutput = z.infer<typeof BenfordsLawAnalysisOutputSchema>;


export const ReconciliationAnalysisInputSchema = z.object({
  unmatchedBankTxns: z.string().describe("A JSON string of unmatched bank transactions."),
  unmatchedExpenses: z.string().describe("A JSON string of unmatched expense ledger entries."),
});
export type ReconciliationAnalysisInput = z.infer<typeof ReconciliationAnalysisInputSchema>;

export const ReconciliationAnalysisOutputSchema = z.object({
  analysis: z.string().describe("A detailed analysis of the unmatched transactions, highlighting potential reasons for mismatches and suggesting next steps."),
});
export type ReconciliationAnalysisOutput = z.infer<typeof ReconciliationAnalysisOutputSchema>;

export const GenerateNoteSuggestionInputSchema = z.object({
    anomaly: AnomalySchema,
});
export type GenerateNoteSuggestionInput = z.infer<typeof GenerateNoteSuggestionInputSchema>;

export const GenerateNoteSuggestionOutputSchema = z.object({
    noteSuggestion: z.string().describe("A concise, relevant note suggestion for the provided anomaly."),
});
export type GenerateNoteSuggestionOutput = z.infer<typeof GenerateNoteSuggestionOutputSchema>;


export const SummarizeBenfordAnalysisInputSchema = z.object({
  analysisResults: z.string().describe("JSON string of Benford analysis results."),
});
export type SummarizeBenfordAnalysisInput = z.infer<typeof SummarizeBenfordAnalysisInputSchema>;


export const SummarizeBenfordAnalysisOutputSchema = z.object({
  summary: z.string().describe("A concise summary of the Benford analysis findings."),
});
export type SummarizeBenfordAnalysisOutput = z.infer<typeof SummarizeBenfordAnalysisOutputSchema>;

export const CleansingSuggestionSchema = z.object({
    originalValue: z.string(),
    suggestedValue: z.string(),
    reason: z.string(),
    count: z.number(),
});
export type CleansingSuggestion = z.infer<typeof CleansingSuggestionSchema>;

export const SuggestDataCleansingInputSchema = z.object({
    dataSample: z.array(DataRowSchema),
    columnToCleanse: z.string(),
});
export type SuggestDataCleansingInput = z.infer<typeof SuggestDataCleansingInputSchema>;

export const SuggestDataCleansingOutputSchema = z.object({
    suggestions: z.array(CleansingSuggestionSchema),
});
export type SuggestDataCleansingOutput = z.infer<typeof SuggestDataCleansingOutputSchema>;

export const FilterSuggestionSchema = z.object({
    filterCombination: z.record(z.string()),
    reasoning: z.string(),
    potentialImpact: z.string(),
});
export type FilterSuggestion = z.infer<typeof FilterSuggestionSchema>;

export const SuggestFiltersInputSchema = z.object({
    dataSample: z.array(DataRowSchema),
});
export type SuggestFiltersInput = z.infer<typeof SuggestFiltersInputSchema>;

export const SuggestFiltersOutputSchema = z.object({
    suggestions: z.array(FilterSuggestionSchema),
});
export type SuggestFiltersOutput = z.infer<typeof SuggestFiltersOutputSchema>;

export const FuzzyMatchDescriptionsInputSchema = z.object({
    unmatchedExpenses: z.array(z.object({ expenseDescription: z.string(), expenseIndex: z.number() })),
    unmatchedBankTxns: z.array(z.object({ description: z.string(), bankTxIndex: z.number() })),
});
export type FuzzyMatchDescriptionsInput = z.infer<typeof FuzzyMatchDescriptionsInputSchema>;

export const FuzzyMatchSchema = z.object({
    expenseIndex: z.number(),
    bankTxDescription: z.string(),
    confidence: z.number(),
});
export const FuzzyMatchDescriptionsOutputSchema = z.object({
    matches: z.array(FuzzyMatchSchema),
});
export type FuzzyMatchDescriptionsOutput = z.infer<typeof FuzzyMatchDescriptionsOutputSchema>;

export const CategorySuggestionSchema = z.object({
  newCategory: z.string(),
  originalDescriptions: z.array(z.string()),
  reason: z.string(),
});
export type CategorySuggestion = z.infer<typeof CategorySuggestionSchema>;


export const SuggestNewCategoryColumnInputSchema = z.object({
  dataSample: z.array(DataRowSchema),
  descriptionColumn: z.string(),
  existingCategories: z.array(z.string()).optional(),
});
export type SuggestNewCategoryColumnInput = z.infer<typeof SuggestNewCategoryColumnInputSchema>;

export const SuggestNewCategoryColumnOutputSchema = z.object({
  suggestions: z.array(CategorySuggestionSchema),
});
export type SuggestNewCategoryColumnOutput = z.infer<typeof SuggestNewCategoryColumnOutputSchema>;


export const EnrichedTransactionDetailsSchema = z.object({
  location: z.string().optional(),
  entityType: z.enum(['individual', 'business', 'utility', 'internal', 'other']).optional(),
  website: z.string().optional(),
});
export type EnrichedTransactionDetails = z.infer<typeof EnrichedTransactionDetailsSchema>;

export const EnrichTransactionDetailsInputSchema = z.object({
  description: z.string(),
});
export type EnrichTransactionDetailsInput = z.infer<typeof EnrichTransactionDetailsInputSchema>;

export const EnrichTransactionDetailsOutputSchema = EnrichedTransactionDetailsSchema;
export type EnrichTransactionDetailsOutput = z.infer<typeof EnrichTransactionDetailsOutputSchema>;

export const SuggestBatchReconciliationInputSchema = z.object({
  unmatchedExpenses: z.array(z.record(z.any())),
  unmatchedBankTxns: z.array(z.record(z.any())),
  expenseDescriptionColumn: z.string(),
  expenseAmountColumn: z.string(),
  bankDescriptionColumn: z.string(),
  bankAmountColumn: z.string(),
});
export type SuggestBatchReconciliationInput = z.infer<typeof SuggestBatchReconciliationInputSchema>;

export const BatchReconciliationSuggestionSchema = z.object({
  batchName: z.string(),
  expenseIds: z.array(z.union([z.string(), z.number()])),
  bankTxnIds: z.array(z.union([z.string(), z.number()])),
  totalExpenseAmount: z.number(),
  totalBankAmount: z.number(),
  confidence: z.number(),
  reason: z.string(),
});
export type BatchReconciliationSuggestion = z.infer<typeof BatchReconciliationSuggestionSchema>;

export const SuggestBatchReconciliationOutputSchema = z.object({
  suggestions: z.array(BatchReconciliationSuggestionSchema),
});
export type SuggestBatchReconciliationOutput = z.infer<typeof SuggestBatchReconciliationOutputSchema>;

export const ExtractedInvoiceDataSchema = z.object({
    vendor: z.string().optional(),
    invoiceDate: z.string().optional(),
    totalAmount: z.number().optional(),
    lineItems: z.array(z.object({
        description: z.string(),
        amount: z.number(),
    })).optional(),
});
export type ExtractedInvoiceData = z.infer<typeof ExtractedInvoiceDataSchema>;

export const ExtractFromImageInputSchema = z.object({
    invoiceImage: z.string().describe("A base64 encoded image of an invoice."),
});
export type ExtractFromImageInput = z.infer<typeof ExtractFromImageInputSchema>;

export const ExtractFromImageOutputSchema = z.object({
    extractedData: ExtractedInvoiceDataSchema,
});
export type ExtractFromImageOutput = z.infer<typeof ExtractFromImageOutputSchema>;

export const SentimentAnalysisInputSchema = z.object({
    text: z.string(),
});
export type SentimentAnalysisInput = z.infer<typeof SentimentAnalysisInputSchema>;

export const SentimentAnalysisOutputSchema = z.object({
    sentiment: z.enum(['positive', 'neutral', 'negative']),
    confidence: z.number(),
});
export type SentimentAnalysisOutput = z.infer<typeof SentimentAnalysisOutputSchema>;


export const GenerateAuditNarrativeInputSchema = z.object({
    anomalies: z.array(AnomalySchema),
    analysisSummary: z.string().optional(),
    isCostOptimized: z.boolean().optional(),
});
export type GenerateAuditNarrativeInput = z.infer<typeof GenerateAuditNarrativeInputSchema>;

export const GenerateAuditNarrativeOutputSchema = z.object({
    narrative: z.string().describe("A full, multi-paragraph audit narrative in Markdown format."),
});
export type GenerateAuditNarrativeOutput = z.infer<typeof GenerateAuditNarrativeOutputSchema>;


export const FrenlySuggestionSchema = z.object({
  action: z.enum(['run_analysis', 'suggest_rule', 'cleanse_data', 'none']),
  title: z.string(),
  description: z.string(),
  details: z.any().optional(),
});

export const FrenlySuggestionSchemaWithId = FrenlySuggestionSchema.extend({
  id: z.string(),
});
export type FrenlySuggestion = z.infer<typeof FrenlySuggestionSchemaWithId>;


export const SelfLearningOrganizerInputSchema = z.object({
    userActions: z.array(z.object({
        action: z.string(),
        details: z.any(),
    })),
    existingRules: z.array(RuleSchema),
});
export type SelfLearningOrganizerInput = z.infer<typeof SelfLearningOrganizerInputSchema>;


export const SelfLearningOrganizerOutputSchema = z.object({
    suggestedRules: z.array(RuleSchema),
    reasoning: z.string(),
});
export type SelfLearningOrganizerOutput = z.infer<typeof SelfLearningOrganizerOutputSchema>;

export const ReportTemplateSchema = z.object({
    id: z.string(),
    name: z.string(),
    ownerId: z.string(),
    sections: z.array(z.object({
        title: z.string(),
        content: z.enum(['summary', 'anomalies', 'benford']),
    })),
});
export type ReportTemplate = z.infer<typeof ReportTemplateSchema>;


export const IntelliLedgerAiAgentInputSchema = z.object({
  question: z.string().describe("The user's question about the financial data."),
  context: z.string().describe("A JSON string representing the current data context (e.g., filtered anomalies)."),
});
export type IntelliLedgerAiAgentInput = z.infer<typeof IntelliLedgerAiAgentInputSchema>;

export const IntelliLedgerAiAgentOutputSchema = z.object({
  answer: z.string().describe("A natural language answer to the user's question."),
  suggestedAction: z.string().optional().describe("A suggestion for a next action the user could take."),
});
export type IntelliLedgerAiAgentOutput = z.infer<typeof IntelliLedgerAiAgentOutputSchema>;


export const SynonymSchema = z.object({
    id: z.string(),
    original: z.string(),
    standardized: z.string(),
    createdAt: z.string(),
});
export type Synonym = z.infer<typeof SynonymSchema>;


export const LegalSynthesisInputSchema = z.object({
    anomalies: z.array(AnomalySchema),
});
export type LegalSynthesisInput = z.infer<typeof LegalSynthesisInputSchema>;

const LegalSynthesisResultSchema = AnomalySchema.pick({
    id: true,
}).extend({
    legalRiskTags: AnomalySchema.shape.legalRiskTags.optional(),
    caseLinkabilityScore: AnomalySchema.shape.caseLinkabilityScore.optional(),
    legalRiskNarrative: AnomalySchema.shape.legalRiskNarrative.optional(),
});

export const LegalSynthesisOutputSchema = z.object({
    results: z.array(LegalSynthesisResultSchema),
});
export type LegalSynthesisOutput = z.infer<typeof LegalSynthesisOutputSchema>;

// Defines a single vendor entity, which can be linked to multiple transactions.
export const VendorSchema = z.object({
  id: z.string(),
  name: z.string(),
  transactions: z.array(TransactionSchema),
  riskScore: z.number().optional(),
  knownAliases: z.array(z.string()).optional(),
  associatedEntities: z.array(z.string()).optional(),
});
export type Vendor = z.infer<typeof VendorSchema>;
