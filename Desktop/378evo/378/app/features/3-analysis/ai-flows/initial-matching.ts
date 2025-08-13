
'use server';
/**
 * @fileOverview Performs the initial multi-pass matching of transactions.
 */

import { ai } from '@/ai/genkit';
import { z } from 'zod';
import { ColumnMappingSchema, TolerancesSchema, MatchedTransactionSchema, UnmatchedBankTransactionSchema } from '@/types/types';
import { v4 as uuidv4 } from 'uuid';
import { differenceInDays } from 'date-fns';
import { parseAmount, parseDate } from '@/lib/utils';

const MatchingInputSchema = z.object({
  sourceData: z.any().describe('The source ledger data as a JSON object.'),
  bankData: z.any().describe('The bank statement data as a JSON object.'),
  sourceMap: ColumnMappingSchema,
  bankMap: ColumnMappingSchema,
  tolerances: TolerancesSchema,
  thousandSeparator: z.enum([',', '.']),
});

const MatchingOutputSchema = z.object({
    matchedExpenses: z.array(MatchedTransactionSchema),
    unmatchedExpenses: z.any(),
    unmatchedBankTxns: z.array(UnmatchedBankTransactionSchema),
    benfordChartData: z.any(), // Simplified for now
});


export const initialMatchingFlow = ai.defineFlow(
  {
    name: 'initialMatchingFlow',
    inputSchema: MatchingInputSchema,
    outputSchema: MatchingOutputSchema,
  },
  async ({ sourceData, bankData, sourceMap, bankMap, tolerances, thousandSeparator }) => {
    
    // BENFORD'S LAW
    const benfordChartData = (() => {
        if (!sourceMap.debit) return [];
        const leadingDigits = sourceData.map((row: any) => {
            const value = String(row[sourceMap.debit!]);
            const firstDigit = value.trim().match(/^[1-9]/);
            return firstDigit ? parseInt(firstDigit[0], 10) : null;
        }).filter((digit: any): digit is number => digit !== null);

        if (leadingDigits.length === 0) return [];
        const digitCounts = leadingDigits.reduce((acc, digit) => {
            acc[digit] = (acc[digit] || 0) + 1;
            return acc;
        }, {} as Record<number, number>);
        const totalDigits = leadingDigits.length;
        const benfordDistribution = [0, 30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6];
        return Array.from({ length: 9 }, (_, i) => {
            const digit = i + 1;
            const actualPercentage = ((digitCounts[digit] || 0) / totalDigits) * 100;
            return { digit, actual: parseFloat(actualPercentage.toFixed(1)), expected: benfordDistribution[digit] };
        });
    })();

    // MULTI-PASS MATCHING
    let matchedExpenses: z.infer<typeof MatchedTransactionSchema>[] = [];
    let unmatchedExpenses = [...sourceData];
    let unmatchedBankTxnsPool = [...bankData];
    
    if (bankData.length > 0 && bankMap) {
        const toleranceTiers: [number, number, number][] = [
            [tolerances.date, tolerances.amount, 95],
            [tolerances.date + 2, tolerances.amount, 85],
            [tolerances.date, tolerances.amount + 0.5, 80],
            [tolerances.date + 3, tolerances.amount + 1.0, 70],
        ];

        for (const [dateTol, amountTol, confidence] of toleranceTiers) {
            if (unmatchedExpenses.length === 0 || unmatchedBankTxnsPool.length === 0) break;
            
            const passResult = runSingleMatchingPass(unmatchedExpenses, unmatchedBankTxnsPool, sourceMap, bankMap, { date: dateTol, amount: amountTol }, thousandSeparator, confidence);
            matchedExpenses.push(...passResult.matchedInPass);
            unmatchedExpenses = passResult.remainingExpenses;
            unmatchedBankTxnsPool = passResult.remainingBankTxns;
        }
    }
    
    const finalUnmatchedBankTxns: z.infer<typeof UnmatchedBankTransactionSchema>[] = unmatchedBankTxnsPool.map(txn => ({
        id: uuidv4(), date: txn[bankMap.date!], description: txn[bankMap.description!], amount: parseAmount(txn[bankMap.debit!], thousandSeparator)!, original: txn, status: "Unreviewed"
    }));

    return {
        matchedExpenses,
        unmatchedExpenses,
        unmatchedBankTxns: finalUnmatchedBankTxns,
        benfordChartData,
    };
  }
);


function runSingleMatchingPass(unmatchedExpenses: any[], unmatchedBankTxnsPool: any[], sourceMap: z.infer<typeof ColumnMappingSchema>, bankMap: z.infer<typeof ColumnMappingSchema>, tolerances: { date: number; amount: number; }, thousandSeparator: "," | ".", confidence: number) {
    const matchedInPass: z.infer<typeof MatchedTransactionSchema>[] = [];
    const remainingExpenses = [...unmatchedExpenses];
    const remainingBankTxns = [...unmatchedBankTxnsPool];

    for (let i = remainingExpenses.length - 1; i >= 0; i--) {
        const expense = remainingExpenses[i];
        if (!sourceMap.debit || !sourceMap.date) continue;
        const expenseAmount = parseAmount(expense[sourceMap.debit], thousandSeparator);
        const expenseDate = parseDate(expense[sourceMap.date]);
        if (expenseAmount === null || expenseDate === null) continue;

        const bankMatchIndex = remainingBankTxns.findIndex((bt) => {
            if (!bankMap.debit || !bankMap.date) return false;
            const bankAmount = parseAmount(bt[bankMap.debit], thousandSeparator);
            const bankDate = parseDate(bt[bankMap.date]);
            if (bankAmount === null || bankDate === null) return false;

            const dateDiff = Math.abs(differenceInDays(bankDate, expenseDate));
            const amountDiff = Math.abs(expenseAmount - bankAmount);
            const amountToleranceValue = expenseAmount * (tolerances.amount / 100);
            
            return dateDiff <= tolerances.date && amountDiff <= amountToleranceValue;
        });

        if (bankMatchIndex !== -1) {
            const bankMatch = remainingBankTxns[bankMatchIndex];
            if (!bankMap.debit || !bankMap.date || !bankMap.description) continue;
            const bankAmount = parseAmount(bankMatch[bankMap.debit], thousandSeparator)!;
            matchedInPass.push({ id: uuidv4(), expenseOriginal: expense, bankTxOriginal: bankMatch, expenseDate: expense[sourceMap.date!], expenseDescription: expense[sourceMap.description!], expenseAmount: expenseAmount, bankDate: bankMatch[bankMap.date], bankDescription: bankMatch[bankMap.description], bankAmount: bankAmount, amountDifference: Math.abs(expenseAmount - bankAmount), dateDifference: Math.abs(differenceInDays(parseDate(bankMatch[bankMap.date])!, expenseDate)), matchMethod: `Tolerance Match (D:${tolerances.date}d, A:${tolerances.amount}%)`, confidence: confidence, });
            remainingExpenses.splice(i, 1);
            remainingBankTxns.splice(bankMatchIndex, 1);
        }
    }
    return { matchedInPass, remainingExpenses, remainingBankTxns };
}
