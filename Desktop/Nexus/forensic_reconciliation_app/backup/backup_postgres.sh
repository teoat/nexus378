#!/bin/bash

# This script creates a backup of the PostgreSQL database.

# Set variables
CONTAINER_NAME="forensic_postgres"
DB_USER="forensic_user"
DB_NAME="forensic_reconciliation"
BACKUP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/postgres_backup_$TIMESTAMP.sql"

# Check if the container is running
if ! docker ps -f "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
  echo "Error: Container '$CONTAINER_NAME' is not running."
  exit 1
fi

echo "Creating PostgreSQL backup..."

# Execute pg_dump inside the container
docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"

# Check if the backup was successful
if [ $? -eq 0 ]; then
  echo "PostgreSQL backup created successfully: $BACKUP_FILE"
else
  echo "Error: PostgreSQL backup failed."
  rm -f "$BACKUP_FILE" # Clean up failed backup file
  exit 1
fi

# Optional: Compress the backup file
gzip "$BACKUP_FILE"

if [ $? -eq 0 ]; then
  echo "Backup file compressed: $BACKUP_FILE.gz"
else
  echo "Error: Failed to compress the backup file."
  exit 1
fi

echo "PostgreSQL backup process completed."
