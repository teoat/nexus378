#!/bin/bash

# This script creates a backup of the MinIO object storage.

# Set variables
CONTAINER_NAME="forensic_minio"
BACKUP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
MINIO_BACKUP_DIR="$BACKUP_DIR/minio_backup_$TIMESTAMP"

# Create backup directory
mkdir -p "$MINIO_BACKUP_DIR"

# Check if the container is running
if ! docker ps -f "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
  echo "Error: Container '$CONTAINER_NAME' is not running."
  exit 1
fi

echo "Creating MinIO backup..."

# Copy the data from the MinIO container
docker cp "$CONTAINER_NAME":/data "$MINIO_BACKUP_DIR"

# Check if the backup was successful
if [ $? -eq 0 ]; then
  echo "MinIO backup created successfully in: $MINIO_BACKUP_DIR"
else
  echo "Error: MinIO backup failed."
  rm -rf "$MINIO_BACKUP_DIR" # Clean up failed backup directory
  exit 1
fi

# Optional: Compress the backup directory
echo "Compressing MinIO backup..."
tar -czf "$MINIO_BACKUP_DIR.tar.gz" -C "$BACKUP_DIR" "$(basename "$MINIO_BACKUP_DIR")"

if [ $? -eq 0 ]; then
  echo "MinIO backup compressed: $MINIO_BACKUP_DIR.tar.gz"
  rm -rf "$MINIO_BACKUP_DIR" # Remove the uncompressed directory
else
  echo "Error: Failed to compress the MinIO backup."
  exit 1
fi

echo "MinIO backup process completed."
