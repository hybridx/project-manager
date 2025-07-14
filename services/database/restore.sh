#!/bin/bash
set -e

# MongoDB Restore Script for Project Manager

# Configuration
CONTAINER_NAME="project-manager-mongodb"
BACKUP_DIR="./backups"
MONGO_USER="admin"
MONGO_PASSWORD="projectmanager123"
DATABASE="project_manager"

# Function to display usage
usage() {
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 mongodb_backup_20240101_120000.gz"
    echo ""
    echo "Available backups:"
    ls -1 "$BACKUP_DIR"/mongodb_backup_*.gz 2>/dev/null || echo "No backups found"
    exit 1
}

# Check if backup file is provided
if [ $# -eq 0 ]; then
    echo "Error: No backup file specified"
    usage
fi

BACKUP_FILE="$1"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILE"

# Check if backup file exists
if [ ! -f "$BACKUP_PATH" ]; then
    echo "Error: Backup file not found: $BACKUP_PATH"
    usage
fi

# Confirmation prompt
echo "WARNING: This will drop the existing database and restore from backup!"
echo "Backup file: $BACKUP_PATH"
echo "Database: $DATABASE"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restore cancelled"
    exit 1
fi

echo "Starting MongoDB restore..."

# Drop existing database first
echo "Dropping existing database..."
podman exec "$CONTAINER_NAME" mongo \
    --username "$MONGO_USER" \
    --password "$MONGO_PASSWORD" \
    --authenticationDatabase admin \
    --eval "db.getSiblingDB('$DATABASE').dropDatabase()"

# Restore from backup
echo "Restoring from backup: $BACKUP_FILE"
podman exec "$CONTAINER_NAME" mongorestore \
    --username "$MONGO_USER" \
    --password "$MONGO_PASSWORD" \
    --authenticationDatabase admin \
    --db "$DATABASE" \
    --gzip \
    --archive="/backups/$BACKUP_FILE"

echo "Restore completed successfully!"

# Verify restore
echo "Verifying restore..."
COLLECTION_COUNT=$(podman exec "$CONTAINER_NAME" mongo \
    --username "$MONGO_USER" \
    --password "$MONGO_PASSWORD" \
    --authenticationDatabase admin \
    --quiet \
    --eval "db.getSiblingDB('$DATABASE').getCollectionNames().length")

echo "Database restored with $COLLECTION_COUNT collections"
echo "Restore verification completed!" 