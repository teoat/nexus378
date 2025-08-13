
"use client";

import { AlertCircleIcon, InfoIcon, ShieldAlertIcon } from "@/components/ui/icons";
import { Badge } from "@/components/ui/badge";
import { memo } from "react";

export const RiskBadge = memo(({ score }: { score: number | undefined | null }) => {
  if (score === undefined || score === null) {
     return <Badge variant="outline" className="font-normal text-muted-foreground whitespace-nowrap">N/A</Badge>;
  }
  if (score > 80) {
    return (
      <Badge variant="destructive" className="flex items-center gap-1 whitespace-nowrap">
        <ShieldAlertIcon className="h-3 w-3" /> High
      </Badge>
    );
  }
  if (score > 40) {
    return (
      <Badge className="bg-yellow-500 hover:bg-yellow-500/80 text-black flex items-center gap-1 whitespace-nowrap">
        <AlertCircleIcon className="h-3 w-3" /> Medium
      </Badge>
    );
  }
   if (score > 0) {
    return (
        <Badge variant="secondary" className="flex items-center gap-1 whitespace-nowrap">
            <InfoIcon className="h-3 w-3" /> Low
        </Badge>
    );
  }
  return (
    <Badge variant="outline" className="font-normal text-muted-foreground whitespace-nowrap">
      N/A
    </Badge>
  );
});
RiskBadge.displayName = 'RiskBadge';
