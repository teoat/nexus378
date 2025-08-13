
"use server";
import { benfordsLawAnalysis } from '@/features/3-analysis/ai-flows/benfords-law-analysis';
import { Anomaly, MatchedTransaction, ColumnMapping, UnmatchedBankTransaction } from '@/types/types';
import { parseAmount, parseDate } from '@/lib/utils';
import { v4 as uuidv4 } from 'uuid';
import { differenceInDays } from 'date-fns';
import { fuzzyMatchDescriptions } from '@/features/2-reconciliation/ai-flows/fuzzy-match-descriptions';
import { withPerformanceTrace } from '@/lib/performance-trace';

type ThousandSeparator = ',' | '.';
type Tolerances = {
    date: number;
    amount: number;
}
type FuzzyMatch = {
    expenseIndex: number;
    bankTxDescription: string;
    confidence: number;
};

/**
 * Executes a single matching pass on the provided data with a specific set of tolerances.
 * @param confidence The confidence score to assign to matches found in this pass.
 */
function runSingleMatchingPass(
    unmatchedExpenses: any[],
    unmatchedBankTxnsPool: any[],
    sourceMap: ColumnMapping,
    bankMap: ColumnMapping,
    tolerances: Tolerances,
    thousandSeparator: ThousandSeparator,
    confidence: number
) {
    const matchedInPass: MatchedTransaction[] = [];
    const remainingExpenses = [...unmatchedExpenses];
    const remainingBankTxns = [...unmatchedBankTxnsPool];

    // Pass 1: Exact Reference Number Match (if available)
    if (sourceMap.numbering && bankMap.numbering) {
        for (let i = remainingExpenses.length - 1; i >= 0; i--) {
            const expense = remainingExpenses[i];
            const expenseRef = expense[sourceMap.numbering!];
            if (!expenseRef) continue;

            const bankMatchIndex = remainingBankTxns.findIndex(
                (bt) => bt[bankMap.numbering!] === expenseRef
            );

            if (bankMatchIndex !== -1) {
                const bankMatch = remainingBankTxns[bankMatchIndex];
                matchedInPass.push({
                    id: uuidv4(),
                    expenseOriginal: expense,
                    bankTxOriginal: bankMatch,
                    expenseDate: expense[sourceMap.date!],
                    expenseDescription: expense[sourceMap.description!],
                    expenseAmount: parseAmount(expense[sourceMap.debit!], thousandSeparator)!,
                    bankDate: bankMatch[bankMap.date!],
                    bankDescription: bankMatch[bankMap.description!],
                    bankAmount: parseAmount(bankMatch[bankMap.debit!], thousandSeparator)!,
                    amountDifference: 0,
                    dateDifference: 0,
                    matchMethod: "Reference Number",
                    confidence: 100, // Reference number is always highest confidence
                });
                remainingExpenses.splice(i, 1);
                remainingBankTxns.splice(bankMatchIndex, 1);
            }
        }
    }
    
    // Pass 2: Date and Amount Match within tolerance
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
            matchedInPass.push({
                id: uuidv4(),
                expenseOriginal: expense,
                bankTxOriginal: bankMatch,
                expenseDate: expense[sourceMap.date!],
                expenseDescription: expense[sourceMap.description!],
                expenseAmount: expenseAmount,
                bankDate: bankMatch[bankMap.date],
                bankDescription: bankMatch[bankMap.description],
                bankAmount: bankAmount,
                amountDifference: Math.abs(expenseAmount - bankAmount),
                dateDifference: Math.abs(differenceInDays(parseDate(bankMatch[bankMap.date])!, expenseDate)),
                matchMethod: `Tolerance Match (D:${tolerances.date}d, A:${tolerances.amount}%)`,
                confidence: confidence,
            });
            remainingExpenses.splice(i, 1);
            remainingBankTxns.splice(bankMatchIndex, 1);
        }
    }

    return { matchedInPass, remainingExpenses, remainingBankTxns };
}

