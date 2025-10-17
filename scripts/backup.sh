#!/bin/bash
# Backup script optimized for Raspberry Pi 4 local network deployment
# Enhanced backup strategy with local storage optimization

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-90}"  # Increased retention for local storage
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_FILE:-./logs/backup.log}"

# Create directories
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🔄 Starting backup process..."

# Backup database with integrity check
if [ -f "data/nutrition.db" ]; then
    # Check database integrity first
    if sqlite3 data/nutrition.db "PRAGMA integrity_check;" | grep -q "ok"; then
        sqlite3 data/nutrition.db ".backup $BACKUP_DIR/nutrition_$TIMESTAMP.db"
        
        # Compress with better compression for local storage
        gzip -9 "$BACKUP_DIR/nutrition_$TIMESTAMP.db"
        
        # Verify backup integrity
        if [ -f "$BACKUP_DIR/nutrition_$TIMESTAMP.db.gz" ]; then
            log "✅ Database backed up successfully: nutrition_$TIMESTAMP.db.gz"
        else
            log "❌ Database backup failed"
            exit 1
        fi
    else
        log "❌ Database integrity check failed, skipping backup"
        exit 1
    fi
else
    log "❌ Database file not found: data/nutrition.db"
    exit 1
fi

# Backup application configuration
if [ -f "config.py" ]; then
    cp config.py "$BACKUP_DIR/config_$TIMESTAMP.py"
    log "✅ Configuration backed up: config_$TIMESTAMP.py"
fi

# Backup environment file if exists
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/env_$TIMESTAMP"
    log "✅ Environment file backed up: env_$TIMESTAMP"
fi

# Cleanup old backups with more aggressive cleanup for local storage
find "$BACKUP_DIR" -name "*.db.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "config_*.py" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "env_*" -mtime +$RETENTION_DAYS -delete
log "🧹 Cleaned up backups older than $RETENTION_DAYS days"

# Show backup stats
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.db.gz 2>/dev/null | wc -l)
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "📊 Total backups: $BACKUP_COUNT ($BACKUP_SIZE)"

# Check available disk space
AVAILABLE_SPACE=$(df -h . | awk 'NR==2 {print $4}')
log "💾 Available disk space: $AVAILABLE_SPACE"

log "✅ Backup process completed successfully"
