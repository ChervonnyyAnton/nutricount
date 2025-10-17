#!/bin/bash
# Simple update script for Nutrition Tracker
# Usage: ./update.sh [repository-url]

set -e

# Configuration
REPO_URL="${1:-https://github.com/your-username/nutricount.git}"
APP_DIR="/home/pi/nutricount"

echo "🔄 Updating Nutrition Tracker from $REPO_URL"

# Stop current application
echo "⏹️  Stopping current application..."
pkill -f "gunicorn.*app:app" || echo "No running application found"
pkill -f "python.*app.py" || echo "No running application found"
sleep 2

# Backup current data
echo "💾 Creating backup..."
if [ -d "$APP_DIR/data" ]; then
    cp -r "$APP_DIR/data" "$APP_DIR/data.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Data backed up successfully"
else
    echo "⚠️ No data directory found"
fi

# Backup logs and other important files
if [ -d "$APP_DIR/logs" ]; then
    cp -r "$APP_DIR/logs" "$APP_DIR/logs.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Update code
echo "📥 Updating code..."
if [ -d "$APP_DIR" ]; then
    cd "$APP_DIR"
    if [ -d ".git" ]; then
        git fetch origin
        git reset --hard origin/main
    else
        echo "❌ Not a git repository. Please clone manually."
        exit 1
    fi
else
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

# Update dependencies
echo "📦 Updating dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Update database (only if needed)
echo "🗄️ Checking database..."
python init_db.py

# Restart application
echo "🚀 Starting application..."
nohup gunicorn --config gunicorn.conf.py app:app > /dev/null 2>&1 &

# Wait and check
sleep 5
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Update completed successfully!"
    echo "🌐 Application is running at http://192.168.188.43:5000/"
else
    echo "❌ Failed to start application"
    exit 1
fi