/**
 * Orchestrates a multi-pass reconciliation strategy with iterative loosening of tolerances.
 */
function runMultiPassMatchingEngine(
    sourceData: any[],
    sourceMap: ColumnMapping,
    bankData: any[],
    bankMap: ColumnMapping,
    initialTolerances: Tolerances,
    thousandSeparator: ThousandSeparator
) {
    const allMatched: MatchedTransaction[] = [];
    let currentUnmatchedExpenses = [...sourceData];
    let currentUnmatchedBankTxns = [...bankData];

    // Define the iterative tolerance tiers. Each tier is [date tolerance, amount tolerance, confidence score].
    const toleranceTiers: [number, number, number][] = [
        [initialTolerances.date, initialTolerances.amount, 95], // Strict Pass (User's setting)
        [initialTolerances.date + 2, initialTolerances.amount, 85],       // Looser Date Pass
        [initialTolerances.date, initialTolerances.amount + 0.5, 80],     // Looser Amount Pass
        [initialTolerances.date + 3, initialTolerances.amount + 1.0, 70], // Loosest Pass
    ];

    for (const [dateTol, amountTol, confidence] of toleranceTiers) {
        if (currentUnmatchedExpenses.length === 0 || currentUnmatchedBankTxns.length === 0) {
            break; // Stop if there's nothing left to match
        }

        const passResult = runSingleMatchingPass(
            currentUnmatchedExpenses,
            currentUnmatchedBankTxns,
            sourceMap,
            bankMap,
            { date: dateTol, amount: amountTol },
            thousandSeparator,
            confidence
        );

        allMatched.push(...passResult.matchedInPass);
        currentUnmatchedExpenses = passResult.remainingExpenses;
        currentUnmatchedBankTxns = passResult.remainingBankTxns;
    }

    // Note: The `toleranceMatches` from the original design are now integrated into `allMatched` with varying confidence.
    return { matchedExpenses: allMatched, toleranceMatches: [], unmatchedExpenses: currentUnmatchedExpenses, unmatchedBankTxnsPool: currentUnmatchedBankTxns };
}


function runBenfordsAnalysis(sourceData: any[], amountColumn: string | null) {
    if (!amountColumn) return [];
    
    const leadingDigits = sourceData.map(row => {
        const value = String(row[amountColumn]);
        const firstDigit = value.trim().match(/^[1-9]/);
        return firstDigit ? parseInt(firstDigit[0], 10) : null;
    }).filter(digit => digit !== null);

    if (leadingDigits.length === 0) return [];

    const digitCounts = leadingDigits.reduce((acc, digit) => {
        if(digit) acc[digit] = (acc[digit] || 0) + 1;
        return acc;
    }, {} as Record<number, number>);

    const totalDigits = leadingDigits.length;
    const benfordDistribution = [0, 30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6];

    return Array.from({ length: 9 }, (_, i) => {
        const digit = i + 1;
        const actualPercentage = ((digitCounts[digit] || 0) / totalDigits) * 100;
        return {
            digit,
            actual: parseFloat(actualPercentage.toFixed(1)),
            expected: benfordDistribution[digit],
        };
    });
}


