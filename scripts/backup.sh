#!/bin/bash

# SQL Server Backup Script
# Runs daily backups with retention policy

set -e

# Configuration
DB_NAME="MarketingIQ"
BACKUP_PATH="/backups"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_PATH}/${DB_NAME}_${TIMESTAMP}.bak"

# Read password from secret
SA_PASSWORD=$(cat /run/secrets/db_password)

echo "Starting backup for ${DB_NAME} at $(date)"

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_PATH}

# Perform full backup
/opt/mssql-tools/bin/sqlcmd \
    -S localhost \
    -U sa \
    -P "${SA_PASSWORD}" \
    -Q "BACKUP DATABASE [${DB_NAME}] TO DISK = N'${BACKUP_FILE}' WITH FORMAT, INIT, COMPRESSION, CHECKSUM, STATS = 10"

# Verify backup
/opt/mssql-tools/bin/sqlcmd \
    -S localhost \
    -U sa \
    -P "${SA_PASSWORD}" \
    -Q "RESTORE VERIFYONLY FROM DISK = N'${BACKUP_FILE}'"

echo "Backup completed successfully: ${BACKUP_FILE}"

# Compress backup
gzip "${BACKUP_FILE}"
echo "Compressed backup: ${BACKUP_FILE}.gz"

# Clean up old backups
echo "Cleaning up backups older than ${RETENTION_DAYS} days"
find ${BACKUP_PATH} -name "*.bak.gz" -mtime +${RETENTION_DAYS} -delete

# Generate backup report
echo "Current backups:"
ls -lh ${BACKUP_PATH}/*.bak.gz 2>/dev/null || echo "No backups found"

echo "Backup process completed at $(date)"