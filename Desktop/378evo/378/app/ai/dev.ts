
import { config } from 'dotenv';
config();

// Active and essential AI flows for the application
import '@/features/1-ingestion/ai-flows/ingest-file';
import '@/features/3-analysis/ai-flows/generate-audit-narrative';
import '@/features/3-analysis/ai-flows/legal-synthesis';
import '@/features/3-analysis/ai-flows/summarize-benford-analysis';
import '@/features/2-reconciliation/ai-flows/fuzzy-match-descriptions';
import '@/features/2-reconciliation/ai-flows/enrich-transaction-details';

// Flows that are part of the full feature set but currently stubbed or less critical
import '@/features/3-analysis/ai-flows/intelli-ledger-ai-agent';
import '@/features/3-analysis/ai-flows/benfords-law-analysis';
import '@/features/3-analysis/ai-flows/generate-note-suggestion';
import '@/features/3-analysis/ai-flows/suggest-data-cleansing';
import '@/features/3-analysis/ai-flows/suggest-filters';
import '@/features/3-analysis/ai-flows/suggest-new-category-column';
import '@/features/3-analysis/ai-flows/sentiment-analysis';
import '@/features/4-maintenance/ai-flows/self-learning-organizer';
