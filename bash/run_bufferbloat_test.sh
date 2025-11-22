#!/bin/bash

run_bufferbloat_test() {
    local target="$1"
    local log_path="$2"
    local packet_size=${3:-$BUFFER_START_SIZE}

    write_log_entry "--- Bufferbloat / MTU Discovery ---" "$log_path" "$COLOR_CYAN"
    write_log_entry "Target: $target" "$log_path" "$COLOR_GRAY"

    while [[ $packet_size -ge $MTU_STOP_SIZE ]]; do
        write_log_entry "Testing with packet size: ${packet_size} bytes" "$log_path" "$COLOR_YELLOW"

        local cmd output status fragmented=false
        if [[ "$(uname -s | tr '[:upper:]' '[:lower:]')" == *"mingw"* ]]; then
            cmd=(ping "$target" -f -l "$packet_size" -n 1)
        elif [[ "$(uname -s)" == "Darwin" ]]; then
            cmd=(ping -c 1 -D -s $((packet_size - 28)) "$target")
        else
            cmd=(ping -c 1 -M do -s $((packet_size - 28)) "$target")
        fi

        output=$("${cmd[@]}" 2>&1)
        status=$?
        echo "$output" >>"$log_path"

        if echo "$output" | grep -qiE "fragment|frag needed|message too long"; then
            fragmented=true
        fi

        if [[ $status -ne 0 || $fragmented == true ]]; then
            write_log_entry "Fragmentation detected at ${packet_size} bytes. Reducing size..." "$log_path" "$COLOR_RED"
            packet_size=$((packet_size - MTU_DECREMENT))
            continue
        fi

        write_log_entry "Non-fragmented response at ${packet_size} bytes." "$log_path" "$COLOR_GREEN"
        echo "$packet_size"
        return 0
    done

    write_log_entry "Unable to find non-fragmented size above ${MTU_STOP_SIZE} bytes." "$log_path" "$COLOR_RED"
    return 1
}

