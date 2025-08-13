package handlers

import (
	"encoding/json"
	"ingestion-service/parsers"
	"net/http"
)

func UploadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Only POST method is allowed", http.StatusMethodNotAllowed)
		return
	}

	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Error retrieving the file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// For now, we'll just support CSV files.
	// In a real implementation, we would use the file extension or MIME type
	// to determine which parser to use.
	records, err := parsers.ParseCSV(file)
	if err != nil {
		http.Error(w, "Error parsing CSV file", http.StatusBadRequest)
		return
	}

	// Return the parsed records as JSON
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(records)
}
