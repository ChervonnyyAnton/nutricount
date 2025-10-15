#!/bin/bash
# Simple backup script with rotation

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup database
if [ -f "data/nutrition.db" ]; then
    sqlite3 data/nutrition.db ".backup $BACKUP_DIR/nutrition_$TIMESTAMP.db"
    gzip "$BACKUP_DIR/nutrition_$TIMESTAMP.db"
    echo "✅ Database backed up: nutrition_$TIMESTAMP.db.gz"
fi

# Cleanup old backups
find "$BACKUP_DIR" -name "*.db.gz" -mtime +$RETENTION_DAYS -delete
echo "🧹 Cleaned up backups older than $RETENTION_DAYS days"

# Show backup stats
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.db.gz 2>/dev/null | wc -l)
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "📊 Total backups: $BACKUP_COUNT ($BACKUP_SIZE)"
