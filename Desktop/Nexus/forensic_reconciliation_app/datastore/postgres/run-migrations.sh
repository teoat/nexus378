#!/bin/bash

# This script applies database migrations and optionally seeds the database.

set -e

# --- Configuration ---
# The script expects the standard PostgreSQL environment variables to be set:
# PGPASSWORD, PGUSER, PGDATABASE, PGHOST, PGPORT

MIGRATIONS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/migrations"
SEED_FILE="$MIGRATIONS_DIR/seed.sql"
CONTAINER_NAME="forensic_postgres"

# --- Functions ---

function apply_migration() {
  local file=$1
  echo "Applying migration: $(basename "$file")..."
  docker exec -i "$CONTAINER_NAME" psql -U "$PGUSER" -d "$PGDATABASE" < "$file"
}

function seed_database() {
  if [ -f "$SEED_FILE" ]; then
    echo "Seeding database..."
    docker exec -i "$CONTAINER_NAME" psql -U "$PGUSER" -d "$PGDATABASE" < "$SEED_FILE"
  else
    echo "Warning: Seed file not found at $SEED_FILE"
  fi
}

# --- Main Logic ---

# Check if the container is running
if ! docker ps -f "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
  echo "Error: Container '$CONTAINER_NAME' is not running."
  echo "Please start the services with 'docker-compose up -d' before running migrations."
  exit 1
fi

# Apply all migration files in order
for file in $(ls "$MIGRATIONS_DIR"/*.sql | grep -v "seed.sql" | sort); do
  apply_migration "$file"
done

echo "All migrations applied successfully."

# Check for --seed flag
if [[ "$1" == "--seed" ]]; then
  seed_database
fi

echo "Database migration process completed."
