
/// <reference lib="webworker" />
import Papa from 'papaparse';

// Helper function to clean header names
function cleanHeader(header: string): string {
    // Remove BOM and quotes, then trim whitespace
    return header.trim().replace(/"/g, '').replace(/^\uFEFF/, '');
}

// Listen for messages from the main thread
self.onmessage = (e: MessageEvent<string>) => {
  const csvString = e.data;
  
  // Use Papaparse to parse the CSV string
  Papa.parse(csvString, {
    header: true,         // Treat the first row as headers
    skipEmptyLines: true, // Skip empty lines
    dynamicTyping: true,  // Automatically convert numbers and booleans
    transformHeader: cleanHeader, // Clean up header names
    complete: (results) => {
      // Send the parsed data back to the main thread
      self.postMessage({ data: results.data });
    },
    error: (error) => {
      // Send any parsing errors back to the main thread
      self.postMessage({ error: error.message });
    },
  });
};
