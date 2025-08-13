
"use client";

import { useMemo, useState } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ChevronsUpDownIcon, CheckIcon, XIcon } from "@/components/ui/icons";
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

interface ToleranceMatchesTableProps {
  data: MatchedTransaction[];
  currency: string;
  thousandSeparator: ',' | '.';
  onUpdateMatchData: (payload: { confirmedMatch: MatchedTransaction, rejectedMatch?: never } | { rejectedMatch: MatchedTransaction, confirmedMatch?: never }) => void;
}

export function ToleranceMatchesTable({ data, currency, thousandSeparator, onUpdateMatchData }: ToleranceMatchesTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);

  const handleConfirm = (match: MatchedTransaction) => {
    onUpdateMatchData({ confirmedMatch: match });
  }

  const handleReject = (match: MatchedTransaction) => {
    onUpdateMatchData({ rejectedMatch: match });
  }

  const columns: ColumnDef<MatchedTransaction>[] = useMemo(() => [
    {
      accessorKey: 'confidence',
      header: 'Confidence',
      cell: ({ row }) => <Badge variant="secondary">{row.original.confidence}%</Badge>,
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
      accessorKey: 'bankDescription',
      header: 'Bank Description',
      cell: ({ row }) => <div className="truncate max-w-xs">{row.original.bankDescription}</div>,
    },
    {
        id: 'actions',
        cell: ({ row }) => (
          <div className="flex gap-2">
            <Button size="icon" variant="outline" className="h-7 w-7 bg-green-500/10 text-green-700 hover:bg-green-500/20" onClick={() => handleConfirm(row.original)}>
              <CheckIcon className="h-4 w-4" />
            </Button>
            <Button size="icon" variant="outline" className="h-7 w-7 bg-red-500/10 text-red-700 hover:bg-red-500/20" onClick={() => handleReject(row.original)}>
              <XIcon className="h-4 w-4" />
            </Button>
          </div>
        )
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
  });

  if(data.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Tolerance Matches for Review</CardTitle>
        <CardDescription>
          These transactions were matched using looser date or amount tolerances. Please review and confirm or reject them.
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
                      <TableCell key={cell.id}>
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={columns.length} className="h-24 text-center">
                    No tolerance matches found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
