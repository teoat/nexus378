
"use client";

import { useGamificationStore, achievements } from "@/store/gamification.store";
import { AchievementCard } from "@/components/ui/achievement-card";
import { Progress } from "@/components/ui/progress";
import { TrophyIcon } from "../ui/icons";

export function AchievementsView() {
    const { achievements, getProgress } = useGamificationStore();
    const progress = getProgress();
    const achievementList = Object.values(achievements);

    return (
        <div className="space-y-6">
             <div>
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                        <TrophyIcon className="h-5 w-5 text-yellow-500" />
                        <p className="text-sm font-semibold">Achievements Progress</p>
                    </div>
                    <p className="text-sm font-mono">{progress.unlockedCount} / {progress.totalCount}</p>
                </div>
                <Progress value={progress.percentage} className="h-2" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {achievementList.map(ach => (
                    <AchievementCard 
                        key={ach.name}
                        name={ach.name}
                        description={ach.description}
                        unlocked={ach.unlocked}
                    />
                ))}
            </div>
        </div>
    )
}

  