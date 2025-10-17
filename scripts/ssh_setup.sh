#!/bin/bash
# SSH Key Setup Script for Raspberry Pi
# This script helps you add your SSH keys to the Pi

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
    echo -e "${BLUE}[SSH SETUP]${NC} $1"
}

# Function to add SSH key to Pi
add_ssh_key() {
    local pi_ip="$1"
    local username="${2:-pi}"
    
    print_header "Adding SSH keys to Raspberry Pi at $pi_ip"
    
    # Check if Pi is reachable
    if ! ping -c 1 "$pi_ip" > /dev/null 2>&1; then
        print_error "Cannot reach Raspberry Pi at $pi_ip"
        print_warning "Make sure Pi is connected to network and SSH is enabled"
        return 1
    fi
    
    # Create .ssh directory on Pi
    ssh -o StrictHostKeyChecking=no "$username@$pi_ip" "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
    
    # Add ED25519 key (recommended)
    if [ -f ~/.ssh/id_ed25519.pub ]; then
        print_status "Adding ED25519 key..."
        ssh-copy-id -i ~/.ssh/id_ed25519.pub "$username@$pi_ip"
    fi
    
    # Add RSA key (backup)
    if [ -f ~/.ssh/id_rsa.pub ]; then
        print_status "Adding RSA key..."
        ssh-copy-id -i ~/.ssh/id_rsa.pub "$username@$pi_ip"
    fi
    
    # Test connection
    print_status "Testing SSH connection..."
    if ssh -o StrictHostKeyChecking=no "$username@$pi_ip" "echo 'SSH connection successful!'"; then
        print_status "✅ SSH keys added successfully!"
        print_status "You can now connect without password: ssh $username@$pi_ip"
    else
        print_error "❌ SSH connection failed"
        return 1
    fi
}

# Function to show manual instructions
show_manual_instructions() {
    print_header "Manual SSH Key Setup Instructions"
    echo ""
    echo "1. Connect to Pi via SSH with password:"
    echo "   ssh pi@<PI_IP_ADDRESS>"
    echo ""
    echo "2. Create SSH directory:"
    echo "   mkdir -p ~/.ssh"
    echo "   chmod 700 ~/.ssh"
    echo ""
    echo "3. Add your public key to authorized_keys:"
    echo "   nano ~/.ssh/authorized_keys"
    echo ""
    echo "4. Copy and paste one of these keys:"
    echo ""
    echo "   ED25519 (Recommended):"
    cat ~/.ssh/id_ed25519.pub
    echo ""
    echo "   RSA (Backup):"
    cat ~/.ssh/id_rsa.pub
    echo ""
    echo "5. Set correct permissions:"
    echo "   chmod 600 ~/.ssh/authorized_keys"
    echo "   chmod 700 ~/.ssh"
    echo ""
    echo "6. Test connection:"
    echo "   ssh pi@<PI_IP_ADDRESS>"
}

# Function to find Pi on network
find_pi() {
    print_header "Scanning network for Raspberry Pi..."
    
    # Get local network range
    local network=$(route -n get default | grep interface | awk '{print $2}' | head -1)
    local ip_range=$(ifconfig "$network" | grep "inet " | awk '{print $2}' | sed 's/\.[0-9]*$/.0\/24/')
    
    print_status "Scanning $ip_range for Raspberry Pi..."
    
    # Scan for Pi devices
    nmap -sn "$ip_range" | grep -A2 "Raspberry Pi" || {
        print_warning "No Raspberry Pi found in scan"
        print_status "Try scanning manually:"
        echo "nmap -sn $ip_range"
        return 1
    }
}

# Main menu
show_menu() {
    echo "🔑 SSH Key Setup for Raspberry Pi"
    echo "=================================="
    echo "1. Add SSH keys automatically"
    echo "2. Show manual instructions"
    echo "3. Find Raspberry Pi on network"
    echo "4. Test SSH connection"
    echo "5. Exit"
    echo ""
}

# Test SSH connection
test_connection() {
    local pi_ip="$1"
    local username="${2:-pi}"
    
    print_header "Testing SSH connection to $pi_ip"
    
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$username@$pi_ip" "echo 'Connection successful!'"; then
        print_status "✅ SSH connection successful!"
    else
        print_error "❌ SSH connection failed"
        print_warning "Make sure:"
        echo "  - Pi is connected to network"
        echo "  - SSH is enabled"
        echo "  - IP address is correct"
        echo "  - Username is correct (default: pi)"
    fi
}

# Main execution
main() {
    if [ "$1" = "--help" ]; then
        echo "Usage: $0 [--help|--auto <pi_ip>|--manual|--find|--test <pi_ip>]"
        echo "  --auto <pi_ip>    Add SSH keys automatically"
        echo "  --manual         Show manual instructions"
        echo "  --find           Find Pi on network"
        echo "  --test <pi_ip>   Test SSH connection"
        echo "  --help           Show this help"
        exit 0
    elif [ "$1" = "--auto" ] && [ -n "$2" ]; then
        add_ssh_key "$2"
    elif [ "$1" = "--manual" ]; then
        show_manual_instructions
    elif [ "$1" = "--find" ]; then
        find_pi
    elif [ "$1" = "--test" ] && [ -n "$2" ]; then
        test_connection "$2"
    else
        while true; do
            show_menu
            read -p "Select an option (1-5): " choice
            
            case $choice in
                1)
                    read -p "Enter Raspberry Pi IP address: " pi_ip
                    read -p "Enter username (default: pi): " username
                    username=${username:-pi}
                    add_ssh_key "$pi_ip" "$username"
                    ;;
                2)
                    show_manual_instructions
                    ;;
                3)
                    find_pi
                    ;;
                4)
                    read -p "Enter Raspberry Pi IP address: " pi_ip
                    read -p "Enter username (default: pi): " username
                    username=${username:-pi}
                    test_connection "$pi_ip" "$username"
                    ;;
                5)
                    print_status "Goodbye!"
                    exit 0
                    ;;
                *)
                    print_error "Invalid option. Please select 1-5."
                    ;;
            esac
            
            echo ""
            read -p "Press Enter to continue..."
        done
    fi
}

# Run main function
main "$@"
