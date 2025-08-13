
"use client";

import { useAuditStore } from "@/hooks/use-audit-store";
import { FileUploader } from "./file-uploader";
import { Button } from "@/components/ui/button";
import { SparklesIcon } from "@/components/ui/icons";
import { useToast } from "@/hooks/use-toast";
import { ingestFile } from "../actions/ingest.actions";
import { useCallback } from "react";

interface IngestionViewProps {
    onAnalysisRequest: () => void;
}

export default function IngestionView({ onAnalysisRequest }: IngestionViewProps) {
    const { activeCase, setSourceFile, setBankFile, setColumnMapping, setBankColumnMapping, createCase } = useAuditStore();
    const { toast } = useToast();
    
    const handleFileIngest = useCallback(async (fileType: 'source' | 'bank', fileContent: string) => {
        try {
            // Ensure a case exists before ingesting a file
            if (!activeCase) {
                createCase();
            }

            const result = await ingestFile(fileType, fileContent);
            
            if (result.fileType === 'source') {
                setSourceFile(result.jsonContent, JSON.parse(result.jsonContent).length);
                setColumnMapping(result.mapping);
            } else {
                setBankFile(result.jsonContent, JSON.parse(result.jsonContent).length);
                setBankColumnMapping(result.mapping);
            }
        } catch (e: any) {
            console.error(e);
            toast({
                variant: 'destructive',
                title: 'File Processing Error',
                description: e.message || 'An unexpected error occurred during server-side ingestion.',
            });
        }
    }, [activeCase, createCase, setSourceFile, setBankFile, setColumnMapping, setBankColumnMapping, toast]);
    
    return (
        <div className="flex flex-col items-center gap-6">
            <FileUploader onFileIngest={handleFileIngest} />
             <Button size="lg" onClick={onAnalysisRequest} disabled={!activeCase?.sourceFileContent}>
                <SparklesIcon className="mr-2 h-4 w-4" />
                Run Analysis
            </Button>
        </div>
    );
}
