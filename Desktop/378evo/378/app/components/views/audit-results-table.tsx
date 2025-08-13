

"use client"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useState, useEffect, useMemo, memo, useCallback, lazy, Suspense, useRef } from "react";
import type { Anomaly, AnomalyStatus, AuditLog, MatchedTransaction, UnmatchedBankTransaction, Rule, RiskFilter } from "@/types/types";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuRadioGroup, DropdownMenuRadioItem, DropdownMenuLabel, DropdownMenuSeparator } from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { cn, formatCurrency } from "@/lib/utils";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { CalendarIcon, ChevronDownIcon, ChevronsUpDownIcon, DownloadIcon, FileTextIcon, XIcon, MessageSquareIcon, GavelIcon } from "@/components/ui/icons";
import { Input } from "@/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { format, startOfDay, endOfDay, subDays } from "date-fns";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
  type SortingState,
  type ColumnFiltersState,
  type VisibilityState,
  type RowSelectionState,
  getFilteredRowModel,
  getSortedRowModel,
  getPaginationRowModel,
} from "@tanstack/react-table"
import { RiskBadge } from "@/components/risk-badge";
import { Separator } from "@/components/ui/separator";
import { useAuditStore, type TableDensity, type ColumnSizing } from "@/hooks/use-audit-store";
import type { SavedFilterSet } from "@/features/3-analysis/components/client-only-anomaly-table";
import { useVirtualizer } from '@tanstack/react-virtual';
import { AchievementId } from "@/store/gamification.store";
import { Filters } from "@/hooks/use-audit-store";

const AnomalyDetailDialog = lazy(() => import('@/features/2-reconciliation/components/anomaly-detail-dialog').then(module => ({ default: module.AnomalyDetailDialog })));


interface AuditResultsTableProps {
  data: Anomaly[];
  currency: string;
  thousandSeparator: ',' | '.';
  onUpdateAnomalies: (ids: string[], updates: Partial<Anomaly>, oldValues?: Anomaly[]) => void;
  tableDensity: TableDensity;
  onTableDensityChange: (density: TableDensity) => void;
  columnSizing: ColumnSizing;
  onColumnSizingChange: (sizing: ColumnSizing) => void;
}

const AnomalyStatusBadge = memo(({ status, isAutoAdjudicated }: { status: Anomaly['status'], isAutoAdjudicated: boolean}) => {
    
    const badgeContent = (
      <>
        {isAutoAdjudicated && <GavelIcon className="h-3 w-3 mr-1.5" />}
        {status}
      </>
    )

    switch (status) {
        case "Reviewed":
            return <Badge variant="secondary" className="border-green-500/50">{badgeContent}</Badge>;
        case "Flagged":
            return <Badge variant="destructive">{badgeContent}</Badge>;
        default:
            return <Badge variant="outline">{badgeContent}</Badge>;
    }
});
AnomalyStatusBadge.displayName = 'AnomalyStatusBadge';

const getCategoryColor = (category: string) => {
    let hash = 0;
    for (let i = 0; i < category.length; i++) {
        hash = category.charCodeAt(i) + ((hash << 5) - hash);
    }
    const h = hash % 360;
    return `hsl(${h}, 70%, 50%)`;
}

