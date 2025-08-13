
"use client";

import { Label } from "./ui/label";
import { Switch } from "./ui/switch";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./ui/tooltip";
import { InfoIcon, SparklesIcon } from "./ui/icons";

export interface AnalysisModuleConfig {
    aiFuzzyMatching: boolean;
    dataIntegrityAnalysis: boolean;
    anomalyEnrichment: boolean;
}

interface AnalysisModulesProps {
    config: AnalysisModuleConfig;
    onConfigChange: (config: AnalysisModuleConfig) => void;
}

export function AnalysisModules({ config, onConfigChange }: AnalysisModulesProps) {

    const handleToggle = (key: keyof AnalysisModuleConfig) => {
        onConfigChange({ ...config, [key]: !config[key] });
    };

    return (
        <div className="space-y-1">
            <h3 className="text-xs font-medium text-muted-foreground px-1">Analysis Modules</h3>
            <div className="p-2 space-y-3 rounded-lg border">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                         <SparklesIcon className="h-4 w-4 text-primary" />
                         <Label htmlFor="ai-fuzzy-matching" className="text-xs font-normal">AI Fuzzy Matching</Label>
                         <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger><InfoIcon className="h-3 w-3 text-muted-foreground"/></TooltipTrigger>
                                <TooltipContent><p>Uses AI to find matches based on semantic description similarity.</p></TooltipContent>
                            </Tooltip>
                         </TooltipProvider>
                    </div>
                    <Switch
                        id="ai-fuzzy-matching"
                        checked={config.aiFuzzyMatching}
                        onCheckedChange={() => handleToggle('aiFuzzyMatching')}
                    />
                </div>
                 <div className="flex items-center justify-between">
                     <div className="flex items-center gap-1.5">
                         <SparklesIcon className="h-4 w-4 text-primary" />
                         <Label htmlFor="data-integrity-analysis" className="text-xs font-normal">Data Integrity Analysis</Label>
                         <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger><InfoIcon className="h-3 w-3 text-muted-foreground"/></TooltipTrigger>
                                <TooltipContent><p>AI summary of Benford's Law and checks for data gaps.</p></TooltipContent>
                            </Tooltip>
                         </TooltipProvider>
                    </div>
                    <Switch
                        id="data-integrity-analysis"
                        checked={config.dataIntegrityAnalysis}
                        onCheckedChange={() => handleToggle('dataIntegrityAnalysis')}
                    />
                </div>
                 <div className="flex items-center justify-between">
                     <div className="flex items-center gap-1.5">
                         <SparklesIcon className="h-4 w-4 text-primary" />
                         <Label htmlFor="anomaly-enrichment" className="text-xs font-normal">Anomaly Enrichment</Label>
                         <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger><InfoIcon className="h-3 w-3 text-muted-foreground"/></TooltipTrigger>
                                <TooltipContent><p>AI extracts location, type, and entity data from descriptions.</p></TooltipContent>
                            </Tooltip>
                         </TooltipProvider>
                    </div>
                    <Switch
                        id="anomaly-enrichment"
                        checked={config.anomalyEnrichment}
                        onCheckedChange={() => handleToggle('anomalyEnrichment')}
                    />
                </div>
            </div>
        </div>
    );
}
