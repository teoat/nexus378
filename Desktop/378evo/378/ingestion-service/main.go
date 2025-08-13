package main

import (
	"fmt"
	"ingestion-service/handlers"
	"net/http"
)

func main() {
	http.HandleFunc("/upload", handlers.UploadHandler)
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Hello from the ingestion service!")
	})

	fmt.Println("Server started on port 8080")
	http.ListenAndServe(":8080", nil)
}
