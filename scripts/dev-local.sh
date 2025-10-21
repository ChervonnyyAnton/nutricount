#!/bin/bash
# Development script for Local version
#
# Watches for changes and rebuilds automatically

echo "🔧 Starting Nutricount Local Version in development mode..."
echo "👀 Watching for changes in frontend/src/..."
echo ""

# Function to build on change
build_on_change() {
    echo "🔨 Change detected, rebuilding..."
    ./scripts/build-local.sh
    echo "✅ Rebuild complete at $(date '+%H:%M:%S')"
    echo ""
}

# Initial build
./scripts/build-local.sh

# Check if fswatch is available
if command -v fswatch &> /dev/null; then
    echo "Using fswatch for file watching..."
    fswatch -o frontend/src/ | while read; do
        build_on_change
    done
elif command -v inotifywait &> /dev/null; then
    echo "Using inotifywait for file watching..."
    while inotifywait -r -e modify,create,delete frontend/src/; do
        build_on_change
    done
else
    echo "⚠️  No file watcher found (fswatch or inotifywait)"
    echo "   Install one for automatic rebuilds:"
    echo "   - macOS: brew install fswatch"
    echo "   - Linux: apt-get install inotify-tools"
    echo ""
    echo "📝 Manual mode: Run ./scripts/build-local.sh after each change"
fi
