
import { produce } from 'immer';
import { Anomaly, Rule } from '@/types/types';

const checkCondition = (anomaly: Anomaly, condition: Rule['conditions'][0]): boolean => {
    const anomalyValue = anomaly[condition.field as keyof Anomaly];
    const conditionValue = condition.value;

    switch (condition.operator) {
        case 'equals':
            return String(anomalyValue).toLowerCase() === String(conditionValue).toLowerCase();
        case 'not_equals':
            return String(anomalyValue).toLowerCase() !== String(conditionValue).toLowerCase();
        case 'contains':
            return String(anomalyValue).toLowerCase().includes(String(conditionValue).toLowerCase());
        case 'greater_than':
            if (typeof anomalyValue === 'number' && typeof conditionValue === 'number') {
                return anomalyValue > conditionValue;
            }
            return false;
        case 'less_than':
            if (typeof anomalyValue === 'number' && typeof conditionValue === 'number') {
                return anomalyValue < conditionValue;
            }
            return false;
        default:
            return false;
    }
};

export const runRuleEngine = (anomalies: Anomaly[], rules: Rule[]): Anomaly[] => {
    if (!rules || rules.length === 0) {
        return anomalies;
    }

    const enabledRules = rules.filter(rule => rule.isEnabled);

    return produce(anomalies, draft => {
        draft.forEach(anomaly => {
            for (const rule of enabledRules) {
                const allConditionsMet = rule.conditions.every(condition => checkCondition(anomaly, condition));

                if (allConditionsMet) {
                    if (rule.action.status) {
                        anomaly.status = rule.action.status;
                    }
                    if (rule.action.category) {
                        anomaly.category = rule.action.category;
                    }
                    if (rule.action.riskScore !== undefined) {
                        anomaly.riskScore = rule.action.riskScore;
                    }
                    if (rule.action.note) {
                        anomaly.notes = anomaly.notes ? `${anomaly.notes}\n${rule.action.note}` : rule.action.note;
                    }
                    
                    anomaly.auditHistory.push({
                        timestamp: new Date().toISOString(),
                        user: "Rule Engine",
                        action: "Rule Applied",
                        details: `Rule "${rule.name}" triggered.`
                    });
                    
                    // A rule has been applied, so we stop processing more rules for this anomaly.
                    break;
                }
            }
        });
    });
};
