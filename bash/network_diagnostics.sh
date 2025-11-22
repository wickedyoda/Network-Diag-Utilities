#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"
source "$SCRIPT_DIR/custom_logging.sh"
source "$SCRIPT_DIR/run_ping_test.sh"
source "$SCRIPT_DIR/run_traceroute.sh"
source "$SCRIPT_DIR/run_bufferbloat_test.sh"
source "$SCRIPT_DIR/run_speedtest.sh"
source "$SCRIPT_DIR/run_ip_geolocation.sh"

mkdir -p "$LOG_DIR"

echo "--- Network Diagnostics ---"
echo "1. Ping Test"
echo "2. Traceroute Test"
echo "3. Speed Test"
echo "4. Bufferbloat / MTU Test"
echo "5. IP Geolocation Test"
echo "6. Run All Tests"
echo "7. Exit"
read -rp "Enter your choice: " choice

if [[ "$choice" == "7" ]]; then
    echo "Exiting diagnostics suite."
    exit 0
fi

read -rp "Enter target host (default: $DEFAULT_TARGET): " target
target=${target:-$DEFAULT_TARGET}

log_file="$LOG_DIR/Diagnostics_$(date '+%Y%m%d_%H%M%S').log"

case "$choice" in
    1)
        run_ping_test "$target" "$log_file" ;;
    2)
        run_traceroute_test "$target" "$log_file" ;;
    3)
        run_speedtest "$log_file" ;;
    4)
        run_bufferbloat_test "$target" "$log_file" ;; 
    5)
        if [[ "$ENABLE_IP_GEO" == "true" ]]; then
            run_ip_geolocation_test "$log_file"
        else
            write_log_entry "IP geolocation is disabled in config." "$log_file" "$COLOR_YELLOW"
        fi
        ;;
    6)
        write_log_entry "Running full diagnostics on $target" "$log_file" "$COLOR_CYAN"
        if [[ "$ENABLE_IP_GEO" == "true" ]]; then
            run_ip_geolocation_test "$log_file"
        fi
        run_ping_test "$target" "$log_file"
        run_traceroute_test "$target" "$log_file"
        mtu_value=$(run_bufferbloat_test "$target" "$log_file")
        run_speedtest "$log_file"
        [[ -n "$mtu_value" ]] && write_log_entry "MTU discovered: $mtu_value bytes" "$log_file" "$COLOR_GREEN"
        ;;
    *)
        echo "Invalid option";;
esac

echo "Diagnostics complete. Results saved to $log_file"

