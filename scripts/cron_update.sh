#!/bin/bash
# Cron job script for automatic updates
# This script checks for updates every hour

LOG_FILE="/home/pi/logs/cron_update.log"
APP_DIR="/home/pi/nutricount"

# Create log directory
mkdir -p "$(dirname "$LOG_FILE")"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "Starting cron update check"

# Check if application is running
if ! curl -f http://localhost:5000/health > /dev/null 2>&1; then
    log "Application is not running, skipping update check"
    exit 0
fi

# Check for updates
cd "$APP_DIR"
if git fetch origin > /dev/null 2>&1; then
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)
    
    if [ "$LOCAL" != "$REMOTE" ]; then
        log "Updates available, running update script"
        /home/pi/simple_update.sh
    else
        log "No updates available"
    fi
else
    log "Failed to fetch updates"
fi
