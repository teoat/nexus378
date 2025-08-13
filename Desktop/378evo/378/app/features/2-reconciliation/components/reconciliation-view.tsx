

"use client";

import { useAuditStore, type Filters } from "@/hooks/use-audit-store";
import { AuditResultsTable } from "@/components/views/audit-results-table";
import { getJsonHeaders, getJsonSample } from "@/lib/csv-to-json";
import { ColumnMapper } from "../../1-ingestion/components/column-mapper";
import { MatchedTransactionsTable } from "./matched-transactions-table";
import { ToleranceMatchesTable } from "./tolerance-matches-table";
import { UnmatchedBankTransactionsTable } from "./unmatched-bank-transactions-table";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BenfordAnalysisChart } from "../../3-analysis/components/benford-analysis-chart";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { useMemo, useState } from "react";
import { Anomaly, SavedFilterSet } from "@/types/types";
import { useToast } from "@/hooks/use-toast";
import { produce } from "immer";
import { AchievementId } from "@/store/gamification.store";
import ErrorBoundary from "@/components/error-boundary";

interface ReconciliationViewProps {
    onUnlockAchievement: (id: AchievementId) => void;
}

export function ReconciliationView({ 
    onUnlockAchievement,
}: ReconciliationViewProps) {
    const { 
        activeCase, 
        updateMatchData, 
        updateAnomalies,
    } = useAuditStore();
    
    if (!activeCase || !activeCase.analysisResult) {
        return <div>No analysis results found. Please run an analysis.</div>;
    }

    const { analysisResult, currency, thousandSeparator } = activeCase;
    const { matchedExpenses, toleranceMatches, unmatchedExpenses, unmatchedBankTxns, benfordChartData, anomalies } = analysisResult;
    
    return (
        <div className="space-y-6">
            <ErrorBoundary>
                 <MatchedTransactionsTable 
                    data={matchedExpenses} 
                    currency={currency} 
                    thousandSeparator={thousandSeparator}
                 />
            </ErrorBoundary>
            {toleranceMatches.length > 0 && (
                <ErrorBoundary>
                    <ToleranceMatchesTable
                        data={toleranceMatches}
                        currency={currency}
                        thousandSeparator={thousandSeparator}
                        onUpdateMatchData={updateMatchData}
                    />
                </ErrorBoundary>
            )}
            <ErrorBoundary>
                 <UnmatchedBankTransactionsTable 
                    data={unmatchedBankTxns} 
                    currency={currency} 
                    thousandSeparator={thousandSeparator}
                 />
            </ErrorBoundary>
            {benfordChartData && benfordChartData.length > 0 && (
                <ErrorBoundary>
                    <BenfordAnalysisChart data={benfordChartData} />
                </ErrorBoundary>
            )}
        </div>
    );
}
