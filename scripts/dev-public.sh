#!/bin/bash
# Development script for Public version
#
# Watches for changes, rebuilds, and serves locally

echo "🔧 Starting Nutricount Public Version in development mode..."
echo "👀 Watching for changes in frontend/src/..."
echo ""

# Function to build on change
build_on_change() {
    echo "🔨 Change detected, rebuilding..."
    ./scripts/build-public.sh
    echo "✅ Rebuild complete at $(date '+%H:%M:%S')"
    echo ""
}

# Initial build
./scripts/build-public.sh

# Start HTTP server in background
echo "🌐 Starting local server on http://localhost:8000"
cd frontend/build/public && python3 -m http.server 8000 &
SERVER_PID=$!
cd ../../..

echo "   Open http://localhost:8000 in your browser"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping server..."
    kill $SERVER_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

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
    echo "📝 Manual mode: Run ./scripts/build-public.sh after each change"
    echo ""
    echo "Press Ctrl+C to stop the server"
    wait $SERVER_PID
fi

cleanup
