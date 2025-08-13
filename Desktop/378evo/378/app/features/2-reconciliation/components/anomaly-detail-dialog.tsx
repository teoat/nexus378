
"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Anomaly, AnomalyStatus } from "@/types/types";
import { Badge } from "@/components/ui/badge";
import { formatCurrency, parseDate } from "@/lib/utils";
import { format } from "date-fns";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { useState, useEffect, useCallback } from "react";
import { generateSuggestedNote } from "@/app/actions/suggestion.actions";
import { Loader2Icon, SparklesIcon } from "@/components/ui/icons";
import { RiskBadge } from "@/components/risk-badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { produce } from "immer";
import { Label } from "@/components/ui/label";

interface AnomalyDetailDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  anomaly: Anomaly | null;
  onUpdateAnomalies: (ids: string[], updates: Partial<Anomaly>, oldValues?: Anomaly[]) => void;
  currency: string;
  thousandSeparator: ',' | '.';
}

export function AnomalyDetailDialog({ isOpen, onOpenChange, anomaly, onUpdateAnomalies, currency, thousandSeparator }: AnomalyDetailDialogProps) {
    const [currentAnomaly, setCurrentAnomaly] = useState<Anomaly | null>(anomaly);
    const [note, setNote] = useState(anomaly?.notes || "");
    const [isGeneratingNote, setIsGeneratingNote] = useState(false);

    useEffect(() => {
        if (anomaly) {
            setCurrentAnomaly(anomaly);
            setNote(anomaly.notes || "");
        }
    }, [anomaly]);
    
    const handleStatusChange = (status: AnomalyStatus) => {
        if (currentAnomaly) {
            const updatedAnomaly = { ...currentAnomaly, status };
            setCurrentAnomaly(updatedAnomaly);
            onUpdateAnomalies([currentAnomaly.id], { status }, [currentAnomaly]);
        }
    };

    const handleNoteSave = () => {
         if (currentAnomaly && note !== currentAnomaly.notes) {
            onUpdateAnomalies([currentAnomaly.id], { notes: note }, [currentAnomaly]);
        }
    }

    const handleGenerateNote = async () => {
        if (!currentAnomaly) return;
        setIsGeneratingNote(true);
        try {
            const suggestion = await generateSuggestedNote({ anomaly: currentAnomaly });
            setNote(prev => prev ? `${prev}\n${suggestion}` : suggestion);
        } catch (error) {
            console.error("Failed to generate note:", error);
        } finally {
            setIsGeneratingNote(false);
        }
    };

    if (!currentAnomaly) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Anomaly Details</DialogTitle>
          <DialogDescription>
            Review, annotate, and adjudicate the selected anomaly.
          </DialogDescription>
        </DialogHeader>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-4">
            <div className="md:col-span-2 space-y-4">
                <p className="text-sm text-muted-foreground">{currentAnomaly.description}</p>
                <div className="flex flex-wrap gap-2">
                    <Badge variant="outline">{currentAnomaly.category}</Badge>
                    <Badge variant="secondary">{currentAnomaly.reason}</Badge>
                </div>
                 <Separator />
                <div className="space-y-2">
                    <Label htmlFor="notes">Auditor Notes</Label>
                    <Textarea 
                        id="notes" 
                        value={note}
                        onChange={(e) => setNote(e.target.value)}
                        onBlur={handleNoteSave}
                        placeholder="Add your notes here..."
                        rows={4}
                    />
                    <div className="flex justify-end">
                        <Button size="sm" variant="ghost" onClick={handleGenerateNote} disabled={isGeneratingNote}>
                            {isGeneratingNote ? <Loader2Icon className="h-4 w-4 mr-2 animate-spin"/> : <SparklesIcon className="h-4 w-4 mr-2"/>}
                            Suggest Note
                        </Button>
                    </div>
                </div>
                <div className="space-y-2">
                    <h4 className="text-sm font-semibold">Original Data</h4>
                    <ScrollArea className="h-40 bg-muted rounded-md p-2">
                        <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(currentAnomaly.original, null, 2)}</pre>
                    </ScrollArea>
                </div>
            </div>
            <div className="space-y-4">
                <div className="p-4 border rounded-lg space-y-3">
                     <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Risk Score</span>
                        <RiskBadge score={currentAnomaly.riskScore}/>
                     </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Amount</span>
                        <span className="font-mono">{currentAnomaly.amount}</span>
                     </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Date</span>
                        <span className="text-sm">{format(parseDate(currentAnomaly.date) || new Date(), 'PPP')}</span>
                     </div>
                </div>
                <div className="space-y-2">
                    <Label>Status</Label>
                    <div className="flex gap-2">
                        <Button variant={currentAnomaly.status === 'Unreviewed' ? 'default' : 'outline'} size="sm" onClick={() => handleStatusChange('Unreviewed')}>Unreviewed</Button>
                        <Button variant={currentAnomaly.status === 'Reviewed' ? 'default' : 'outline'} size="sm" onClick={() => handleStatusChange('Reviewed')}>Reviewed</Button>
                        <Button variant={currentAnomaly.status === 'Flagged' ? 'destructive' : 'outline'} size="sm" onClick={() => handleStatusChange('Flagged')}>Flagged</Button>
                    </div>
                </div>
                 <div className="space-y-2">
                    <h4 className="text-sm font-semibold">Audit History</h4>
                    <ScrollArea className="h-32">
                        <div className="space-y-3 text-xs">
                        {currentAnomaly.auditHistory.map((log, index) => (
                            <div key={index}>
                                <p className="font-medium">{log.user} - {log.action}</p>
                                <p className="text-muted-foreground">{format(new Date(log.timestamp), 'PPpp')}</p>
                                <p className="text-muted-foreground italic">"{log.details}"</p>
                            </div>
                        ))}
                        </div>
                    </ScrollArea>
                 </div>
            </div>
        </div>
        <DialogFooter>
          <Button onClick={() => onOpenChange(false)}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