const BulkActions = memo(({ table, onBulkUpdate, tableDensity, onTableDensityChange, columnSizing, onColumnSizingChange }: { table: ReturnType<typeof useReactTable<Anomaly>>, onBulkUpdate: (status: AnomalyStatus) => void, tableDensity: TableDensity, onTableDensityChange: (density: TableDensity) => void, columnSizing: ColumnSizing, onColumnSizingChange: (sizing: ColumnSizing) => void; }) => {
    const selectedCount = Object.keys(table.getState().rowSelection).length;
    const hasAnomalies = table.getCoreRowModel().rows.length > 0;

    if (selectedCount === 0 && !hasAnomalies) return null;

    return (
        <div className="flex items-center gap-2 mb-4">
            {selectedCount > 0 && (
                <>
                    <span className="text-sm text-muted-foreground">{selectedCount} selected</span>
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="outline" size="sm">
                                Bulk Actions
                                <ChevronDownIcon className="ml-2 h-4 w-4" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                            <DropdownMenuItem onSelect={() => onBulkUpdate("Unreviewed")}>Set status to Unreviewed</DropdownMenuItem>
                            <DropdownMenuItem onSelect={() => onBulkUpdate("Reviewed")}>Set status to Reviewed</DropdownMenuItem>
                            <DropdownMenuItem onSelect={() => onBulkUpdate("Flagged")}>Set status to Flagged</DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </>
            )}
             {hasAnomalies && (
                 <div className="ml-auto flex items-center gap-2">
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="outline" size="sm">View Options<ChevronDownIcon className="ml-2 h-4 w-4" /></Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                           <DropdownMenuLabel>Table Density</DropdownMenuLabel>
                           <DropdownMenuRadioGroup value={tableDensity} onValueChange={(v) => onTableDensityChange(v as TableDensity)}>
                                <DropdownMenuRadioItem value="comfortable">Comfortable</DropdownMenuRadioItem>
                                <DropdownMenuRadioItem value="default">Default</DropdownMenuRadioItem>
                                <DropdownMenuRadioItem value="compact">Compact</DropdownMenuRadioItem>
                           </DropdownMenuRadioGroup>
                           <DropdownMenuSeparator />
                           <DropdownMenuLabel>Column Sizing</DropdownMenuLabel>
                           <DropdownMenuRadioGroup value={columnSizing} onValueChange={(v) => onColumnSizingChange(v as ColumnSizing)}>
                               <DropdownMenuRadioItem value="auto">Fit to Container</DropdownMenuRadioItem>
                               <DropdownMenuRadioItem value="fitContent">Fit to Content</DropdownMenuRadioItem>
                           </DropdownMenuRadioGroup>
                           <DropdownMenuSeparator />
                           <DropdownMenuLabel>Visible Columns</DropdownMenuLabel>
                           {table.getAllColumns().filter(c => c.getCanHide()).map(column => (
                                <DropdownMenuItem key={column.id} className="capitalize" onSelect={(e) => { e.preventDefault(); column.toggleVisibility(!column.getIsVisible())}}>
                                    <Checkbox checked={column.getIsVisible()} className="mr-2"/>
                                    {column.id.replace(/_/g, ' ')}
                                </DropdownMenuItem>
                           ))}
                        </DropdownMenuContent>
                    </DropdownMenu>
                 </div>
            )}
        </div>
    );
});
BulkActions.displayName = 'BulkActions';


const PaginationControls = memo(({ table }: { table: ReturnType<typeof useReactTable<Anomaly>> }) => {
    if (table.getPageCount() <= 1) return null;

    return (
        <div className="flex items-center justify-end space-x-2 py-4">
            <Button
                variant="outline"
                size="sm"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
            >
                Previous
            </Button>
            <span className="text-sm text-muted-foreground">
                Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
            </span>
            <Button
                variant="outline"
                size="sm"
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
            >
                Next
            </Button>
        </div>
    );
});
PaginationControls.displayName = 'PaginationControls';

