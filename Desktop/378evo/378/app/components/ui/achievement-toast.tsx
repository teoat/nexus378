
import { TrophyIcon } from 'lucide-react';

interface AchievementToastProps {
  name: string;
  description: string;
}

export function AchievementToast({ name, description }: AchievementToastProps) {
  return (
    <div className="flex items-start">
      <TrophyIcon className="h-6 w-6 text-yellow-500 mr-4 mt-1" />
      <div className="flex-1">
        <p className="font-semibold">Achievement Unlocked!</p>
        <p className="text-sm font-medium">{name}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
    </div>
  );
}

  