export async function runInitialMatching(
    sourceJson: string, 
    sourceMap: ColumnMapping, 
    bankJson: string, 
    bankMap: ColumnMapping,
    tolerances: Tolerances,
    thousandSeparator: ThousandSeparator,
    isFuzzyMatchingEnabled: boolean
) {
    return withPerformanceTrace("run_initial_matching", async (trace) => {
        const sourceData = JSON.parse(sourceJson);
        const bankData = bankJson ? JSON.parse(bankJson) : [];

        trace.putMetric("source_rows", sourceData.length);
        trace.putMetric("bank_rows", bankData.length);
        
        const benfordChartData = runBenfordsAnalysis(sourceData, sourceMap.debit);
        
        let matchedExpenses: MatchedTransaction[] = [];
        let unmatchedExpenses = [...sourceData];
        let unmatchedBankTxnsPool = [...bankData];

        if (bankData.length > 0) {
            const matchResult = runMultiPassMatchingEngine(
                sourceData, sourceMap, bankData, bankMap, tolerances, thousandSeparator
            );
            matchedExpenses = matchResult.matchedExpenses;
            unmatchedExpenses = matchResult.unmatchedExpenses;
            unmatchedBankTxnsPool = matchResult.unmatchedBankTxnsPool;
        }


        trace.putMetric("programmatic_matches", matchedExpenses.length);
        
        if (isFuzzyMatchingEnabled && unmatchedExpenses.length > 0 && unmatchedBankTxnsPool.length > 0 && sourceMap.description && bankMap.description) {
            const expenseDescriptions = unmatchedExpenses.map((e, index) => ({ expenseDescription: e[sourceMap.description!], expenseIndex: index }));
            const bankDescriptions = unmatchedBankTxnsPool.map((b, index) => ({ description: b[bankMap.description!], bankTxIndex: index }));
            
            const fuzzyResult = await fuzzyMatchDescriptions({ unmatchedExpenses: expenseDescriptions, unmatchedBankTxns: bankDescriptions });
            
            trace.putMetric("fuzzy_matches_found", fuzzyResult.matches.length);

            fuzzyResult.matches.forEach((match: FuzzyMatch) => {
                const expense = unmatchedExpenses[match.expenseIndex];
                const bankMatch = unmatchedBankTxnsPool.find(b => b[bankMap.description!] === match.bankTxDescription);
                if (expense && bankMatch && sourceMap.debit && sourceMap.date && bankMap.debit && bankMap.date) {
                    matchedExpenses.push({
                        id: uuidv4(),
                        expenseOriginal: expense,
                        bankTxOriginal: bankMatch,
                        expenseDate: expense[sourceMap.date],
                        expenseDescription: expense[sourceMap.description!],
                        expenseAmount: parseAmount(expense[sourceMap.debit], thousandSeparator)!,
                        bankDate: bankMatch[bankMap.date],
                        bankDescription: bankMatch[bankMap.description!],
                        bankAmount: parseAmount(bankMatch[bankMap.debit], thousandSeparator)!,
                        amountDifference: Math.abs(parseAmount(expense[sourceMap.debit], thousandSeparator)! - parseAmount(bankMatch[bankMap.debit], thousandSeparator)!),
                        dateDifference: Math.abs(differenceInDays(parseDate(bankMatch[bankMap.date])!, parseDate(expense[sourceMap.date])!)),
                        matchMethod: "AI Fuzzy Match",
                        confidence: match.confidence,
                    });
                    
                    // Remove from unmatched pools by marking for removal
                    (unmatchedExpenses as any)[match.expenseIndex] = null;
                    const bankIndex = unmatchedBankTxnsPool.indexOf(bankMatch);
                    if (bankIndex > -1) unmatchedBankTxnsPool.splice(bankIndex, 1);
                }
            });
            unmatchedExpenses = unmatchedExpenses.filter(e => e !== null);
        }

        const finalUnmatchedBankTxns: UnmatchedBankTransaction[] = unmatchedBankTxnsPool.map(txn => ({
            id: uuidv4(),
            date: txn[bankMap.date!],
            description: txn[bankMap.description!],
            amount: parseAmount(txn[bankMap.debit!], thousandSeparator)!,
            original: txn,
            status: "Unreviewed"
        }));

        // The new engine doesn't produce separate `toleranceMatches`, they are all in `matchedExpenses` now.
        return { matchedExpenses, toleranceMatches: [], unmatchedExpenses, unmatchedBankTxns: finalUnmatchedBankTxns, benfordChartData };
    });
}
