#!/bin/bash

# This script creates a backup of the Redis database.

# Set variables
CONTAINER_NAME="forensic_redis"
BACKUP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REDIS_BACKUP_DIR="$BACKUP_DIR/redis_backups"
BACKUP_FILE="$REDIS_BACKUP_DIR/redis_backup_$TIMESTAMP.rdb"

# Create backup directory if it doesn't exist
mkdir -p "$REDIS_BACKUP_DIR"

# Check if the container is running
if ! docker ps -f "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
  echo "Error: Container '$CONTAINER_NAME' is not running."
  exit 1
fi

echo "Creating Redis backup..."

# It's recommended to run BGSAVE before copying the dump file
# to ensure the snapshot is up-to-date.
docker exec "$CONTAINER_NAME" redis-cli -a "$REDIS_PASSWORD" BGSAVE

# Wait for the BGSAVE to complete. This is a simple wait, a more
# robust solution would check the output of INFO persistence.
echo "Waiting for Redis to save the snapshot..."
sleep 10

# Copy the RDB file from the volume
docker cp "$CONTAINER_NAME":/data/dump.rdb "$BACKUP_FILE"

# Check if the backup was successful
if [ $? -eq 0 ]; then
  echo "Redis backup created successfully: $BACKUP_FILE"
else
  echo "Error: Redis backup failed."
  exit 1
fi

echo "Redis backup process completed."
