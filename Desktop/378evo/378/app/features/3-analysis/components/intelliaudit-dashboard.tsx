

"use client";

import { useState, useEffect, useCallback, useMemo, lazy, Suspense } from 'react';
import { useAuditStore } from '@/hooks/use-audit-store';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2Icon, SparklesIcon, UndoIcon, RedoIcon } from '@/components/ui/icons';
import { Anomaly, MatchedTransaction, UnmatchedBankTransaction, Rule, AnalysisResult, JobStatus, RiskFilter } from '@/types/types';
import { toast } from '@/hooks/use-toast';
import { FrenlySuggestionBar } from '@/features/4-maintenance/components/frenly-suggestion-bar';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';
import { format } from 'date-fns';
import { formatCurrency } from '@/lib/utils';
import { useGamificationStore } from '@/store/gamification.store';
import { EmptyState } from '@/components/ui/empty-state';
import { FileIcon } from 'lucide-react';
import { produce } from 'immer';
import IngestionView from '@/features/1-ingestion/components/ingestion-view';
import { ReconciliationView } from '@/features/2-reconciliation/components/reconciliation-view';
import { functions } from '@/lib/firebase';
import { httpsCallable } from 'firebase/functions';
import { generateAuditNarrative, runLegalSynthesis } from '../actions/analysis.actions';
import dynamic from 'next/dynamic';

const RuleEngineDialog = lazy(() => import('@/components/rule-engine-dialog'));
const FrenlyCommandCenter = lazy(() => import('@/features/4-maintenance/components/frenly-command-center'));
const ClientOnlyAnomalyTable = dynamic(() => import('@/features/3-analysis/components/client-only-anomaly-table').then(mod => mod.ClientOnlyAnomalyTable), {
    ssr: false,
    loading: () => <div className="flex justify-center items-center h-96"><Loader2Icon className="h-8 w-8 animate-spin"/></div>
});


