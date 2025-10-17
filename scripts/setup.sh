#!/bin/bash
# Installation script for Nutrition Tracker on Raspberry Pi OS Lite 64-bit
# Optimized for Raspberry Pi 4 Model B 2018

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

# Check if running on Raspberry Pi OS Lite 64-bit
check_system() {
    print_header "Checking system requirements..."
    
    # Check architecture
    local arch=$(uname -m)
    if [ "$arch" != "aarch64" ]; then
        print_error "This script is designed for ARM64 (aarch64) architecture"
        print_error "Current architecture: $arch"
        exit 1
    fi
    
    # Check OS
    if ! grep -q "Raspberry Pi OS" /etc/os-release 2>/dev/null; then
        print_warning "This script is optimized for Raspberry Pi OS"
        print_warning "Current OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
    fi
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run this script as root"
        print_error "Run as regular user and use sudo when needed"
        exit 1
    fi
    
    print_status "System check passed"
}

# Update system packages
update_system() {
    print_header "Updating system packages..."
    
    sudo apt update
    sudo apt upgrade -y
    
    print_status "System updated successfully"
}

# Install required packages
install_packages() {
    print_header "Installing required packages..."
    
    sudo apt install -y \
        git \
        curl \
        wget \
        htop \
        vim \
        nano \
        lm-sensors \
        sqlite3 \
        python3-pip \
        python3-venv \
        build-essential \
        libffi-dev \
        python3-dev \
        ca-certificates \
        gnupg \
        lsb-release \
        ufw \
        fail2ban
    
    print_status "Required packages installed"
}

# Install Docker
install_docker() {
    print_header "Installing Docker for ARM64..."
    
    # Remove old Docker installations
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    # Install Docker Compose
    sudo apt install -y docker-compose
    
    # Enable Docker service
    sudo systemctl enable docker
    sudo systemctl start docker
    
    print_status "Docker installed successfully"
}

# Configure system for Pi 4 Model B 2018
configure_system() {
    print_header "Configuring system for Pi 4 Model B 2018..."
    
    # Enable SSH
    sudo systemctl enable ssh
    sudo systemctl start ssh
    
    # Configure boot settings for Pi 4 Model B 2018
    sudo tee -a /boot/config.txt > /dev/null << EOF

# Nutrition Tracker optimizations for Pi 4 Model B 2018
gpu_mem=128
arm_freq=1500
over_voltage=1
temp_limit=75
avoid_warnings=1
dtparam=thermal
EOF
    
    # Configure swap
    sudo dphys-swapfile swapoff
    sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
    sudo dphys-swapfile setup
    sudo dphys-swapfile swapon
    
    # Disable unnecessary services
    sudo systemctl disable bluetooth
    sudo systemctl disable hciuart
    sudo systemctl disable ModemManager 2>/dev/null || true
    
    # Configure logging
    sudo tee -a /etc/systemd/journald.conf > /dev/null << EOF

# Nutrition Tracker logging optimization
SystemMaxUse=100M
RuntimeMaxUse=50M
EOF
    
    print_status "System configured successfully"
}

# Setup firewall
setup_firewall() {
    print_header "Setting up firewall..."
    
    # Configure UFW
    sudo ufw --force reset
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw --force enable
    
    # Configure fail2ban
    sudo systemctl enable fail2ban
    sudo systemctl start fail2ban
    
    print_status "Firewall configured successfully"
}

# Clone and setup application
setup_application() {
    print_header "Setting up Nutrition Tracker application..."
    
    # Clone repository (replace with actual repository URL)
    if [ ! -d "nutricount" ]; then
        print_warning "Please clone the repository manually:"
        print_warning "git clone <your-repository-url> nutricount"
        print_warning "cd nutricount"
        return 1
    fi
    
    cd nutricount
    
    # Create necessary directories
    mkdir -p data logs backups
    
    # Set permissions
    chmod 755 data logs backups
    
    # Create environment file
    if [ ! -f ".env" ]; then
        cp env.example .env
        print_status "Environment file created. Please edit .env with your settings"
    fi
    
    # Build and start application
    docker-compose build
    docker-compose up -d
    
    print_status "Application setup completed"
}

# Setup monitoring and backup
setup_monitoring() {
    print_header "Setting up monitoring and backup..."
    
    # Make scripts executable
    chmod +x scripts/*.sh
    
    # Setup cron jobs
    (crontab -l 2>/dev/null; echo "0 2 * * * $(pwd)/scripts/backup.sh") | crontab -
    (crontab -l 2>/dev/null; echo "*/5 * * * * $(pwd)/scripts/temp_monitor.sh --log") | crontab -
    
    # Create systemd service
    sudo tee /etc/systemd/system/nutrition-tracker.service > /dev/null << EOF
[Unit]
Description=Nutrition Tracker
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
    
    # Enable service
    sudo systemctl enable nutrition-tracker.service
    sudo systemctl start nutrition-tracker.service
    
    print_status "Monitoring and backup setup completed"
}

# Final checks
final_checks() {
    print_header "Running final checks..."
    
    # Check Docker
    if docker --version > /dev/null 2>&1; then
        print_status "✅ Docker is working"
    else
        print_error "❌ Docker is not working"
    fi
    
    # Check application
    if docker-compose ps | grep -q "Up"; then
        print_status "✅ Application is running"
    else
        print_warning "⚠️  Application may not be running properly"
    fi
    
    # Check temperature
    if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        local temp=$(cat /sys/class/thermal/thermal_zone0/temp)
        local temp_c=$((temp / 1000))
        print_status "🌡️  Current temperature: ${temp_c}°C"
        
        if [ $temp_c -gt 70 ]; then
            print_warning "⚠️  Temperature is high - check cooling"
        fi
    fi
    
    # Show access information
    local ip=$(hostname -I | awk '{print $1}')
    print_header "Installation completed!"
    echo ""
    print_status "Application is available at:"
    print_status "  http://$ip/"
    print_status "  http://$ip/api/"
    print_status "  http://$ip/health"
    echo ""
    print_status "Monitoring scripts:"
    print_status "  ./scripts/monitor.sh - Main monitoring"
    print_status "  ./scripts/temp_monitor.sh - Temperature monitoring"
    print_status "  ./scripts/backup.sh - Manual backup"
    echo ""
    print_warning "IMPORTANT: Please reboot the system to apply all changes"
    print_warning "sudo reboot"
}

# Main installation process
main() {
    echo "🥗 Nutrition Tracker - Raspberry Pi OS Lite 64-bit Installer"
    echo "=========================================================="
    echo "This script will install Nutrition Tracker on Raspberry Pi OS Lite 64-bit"
    echo "Optimized for Raspberry Pi 4 Model B 2018"
    echo ""
    
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installation cancelled"
        exit 0
    fi
    
    check_system
    update_system
    install_packages
    install_docker
    configure_system
    setup_firewall
    
    print_header "Manual steps required:"
    echo "1. Clone the repository: git clone <your-repo-url> nutricount"
    echo "2. Edit configuration: nano nutricount/.env"
    echo "3. Run: cd nutricount && ./scripts/setup.sh"
    echo ""
    
    read -p "Have you completed the manual steps? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_application
        setup_monitoring
        final_checks
    else
        print_status "Please complete the manual steps and run this script again"
    fi
}

# Run main function
main "$@"