#!/bin/bash
# Auto-update script for Nutrition Tracker on Raspberry Pi
# This script pulls updates from GitHub and restarts the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="${REPO_URL:-https://github.com/your-username/nutricount.git}"
BRANCH="${BRANCH:-main}"
APP_DIR="/home/pi/nutricount"
BACKUP_DIR="/home/pi/backups"
LOG_FILE="/home/pi/logs/update.log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
    log "INFO: $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    log "WARNING: $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    log "ERROR: $1"
}

print_header() {
    echo -e "${BLUE}[UPDATE]${NC} $1"
    log "UPDATE: $1"
}

# Create necessary directories
create_directories() {
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$BACKUP_DIR"
}

# Backup current application
backup_current() {
    print_header "Creating backup of current application"
    
    local backup_name="backup_$(date +%Y%m%d_%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    if [ -d "$APP_DIR" ]; then
        cp -r "$APP_DIR" "$backup_path"
        print_status "Backup created: $backup_path"
    else
        print_warning "No existing application directory found"
    fi
}

# Clone or update repository
update_code() {
    print_header "Updating code from repository"
    
    if [ -d "$APP_DIR" ]; then
        print_status "Updating existing repository"
        cd "$APP_DIR"
        
        # Check if it's a git repository
        if [ -d ".git" ]; then
            # Update existing repository
            git fetch origin
            git reset --hard origin/$BRANCH
            print_status "Repository updated to latest commit"
        else
            print_error "Directory exists but is not a git repository"
            return 1
        fi
    else
        print_status "Cloning repository for the first time"
        git clone -b "$BRANCH" "$REPO_URL" "$APP_DIR"
        print_status "Repository cloned successfully"
    fi
}

# Install/update dependencies
update_dependencies() {
    print_header "Updating Python dependencies"
    
    cd "$APP_DIR"
    
    if [ -f "requirements.txt" ]; then
        source venv/bin/activate
        pip install -r requirements.txt
        print_status "Dependencies updated"
    else
        print_warning "No requirements.txt found"
    fi
}

# Update database schema if needed
update_database() {
    print_header "Checking database schema"
    
    cd "$APP_DIR"
    
    if [ -f "init_db.py" ]; then
        source venv/bin/activate
        python init_db.py
        print_status "Database schema updated"
    else
        print_warning "No init_db.py found"
    fi
}

# Restart application
restart_application() {
    print_header "Restarting application"
    
    # Stop current application
    pkill -f "gunicorn.*app:app" || print_warning "No running application found"
    pkill -f "python.*app.py" || print_warning "No running application found"
    
    # Wait a moment
    sleep 2
    
    # Start application with Gunicorn
    cd "$APP_DIR"
    source venv/bin/activate
    nohup gunicorn --config gunicorn.conf.py app:app > /dev/null 2>&1 &
    
    # Wait for application to start
    sleep 5
    
    # Check if application is running
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        print_status "Application restarted successfully"
    else
        print_error "Failed to restart application"
        return 1
    fi
}

# Cleanup old backups
cleanup_backups() {
    print_header "Cleaning up old backups"
    
    # Keep only last 5 backups
    find "$BACKUP_DIR" -maxdepth 1 -type d -name "backup_*" | sort -r | tail -n +6 | xargs rm -rf
    print_status "Old backups cleaned up"
}

# Main update function
main() {
    print_header "Starting automatic update process"
    
    create_directories
    backup_current
    update_code
    update_dependencies
    update_database
    restart_application
    cleanup_backups
    
    print_status "Update completed successfully!"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [--help|--force|--backup-only]"
        echo "  --help        Show this help message"
        echo "  --force       Force update even if no changes detected"
        echo "  --backup-only Only create backup, don't update"
        exit 0
        ;;
    --force)
        print_warning "Force update requested"
        main
        ;;
    --backup-only)
        print_header "Creating backup only"
        create_directories
        backup_current
        print_status "Backup completed"
        ;;
    *)
        main
        ;;
esac
