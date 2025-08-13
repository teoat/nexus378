
"use client";

import { useState, useMemo, useCallback } from 'react';
import { useAuditStore, type Filters, initialFilters } from '@/hooks/use-audit-store';
import { AuditResultsTable } from '@/components/views/audit-results-table';
import { FilterControls } from './filter-controls';
import { Anomaly, SavedFilterSet } from '@/types/types';
import { useToast } from '@/hooks/use-toast';
import { produce } from 'immer';
import { useGamificationStore } from '@/store/gamification.store';

export function ClientOnlyAnomalyTable() {
    const { activeCase, updateAnomalies, setTableDensity, setColumnSizing } = useAuditStore();
    const { toast } = useToast();
    const { unlockAchievement } = useGamificationStore();

    const [filters, setFilters] = useState<Filters>(initialFilters);
    const [savedFilterSets, setSavedFilterSets] = useState<SavedFilterSet[]>(() => {
        if (typeof window === 'undefined') return [];
        const saved = localStorage.getItem('intelliaudit-filtersets');
        return saved ? JSON.parse(saved) : [];
    });

    const handleSaveFilterSet = (name: string) => {
        const newSet = { name, filters };
        const updatedSets = produce(savedFilterSets, draft => {
            const existingIndex = draft.findIndex(s => s.name === name);
            if (existingIndex > -1) {
                draft[existingIndex] = newSet;
            } else {
                draft.push(newSet);
            }
        });
        setSavedFilterSets(updatedSets);
        localStorage.setItem('intelliaudit-filtersets', JSON.stringify(updatedSets));
        toast({ title: `Filter set "${name}" saved.` });
    };

    const handleDeleteFilterSet = (name: string) => {
        const updatedSets = savedFilterSets.filter(s => s.name !== name);
        setSavedFilterSets(updatedSets);
        localStorage.setItem('intelliaudit-filtersets', JSON.stringify(updatedSets));
        toast({ title: "Filter set deleted." });
    };

    const handleLoadFilterSet = (filters: Filters) => {
        setFilters(filters);
    };

    const handleClearFilters = () => {
        setFilters(initialFilters);
    };

    const handleFiltersChange = <K extends keyof Filters>(key: K, value: Filters[K]) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const filteredAnomalies = useMemo(() => {
        if (!activeCase?.analysisResult?.anomalies) return [];
        return activeCase.analysisResult.anomalies.filter(anomaly => {
            if (filters.status !== 'all' && anomaly.status !== filters.status) return false;
            if (filters.risk !== 'all') {
                if (filters.risk === 'High' && anomaly.riskScore <= 80) return false;
                if (filters.risk === 'Medium' && (anomaly.riskScore <= 40 || anomaly.riskScore > 80)) return false;
                if (filters.risk === 'Low' && (anomaly.riskScore <= 0 || anomaly.riskScore > 40)) return false;
            }
            if (filters.category !== 'all' && anomaly.category !== filters.category) return false;
            if (filters.reason !== 'all' && anomaly.reason !== filters.reason) return false;
            if (filters.description && !anomaly.description.toLowerCase().includes(filters.description.toLowerCase())) return false;
            if (filters.minAmount && anomaly.amount < parseFloat(filters.minAmount)) return false;
            if (filters.maxAmount && anomaly.amount > parseFloat(filters.maxAmount)) return false;
            if (filters.notes === 'has_notes' && !anomaly.notes) return false;
            if (filters.notes === 'no_notes' && anomaly.notes) return false;
            if (filters.startDate && new Date(anomaly.date) < filters.startDate) return false;
            if (filters.endDate && new Date(anomaly.date) > filters.endDate) return false;
            return true;
        });
    }, [activeCase?.analysisResult?.anomalies, filters]);

    const handleUpdateAnomalies = useCallback((ids: string[], updates: Partial<Anomaly>) => {
        updateAnomalies(ids, updates, { timestamp: new Date().toISOString(), user: 'user', action: 'update', details: 'Updated from dialog' });
        if (updates.status === 'Reviewed') {
            unlockAchievement('FIRST_REVIEW');
        }
    }, [updateAnomalies, unlockAchievement]);

    if (!activeCase || !activeCase.analysisResult) {
        return <div>Loading...</div>
    }

    return (
        <div>
            <FilterControls 
                filters={filters}
                onFiltersChange={handleFiltersChange}
                onClearFilters={handleClearFilters}
                savedFilterSets={savedFilterSets}
                onSaveFilterSet={handleSaveFilterSet}
                onLoadFilterSet={handleLoadFilterSet}
                onDeleteFilterSet={handleDeleteFilterSet}
                onUnlockAchievement={unlockAchievement}
                allAnomalies={activeCase.analysisResult.anomalies}
            />
            <AuditResultsTable
                data={filteredAnomalies}
                currency={activeCase.currency!}
                thousandSeparator={activeCase.thousandSeparator!}
                onUpdateAnomalies={handleUpdateAnomalies}
                tableDensity={activeCase.tableDensity!}
                onTableDensityChange={setTableDensity}
                columnSizing={activeCase.columnSizing!}
                onColumnSizingChange={setColumnSizing}
            />
        </div>
    );
}
