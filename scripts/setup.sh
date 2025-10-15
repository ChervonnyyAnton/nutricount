#!/bin/bash
# Raspberry Pi Zero 2W Setup Script for Nutrition Tracker
# Optimized for 512MB RAM constraint

set -e

echo "🥗 Setting up Nutrition Tracker on Raspberry Pi Zero 2W..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Raspberry Pi
check_pi() {
    if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
        print_warning "This script is optimized for Raspberry Pi Zero 2W"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Check available memory
check_memory() {
    local total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [ $total_mem -lt 400 ]; then
        print_error "Insufficient memory. Pi Zero 2W should have at least 400MB available."
        exit 1
    fi
    print_status "Available memory: ${total_mem}MB"
}

# Optimize system for Pi Zero 2W
optimize_system() {
    print_status "Optimizing system for Pi Zero 2W..."
    
    # Increase swap for Pi Zero 2W
    if ! grep -q "CONF_SWAPSIZE=1024" /etc/dphys-swapfile; then
        print_status "Increasing swap size to 1GB..."
        sudo dphys-swapfile swapoff
        sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
        sudo dphys-swapfile setup
        sudo dphys-swapfile swapon
    fi
    
    # Optimize Docker for Pi Zero 2W
    if ! grep -q "log-driver" /etc/docker/daemon.json 2>/dev/null; then
        print_status "Optimizing Docker configuration..."
        sudo mkdir -p /etc/docker
        echo '{
            "log-driver": "json-file",
            "log-opts": {
                "max-size": "10m",
                "max-file": "1"
            },
            "storage-driver": "overlay2",
            "default-ulimits": {
                "memlock": {
                    "Hard": -1,
                    "Name": "memlock",
                    "Soft": -1
                }
            }
        }' | sudo tee /etc/docker/daemon.json
        sudo systemctl restart docker
    fi
    
    # Disable unnecessary services
    print_status "Disabling unnecessary services..."
    sudo systemctl disable bluetooth 2>/dev/null || true
    sudo systemctl disable hciuart 2>/dev/null || true
    sudo systemctl disable ModemManager 2>/dev/null || true
}

# Install Docker if not present
install_docker() {
    if ! command -v docker &> /dev/null; then
        print_status "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
        print_warning "Please log out and log back in for Docker group changes to take effect"
    else
        print_status "Docker is already installed"
    fi
}

# Install Docker Compose if not present
install_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_status "Installing Docker Compose..."
        sudo pip3 install docker-compose
    else
        print_status "Docker Compose is already installed"
    fi
}

# Create optimized environment file
create_env_file() {
    if [ ! -f .env ]; then
        print_status "Creating optimized .env file for Pi Zero 2W..."
        cat > .env << EOF
# Raspberry Pi Zero 2W Optimized Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
DATABASE_URL=sqlite:///data/nutrition.db

# Pi Zero 2W Optimizations
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
WORKERS=1
WORKER_CONNECTIONS=50
TIMEOUT=60

# Memory limits
MEMORY_LIMIT=300M
CPU_LIMIT=1.0

# Logging
LOG_LEVEL=warning
LOG_MAX_SIZE=10m
LOG_MAX_FILES=1
EOF
        print_status ".env file created"
    else
        print_status ".env file already exists"
    fi
}

# Build and start the application
build_and_start() {
    print_status "Building optimized Docker image for Pi Zero 2W..."
    docker-compose build --no-cache
    
    print_status "Starting Nutrition Tracker..."
    docker-compose up -d
    
    # Wait for application to start
    print_status "Waiting for application to start..."
    sleep 30
    
    # Check if application is running
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        print_status "✅ Nutrition Tracker is running successfully!"
        print_status "🌐 Access the application at: http://$(hostname -I | awk '{print $1}'):80"
        print_status "🔧 API endpoint: http://$(hostname -I | awk '{print $1}'):5000"
    else
        print_error "❌ Application failed to start. Check logs with: docker-compose logs"
        exit 1
    fi
}

# Create systemd service for auto-start
create_systemd_service() {
    print_status "Creating systemd service for auto-start..."
    sudo tee /etc/systemd/system/nutrition-tracker.service > /dev/null << EOF
[Unit]
Description=Nutrition Tracker on Pi Zero 2W
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable nutrition-tracker.service
    print_status "Systemd service created and enabled"
}

# Main execution
main() {
    print_status "Starting Pi Zero 2W setup for Nutrition Tracker..."
    
    check_pi
    check_memory
    optimize_system
    install_docker
    install_docker_compose
    create_env_file
    build_and_start
    create_systemd_service
    
    print_status "🎉 Setup completed successfully!"
    print_status ""
    print_status "📋 Next steps:"
    print_status "1. Log out and log back in to apply Docker group changes"
    print_status "2. Access the application at: http://$(hostname -I | awk '{print $1}'):80"
    print_status "3. Monitor logs with: docker-compose logs -f"
    print_status "4. Stop the service with: docker-compose down"
    print_status "5. Restart the service with: sudo systemctl restart nutrition-tracker"
}

# Run main function
main "$@"
