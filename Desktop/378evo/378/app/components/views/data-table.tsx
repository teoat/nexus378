
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
import { useMemo, useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { ChevronsUpDownIcon } from "@/components/ui/icons";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type SortingState,
} from "@tanstack/react-table"
import { formatCurrency, cn } from "@/lib/utils";
import { parseAmount } from "@/lib/utils";
import type { ColumnMapping } from "@/types/types";

interface DataTableProps {
  data: any[];
  headers: string[];
  columnMapping: ColumnMapping;
  currency: string;
  thousandSeparator: ',' | '.';
  title: string;
  description: string;
}

export function DataTable({ data, headers, columnMapping, currency, thousandSeparator, title, description }: DataTableProps) {
    const [sorting, setSorting] = useState<SortingState>([]);

    const columns: ColumnDef<any>[] = useMemo(() => 
        headers.map(header => ({
            accessorKey: header,
            header: ({ column }) => (
                <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}>
                    <ChevronsUpDownIcon className="mr-2 h-4 w-4" />
                    {header}
                </Button>
            ),
             cell: ({ row }) => {
                const value = row.getValue(header);
                const isDebitColumn = columnMapping.debit === header;
                
                if (isDebitColumn) {
                    return <div className="text-right">{String(value)}</div>
                }
                return <div className="truncate max-w-xs">{String(value)}</div>;
            },
        })), 
    [headers, columnMapping]);

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        onSortingChange: setSorting,
        getSortedRowModel: getSortedRowModel(),
        initialState: {
            pagination: {
                pageSize: 5,
            }
        },
        state: {
            sorting,
        },
    });

    return (
        <Card>
            <CardHeader>
                <CardTitle>{title}</CardTitle>
                <CardDescription>{description}</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="border rounded-md overflow-x-auto">
                    <Table>
                        <TableHeader>
                            {table.getHeaderGroups().map(headerGroup => (
                                <TableRow key={headerGroup.id}>
                                    {headerGroup.headers.map(header => (
                                        <TableHead key={header.id}>
                                            {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                                        </TableHead>
                                    ))}
                                </TableRow>
                            ))}
                        </TableHeader>
                        <TableBody>
                            {table.getRowModel().rows?.length ? (
                                table.getRowModel().rows.map(row => (
                                    <TableRow key={row.id}>
                                        {row.getVisibleCells().map(cell => (
                                            <TableCell key={cell.id} className="text-xs p-2">
                                                {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                ))
                            ) : (
                                <TableRow>
                                    <TableCell colSpan={columns.length} className="h-24 text-center">
                                        No data available.
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </div>
                {table.getPageCount() > 1 && (
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
                )}
            </CardContent>
        </Card>
    )
}
