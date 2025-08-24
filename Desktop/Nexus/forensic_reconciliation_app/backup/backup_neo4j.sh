#!/bin/bash

# This script creates a backup of the Neo4j database.

# Set variables
CONTAINER_NAME="forensic_neo4j"
BACKUP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
NEO4J_BACKUP_DIR="$BACKUP_DIR/neo4j_backups"
BACKUP_FILE="$NEO4J_BACKUP_DIR/neo4j_backup_$TIMESTAMP.dump"

# Create backup directory if it doesn't exist
mkdir -p "$NEO4J_BACKUP_DIR"

# Check if the container is running
if ! docker ps -f "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
  echo "Error: Container '$CONTAINER_NAME' is not running."
  exit 1
fi

echo "Creating Neo4j backup..."

# Execute neo4j-admin dump inside the container
# Note: The database needs to be stopped for a consistent backup.
# This script will stop and restart the database.

echo "Stopping Neo4j database for consistent backup..."
docker stop "$CONTAINER_NAME"

# Wait for the container to stop
sleep 10

# Create a temporary container to perform the backup from the volume
docker run --rm -v neo4j_data:/data -v "$NEO4J_BACKUP_DIR":/backups neo4j:5-community bin/neo4j-admin database dump --database=neo4j --to-path=/backups

# Rename the backup file to include a timestamp
mv "$NEO4J_BACKUP_DIR/neo4j.dump" "$BACKUP_FILE"

# Check if the backup was successful
if [ $? -eq 0 ]; then
  echo "Neo4j backup created successfully: $BACKUP_FILE"
else
  echo "Error: Neo4j backup failed."
  docker start "$CONTAINER_NAME" # Attempt to restart the container on failure
  exit 1
fi

echo "Starting Neo4j database..."
docker start "$CONTAINER_NAME"

echo "Neo4j backup process completed."
