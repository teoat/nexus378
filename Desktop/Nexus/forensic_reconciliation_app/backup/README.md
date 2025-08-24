# Backup and Recovery Procedures

This directory contains scripts to back up the critical data stores used in the Forensic Reconciliation + Fraud Platform.

## Backup Scripts

To run the backup scripts, you must have `docker` installed and running. The scripts need to be made executable first:

```bash
chmod +x *.sh
```

### 1. PostgreSQL Backup

This script creates a compressed SQL dump of the PostgreSQL database.

**To run the backup:**

```bash
./backup_postgres.sh
```

**To restore from a backup:**

1.  Make sure the `forensic_postgres` container is running.
2.  Copy the backup file into the container.
3.  Execute `psql` to restore the database.

```bash
# Example:
gunzip postgres_backup_20231027_120000.sql.gz
docker cp postgres_backup_20231027_120000.sql forensic_postgres:/tmp/backup.sql
docker exec -it forensic_postgres psql -U forensic_user -d forensic_reconciliation -f /tmp/backup.sql
```

### 2. Neo4j Backup

This script creates a dump of the Neo4j graph database. Note that this script will temporarily stop the `forensic_neo4j` container to ensure a consistent backup.

**To run the backup:**

```bash
./backup_neo4j.sh
```

**To restore from a backup:**

1.  Stop the `forensic_neo4j` container.
2.  Remove the existing data in the `neo4j_data` volume.
3.  Run the `neo4j-admin load` command in a temporary container.

```bash
# Example:
docker stop forensic_neo4j
docker run --rm -v neo4j_data:/data -v $(pwd)/neo4j_backups:/backups neo4j:5-community neo4j-admin database load --from-path=/backups/neo4j_backup_20231027_120000.dump --database=neo4j --force
docker start forensic_neo4j
```

### 3. Redis Backup

This script copies the Redis `dump.rdb` snapshot file.

**To run the backup:**

```bash
./backup_redis.sh
```

**To restore from a backup:**

1.  Stop the `forensic_redis` container.
2.  Replace the `dump.rdb` file in the `redis_data` volume with the backup file.
3.  Start the `forensic_redis` container.

```bash
# Example:
docker stop forensic_redis
docker run --rm -v redis_data:/data -v $(pwd)/redis_backups:/backups alpine cp /backups/redis_backup_20231027_120000.rdb /data/dump.rdb
docker start forensic_redis
```

### 4. MinIO Backup

This script creates a compressed tarball of the MinIO object storage.

**To run the backup:**

```bash
./backup_minio.sh
```

**To restore from a backup:**

1.  Stop the `forensic_minio` container.
2.  Extract the backup tarball.
3.  Replace the contents of the `minio_data` volume with the backup data.
4.  Start the `forensic_minio` container.

```bash
# Example:
docker stop forensic_minio
tar -xzf minio_backup_20231027_120000.tar.gz
docker run --rm -v minio_data:/data -v $(pwd)/minio_backup_20231027_120000/data:/backup_data alpine sh -c "rm -rf /data/* && cp -r /backup_data/* /data/"
docker start forensic_minio
```

## Automation

These scripts can be automated using a cron job or a similar scheduling tool to perform regular backups. Ensure that the backup files are stored in a secure, remote location.
