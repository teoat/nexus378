
"use client";

import { useState, useRef, useMemo } from 'react';
import { Anomaly, RiskFilter, SavedFilterSet } from '@/types/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuLabel, DropdownMenuSeparator } from "@/components/ui/dropdown-menu";
import { Calendar } from '@/components/ui/calendar';
import { format, startOfDay, endOfDay, subDays } from 'date-fns';
import { CalendarIcon, ChevronDownIcon, XIcon } from '@/components/ui/icons';
import { cn } from '@/lib/utils';
import { Filters } from '@/hooks/use-audit-store';
import { AchievementId } from '@/store/gamification.store';
import { Separator } from '@/components/ui/separator';

const DateRangePresets = ({ onPresetSelect }: { onPresetSelect: (range: { from: Date, to: Date }) => void }) => {
    const today = new Date();
    const presets = [
        { label: "Last 7 Days", days: 7 },
        { label: "Last 30 Days", days: 30 },
        { label: "Last 90 Days", days: 90 },
    ];

    return (
        <div className="flex flex-col p-2 space-y-1">
            {presets.map(({ label, days }) => (
                <Button 
                    key={label} 
                    variant="ghost" 
                    className="justify-start"
                    onClick={() => onPresetSelect({ from: startOfDay(subDays(today, days - 1)), to: endOfDay(today) })}
                >
                    {label}
                </Button>
            ))}
        </div>
    )
};


interface FilterControlsProps {
    filters: Filters;
    onFiltersChange: <K extends keyof Filters>(key: K, value: Filters[K]) => void;
    onClearFilters: () => void;
    savedFilterSets: SavedFilterSet[];
    onSaveFilterSet: (name: string) => void;
    onLoadFilterSet: (filters: Filters) => void;
    onDeleteFilterSet: (name: string) => void;
    onUnlockAchievement: (id: AchievementId) => void;
    allAnomalies: Anomaly[];
}

