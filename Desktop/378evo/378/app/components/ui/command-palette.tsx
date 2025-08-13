
"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Command, CommandDialog, CommandInput, CommandList, CommandEmpty, CommandGroup, CommandItem } from "@/components/ui/command";
import { useAuditStore } from "@/hooks/use-audit-store";
import ClientOnly from "../client-only";

interface Action {
    id: string;
    label: string;
    action: () => void;
    group: string;
    isVisible?: (state: any) => boolean;
}

export function CommandPalette() {
    const [open, setOpen] = useState(false);
    const state = useAuditStore(state => state);
    const { setAppView, setLoadingStage } = useAuditStore();


    const allActions: Action[] = [
        { id: 'new-case', label: 'New Analysis Case', group: 'File', action: () => state.clearAll() },
        { id: 'save-case', label: 'Save Current Case', group: 'File', action: () => { /* Logic handled in dashboard */ }, isVisible: state => !!state.sourceFileContent },
        { id: 'export-csv', label: 'Export Anomalies (CSV)', group: 'File', action: () => { /* Logic handled in dashboard */ }, isVisible: state => state.appView === 'workbench' && !!state.analysisResult?.anomalies?.length },
        { id: 'export-pdf', label: 'Export Report (PDF)', group: 'File', action: () => { /* Logic handled in dashboard */ }, isVisible: state => state.appView === 'workbench' && !!state.analysisResult?.anomalies?.length },
        { id: 'open-settings', label: 'Open Settings', group: 'Navigation', action: () => setAppView('settings') /*This would navigate to a settings page*/ },
        { id: 'open-workbench', label: 'Go to Workbench', group: 'Navigation', action: () => setAppView('workbench'), isVisible: state => !!state.analysisResult },
        { id: 'open-frenly', label: 'Open Frenly Command Center', group: 'Navigation', action: () => setAppView('frenly-command-center') /* This would switch tab */ },
        { id: 'run-analysis', label: 'Run Full Analysis', group: 'Actions', action: () => { /* Logic in dashboard */ }, isVisible: state => !!state.sourceFileContent && !state.analysisResult },
        { id: 'open-rule-engine', label: 'Manage Rules', group: 'Actions', action: () => { /* Logic in dashboard */ }, isVisible: state => state.appView === 'workbench' },
    ];
    
    const availableActions = React.useMemo(() => {
        return allActions.filter(action => !action.isVisible || action.isVisible(state));
    }, [state]);

    const groupedActions = React.useMemo(() => {
        return availableActions.reduce((groups, action) => {
            const group = action.group;
            if (!groups[group]) {
                groups[group] = [];
            }
            groups[group].push(action);
            return groups;
        }, {} as Record<string, Action[]>);
    }, [availableActions]);


    useEffect(() => {
        const down = (e: KeyboardEvent) => {
            if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                setOpen((open) => !open);
            }
        };
        document.addEventListener("keydown", down);
        return () => document.removeEventListener("keydown", down);
    }, []);

    const runCommand = (action: () => void) => {
        action();
        setOpen(false);
    }

    return (
        <ClientOnly>
            <>
                <p className="fixed bottom-4 left-4 text-sm text-muted-foreground z-50">
                    Press{" "}
                    <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
                        <span className="text-xs">⌘</span>K
                    </kbd>{" "}
                    to open the command palette.
                </p>
                <CommandDialog open={open} onOpenChange={setOpen}>
                    <CommandInput placeholder="Type a command or search..." />
                    <CommandList>
                        <CommandEmpty>No results found.</CommandEmpty>
                        {Object.entries(groupedActions).map(([group, actions]) => (
                             <CommandGroup key={group} heading={group}>
                                {actions.map(action => (
                                    <CommandItem key={action.id} onSelect={() => runCommand(action.action)}>
                                        {action.label}
                                    </CommandItem>
                                ))}
                            </CommandGroup>
                        ))}
                    </CommandList>
                </CommandDialog>
            </>
        </ClientOnly>
    );
}