export default function IntelliAuditDashboard() {
    const { 
        loadingStage, setLoadingStage, appView, setAppView, 
        activeCase,
        setAnalysisResult,
        rules, setRules,
        undo, redo, pastStates, futureStates,
    } = useAuditStore();

    const { 
        id: caseId, sourceFileContent, analysisResult, jobStatus, operationMode,
    } = activeCase || {};


    const [isRuleEngineOpen, setIsRuleEngineOpen] = useState(false);
    const { unlockAchievement } = useGamificationStore();
    
    const handleRunAnalysis = useCallback(async () => {
        if (!caseId) return;
        setLoadingStage('processing');
        try {
            const analysisTasks = httpsCallable(functions, 'analysisTasks');
            await analysisTasks({
                 type: 'initialMatching',
                 payload: { caseId, operationMode, analysisModules: { aiFuzzyMatching: true, dataIntegrityAnalysis: true, anomalyEnrichment: true } }
             });
            toast({ title: "Analysis Queued", description: "The forensic analysis has started and will run in the background." });
        } catch (error) {
            console.error("Analysis failed:", error);
            toast({ variant: "destructive", title: "Analysis Failed", description: "Could not queue the analysis task." });
             setLoadingStage('idle');
        } 
    }, [caseId, operationMode, setLoadingStage]);
    
    const regenerateAuditNarrative = useCallback(async () => {
        if (!analysisResult) return;
        setLoadingStage('processing');
        try {
            const result = await generateAuditNarrative({ anomalies: analysisResult.anomalies, analysisSummary: analysisResult.analysisSummary });
            setAnalysisResult({ ...analysisResult, analysisSummary: result.narrative });
            toast({ title: "AI Narrative Generated", description: "The audit summary has been updated with an AI-powered narrative." });
        } catch (error) {
            console.error(error);
            toast({ variant: "destructive", title: "Narrative Generation Failed" });
        } finally {
            setLoadingStage('idle');
        }
    }, [analysisResult, setAnalysisResult, setLoadingStage]);
    
    const handleRunLegalSynthesis = useCallback(async () => {
        if (!analysisResult) return;
        setLoadingStage('processing');
        try {
            const result = await runLegalSynthesis({ anomalies: analysisResult.anomalies });
            const updatedAnomalies = analysisResult.anomalies.map(anomaly => {
                const legalInfo = result.results.find(r => r.id === anomaly.id);
                return legalInfo ? { ...anomaly, ...legalInfo } : anomaly;
            });
            setAnalysisResult({ ...analysisResult, anomalies: updatedAnomalies });
            unlockAchievement('LEGAL_EAGLE');
            toast({ title: "Legal Synthesis Complete", description: "Anomalies have been enriched with legal risk analysis." });
        } catch (error) {
            console.error(error);
            toast({ variant: "destructive", title: "Legal Synthesis Failed" });
        } finally {
            setLoadingStage('idle');
        }
    }, [analysisResult, setAnalysisResult, setLoadingStage, unlockAchievement]);

    const exportToPdf = () => {
        if (!analysisResult || !activeCase) return;
        const { currency, thousandSeparator } = activeCase;
        const doc = new jsPDF();
        
        doc.setFontSize(18);
        doc.text("IntelliAudit AI Report", 14, 22);
        doc.setFontSize(11);
        doc.setTextColor(100);
        doc.text(`Case: ${activeCase?.name}`, 14, 32);
        doc.text(`Date: ${format(new Date(), "MMMM dd, yyyy")}`, 14, 38);

        doc.setFontSize(12);
        doc.text("Analysis Summary", 14, 50);
        const splitSummary = doc.splitTextToSize(analysisResult.analysisSummary, 180);
        doc.text(splitSummary, 14, 56);
        
        const tableData = analysisResult.anomalies.map(a => [
            a.date,
            a.description,
            a.category,
            formatCurrency(a.amount, currency, thousandSeparator),
            a.riskScore,
            a.status,
        ]);
        
        (doc as any).autoTable({
            startY: 80,
            head: [['Date', 'Description', 'Category', 'Amount', 'Risk', 'Status']],
            body: tableData,
            theme: 'striped',
            headStyles: { fillColor: [22, 163, 74] },
        });

        doc.save(`IntelliAudit_Report_${new Date().toISOString()}.pdf`);
        unlockAchievement('FIRST_EXPORT');
    };

    const handleFrenlyAccept = (action: string) => {
        if (action === 'run_analysis') {
            handleRunAnalysis();
        } else if (action === 'suggest_rule') {
            setIsRuleEngineOpen(true);
        }
    }

    if (loadingStage === 'processing') {
        return (
            <div className="flex h-screen w-full flex-col items-center justify-center gap-2">
                <Loader2Icon className="h-12 w-12 animate-spin text-primary" />
                <p className="text-muted-foreground">{jobStatus?.stage || 'Processing...'}</p>
            </div>
        )
    }
    
    if (!sourceFileContent) {
        return (
            <div className="flex h-full flex-1 items-center justify-center">
                 <EmptyState 
                    title="No Active Case"
                    description="Get started by uploading your financial data to begin an analysis."
                    icon={FileIcon}
                 >
                    <IngestionView onAnalysisRequest={handleRunAnalysis} />
                 </EmptyState>
            </div>
        );
    }
    
    if (appView === 'frenly-command-center') {
        return <Suspense><FrenlyCommandCenter /></Suspense>
    }

    if (appView === 'settings') {
        // This would be a router push in a real app
        // For now, it will just show a message.
        return <div>Settings View would be here. <Button onClick={() => setAppView('workbench')}>Back to Workbench</Button></div>
    }

    if (!analysisResult) {
        return (
             <div className="flex h-full flex-1 items-center justify-center">
                <EmptyState 
                    title="Ready for Analysis"
                    description="Your data is staged. Review the column mappings, then run the analysis."
                    actionText="Run Analysis"
                    onAction={handleRunAnalysis}
                    icon={SparklesIcon}
                 />
            </div>
        )
    }

    return (
        <div className="flex-1 space-y-4 p-4 md:p-8 pt-6 relative">
            <div className="flex items-center justify-between space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">IntelliAudit Workbench</h2>
                <div className="flex items-center space-x-2">
                    <Button variant="outline" size="icon" onClick={undo} disabled={pastStates.length === 0}><UndoIcon className="h-4 w-4" /></Button>
                    <Button variant="outline" size="icon" onClick={redo} disabled={futureStates.length === 0}><RedoIcon className="h-4 w-4" /></Button>
                    <Button onClick={exportToPdf} disabled={!analysisResult?.anomalies.length}>Export PDF</Button>
                    <Button onClick={() => setIsRuleEngineOpen(true)}>Manage Rules</Button>
                </div>
            </div>
             <FrenlySuggestionBar onAccept={handleFrenlyAccept} />

            <Tabs defaultValue="anomalies">
                <div className="flex justify-between items-end">
                    <TabsList>
                        <TabsTrigger value="anomalies">Anomalies ({analysisResult.anomalies.length})</TabsTrigger>
                        <TabsTrigger value="reconciliation">Reconciliation</TabsTrigger>
                        <TabsTrigger value="summary">AI Summary</TabsTrigger>
                    </TabsList>
                    <div className="flex gap-2">
                         <Button variant="outline" size="sm" onClick={handleRunLegalSynthesis}>
                            <SparklesIcon className="mr-2 h-4 w-4" /> Run Legal Synthesis
                         </Button>
                         <Button variant="outline" size="sm" onClick={regenerateAuditNarrative}>
                            <SparklesIcon className="mr-2 h-4 w-4" /> Regenerate Narrative
                        </Button>
                    </div>
                </div>
                <TabsContent value="anomalies">
                    <ClientOnlyAnomalyTable />
                </TabsContent>
                <TabsContent value="reconciliation">
                     {analysisResult && (
                        <ReconciliationView 
                           onUnlockAchievement={unlockAchievement}
                         />
                     )}
                </TabsContent>
                <TabsContent value="summary">
                    <Card>
                        <CardHeader>
                            <CardTitle>AI-Generated Audit Summary</CardTitle>
                            <CardDescription>This narrative is generated by AI based on the detected anomalies and reconciliation results.</CardDescription>
                        </CardHeader>
                        <CardContent>
                             <div className="prose dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: analysisResult?.analysisSummary || "" }}></div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
            <Suspense>
                <RuleEngineDialog
                    isOpen={isRuleEngineOpen}
                    onOpenChange={setIsRuleEngineOpen}
                    rules={rules || []}
                    onSave={setRules}
                    onUnlockAchievement={unlockAchievement}
                />
            </Suspense>
        </div>
    );
}
