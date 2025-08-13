

import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { parse, isValid, startOfMonth, endOfMonth, startOfQuarter, endOfQuarter, subMonths, startOfYear, endOfYear, format, getYear, getMonth, getQuarter } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

function formatAsCurrency(num: number, currency: string, thousandSeparator: ',' | '.'): string {
     let locale = 'en-US'; // Default to a locale that uses commas
     if (thousandSeparator === '.') {
         locale = 'de-DE'; // German uses periods as thousand separators
     }
     // Specific locales for certain currencies can override the default
     if (currency === 'IDR') locale = 'id-ID';
     if (currency === 'JPY') locale = 'ja-JP';

    return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: currency,
    }).format(num);
}

export function formatCurrency(amount: any, currency: string = 'USD', thousandSeparator: ',' | '.' = ','): string {
    const numericValue = parseAmount(amount, thousandSeparator);
    if (numericValue === null) {
        return String(amount); // Return original string if not a valid number
    }
    return formatAsCurrency(numericValue, currency, thousandSeparator);
}


// Helper: Smartly parse amount strings by removing currency symbols and separators
export function parseAmount(value: any, thousandSeparator: ',' | '.' = ','): number | null {
    if (value === null || value === undefined) return null;
    
    let stringValue = String(value).trim();
    if (stringValue === '') return null;

    // Remove currency symbols and whitespace
    stringValue = stringValue.replace(/[$\€\£\¥Rp\s]/g, '');

    // Handle the two main formats based on the thousand separator
    if (thousandSeparator === ',') {
        // Standard US-style: 1,234.56 -> remove commas
        stringValue = stringValue.replace(/,/g, '');
    } else {
        // European-style: 1.234,56 -> remove periods, then replace comma with period
        stringValue = stringValue.replace(/\./g, '');
        stringValue = stringValue.replace(/,/g, '.');
    }

    const numberValue = parseFloat(stringValue);
    return isNaN(numberValue) ? null : numberValue;
}

export const parseDate = (dateStr: string | null | undefined): Date | null => {
    if (!dateStr) return null;
    
    // Add a Z to the end of date-only strings to treat them as UTC
    // This prevents timezone shifts when parsing.
    const isDateOnly = /^\d{4}-\d{2}-\d{2}$/.test(dateStr) || /^\d{1,2}\/\d{1,2}\/\d{2,4}$/.test(dateStr) || /^\d{2}\/\d{1,2}\/\d{2,4}$/.test(dateStr);
    
    const dateToParse = (isDateOnly && !dateStr.includes('T') && !dateStr.endsWith('Z')) ? `${dateStr}T00:00:00.000Z` : dateStr;

    // Attempt with native Date constructor first for ISO 8601 and other standard formats
    const nativeDate = new Date(dateToParse);
    if (isValid(nativeDate)) {
      return nativeDate;
    }
    
    // Fallback to date-fns for more complex formats
    const formats = [
        'yyyy-MM-dd', 'MM/dd/yyyy', 'dd/MM/yyyy', 'M/d/yy', 'yyyy.MM.dd',
        "MM/dd/yy", "dd-MMM-yy",
    ];

    for (const formatStr of formats) {
        try {
            const date = parse(dateStr, formatStr, new Date());
            if (isValid(date)) {
                return date;
            }
        } catch (e) {
            // Ignore parsing errors and try the next format
        }
    }
    
    console.warn(`Could not parse date: "${dateStr}". Returning null.`);
    return null;
}

export type PeriodOption = { value: string; label: string };

export function getAvailableMonths(minDate: Date, maxDate: Date): PeriodOption[] {
    const months: PeriodOption[] = [];
    let currentDate = startOfMonth(minDate);
    while (currentDate <= maxDate) {
        const value = format(currentDate, 'yyyy-MM');
        const label = format(currentDate, 'MMMM yyyy');
        months.push({ value, label });
        currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1);
    }
    return months.reverse();
}

export function getAvailableTrimesters(minDate: Date, maxDate: Date): PeriodOption[] {
    const trimesters: PeriodOption[] = [];
    const seen = new Set<string>();
    let currentDate = startOfQuarter(minDate);
    while (currentDate <= maxDate) {
        const year = getYear(currentDate);
        const quarter = getQuarter(currentDate);
        const value = `${year}-Q${quarter}`;
        if (!seen.has(value)) {
            const start = startOfQuarter(currentDate);
            const end = endOfQuarter(currentDate);
            const label = `Q${quarter} ${year} (${format(start, 'MMM')} - ${format(end, 'MMM')})`;
            trimesters.push({ value, label });
            seen.add(value);
        }
        currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 3, 1);
    }
    return trimesters.reverse();
}

