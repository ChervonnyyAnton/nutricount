#!/bin/bash
# mDNS Setup Script for Raspberry Pi
# This script configures mDNS (avahi) for easy access via raspberrypi.local

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[mDNS SETUP]${NC} $1"
}

# Function to setup mDNS via web interface
setup_mdns_via_web() {
    local pi_ip="$1"
    
    print_header "Setting up mDNS via web interface"
    
    # Check if Pi is reachable
    if ! ping -c 1 "$pi_ip" > /dev/null 2>&1; then
        print_error "Cannot reach Raspberry Pi at $pi_ip"
        return 1
    fi
    
    print_status "Pi is reachable at $pi_ip"
    
    # Try to access the application
    if curl -f http://$pi_ip:5000/health > /dev/null 2>&1; then
        print_status "✅ Application is running on port 5000"
        print_status "🌐 Web interface: http://$pi_ip:5000/"
        print_status "🌐 Alternative: http://$pi_ip:8080/"
    elif curl -f http://$pi_ip:8080/health > /dev/null 2>&1; then
        print_status "✅ Application is running on port 8080"
        print_status "🌐 Web interface: http://$pi_ip:8080/"
    else
        print_error "❌ Application is not responding on either port"
        return 1
    fi
    
    print_status "📱 For iPhone access, try these URLs:"
    echo "   http://$pi_ip:5000/"
    echo "   http://$pi_ip:8080/"
    echo ""
    
    print_status "🔧 To enable mDNS on Pi, you need SSH access to run:"
    echo "   sudo apt update"
    echo "   sudo apt install -y avahi-daemon"
    echo "   sudo systemctl enable avahi-daemon"
    echo "   sudo systemctl start avahi-daemon"
    echo ""
    
    print_status "📋 Manual mDNS setup instructions:"
    echo "1. Connect to Pi via SSH or physical access"
    echo "2. Install avahi-daemon: sudo apt install -y avahi-daemon"
    echo "3. Enable service: sudo systemctl enable avahi-daemon"
    echo "4. Start service: sudo systemctl start avahi-daemon"
    echo "5. Test: ping raspberrypi.local"
}

# Function to test mDNS resolution
test_mdns() {
    print_header "Testing mDNS resolution"
    
    if ping -c 1 raspberrypi.local > /dev/null 2>&1; then
        print_status "✅ mDNS is working! raspberrypi.local resolves to:"
        nslookup raspberrypi.local | grep "Address:" | tail -1
        print_status "🌐 Try these URLs on iPhone:"
        echo "   http://raspberrypi.local:5000/"
        echo "   http://raspberrypi.local:8080/"
    else
        print_warning "❌ mDNS is not working yet"
        print_status "You can still use IP address:"
        echo "   http://192.168.64.3:5000/"
        echo "   http://192.168.64.3:8080/"
    fi
}

# Function to create a simple mDNS test page
create_test_page() {
    local pi_ip="$1"
    
    print_header "Creating test page for iPhone"
    
    # Create a simple test HTML page
    cat > /tmp/test_page.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pi Connection Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .success { color: green; }
        .error { color: red; }
        .info { color: blue; }
        button { padding: 10px 20px; margin: 10px; font-size: 16px; }
    </style>
</head>
<body>
    <h1>🥗 Raspberry Pi Connection Test</h1>
    
    <div class="info">
        <h2>Current Status:</h2>
        <p>✅ Pi is reachable at: $pi_ip</p>
        <p>✅ Application is running</p>
    </div>
    
    <h2>Test Links:</h2>
    <button onclick="window.open('http://$pi_ip:5000/', '_blank')">
        Open App (Port 5000)
    </button>
    <button onclick="window.open('http://$pi_ip:8080/', '_blank')">
        Open App (Port 8080)
    </button>
    
    <h2>For iPhone Users:</h2>
    <div class="info">
        <p>If the buttons above don't work on iPhone:</p>
        <ol>
            <li>Copy this URL: <code>http://$pi_ip:5000/</code></li>
            <li>Paste it in Safari</li>
            <li>Wait 10-15 seconds for loading</li>
        </ol>
    </div>
    
    <h2>mDNS Setup:</h2>
    <div class="info">
        <p>To enable raspberrypi.local access:</p>
        <ol>
            <li>SSH to Pi: <code>ssh pi@$pi_ip</code></li>
            <li>Install avahi: <code>sudo apt install -y avahi-daemon</code></li>
            <li>Enable service: <code>sudo systemctl enable avahi-daemon</code></li>
            <li>Start service: <code>sudo systemctl start avahi-daemon</code></li>
        </ol>
    </div>
    
    <script>
        // Test if we can reach the app
        fetch('http://$pi_ip:5000/health')
            .then(response => response.json())
            .then(data => {
                document.getElementById('status').innerHTML = 
                    '<span class="success">✅ App is healthy: ' + data.status + '</span>';
            })
            .catch(error => {
                document.getElementById('status').innerHTML = 
                    '<span class="error">❌ App not reachable: ' + error + '</span>';
            });
    </script>
    
    <div id="status">🔄 Testing app connection...</div>
</body>
</html>
EOF
    
    print_status "Test page created at: /tmp/test_page.html"
    print_status "You can serve this page locally to test iPhone connection"
}

# Main execution
main() {
    local pi_ip="${1:-192.168.64.3}"
    
    print_header "mDNS Setup for Raspberry Pi"
    echo "Target IP: $pi_ip"
    echo ""
    
    # Test current mDNS status
    test_mdns
    echo ""
    
    # Setup mDNS via web interface
    setup_mdns_via_web "$pi_ip"
    echo ""
    
    # Create test page
    create_test_page "$pi_ip"
    
    print_status "Setup complete! 🎉"
}

# Run main function
main "$@"
