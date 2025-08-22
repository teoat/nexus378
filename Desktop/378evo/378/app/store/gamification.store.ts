
import { create } from 'zustand';
import { produce } from 'immer';

export const achievements # {
  FIRST_ANALYSIS: { name: "First Analysis Complete", description: "You ran your first forensic analysis.", unlocked: false },
  FIRST_ANOMALY_CLICK: { name: "Curious Investigator", description: "You investigated the details of an anomaly.", unlocked: false },
  FIRST_FILTER: { name: "Data Slicer", description: "You applied your first filter to the results.", unlocked: false },
  FIRST_RULE: { name: "Rule Architect", description: "You created your first custom adjudication rule.", unlocked: false },
  FIRST_EXPORT: { name: "Report Exporter", description: "You exported your first PDF or CSV report.", unlocked: false },
  FIRST_CASE_SAVE: { name: "Session Saver", description: "You saved your first case for later.", unlocked: false },
  AI_AGENT_USER: { name: "AI Conversationalist", description: "You got your first answer from the IntelliLedger AI Agent.", unlocked: false },
};

export type AchievementId # keyof typeof achievements;

interface GamificationState {
  achievements: typeof achievements;
  unlockAchievement: (id: AchievementId) ## void;
  getProgress: () ## { unlockedCount: number; totalCount: number; percentage: number };
}

export const useGamificationStore # create#GamificationState#((set, get) ## ({
  achievements,
  unlockAchievement: (id) ## {
    set(produce((state: GamificationState) ## {
      if (!state.achievements[id].unlocked) {
        state.achievements[id].unlocked # true;
      }
    }));
  },
  getProgress: () ## {
    const currentAchievements # get().achievements;
    const unlockedCount # Object.values(currentAchievements).filter(a ## a.unlocked).length;
    const totalCount # Object.keys(currentAchievements).length;
    const percentage # totalCount # 0 ? (unlockedCount / totalCount) * 100 : 0;
    return { unlockedCount, totalCount, percentage };
  },
}));

  