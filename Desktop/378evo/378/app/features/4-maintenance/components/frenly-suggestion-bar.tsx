
"use client";

import { useEffect, useState, useMemo } from "react";
import { useAuditStore } from "@/hooks/use-audit-store";
import { getFrenlySuggestion, type FrenlySuggestion } from "@/app/actions/frenly.actions";
import { Button } from "@/components/ui/button";
import { BotIcon, CheckIcon, XIcon, Loader2Icon } from "@/components/ui/icons";
import { AnimatePresence, motion } from "framer-motion";

interface FrenlySuggestionBarProps {
  onAccept: (action: FrenlySuggestion['action'], details?: any) => void;
}

export function FrenlySuggestionBar({ onAccept }: FrenlySuggestionBarProps) {
  const [suggestion, setSuggestion] = useState<FrenlySuggestion | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isVisible, setIsVisible] = useState(false);
  const [dismissedSuggestionIds, setDismissedSuggestionIds] = useState<string[]>([]);

  const appState = useAuditStore(state => ({
    sourceFileContent: !!state.activeCase?.sourceFileContent,
    analysisResult: state.activeCase?.analysisResult,
    rules: state.activeCase?.rules || [],
  }));
  
  // Create a stable dependency for the effect
  const appStateJson = JSON.stringify(appState);

  useEffect(() => {
    setIsLoading(true);
    const currentAppState = JSON.parse(appStateJson);
    getFrenlySuggestion(currentAppState)
      .then(sugg => {
        if (sugg.action !== 'none' && !dismissedSuggestionIds.includes(sugg.id)) {
          setSuggestion(sugg);
          setIsVisible(true);
        } else {
          setSuggestion(null);
          setIsVisible(false);
        }
      })
      .finally(() => setIsLoading(false));
  }, [appStateJson, dismissedSuggestionIds]);

  const handleAccept = () => {
    if (suggestion) {
      onAccept(suggestion.action, suggestion.details);
      handleDismiss(); // Also dismiss after accepting
    }
  };

  const handleDismiss = () => {
    if (suggestion?.id) {
        setDismissedSuggestionIds(prev => [...prev, suggestion.id]);
    }
    setIsVisible(false);
  };
  
  if (isLoading) {
      return (
        <div className="absolute top-0 left-1/2 -translate-x-1/2 p-2 text-center text-sm text-muted-foreground">
            <Loader2Icon className="h-4 w-4 animate-spin inline-block mr-2"/>
            Frenly is thinking...
        </div>
      )
  }

  return (
    <AnimatePresence>
      {isVisible && suggestion && (
        <motion.div
          initial={{ y: -80, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -80, opacity: 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          className="absolute top-2 left-1/2 -translate-x-1/2 w-full max-w-2xl z-20"
        >
          <div className="bg-card border rounded-lg shadow-lg p-3 flex items-center gap-4">
            <div className="p-2 bg-primary/10 rounded-full">
                <BotIcon className="h-6 w-6 text-primary" />
            </div>
            <div className="flex-grow">
                <h4 className="font-bold text-sm">{suggestion.title}</h4>
                <p className="text-xs text-muted-foreground">{suggestion.description}</p>
            </div>
            <div className="flex items-center gap-2">
                <Button size="sm" onClick={handleAccept}>
                    <CheckIcon className="h-4 w-4 mr-1.5"/>
                    Accept
                </Button>
                 <Button size="sm" variant="ghost" onClick={handleDismiss}>
                    <XIcon className="h-4 w-4 mr-1.5"/>
                    Dismiss
                </Button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