export function FilterControls({
    filters,
    onFiltersChange,
    onClearFilters,
    savedFilterSets,
    onSaveFilterSet,
    onLoadFilterSet,
    onDeleteFilterSet,
    onUnlockAchievement,
    allAnomalies,
}: FilterControlsProps) {
    
    const [isSavePopoverOpen, setIsSavePopoverOpen] = useState(false);
    const [newFilterSetName, setNewFilterSetName] = useState("");
    const [descriptionInput, setDescriptionInput] = useState(filters.description);
    const debounceTimeout = useRef<NodeJS.Timeout | null>(null);

    const anomalyCategories = useMemo(() => {
        const categories = new Set(allAnomalies.map(row => row.category));
        return Array.from(categories);
    }, [allAnomalies]);

    const anomalyReasons = useMemo(() => {
        const reasons = new Set(allAnomalies.map(row => row.reason));
        return Array.from(reasons);
    }, [allAnomalies]);


    const handleFilterChange = <K extends keyof Filters>(key: K, value: Filters[K]) => {
        onFiltersChange(key, value);
        onUnlockAchievement('FIRST_FILTER');
    }

    const handleDescriptionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setDescriptionInput(value);
        if (debounceTimeout.current) {
            clearTimeout(debounceTimeout.current);
        }
        debounceTimeout.current = setTimeout(() => {
            handleFilterChange('description', value);
        }, 300); // 300ms debounce delay
    };

    const isAnyFilterActive = Object.values(filters).some(value => {
        if (value instanceof Date) return true;
        if (Array.isArray(value)) return value.length > 0;
        return value && value !== 'all' && value !== '';
    });
    
    const handleSaveSet = () => {
        if (newFilterSetName.trim()) {
            onSaveFilterSet(newFilterSetName.trim());
            setNewFilterSetName("");
            setIsSavePopoverOpen(false);
        }
    }

    return (
         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-4 items-end">
             <div className="space-y-1.5 col-span-1 md:col-span-2 lg:col-span-3 xl:col-span-1">
                <Label htmlFor="description-search">Search Description</Label>
                <Input
                    id="description-search"
                    placeholder="Filter by keyword..."
                    value={descriptionInput}
                    onChange={handleDescriptionChange}
                />
            </div>
            <div className="space-y-1.5">
                <Label htmlFor="date-range">Date Range</Label>
                <Popover>
                    <PopoverTrigger asChild>
                    <Button
                        id="date-range"
                        variant={"outline"}
                        className={cn(
                        "w-full justify-start text-left font-normal",
                        !filters.startDate && !filters.endDate && "text-muted-foreground"
                        )}
                    >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {filters.startDate ? (
                            filters.endDate ? (
                                `${format(filters.startDate, "LLL dd, y")} - ${format(filters.endDate, "LLL dd, y")}`
                            ) : (
                                format(filters.startDate, "LLL dd, y")
                            )
                        ) : (
                            <span>Pick a date range</span>
                        )}
                    </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0 flex" align="start">
                        <DateRangePresets onPresetSelect={(range) => {
                             handleFilterChange('startDate', range.from);
                             handleFilterChange('endDate', range.to);
                        }}/>
                        <Separator orientation="vertical" className="h-auto"/>
                        <Calendar
                            initialFocus
                            mode="range"
                            defaultMonth={filters.startDate || new Date()}
                            selected={{ from: filters.startDate!, to: filters.endDate! }}
                            onSelect={(range) => {
                                handleFilterChange('startDate', range?.from || null);
                                handleFilterChange('endDate', range?.to || null);
                            }}
                            numberOfMonths={2}
                        />
                    </PopoverContent>
                </Popover>
            </div>
            <div className="space-y-1.5">
                <Label>Amount Range</Label>
                <div className="flex items-center gap-2">
                     <Input
                        type="number"
                        placeholder="Min"
                        value={filters.minAmount}
                        onChange={(e) => handleFilterChange('minAmount', e.target.value)}
                        className="w-full"
                    />
                    <span className="text-muted-foreground">-</span>
                     <Input
                        type="number"
                        placeholder="Max"
                        value={filters.maxAmount}
                        onChange={(e) => handleFilterChange('maxAmount', e.target.value)}
                         className="w-full"
                    />
                </div>
            </div>
            <div className="space-y-1.5">
                <Label htmlFor="status-filter">Status</Label>
                <Select value={filters.status} onValueChange={(v: Anomaly['status'] | 'all') => handleFilterChange('status', v)}>
                    <SelectTrigger id="status-filter">
                        <SelectValue placeholder="Filter by status" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Statuses</SelectItem>
                        <SelectItem value="Unreviewed">Unreviewed</SelectItem>
                        <SelectItem value="Reviewed">Reviewed</SelectItem>
                        <SelectItem value="Flagged">Flagged</SelectItem>
                    </SelectContent>
                </Select>
            </div>
             <div className="space-y-1.5">
                <Label htmlFor="risk-filter">Risk</Label>
                <Select value={filters.risk} onValueChange={(v: RiskFilter) => handleFilterChange('risk', v)}>
                    <SelectTrigger id="risk-filter">
                        <SelectValue placeholder="Filter by risk" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Risks</SelectItem>
                        <SelectItem value="High">High</SelectItem>
                        <SelectItem value="Medium">Medium</SelectItem>
                        <SelectItem value="Low">Low</SelectItem>
                    </SelectContent>
                </Select>
            </div>
             <div className="space-y-1.5">
                <Label htmlFor="category-filter">Category</Label>
                <Select value={filters.category} onValueChange={(v) => handleFilterChange('category', v)}>
                    <SelectTrigger id="category-filter">
                        <SelectValue placeholder="Filter by category" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Categories</SelectItem>
                        {anomalyCategories.map(cat => (
                            <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>
             <div className="space-y-1.5">
                <Label htmlFor="reason-filter">Reason</Label>
                <Select value={filters.reason} onValueChange={(v) => handleFilterChange('reason', v)}>
                    <SelectTrigger id="reason-filter">
                        <SelectValue placeholder="Filter by reason" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Reasons</SelectItem>
                        {anomalyReasons.map(reason => (
                            <SelectItem key={reason} value={reason}>{reason}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>
             <div className="space-y-1.5">
                <Label htmlFor="notes-filter">Notes</Label>
                <Select value={filters.notes} onValueChange={(v) => handleFilterChange('notes', v as Filters['notes'])}>
                    <SelectTrigger id="notes-filter">
                        <SelectValue placeholder="Filter by notes" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Notes</SelectItem>
                        <SelectItem value="has_notes">Has Notes</SelectItem>
                        <SelectItem value="no_notes">No Notes</SelectItem>
                    </SelectContent>
                </Select>
            </div>
            <div className="flex gap-2 self-end">
                {isAnyFilterActive && (
                    <Button variant="ghost" onClick={onClearFilters}>
                        <XIcon className="mr-2 h-4 w-4"/>
                        Clear
                    </Button>
                )}
                 <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="outline" className="w-full">
                            Filter Sets
                            <ChevronDownIcon className="ml-2 h-4 w-4"/>
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                         <Popover open={isSavePopoverOpen} onOpenChange={setIsSavePopoverOpen}>
                            <PopoverTrigger asChild>
                                <Button variant="ghost" className="w-full" disabled={!isAnyFilterActive}>
                                    Save current filters...
                                </Button>
                            </PopoverTrigger>
                            <PopoverContent className="p-2 space-y-2">
                                <Input 
                                    placeholder="Filter set name..." 
                                    value={newFilterSetName}
                                    onChange={(e) => setNewFilterSetName(e.target.value)}
                                />
                                <Button onClick={handleSaveSet} className="w-full" size="sm">Save</Button>
                            </PopoverContent>
                        </Popover>
                        {savedFilterSets.length > 0 && <DropdownMenuSeparator />}
                        {savedFilterSets.map(set => (
                            <DropdownMenuItem key={set.name} className="flex justify-between items-center" onSelect={() => onLoadFilterSet(set.filters)}>
                                {set.name}
                                <Button variant="ghost" size="icon" className="h-6 w-6" onClick={(e) => {e.stopPropagation(); onDeleteFilterSet(set.name)}}><XIcon className="h-3 w-3"/></Button>
                            </DropdownMenuItem>
                        ))}
                         {savedFilterSets.length === 0 && (
                            <DropdownMenuLabel className="text-xs text-muted-foreground font-normal text-center py-2">
                                No saved sets.
                            </DropdownMenuLabel>
                        )}
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </div>
    )
}
