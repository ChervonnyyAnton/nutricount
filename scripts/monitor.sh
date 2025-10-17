#!/bin/bash
# Raspberry Pi 4 Model B 2018 Performance Monitor for Nutrition Tracker
# Enhanced monitoring for early revision with thermal management

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
    echo -e "${BLUE}[MONITOR]${NC} $1"
}

# Check system resources
check_system_resources() {
    print_header "System Resources"
    
    # Memory usage
    local total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    local used_mem=$(free -m | awk 'NR==2{printf "%.0f", $3}')
    local mem_percent=$((used_mem * 100 / total_mem))
    
    echo "Memory: ${used_mem}MB / ${total_mem}MB (${mem_percent}%)"
    
    if [ $mem_percent -gt 80 ]; then
        print_warning "High memory usage detected!"
    fi
    
    # CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    echo "CPU Usage: ${cpu_usage}%"
    
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        print_warning "High CPU usage detected!"
    fi
    
    # Disk usage
    local disk_usage=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
    echo "Disk Usage: ${disk_usage}%"
    
    if [ $disk_usage -gt 80 ]; then
        print_warning "High disk usage detected!"
    fi
    
    # Temperature (if available) - Pi 4 Model B 2018 specific thresholds
    if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        local temp=$(cat /sys/class/thermal/thermal_zone0/temp)
        local temp_c=$((temp / 1000))
        echo "Temperature: ${temp_c}°C"
        
        if [ $temp_c -gt 80 ]; then
            print_error "🚨 CRITICAL: Temperature is causing throttling! Pi 4 Model B 2018 throttling starts at 80°C"
        elif [ $temp_c -gt 70 ]; then
            print_warning "⚠️  WARNING: Temperature is getting high - ensure good cooling for Pi 4 Model B 2018"
        fi
        
        # Check throttling status
        local throttled=$(vcgencmd get_throttled 2>/dev/null | cut -d= -f2)
        if [ "$throttled" != "0x0" ]; then
            print_error "⚠️  CPU throttling is ACTIVE! Performance is reduced"
        fi
    fi
    
    echo ""
}

# Check Docker containers
check_docker_containers() {
    print_header "Docker Containers"
    
    if command -v docker &> /dev/null; then
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Size}}"
        
        # Check container resource usage
        echo ""
        print_header "Container Resource Usage"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
    else
        print_error "Docker not found"
    fi
    
    echo ""
}

# Check application health
check_application_health() {
    print_header "Application Health"
    
    # Check if application is responding
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        print_status "✅ Application is healthy"
        
        # Get health response
        local health_response=$(curl -s http://localhost:5000/health)
        echo "Health Response: $health_response"
    else
        print_error "❌ Application is not responding"
    fi
    
    # Check API endpoints
    echo ""
    print_header "API Endpoints"
    
    # Test products endpoint
    if curl -f http://localhost:5000/api/products > /dev/null 2>&1; then
        print_status "✅ Products API is working"
    else
        print_error "❌ Products API is not working"
    fi
    
    # Test stats endpoint
    if curl -f http://localhost:5000/api/stats/$(date +%Y-%m-%d) > /dev/null 2>&1; then
        print_status "✅ Stats API is working"
    else
        print_error "❌ Stats API is not working"
    fi
    
    echo ""
}

# Check logs for errors
check_logs() {
    print_header "Recent Logs"
    
    if command -v docker-compose &> /dev/null; then
        echo "Recent application logs:"
        docker-compose logs --tail=10 nutrition-tracker 2>/dev/null || echo "No logs available"
        
        echo ""
        echo "Recent nginx logs:"
        docker-compose logs --tail=5 nutrition-nginx 2>/dev/null || echo "No logs available"
    else
        print_error "Docker Compose not found"
    fi
    
    echo ""
}

# Performance recommendations
performance_recommendations() {
    print_header "Performance Recommendations"
    
    # Check memory usage
    local mem_percent=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ $mem_percent -gt 80 ]; then
        echo "• Consider increasing swap size"
        echo "• Close unnecessary applications"
        echo "• Restart the application to free memory"
    fi
    
    # Check CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        echo "• CPU usage is high - consider reducing load"
        echo "• Check for background processes"
    fi
    
    # Check disk usage
    local disk_usage=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
    if [ $disk_usage -gt 80 ]; then
        echo "• Disk usage is high - clean up logs and temporary files"
        echo "• Consider using a larger SD card"
    fi
    
    # General recommendations for Pi 4 Model B 2018
    echo "• Use a fast microSD card (Class 10, A2, or better)"
    echo "• OBLIGATORY: Use active cooling (fan) for Pi 4 Model B 2018"
    echo "• Monitor temperature constantly - throttling starts at 80°C"
    echo "• Use thermal paste between CPU and heatsink"
    echo "• Consider reducing arm_freq in /boot/config.txt for stability"
    echo "• Use stable power supply (5.1V/3A official adapter)"
    echo "• Consider USB 3.0 SSD for better I/O performance"
    
    echo ""
}

# Continuous monitoring mode
continuous_monitor() {
    print_header "Starting continuous monitoring (Press Ctrl+C to stop)"
    
    while true; do
        clear
        echo "🥗 Nutrition Tracker - Pi 4 Model B 2018 Monitor"
        echo "==============================================="
        echo "Last updated: $(date)"
        echo ""
        
        check_system_resources
        check_docker_containers
        check_application_health
        
        echo "Press Ctrl+C to stop monitoring"
        sleep 30
    done
}

# Main menu
show_menu() {
    echo "🥗 Nutrition Tracker - Pi 4 Model B 2018 Monitor"
    echo "==============================================="
    echo "1. Check system resources"
    echo "2. Check Docker containers"
    echo "3. Check application health"
    echo "4. Check logs"
    echo "5. Performance recommendations"
    echo "6. Continuous monitoring"
    echo "7. Temperature monitoring"
    echo "8. Exit"
    echo ""
}

# Main execution
main() {
    if [ "$1" = "--continuous" ]; then
        continuous_monitor
    elif [ "$1" = "--help" ]; then
        echo "Usage: $0 [--continuous|--help]"
        echo "  --continuous  Start continuous monitoring"
        echo "  --help        Show this help message"
        exit 0
    else
        while true; do
            show_menu
            read -p "Select an option (1-8): " choice
            
            case $choice in
                1)
                    check_system_resources
                    ;;
                2)
                    check_docker_containers
                    ;;
                3)
                    check_application_health
                    ;;
                4)
                    check_logs
                    ;;
                5)
                    performance_recommendations
                    ;;
                6)
                    continuous_monitor
                    ;;
                7)
                    ./scripts/temp_monitor.sh
                    ;;
                8)
                    print_status "Goodbye!"
                    exit 0
                    ;;
                *)
                    print_error "Invalid option. Please select 1-8."
                    ;;
            esac
            
            echo ""
            read -p "Press Enter to continue..."
        done
    fi
}

# Run main function
main "$@"
