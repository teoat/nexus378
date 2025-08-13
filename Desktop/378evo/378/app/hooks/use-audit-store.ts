

import { createWithEqualityFn } from 'zustand/traditional';
import { temporal, type ZundoOptions, createTemporal } from 'zundo';
import { produce } from 'immer';
import {
  Anomaly, AnalysisResult, AuditLog, ColumnMapping,
  MatchedTransaction, UnmatchedBankTransaction, Rule,
  MapTransactionColumnsOutput, Case, Synonym, OperationMode,
  JobStatus, MapTransactionColumnsOutputSchema, RiskFilter
} from '@/types/types';
import { appConfig } from '@/app/config';
import { v4 as uuidv4 } from 'uuid';
import { z } from 'zod';

type LoadingStage = "idle" | "processing" | "saving" | "loading";
type AppView = 'workbench' | 'frenly-command-center' | 'settings';
export type TableDensity = "comfortable" | "default" | "compact";
export type ColumnSizing = "auto" | "fitContent";

export interface Filters {
    status: 'all' | Anomaly['status'];
    risk: RiskFilter;
    category: 'all' | string;
    reason: 'all' | string;
    description: string;
    minAmount: string;
    maxAmount: string;
    notes: 'all' | 'has_notes' | 'no_notes';
    startDate: Date | null;
    endDate: Date | null;
}

export const initialFilters: Filters = { status: 'all', risk: 'all', category: 'all', reason: 'all', description: '', minAmount: '', maxAmount: '', notes: 'all', startDate: null, endDate: null };

interface DashboardState {
  activeCase: Case | null;
  loadingStage: LoadingStage;
  appView: AppView;
  tableDensity: TableDensity;
  columnSizing: ColumnSizing;
  synonyms: Synonym[];
  ownerId: string | null;
}

interface DashboardActions {
  createCase: () => void;
  setSourceFile: (content: string, rowCount: number) => void;
  setBankFile: (content: string, rowCount: number) => void;
  setColumnMapping: (mapping: ColumnMapping) => void;
  setBankColumnMapping: (mapping: ColumnMapping) => void;
  setLoadingStage: (payload: LoadingStage) => void;
  setAppView: (payload: AppView) => void;
  updateAnomalies: (ids: string[], updates: Partial<Anomaly>, newHistoryEntry: AuditLog) => void;
  updateMatchData: (payload: { confirmedMatch: MatchedTransaction, rejectedMatch?: never } | { rejectedMatch: MatchedTransaction, confirmedMatch?: never }) => void;
  setTableDensity: (payload: TableDensity) => void;
  setColumnSizing: (payload: ColumnSizing) => void;
  setTolerances: (key: 'date' | 'amount', value: number) => void;
  setRules: (payload: Rule[]) => void;
  clearAll: () => void;
  deleteColumn: (fileType: 'source' | 'bank', columnName: string) => void;
  renameColumn: (fileType: 'source' | 'bank', oldName: string, newName: string) => void;
  hydrateFromCase: (payload: Case) => void;
  setSynonyms: (payload: Synonym[]) => void;
  setOwnerId: (payload: string | null) => void;
  setOperationMode: (payload: OperationMode) => void;
  setAnalysisResult: (payload: AnalysisResult) => void;
}

type TemporalState = Pick<DashboardState, 'activeCase'>;

const zundoOptions: ZundoOptions<TemporalState> = {
    partialize: (state) => ({ activeCase: state.activeCase }),
    equality: (a, b) => JSON.stringify(a) === JSON.stringify(b),
};

