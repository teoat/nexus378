
"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency } from "@/lib/utils";
import type { MatchedTransaction, UnmatchedBankTransaction } from "@/types/types";

interface ReconciliationSummaryProps {
  matched: MatchedTransaction[];
  unmatchedExpenses: any[];
  unmatchedBank: UnmatchedBankTransaction[];
  currency: string;
  thousandSeparator: ',' | '.';
}

function SummaryCard({ title, value, count }: { title: string; value: number; count: number }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{count} transactions</p>
      </CardContent>
    </Card>
  );
}

export function ReconciliationSummary({
  matched,
  unmatchedExpenses,
  unmatchedBank,
  currency,
  thousandSeparator,
}: ReconciliationSummaryProps) {

  const matchedValue = matched.reduce((acc, tx) => acc + tx.expenseAmount, 0);
  const unmatchedExpensesValue = unmatchedExpenses.reduce((acc, tx) => acc + (tx.debit || 0), 0);
  const unmatchedBankValue = unmatchedBank.reduce((acc, tx) => acc + tx.amount, 0);

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <SummaryCard
        title="Matched Transactions"
        value={matchedValue}
        count={matched.length}
      />
      <SummaryCard
        title="Unmatched Expenses"
        value={unmatchedExpensesValue}
        count={unmatchedExpenses.length}
      />
      <SummaryCard
        title="Unmatched Bank Transactions"
        value={unmatchedBankValue}
        count={unmatchedBank.length}
      />
    </div>
  );
}
