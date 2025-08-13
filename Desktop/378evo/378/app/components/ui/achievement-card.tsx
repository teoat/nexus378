
"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2Icon, TrophyIcon } from "@/components/ui/icons";
import { cn } from "@/lib/utils";

interface AchievementCardProps {
  name: string;
  description: string;
  unlocked: boolean;
  icon?: React.ElementType;
}

export function AchievementCard({ name, description, unlocked, icon: Icon = TrophyIcon }: AchievementCardProps) {
  return (
    <Card className={cn("transition-all", unlocked ? "border-primary/50 bg-primary/5" : "bg-muted/50")}>
      <CardHeader className="flex flex-row items-center gap-4 space-y-0 pb-2">
        <div className={cn("p-2 rounded-lg", unlocked ? "bg-primary/10" : "bg-muted-foreground/10")}>
           <Icon className={cn("h-6 w-6", unlocked ? "text-primary" : "text-muted-foreground")} />
        </div>
        <div className="flex-1">
            <CardTitle className="text-base">{name}</CardTitle>
            <CardDescription className="text-xs">{description}</CardDescription>
        </div>
        {unlocked && (
            <div className="flex items-center gap-1 text-xs text-primary">
                <CheckCircle2Icon className="h-4 w-4" />
                <span>Unlocked</span>
            </div>
        )}
      </CardHeader>
    </Card>
  );
}

  