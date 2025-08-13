
import { create } from 'zustand';
import { createIngestionSlice, IngestionState } from '@/features/1-ingestion/ingestion.store';
import { createReconciliationSlice, ReconciliationState } from '@/features/2-reconciliation/reconciliation.store';
import { createAnalysisSlice, AnalysisState } from '@/features/3-analysis/analysis.store';

type AppState = IngestionState & ReconciliationState & AnalysisState;

export const useAppStore = create<AppState>()((...a) => ({
    ...createIngestionSlice(...a),
    ...createReconciliationSlice(...a),
    ...createAnalysisSlice(...a),
}));
