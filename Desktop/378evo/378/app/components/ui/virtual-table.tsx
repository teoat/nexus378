
"use client";

import React, { useState, useMemo, useEffect } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
  getSortedRowModel,
  getFilteredRowModel,
  SortingState,
  ColumnFiltersState,
} from '@tanstack/react-table';
import { ChevronsUpDownIcon, ArrowUpIcon, ArrowDownIcon } from './icons';
import { Button } from './button';
import { Input } from './input';

interface VirtualTableProps<TData, TValue> {
    data: TData[];
    columns: ColumnDef<TData, TValue>[];
    height?: number;
    rowHeight?: number;
}

export function VirtualTable<TData, TValue>({
    data,
    columns,
    height = 500,
    rowHeight = 48,
}: VirtualTableProps<TData, TValue>) {
    const [sorting, setSorting] = useState<SortingState>([]);
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
    const [globalFilter, setGlobalFilter] = useState('');

    const table = useReactTable({
        data,
        columns,
        state: {
            sorting,
            columnFilters,
            globalFilter,
        },
        onSortingChange: setSorting,
        onColumnFiltersChange: setColumnFilters,
        onGlobalFilterChange: setGlobalFilter,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
    });

    const parentRef = React.useRef<HTMLDivElement>(null);
    const { rows } = table.getRowModel();

    const rowVirtualizer = useVirtualizer({
        count: rows.length,
        getScrollElement: () => parentRef.current,
        estimateSize: () => rowHeight,
        overscan: 10,
    });
    
    const virtualRows = rowVirtualizer.getVirtualItems();

    return (
        <div>
            <div className="flex items-center py-4">
                <Input
                    placeholder="Filter all columns..."
                    value={globalFilter ?? ''}
                    onChange={(event) => setGlobalFilter(event.target.value)}
                    className="max-w-sm"
                />
            </div>
            <div ref={parentRef} style={{ height: `${height}px`, overflow: 'auto' }} className="border rounded-md">
                <Table style={{ height: `${rowVirtualizer.getTotalSize()}px` }}>
                    <TableHeader className="sticky top-0 bg-background z-10">
                        {table.getHeaderGroups().map(headerGroup => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map(header => (
                                    <TableHead key={header.id} style={{ width: header.getSize() }}>
                                        {header.isPlaceholder
                                            ? null
                                            : (
                                                <div
                                                    className={header.column.getCanSort() ? 'cursor-pointer select-none flex items-center' : ''}
                                                    onClick={header.column.getToggleSortingHandler()}
                                                >
                                                    {flexRender(header.column.columnDef.header, header.getContext())}
                                                    {{
                                                        asc: <ArrowUpIcon className="ml-2 h-4 w-4" />,
                                                        desc: <ArrowDownIcon className="ml-2 h-4 w-4" />,
                                                    }[header.column.getIsSorted() as string] ?? (header.column.getCanSort() ? <ChevronsUpDownIcon className="ml-2 h-4 w-4" /> : null)}
                                                </div>
                                            )}
                                    </TableHead>
                                ))}
                            </TableRow>
                        ))}
                    </TableHeader>
                    <TableBody>
                        {virtualRows.map(virtualRow => {
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
                                        <TableCell key={cell.id} style={{ width: cell.column.getSize() }}>
                                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