export function getAvailableHalfYears(minDate: Date, maxDate: Date): PeriodOption[] {
    const halfYears: PeriodOption[] = [];
    const seen = new Set<string>();
    let currentDate = startOfYear(minDate);

    while (currentDate <= maxDate) {
        const year = getYear(currentDate);
        const month = getMonth(currentDate);
        const half = month < 6 ? 1 : 2;
        const value = `${year}-H${half}`;

        if (!seen.has(value)) {
            const start = new Date(year, (half - 1) * 6, 1);
            const end = endOfMonth(new Date(year, start.getMonth() + 5, 1));
            const label = `H${half} ${year} (${format(start, 'MMM')} - ${format(end, 'MMM')})`;
            halfYears.push({ value, label });
            seen.add(value);
        }

        if (half === 1) {
            currentDate = new Date(year, 6, 1);
        } else {
            currentDate = new Date(year + 1, 0, 1);
        }
    }
    return halfYears.reverse();
}

export function getPeriodDateRange(periodValue: string, periodType: 'month' | 'trimester' | 'halfYear' | 'quarter'): { startDate: Date; endDate: Date } {
    const [yearStr, periodPart] = periodValue.split('-');
    const year = parseInt(yearStr, 10);

    switch (periodType) {
        case 'month': {
            const month = parseInt(periodPart, 10) - 1;
            const date = new Date(year, month, 1);
            return { startDate: startOfMonth(date), endDate: endOfMonth(date) };
        }
        case 'trimester': // Assuming this means quarter now
        case 'quarter': {
            const quarter = parseInt(periodPart.replace('Q', ''), 10);
            const startMonth = (quarter - 1) * 3;
            const startDate = new Date(year, startMonth, 1);
            const endDate = endOfMonth(new Date(year, startMonth + 2, 1));
            return { startDate, endDate };
        }
        case 'halfYear': {
            const half = parseInt(periodPart.replace('H', ''), 10);
            const startMonth = (half - 1) * 6;
            const startDate = new Date(year, startMonth, 1);
            const endDate = endOfMonth(new Date(year, startMonth + 5, 1));
            return { startDate, endDate };
        }
    }
}

export function getMonthsInPeriod(sourceFileContent: string, dateColumn: string | null, periodValue: string, timelineColumn?: string | null): PeriodOption[] {
    if (!sourceFileContent || (!dateColumn && !timelineColumn)) return [];
    
    const data = JSON.parse(sourceFileContent);
    const allDates = data.map((row: any) => parseDate(row[dateColumn!])).filter(Boolean) as Date[];

    if (periodValue === 'all') {
        if (allDates.length === 0) return [];
        const minDate = new Date(Math.min.apply(null, allDates as any));
        const maxDate = new Date(Math.max.apply(null, allDates as any));
        return getAvailableMonths(minDate, maxDate).reverse(); // Process oldest first
    }

    if (timelineColumn && periodValue !== 'all') {
         const timelineDates = data.filter((row: any) => row[timelineColumn] === periodValue)
            .map((row: any) => parseDate(row[dateColumn!]))
            .filter(Boolean);

        if (timelineDates.length > 0) {
            const minDate = new Date(Math.min.apply(null, timelineDates as any));
            const maxDate = new Date(Math.max.apply(null, timelineDates as any));
            return getAvailableMonths(minDate, maxDate).reverse();
        }
        return [];
    }

    const periodType = periodValue.includes('-Q') ? 'quarter' : periodValue.includes('-H') ? 'halfYear' : 'month';
    
    if (periodType === 'month') {
        const { startDate } = getPeriodDateRange(periodValue, 'month');
        return [{ value: periodValue, label: format(startDate, 'MMMM yyyy') }];
    }

    const { startDate, endDate } = getPeriodDateRange(periodValue, periodType);
    const months: PeriodOption[] = [];
    let currentDate = startOfMonth(startDate);
    
    while (currentDate <= endDate) {
        const value = format(currentDate, 'yyyy-MM');
        const label = format(currentDate, 'MMMM yyyy');
        months.push({ value, label });
        currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1);
    }
    return months;
}

    
