#!/bin/bash
# Setup script for GitHub webhook integration

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
    echo -e "${BLUE}[WEBHOOK SETUP]${NC} $1"
}

# Generate webhook secret
generate_secret() {
    print_header "Generating webhook secret"
    WEBHOOK_SECRET=$(openssl rand -hex 32)
    echo "WEBHOOK_SECRET=$WEBHOOK_SECRET" > /home/pi/.webhook_secret
    print_status "Webhook secret generated: $WEBHOOK_SECRET"
}

# Install webhook server
install_webhook_server() {
    print_header "Installing webhook server"
    
    # Copy webhook server
    cp /home/pi/nutricount/webhook_server.py /home/pi/
    
    # Install systemd service
    sudo cp /home/pi/nutricount/nutrition-webhook.service /etc/systemd/system/
    
    # Update service with secret
    if [ -f /home/pi/.webhook_secret ]; then
        source /home/pi/.webhook_secret
        sudo sed -i "s/your-webhook-secret-change-this/$WEBHOOK_SECRET/" /etc/systemd/system/nutrition-webhook.service
    fi
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable and start service
    sudo systemctl enable nutrition-webhook
    sudo systemctl start nutrition-webhook
    
    print_status "Webhook server installed and started"
}

# Setup firewall
setup_firewall() {
    print_header "Setting up firewall"
    
    # Allow webhook port
    sudo ufw allow 8080/tcp comment 'GitHub webhook'
    
    print_status "Firewall configured"
}

# Show GitHub webhook configuration
show_github_config() {
    print_header "GitHub Webhook Configuration"
    
    if [ -f /home/pi/.webhook_secret ]; then
        source /home/pi/.webhook_secret
        echo ""
        echo "📋 Configure GitHub webhook with these settings:"
        echo ""
        echo "🔗 URL: http://192.168.188.43:8080/webhook"
        echo "🔑 Secret: $WEBHOOK_SECRET"
        echo "📡 Content type: application/json"
        echo "🎯 Events: Workflow runs"
        echo ""
        echo "📖 Steps:"
        echo "1. Go to your GitHub repository"
        echo "2. Settings → Webhooks → Add webhook"
        echo "3. Use the URL and secret above"
        echo "4. Select 'Workflow runs' event"
        echo "5. Save webhook"
        echo ""
        echo "🔄 How it works:"
        echo "• Push to main branch triggers CI/CD pipeline"
        echo "• If pipeline passes all tests, webhook triggers deployment"
        echo "• If pipeline fails, no deployment occurs"
        echo "• Manual deployment available at /deploy endpoint"
        echo ""
    else
        print_error "Webhook secret not found"
    fi
}

# Test webhook
test_webhook() {
    print_header "Testing webhook server"
    
    # Check if webhook server is running
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        print_status "✅ Webhook server is running"
        
        # Show status
        curl -s http://localhost:8080/status | python3 -m json.tool
    else
        print_error "❌ Webhook server is not running"
        sudo systemctl status nutrition-webhook
    fi
}

# Main function
main() {
    print_header "Setting up GitHub webhook integration"
    
    generate_secret
    install_webhook_server
    setup_firewall
    show_github_config
    test_webhook
    
    print_status "🎉 Webhook setup completed!"
    print_warning "Don't forget to configure the webhook in GitHub!"
}

# Run main function
main "$@"
