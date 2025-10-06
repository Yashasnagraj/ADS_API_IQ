#!/bin/bash

# SQL Server Restore Script
# Restores database from backup file

set -e

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.bak.gz>"
    echo "Available backups:"
    ls -lh /backups/*.bak.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE=$1
DB_NAME="MarketingIQ"
TEMP_BACKUP="/tmp/restore.bak"

# Read password from secret
SA_PASSWORD=$(cat /run/secrets/db_password)

echo "Starting restore process for ${DB_NAME} from ${BACKUP_FILE}"

# Decompress backup if needed
if [[ $BACKUP_FILE == *.gz ]]; then
    echo "Decompressing backup..."
    gunzip -c "${BACKUP_FILE}" > "${TEMP_BACKUP}"
    BACKUP_FILE="${TEMP_BACKUP}"
fi

# Set database to single user mode
echo "Preparing database for restore..."
/opt/mssql-tools/bin/sqlcmd \
    -S localhost \
    -U sa \
    -P "${SA_PASSWORD}" \
    -Q "ALTER DATABASE [${DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE"

# Restore database
echo "Restoring database..."
/opt/mssql-tools/bin/sqlcmd \
    -S localhost \
    -U sa \
    -P "${SA_PASSWORD}" \
    -Q "RESTORE DATABASE [${DB_NAME}] FROM DISK = N'${BACKUP_FILE}' WITH REPLACE, STATS = 10"

# Set database back to multi user mode
/opt/mssql-tools/bin/sqlcmd \
    -S localhost \
    -U sa \
    -P "${SA_PASSWORD}" \
    -Q "ALTER DATABASE [${DB_NAME}] SET MULTI_USER"

# Clean up temp file
[ -f "${TEMP_BACKUP}" ] && rm "${TEMP_BACKUP}"

echo "Database restored successfully at $(date)"

# Verify restore
/opt/mssql-tools/bin/sqlcmd \
    -S localhost \
    -U sa \
    -P "${SA_PASSWORD}" \
    -Q "SELECT name, state_desc, recovery_model_desc FROM sys.databases WHERE name = '${DB_NAME}'"