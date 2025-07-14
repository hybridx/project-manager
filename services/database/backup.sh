#!/bin/bash
set -e

# MongoDB Backup Script for Project Manager

# Configuration
CONTAINER_NAME="project-manager-mongodb"
BACKUP_DIR="./backups"
MONGO_USER="admin"
MONGO_PASSWORD="projectmanager123"
DATABASE="project_manager"
RETENTION_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate timestamp for backup file
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/mongodb_backup_$TIMESTAMP.gz"

echo "Starting MongoDB backup..."
echo "Backup file: $BACKUP_FILE"

# Create backup using mongodump
podman exec "$CONTAINER_NAME" mongodump \
    --username "$MONGO_USER" \
    --password "$MONGO_PASSWORD" \
    --authenticationDatabase admin \
    --db "$DATABASE" \
    --gzip \
    --archive="/backups/mongodb_backup_$TIMESTAMP.gz"

# Check if backup was created successfully
if [ -f "$BACKUP_FILE" ]; then
    echo "Backup created successfully: $BACKUP_FILE"
    
    # Display backup size
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "Backup size: $BACKUP_SIZE"
    
    # Clean up old backups (keep only last N days)
    echo "Cleaning up old backups (keeping last $RETENTION_DAYS days)..."
    find "$BACKUP_DIR" -name "mongodb_backup_*.gz" -type f -mtime +$RETENTION_DAYS -delete
    
    echo "Backup completed successfully!"
    
    # List remaining backups
    echo "Available backups:"
    ls -lah "$BACKUP_DIR"/mongodb_backup_*.gz 2>/dev/null || echo "No backups found"
    
else
    echo "Backup failed!" >&2
    exit 1
fi 