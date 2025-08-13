
import Papa from 'papaparse';

// Helper to clean header names
function cleanHeader(header: string): string {
    return header.replace(/"/g, '').trim();
}

/**
 * Parses a CSV string into an array of JSON objects.
 * This is a synchronous and potentially blocking operation.
 * For large files, prefer using a web worker.
 * @param csvString The raw CSV data as a string.
 * @returns An array of objects.
 */
export function csvToJson(csvString: string): any[] {
    let data: any[] = [];
    Papa.parse(csvString, {
        header: true,
        skipEmptyLines: true,
        dynamicTyping: true,
        transformHeader: cleanHeader,
        complete: (results) => {
            data = results.data;
        },
        error: (error: any) => {
            console.error("CSV parsing error:", error.message);
            throw new Error(`Failed to parse CSV: ${error.message}`);
        },
    });
    return data;
}


/**
 * Extracts the headers from a JSON array of objects.
 * @param data The JSON data as an array of objects.
 * @returns An array of header strings.
 */
export function getJsonHeaders(data: any[]): string[] {
    if (!data || !Array.isArray(data) || data.length === 0) {
        return [];
    }
    return Object.keys(data[0]);
}

/**
 * Gets a sample of rows from a JSON array.
 * @param jsonString The JSON data as a string.
 * @param count The number of rows to sample.
 * @returns A new array containing the sampled rows.
 */
export function getJsonSample(jsonString: string, count: number): any[] {
    if (!jsonString) return [];
    try {
        const data = JSON.parse(jsonString);
        if (Array.isArray(data)) {
            return data.slice(0, count);
        }
        return [];
    } catch (e) {
        console.error("Failed to parse JSON for sampling", e);
        return [];
    }
}
