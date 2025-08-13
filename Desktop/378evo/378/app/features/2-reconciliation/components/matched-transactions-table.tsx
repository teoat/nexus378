
"use client";

import { useMemo, useState } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ChevronsUpDownIcon } from "@/components/ui/icons";
import { formatCurrency } from "@/lib/utils";
import type { MatchedTransaction } from "@/types/types";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type SortingState,
} from "@tanstack/react-table";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface MatchedTransactionsTableProps {
  data: MatchedTransaction[];
  currency: string;
  thousandSeparator: ',' | '.';
}

export function MatchedTransactionsTable({ data, currency, thousandSeparator }: MatchedTransactionsTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);

  const columns: ColumnDef<MatchedTransaction>[] = useMemo(() => [
    {
        accessorKey: 'confidence',
        header: ({ column }) => <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}><ChevronsUpDownIcon className="mr-2 h-4 w-4" />Confidence</Button>,
        cell: ({ row }) => (
             <TooltipProvider>
                <Tooltip>
                    <TooltipTrigger>
                        <Badge variant={row.original.confidence >= 90 ? 'default' : 'secondary'}>{row.original.confidence}%</Badge>
                    </TooltipTrigger>
                    <TooltipContent><p>{row.original.matchMethod}</p></TooltipContent>
                </Tooltip>
            </TooltipProvider>
        ),
    },
    {
      accessorKey: 'expenseDate',
      header: 'Expense Date',
    },
    {
      accessorKey: 'expenseDescription',
      header: 'Expense Description',
      cell: ({ row }) => <div className="truncate max-w-xs">{row.original.expenseDescription}</div>,
    },
    {
      accessorKey: 'expenseAmount',
      header: () => <div className="text-right">Expense Amount</div>,
      cell: ({ row }) => <div className="text-right font-medium">{formatCurrency(row.original.expenseAmount, currency, thousandSeparator)}</div>,
    },
     {
      accessorKey: 'bankDate',
      header: 'Bank Date',
    },
    {
      accessorKey: 'bankDescription',
      header: 'Bank Description',
       cell: ({ row }) => <div className="truncate max-w-xs">{row.original.bankDescription}</div>,
    },
    {
      accessorKey: 'bankAmount',
      header: () => <div className="text-right">Bank Amount</div>,
      cell: ({ row }) => <div className="text-right font-medium">{formatCurrency(row.original.bankAmount, currency, thousandSeparator)}</div>,
    },
    {
        accessorKey: 'amountDifference',
        header: () => <div className="text-right">Diff</div>,
        cell: ({ row }) => <div className="text-right">{formatCurrency(row.original.amountDifference, currency, thousandSeparator)}</div>,
    }
  ], [currency, thousandSeparator]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    state: {
      sorting,
    },
    initialState: {
        pagination: {
            pageSize: 5
        }
    }
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Matched Transactions</CardTitle>
        <CardDescription>
          These transactions were successfully matched between your expense ledger and bank statements.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="border rounded-md">
          <Table>
            <TableHeader>
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <TableHead key={header.id}>
                      {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                    </TableHead>
                  ))}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {table.getRowModel().rows?.length ? (
                table.getRowModel().rows.map((row) => (
                  <TableRow key={row.id}>
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id} className="text-xs">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={columns.length} className="h-24 text-center">
                    No matched transactions found.
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
                <span className="text-sm text-muted-foreground">Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}</span>
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
  );
}
