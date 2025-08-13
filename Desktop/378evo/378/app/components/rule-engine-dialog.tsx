
"use client";

import { useState, useEffect } from 'react';
import { Rule, ConditionSchema, RuleSchema, ActionSchema } from '@/types/types';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Label } from './ui/label';
import { PlusCircleIcon, Trash2Icon, XIcon } from './ui/icons';
import { Switch } from './ui/switch';
import { v4 as uuidv4 } from 'uuid';
import { produce } from 'immer';
import { ScrollArea } from './ui/scroll-area';
import { isEqual } from 'lodash';
import { useGamificationStore, AchievementId } from '@/store/gamification.store';
import { z } from 'zod';

interface RuleEngineDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  rules: Rule[];
  onSave: (rules: Rule[]) => void;
  onUnlockAchievement: (id: AchievementId) => void;
}

const emptyCondition = (): z.infer<typeof ConditionSchema> => ({
  id: uuidv4(),
  field: "category",
  operator: "equals",
  value: "",
});

const emptyRule = (): Rule => ({
  id: uuidv4(),
  name: "New Rule",
  conditions: [emptyCondition()],
  action: { status: "Reviewed" },
  isEnabled: true,
  versionHistory: [],
});

export default function RuleEngineDialog({ isOpen, onOpenChange, rules: initialRules, onSave, onUnlockAchievement }: RuleEngineDialogProps) {
  const [rules, setRules] = useState<Rule[]>([]);

  useEffect(() => {
    // Deep copy initial rules to avoid mutation issues
    setRules(JSON.parse(JSON.stringify(initialRules)));
  }, [initialRules, isOpen]);

  const handleAddRule = () => {
    setRules(produce(draft => {
      draft.push(emptyRule());
    }));
  };

  const handleDeleteRule = (ruleId: string) => {
    setRules(rules.filter(r => r.id !== ruleId));
  };

  const handleRuleChange = (ruleId: string, updates: Partial<Rule>) => {
    setRules(produce(draft => {
      const rule = draft.find(r => r.id === ruleId);
      if (rule) {
        Object.assign(rule, updates);
      }
    }));
  };
  
  const handleActionChange = (ruleId: string, updates: Partial<z.infer<typeof ActionSchema>>) => {
      setRules(produce(draft => {
          const rule = draft.find(r => r.id === ruleId);
          if (rule) {
              Object.assign(rule.action, updates);
          }
      }));
  }

  const handleConditionChange = (ruleId: string, conditionId: string, updates: Partial<z.infer<typeof ConditionSchema>>) => {
    setRules(produce(draft => {
      const rule = draft.find(r => r.id === ruleId);
      if (rule) {
        const condition = rule.conditions.find(c => c.id === conditionId);
        if (condition) {
          Object.assign(condition, updates);
        }
      }
    }));
  };
  
  const handleAddCondition = (ruleId: string) => {
    setRules(produce(draft => {
      const rule = draft.find(r => r.id === ruleId);
      if (rule) {
        rule.conditions.push(emptyCondition());
      }
    }));
  };
  
  const handleDeleteCondition = (ruleId: string, conditionId: string) => {
    setRules(produce(draft => {
      const rule = draft.find(r => r.id === ruleId);
      if (rule) {
        rule.conditions = rule.conditions.filter(c => c.id !== conditionId);
      }
    }));
  }

  const handleSave = () => {
     const finalRules = produce(rules, draft => {
        draft.forEach(newRule => {
            const originalRule = initialRules.find(r => r.id === newRule.id);
            if (originalRule && !isEqual(originalRule, newRule)) {
                if (!newRule.versionHistory) {
                    newRule.versionHistory = [];
                }
                const { versionHistory, ...previousVersion } = originalRule;
                newRule.versionHistory.push({ ...previousVersion, modifiedAt: new Date().toISOString() });
            }
        });
     });

    if (finalRules.length > initialRules.length) {
        onUnlockAchievement('FIRST_RULE');
    }
    onSave(finalRules);
    onOpenChange(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Auto-Adjudication Rule Engine</DialogTitle>
          <DialogDescription>
            Create rules to automatically change the status of anomalies that meet specific criteria. Rules are applied in order.
          </DialogDescription>
        </DialogHeader>
        <ScrollArea className="flex-grow pr-6 -mr-6">
          <div className="space-y-4 py-4">
            {rules.map((rule, ruleIndex) => (
              <div key={rule.id} className="border p-4 rounded-lg space-y-4 bg-muted/50 relative">
                 <div className="absolute top-2 right-2 flex items-center gap-2">
                    <Switch
                        checked={rule.isEnabled}
                        onCheckedChange={(checked) => handleRuleChange(rule.id, { isEnabled: checked })}
                    />
                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handleDeleteRule(rule.id)}>
                        <XIcon className="h-4 w-4"/>
                    </Button>
                </div>
                <div className="flex items-center gap-4">
                    <Label>Rule Name</Label>
                    <Input 
                        value={rule.name}
                        onChange={(e) => handleRuleChange(rule.id, { name: e.target.value })}
                        className="h-8"
                    />
                </div>
                
                <div className="space-y-2">
                    <Label className="text-xs font-semibold">IF</Label>
                    {rule.conditions.map((condition, condIndex) => (
                        <div key={condition.id} className="flex items-center gap-2 pl-4">
                            <Select value={condition.field} onValueChange={(v) => handleConditionChange(rule.id, condition.id, { field: v as any })}>
                                <SelectTrigger className="h-8 w-40 text-xs"><SelectValue /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="category">Category</SelectItem>
                                    <SelectItem value="description">Description</SelectItem>
                                    <SelectItem value="reason">Reason</SelectItem>
                                    <SelectItem value="amount">Amount</SelectItem>
                                    <SelectItem value="riskScore">Risk Score</SelectItem>
                                </SelectContent>
                            </Select>
                             <Select value={condition.operator} onValueChange={(v) => handleConditionChange(rule.id, condition.id, { operator: v as any })}>
                                <SelectTrigger className="h-8 w-40 text-xs"><SelectValue /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="equals">is equal to</SelectItem>
                                    <SelectItem value="not_equals">is not equal to</SelectItem>
                                    <SelectItem value="contains">contains</SelectItem>
                                    <SelectItem value="greater_than">is greater than</SelectItem>
                                    <SelectItem value="less_than">is less than</SelectItem>
                                </SelectContent>
                            </Select>
                            <Input
                                value={condition.value}
                                onChange={(e) => handleConditionChange(rule.id, condition.id, { value: e.target.value })}
                                placeholder="Value..."
                                className="h-8 text-xs"
                                type={condition.field === 'amount' || condition.field === 'riskScore' ? 'number' : 'text'}
                            />
                            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handleDeleteCondition(rule.id, condition.id)}>
                                <Trash2Icon className="h-4 w-4 text-destructive"/>
                            </Button>
                        </div>
                    ))}
                    <Button variant="outline" size="sm" className="ml-4" onClick={() => handleAddCondition(rule.id)}>
                        <PlusCircleIcon className="mr-2 h-4 w-4"/> AND
                    </Button>
                </div>

                <div className="space-y-2">
                    <Label className="text-xs font-semibold">THEN</Label>
                     <div className="grid grid-cols-2 gap-x-4 gap-y-2 pl-4">
                        <div className="flex items-center gap-2">
                            <Label className="text-xs w-24">Set status to</Label>
                            <Select value={rule.action.status || ''} onValueChange={(v) => handleActionChange(rule.id, { status: v as any })}>
                                 <SelectTrigger className="h-8 w-48 text-xs"><SelectValue placeholder="-- Unchanged --"/></SelectTrigger>
                                 <SelectContent>
                                    <SelectItem value="Reviewed">Reviewed</SelectItem>
                                    <SelectItem value="Flagged">Flagged</SelectItem>
                                    <SelectItem value="Unreviewed">Unreviewed</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="flex items-center gap-2">
                           <Label className="text-xs w-24">Set risk score to</Label>
                           <Input
                                value={rule.action.riskScore || ''}
                                onChange={(e) => handleActionChange(rule.id, { riskScore: e.target.value === '' ? undefined : Number(e.target.value) })}
                                type="number"
                                placeholder="0-100"
                                className="h-8 text-xs"
                           />
                        </div>
                        <div className="flex items-center gap-2">
                           <Label className="text-xs w-24">Set category to</Label>
                            <Input
                                value={rule.action.category || ''}
                                onChange={(e) => handleActionChange(rule.id, { category: e.target.value })}
                                placeholder="e.g., Travel"
                                className="h-8 text-xs"
                           />
                        </div>
                        <div className="flex items-center gap-2">
                            <Label className="text-xs w-24">Add note</Label>
                            <Input
                                value={rule.action.note || ''}
                                onChange={(e) => handleActionChange(rule.id, { note: e.target.value })}
                                placeholder="e.g., Auto-reviewed"
                                className="h-8 text-xs"
                           />
                        </div>
                    </div>
                </div>

              </div>
            ))}
             <Button variant="outline" onClick={handleAddRule}>
                <PlusCircleIcon className="mr-2 h-4 w-4"/> Add Rule
            </Button>
          </div>
        </ScrollArea>
        <DialogFooter>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={handleSave}>Save Rules</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
