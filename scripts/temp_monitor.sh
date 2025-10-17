#!/bin/bash
# Temperature monitoring script for Raspberry Pi 4 Model B 2018
# Specialized monitoring for early revision thermal management

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Temperature thresholds for Pi 4 Model B 2018
TEMP_WARNING=70    # Warning temperature
TEMP_CRITICAL=80   # Critical temperature (throttling starts)
TEMP_MAX=85        # Maximum safe temperature

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
    echo -e "${BLUE}[TEMP MONITOR]${NC} $1"
}

# Get current temperature
get_temperature() {
    if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        local temp=$(cat /sys/class/thermal/thermal_zone0/temp)
        echo $((temp / 1000))
    else
        echo "N/A"
    fi
}

# Get CPU frequency
get_cpu_freq() {
    if [ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq ]; then
        local freq=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq)
        echo $((freq / 1000))
    else
        echo "N/A"
    fi
}

# Check if throttling is active
check_throttling() {
    local throttled=$(vcgencmd get_throttled 2>/dev/null | cut -d= -f2)
    if [ "$throttled" != "0x0" ]; then
        echo "YES"
    else
        echo "NO"
    fi
}

# Get voltage
get_voltage() {
    local voltage=$(vcgencmd measure_volts 2>/dev/null | cut -d= -f2)
    echo "$voltage"
}

# Monitor temperature continuously
continuous_monitor() {
    print_header "Starting continuous temperature monitoring for Pi 4 Model B 2018"
    print_header "Press Ctrl+C to stop"
    
    while true; do
        clear
        echo "🌡️  Pi 4 Model B 2018 Temperature Monitor"
        echo "=========================================="
        echo "Last updated: $(date)"
        echo ""
        
        local temp=$(get_temperature)
        local freq=$(get_cpu_freq)
        local throttled=$(check_throttling)
        local voltage=$(get_voltage)
        
        echo "Temperature: ${temp}°C"
        echo "CPU Frequency: ${freq} MHz"
        echo "Throttling: ${throttled}"
        echo "Voltage: ${voltage}"
        echo ""
        
        # Temperature status
        if [ "$temp" != "N/A" ]; then
            if [ $temp -ge $TEMP_MAX ]; then
                print_error "🚨 CRITICAL: Temperature is at maximum safe level!"
                print_error "   Immediate action required!"
            elif [ $temp -ge $TEMP_CRITICAL ]; then
                print_error "🔥 CRITICAL: Temperature is causing throttling!"
                print_error "   Check cooling immediately!"
            elif [ $temp -ge $TEMP_WARNING ]; then
                print_warning "⚠️  WARNING: Temperature is getting high"
                print_warning "   Monitor closely and check cooling"
            else
                print_status "✅ Temperature is within normal range"
            fi
        fi
        
        # Throttling status
        if [ "$throttled" = "YES" ]; then
            print_error "⚠️  CPU throttling is ACTIVE!"
            print_error "   Performance is reduced due to thermal issues"
        else
            print_status "✅ No CPU throttling detected"
        fi
        
        echo ""
        echo "Press Ctrl+C to stop monitoring"
        sleep 5
    done
}

# Check temperature once
check_temperature() {
    print_header "Temperature Check for Pi 4 Model B 2018"
    
    local temp=$(get_temperature)
    local freq=$(get_cpu_freq)
    local throttled=$(check_throttling)
    local voltage=$(get_voltage)
    
    echo "Current Temperature: ${temp}°C"
    echo "CPU Frequency: ${freq} MHz"
    echo "Throttling Status: ${throttled}"
    echo "Voltage: ${voltage}"
    echo ""
    
    # Temperature analysis
    if [ "$temp" != "N/A" ]; then
        if [ $temp -ge $TEMP_MAX ]; then
            print_error "🚨 CRITICAL: Temperature is at maximum safe level!"
            print_error "   Immediate action required!"
            return 1
        elif [ $temp -ge $TEMP_CRITICAL ]; then
            print_error "🔥 CRITICAL: Temperature is causing throttling!"
            print_error "   Check cooling immediately!"
            return 1
        elif [ $temp -ge $TEMP_WARNING ]; then
            print_warning "⚠️  WARNING: Temperature is getting high"
            print_warning "   Monitor closely and check cooling"
        else
            print_status "✅ Temperature is within normal range"
        fi
    fi
    
    # Recommendations
    echo ""
    print_header "Recommendations for Pi 4 Model B 2018:"
    
    if [ "$temp" != "N/A" ] && [ $temp -ge $TEMP_WARNING ]; then
        echo "• Check if cooling fan is working properly"
        echo "• Ensure good ventilation around the Pi"
        echo "• Consider reducing CPU frequency in /boot/config.txt"
        echo "• Check if thermal paste is properly applied"
        echo "• Consider using a better heatsink"
    fi
    
    if [ "$throttled" = "YES" ]; then
        echo "• CPU throttling is active - performance is reduced"
        echo "• Check cooling system immediately"
        echo "• Consider reducing arm_freq in /boot/config.txt"
    fi
    
    echo "• Monitor temperature regularly with this script"
    echo "• Use active cooling (fan) for Pi 4 Model B 2018"
    echo "• Ensure stable power supply (5.1V/3A)"
}

# Log temperature to file
log_temperature() {
    local temp=$(get_temperature)
    local freq=$(get_cpu_freq)
    local throttled=$(check_throttling)
    local voltage=$(get_voltage)
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    local log_file="/tmp/pi4_temp.log"
    echo "$timestamp,$temp,$freq,$throttled,$voltage" >> "$log_file"
    
    # Keep only last 1000 entries
    tail -n 1000 "$log_file" > "${log_file}.tmp" && mv "${log_file}.tmp" "$log_file"
}

# Main menu
show_menu() {
    echo "🌡️  Pi 4 Model B 2018 Temperature Monitor"
    echo "=========================================="
    echo "1. Check temperature once"
    echo "2. Continuous monitoring"
    echo "3. Log temperature to file"
    echo "4. Show temperature history"
    echo "5. Exit"
    echo ""
}

# Show temperature history
show_history() {
    local log_file="/tmp/pi4_temp.log"
    
    if [ -f "$log_file" ]; then
        print_header "Temperature History (last 20 entries)"
        echo "Timestamp,Temperature,CPU_Freq,Throttling,Voltage"
        tail -n 20 "$log_file"
    else
        print_warning "No temperature log found. Run option 3 first."
    fi
}

# Main execution
main() {
    if [ "$1" = "--continuous" ]; then
        continuous_monitor
    elif [ "$1" = "--check" ]; then
        check_temperature
    elif [ "$1" = "--log" ]; then
        log_temperature
        print_status "Temperature logged successfully"
    elif [ "$1" = "--help" ]; then
        echo "Usage: $0 [--continuous|--check|--log|--help]"
        echo "  --continuous  Start continuous monitoring"
        echo "  --check       Check temperature once"
        echo "  --log         Log temperature to file"
        echo "  --help        Show this help message"
        exit 0
    else
        while true; do
            show_menu
            read -p "Select an option (1-5): " choice
            
            case $choice in
                1)
                    check_temperature
                    ;;
                2)
                    continuous_monitor
                    ;;
                3)
                    log_temperature
                    print_status "Temperature logged successfully"
                    ;;
                4)
                    show_history
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