export const AuditResultsTable = memo(({ 
    data,
    currency, 
    thousandSeparator, 
    onUpdateAnomalies, 
    tableDensity, 
    onTableDensityChange, 
    columnSizing, 
    onColumnSizingChange, 
}: AuditResultsTableProps) => {
    
    const [sorting, setSorting] = useState<SortingState>([{ id: 'riskScore', desc: true }]);
    const [rowSelection, setRowSelection] = useState<RowSelectionState>({});
    const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
    
    const [isDetailViewOpen, setIsDetailViewOpen] = useState(false);
    const [activeAnomaly, setActiveAnomaly] = useState<Anomaly | null>(null);


    const handleStatusChange = useCallback((status: AnomalyStatus, rows: Anomaly[]) => {
        const ids = rows.map(r => r.id);
        const oldValues: Anomaly[] = rows.map(r => ({ ...r }));
        
        const updates = { status };

        onUpdateAnomalies(ids, updates, oldValues);
    }, [onUpdateAnomalies]);


    const columns: ColumnDef<Anomaly>[] = useMemo(() => [
        {
            id: 'select',
            header: ({ table }) => (
                <Checkbox
                    checked={table.getIsAllPageRowsSelected() || (table.getIsSomePageRowsSelected() && 'indeterminate')}
                    onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
                    aria-label="Select all"
                />
            ),
            cell: ({ row }) => (
                <Checkbox
                    checked={row.getIsSelected()}
                    onCheckedChange={(value) => row.toggleSelected(!!value)}
                    aria-label="Select row"
                />
            ),
            enableSorting: false,
            enableHiding: false,
            size: 40,
        },
        {
            accessorKey: 'riskScore',
            header: ({ column }) => <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}><ChevronsUpDownIcon className="mr-2 h-4 w-4" />Risk</Button>,
            cell: ({ row }) => <RiskBadge score={row.original.riskScore} />,
            size: 100,
            filterFn: (row, columnId, filterValue: RiskFilter) => {
                const score = row.original.riskScore;
                if (filterValue === 'all') return true;
                if (filterValue === 'High') return score > 80;
                if (filterValue === 'Medium') return score > 40 && score <= 80;
                if (filterValue === 'Low') return score > 0 && score <= 40;
                return true;
            }
        },
        {
            accessorKey: 'confidenceScore',
            header: ({ column }) => <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}><ChevronsUpDownIcon className="mr-2 h-4 w-4" />Confidence</Button>,
            cell: ({ row }) => <TooltipProvider>
                <Tooltip>
                    <TooltipTrigger>
                        <Badge variant={row.original.confidenceScore >= 80 ? 'default' : 'secondary'} className="w-16 flex justify-center">{row.original.confidenceScore}%</Badge>
                    </TooltipTrigger>
                    <TooltipContent><p>AI Confidence</p></TooltipContent>
                </Tooltip>
            </TooltipProvider>,
            enableHiding: false,
            size: 120,
        },
        {
            accessorKey: 'status',
            header: 'Status',
            cell: ({ row }) => {
                const anomaly = row.original;
                const isAutoAdjudicated = anomaly.auditHistory.some(log => log.user === "Rule Engine");
                return (
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm" className="flex gap-1 items-center -ml-3">
                                <AnomalyStatusBadge status={anomaly.status} isAutoAdjudicated={isAutoAdjudicated} />
                                <ChevronDownIcon className="h-3 w-3" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                            <DropdownMenuItem onClick={() => handleStatusChange("Unreviewed", [anomaly])}>Unreviewed</DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleStatusChange("Reviewed", [anomaly])}>Reviewed</DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleStatusChange("Flagged", [anomaly])}>Flagged</DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                )
            },
            size: 150,
        },
        {
            accessorKey: 'date',
            header: ({ column }) => <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}><ChevronsUpDownIcon className="mr-2 h-4 w-4" />Date</Button>,
            size: 120,
            filterFn: (row, columnId, filterValue: [Date | null, Date | null]) => {
                const date = new Date(row.original.date);
                const [start, end] = filterValue;
                if (start && date < start) return false;
                if (end && date > end) return false;
                return true;
            },
        },
        {
            accessorKey: 'description',
            header: 'Description',
            cell: ({row}) => <div className="truncate" title={row.original.description}>{row.original.description}</div>,
            size: 300,
        },
        {
            accessorKey: 'category',
            header: ({ column }) => <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}><ChevronsUpDownIcon className="mr-2 h-4 w-4" />Category</Button>,
            cell: ({ row }) => (
                <div className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full" style={{ backgroundColor: getCategoryColor(row.original.category) }}></span>
                    <Badge variant="outline">{row.original.category}</Badge>
                </div>
            ),
            size: 180,
        },
        {
            accessorKey: 'amount',
            header: ({ column }) => <div className="text-right"><Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}><ChevronsUpDownIcon className="mr-2 h-4 w-4" />Amount</Button></div>,
            cell: ({ row }) => <div className="text-right font-medium">{String(row.original.amount)}</div>,
            size: 120,
            filterFn: (row, columnId, filterValue: [string, string]) => {
                const amount = row.original.amount;
                const [min, max] = filterValue;
                if (min && amount < parseFloat(min)) return false;
                if (max && amount > parseFloat(max)) return false;
                return true;
            },
        },
        {
            accessorKey: 'reason',
            header: 'Reason',
            cell: ({row}) => <div className="truncate text-muted-foreground text-xs" title={row.original.reason}>{row.original.reason}</div>,
            size: 200,
        },
        {
            id: 'notes',
            accessorKey: 'notes',
            header: 'Notes',
            cell: ({row}) => <div className="truncate text-muted-foreground text-xs" title={row.original.notes}>{row.original.notes}</div>,
            enableHiding: true,
            filterFn: (row, columnId, filterValue: 'has_notes' | 'no_notes') => {
                 if (filterValue === 'has_notes') return !!row.original.notes;
                 if (filterValue === 'no_notes') return !row.original.notes;
                 return true;
            },
        },
        {
            id: 'actions',
            cell: ({ row }) => {
                const anomaly = row.original;
                return (
                    <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => { setActiveAnomaly(anomaly); setIsDetailViewOpen(true); }}>
                        <MessageSquareIcon className="h-4 w-4"/>
                    </Button>
                )
            },
            enableHiding: false,
            size: 50,
        },
    ], [handleStatusChange]);


    const table = useReactTable({
        data: data,
        columns,
        enableMultiSort: true,
        getCoreRowModel: getCoreRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        onSortingChange: setSorting,
        onRowSelectionChange: setRowSelection,
        onColumnVisibilityChange: setColumnVisibility,
        columnResizeMode: 'onChange',
        state: {
            sorting,
            rowSelection,
            columnVisibility,
        },
    });

    const tableContainerRef = useRef<HTMLDivElement>(null);
    const { rows } = table.getRowModel();

    const rowVirtualizer = useVirtualizer({
        count: rows.length,
        getScrollElement: () => tableContainerRef.current,
        estimateSize: () => 49, // Estimate row height
        overscan: 10,
    });

    const virtualRows = rowVirtualizer.getVirtualItems();

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            const selectedRows = table.getSelectedRowModel().rows.map(r => r.original);
            if(selectedRows.length === 0) return;

            if (event.key.toLowerCase() === 'r') {
                handleStatusChange('Reviewed', selectedRows);
                table.resetRowSelection();
            } else if (event.key.toLowerCase() === 'f') {
                handleStatusChange('Flagged', selectedRows);
                table.resetRowSelection();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, [table, handleStatusChange]);

    const handleBulkUpdate = useCallback((status: AnomalyStatus) => {
        const selectedRows = table.getSelectedRowModel().rows.map(r => r.original);
        if(selectedRows.length > 0) {
            handleStatusChange(status, selectedRows);
        }
        table.resetRowSelection();
    }, [table, handleStatusChange]);
    
    const densityClasses = {
        comfortable: 'p-4',
        default: 'p-2',
        compact: 'p-1 text-xs',
    }
    const cellClass = cn(densityClasses[tableDensity], "text-xs");


  return (
    <>
        <BulkActions 
            table={table}
            onBulkUpdate={handleBulkUpdate} 
            tableDensity={tableDensity}
            onTableDensityChange={onTableDensityChange}
            columnSizing={columnSizing}
            onColumnSizingChange={onColumnSizingChange}
        />
        <div ref={tableContainerRef} className="border rounded-md overflow-auto relative" style={{ height: '600px' }}>
            <Table className={cn(columnSizing === 'fitContent' && 'table-auto w-full')}>
                <TableHeader className="sticky top-0 bg-background z-10">
                    {table.getHeaderGroups().map(headerGroup => (
                        <TableRow key={headerGroup.id}>
                            {headerGroup.headers.map(header => (
                                <TableHead key={header.id} style={{ width: header.getSize() }} className="relative group whitespace-nowrap text-xs">
                                    {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                                    <div
                                        onMouseDown={header.getResizeHandler()}
                                        onTouchStart={header.getResizeHandler()}
                                        className={cn("absolute top-0 right-0 h-full w-1 bg-primary/20 cursor-col-resize select-none touch-none opacity-0 group-hover:opacity-100",
                                            {"bg-primary": header.column.getIsResizing()}
                                        )}
                                    />
                                </TableHead>
                            ))}
                        </TableRow>
                    ))}
                </TableHeader>
                <TableBody style={{ height: `${rowVirtualizer.getTotalSize()}px` }}>
                    {rows.length > 0 ? (
                        virtualRows.map(virtualRow => {
                            const row = rows[virtualRow.index];
                            return (
                                <TableRow 
                                    key={row.id} 
                                    data-state={row.getIsSelected() && "selected"}
                                    style={{ 
                                        position: 'absolute',
                                        top: 0,
                                        left: 0,
                                        width: '100%',
                                        height: `${virtualRow.size}px`,
                                        transform: `translateY(${virtualRow.start}px)`,
                                    }}
                                >
                                    {row.getVisibleCells().map(cell => (
                                        <TableCell key={cell.id} style={{ width: cell.column.getSize() }} className={cellClass}>
                                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            )
                        })
                    ) : (
                        <TableRow>
                            <TableCell colSpan={columns.length} className="h-24 text-center text-muted-foreground">
                                 {data.length === 0 ? "No analysis results to display. Please upload data and run an analysis." : "No results match your current filters. Try clearing or adjusting them."}
                            </TableCell>
                        </TableRow>
                    )}
                </TableBody>
            </Table>
        </div>
         <PaginationControls table={table} />
         <Suspense fallback={<div>Loading...</div>}>
            {activeAnomaly && (
                <AnomalyDetailDialog
                    isOpen={isDetailViewOpen}
                    onOpenChange={setIsDetailViewOpen}
                    anomaly={activeAnomaly}
                    onUpdateAnomalies={onUpdateAnomalies}
                    currency={currency}
                    thousandSeparator={thousandSeparator}
                />
            )}
         </Suspense>
    </>
  )
});
AuditResultsTable.displayName = 'AuditResultsTable';