const useStore = createWithEqualityFn<DashboardState & DashboardActions>()(
    (set, get) => ({
      activeCase: null,
      loadingStage: 'idle',
      appView: 'workbench',
      tableDensity: 'default',
      columnSizing: 'auto',
      synonyms: [],
      ownerId: null,

      createCase: () => set(produce((draft: DashboardState) => {
          if (!draft.activeCase) {
              draft.activeCase = {
                  id: uuidv4(),
                  name: `New Case`,
                  savedAt: new Date().toISOString(),
                  currency: 'USD',
                  thousandSeparator: ',',
                  sourceFileContent: '',
                  bankFileContent: '',
                  sourceFileRowCount: 0,
                  bankFileRowCount: 0,
                  columnMapping: { date: null, description: null, debit: null, credit: null, bankAccount: null, category: null, timeline: null, numbering: null, comment: null },
                  bankColumnMapping: { date: null, description: null, debit: null, credit: null, bankAccount: null, category: null, timeline: null, numbering: null, comment: null },
                  analysisResult: null,
                  tolerances: { date: 2, amount: 1 },
                  rules: [],
                  versionHistory: [],
                  operationMode: 'guided',
                  ownerId: get().ownerId || 'anonymous'
              };
          }
      })),

      setSourceFile: (content, rowCount) => set(produce((draft: DashboardState) => {
          if (draft.activeCase) {
              draft.activeCase.sourceFileContent = content;
              draft.activeCase.sourceFileRowCount = rowCount;
          }
      })),

      setBankFile: (content, rowCount) => set(produce((draft: DashboardState) => {
          if (draft.activeCase) {
              draft.activeCase.bankFileContent = content;
              draft.activeCase.bankFileRowCount = rowCount;
          }
      })),

      setColumnMapping: (mapping) => set(produce((draft: DashboardState) => {
          if (draft.activeCase) draft.activeCase.columnMapping = mapping;
      })),
      
      setBankColumnMapping: (mapping) => set(produce((draft: DashboardState) => {
          if (draft.activeCase) draft.activeCase.bankColumnMapping = mapping;
      })),

      setOwnerId: (payload) => set({ ownerId: payload }),
      setLoadingStage: (payload) => set({ loadingStage: payload }),
      setAppView: (payload) => set({ appView: payload }),
      
      updateAnomalies: (ids, updates, newHistoryEntry) => set(produce((draft: DashboardState) => {
        if (draft.activeCase?.analysisResult) {
          draft.activeCase.analysisResult.anomalies.forEach(a => {
            if (ids.includes(a.id)) {
              Object.assign(a, updates);
              a.auditHistory.push(newHistoryEntry);
            }
          });
        }
      })),

      updateMatchData: (payload) => set(produce((draft: DashboardState) => {
        if (!draft.activeCase?.analysisResult) return;
        const { confirmedMatch, rejectedMatch } = payload;
        const matchId = confirmedMatch?.id || rejectedMatch?.id;
        draft.activeCase.analysisResult.toleranceMatches = draft.activeCase.analysisResult.toleranceMatches.filter(m => m.id !== matchId);

        if (confirmedMatch) {
            draft.activeCase.analysisResult.matchedExpenses.push(confirmedMatch);
        }
        if (rejectedMatch) {
            draft.activeCase.analysisResult.unmatchedExpenses.push(rejectedMatch.expenseOriginal);
            const newUnmatchedBankTx: UnmatchedBankTransaction = {
                id: uuidv4(),
                original: rejectedMatch.bankTxOriginal,
                date: rejectedMatch.bankDate,
                description: rejectedMatch.bankDescription,
                amount: rejectedMatch.bankAmount,
                status: 'Unreviewed'
            };
            draft.activeCase.analysisResult.unmatchedBankTxns.push(newUnmatchedBankTx);
        }
      })),

      setTableDensity: (payload) => set({ tableDensity: payload }),
      setColumnSizing: (payload) => set({ columnSizing: payload }),
      setTolerances: (key, value) => set(produce((draft: DashboardState) => { 
        if(draft.activeCase) draft.activeCase.tolerances[key as 'date' | 'amount'] = value; 
      })),
      setRules: (payload) => set(produce((draft: DashboardState) => {
         if(draft.activeCase) draft.activeCase.rules = payload 
      })),
      clearAll: () => set({ activeCase: null }),
      
      deleteColumn: (fileType, columnName) => set(produce((draft: DashboardState) => {
          if (!draft.activeCase) return;
          const contentKey = fileType === 'source' ? 'sourceFileContent' : 'bankFileContent';
          const mappingKey = fileType === 'source' ? 'columnMapping' : 'bankColumnMapping';

          if (draft.activeCase[contentKey]) {
              const data = JSON.parse(draft.activeCase[contentKey]!);
              const cleanedData = data.map((row: any) => {
                  delete row[columnName];
                  return row;
              });
              draft.activeCase[contentKey] = JSON.stringify(cleanedData, null, 2);
              
              for (const key in draft.activeCase[mappingKey]) {
                  if (draft.activeCase[mappingKey][key as keyof ColumnMapping] === columnName) {
                      (draft.activeCase[mappingKey] as any)[key] = null;
                  }
              }
          }
      })),

      renameColumn: (fileType, oldName, newName) => set(produce((draft: DashboardState) => {
          if (!draft.activeCase) return;
          const contentKey = fileType === 'source' ? 'sourceFileContent' : 'bankFileContent';
          const mappingKey = fileType === 'source' ? 'columnMapping' : 'bankColumnMapping';

          if (draft.activeCase[contentKey]) {
              const data = JSON.parse(draft.activeCase[contentKey]!);
              const renamedData = data.map((row: any) => {
                  if (Object.prototype.hasOwnProperty.call(row, oldName)) {
                      row[newName] = row[oldName];
                      delete row[oldName];
                  }
                  return row;
              });
              draft.activeCase[contentKey] = JSON.stringify(renamedData, null, 2);
              
              for (const key in draft.activeCase[mappingKey]) {
                  if (draft.activeCase[mappingKey][key as keyof ColumnMapping] === oldName) {
                      (draft.activeCase[mappingKey] as any)[key] = newName;
                  }
              }
          }
      })),
      
      hydrateFromCase: (payload) => set({ activeCase: payload }),
      setSynonyms: (payload) => set({ synonyms: payload }),
      setOperationMode: (payload) => set(produce((draft: DashboardState) => { 
          if (draft.activeCase) {
            draft.activeCase.operationMode = payload;
          }
      })),
      setAnalysisResult: (payload) => set(produce((draft: DashboardState) => {
        if(draft.activeCase) draft.activeCase.analysisResult = payload;
      })),
    }),
    {
        equality: (a,b) => JSON.stringify(a) === JSON.stringify(b)
    }
);

export const useAuditStore = createTemporal(useStore, zundoOptions);

    