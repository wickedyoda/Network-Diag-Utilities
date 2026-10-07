#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load shared defaults from config.json (single source of truth), falling
# back to native bash variables if the JSON is missing or unreadable.
if [[ -f "$SCRIPT_DIR/config.json" ]]; then
    # Emit scalar keys as KEY=VALUE pairs (skip nested Paths/Notes objects)
    kv_file=
    kv_file=$(mktemp)
    python3 -c '
import json, sys
with open(sys.argv[1]) as f:
    data = json.load(f)
for k, v in data.items():
    if k in ("Paths", "Notes"):
        continue
    if isinstance(v, bool):
        print(f"{k}={str(v).lower()}")
    elif isinstance(v, (int, float)):
        print(f"{k}={v}")
    elif isinstance(v, str):
        print(f"{k}={v}")
' "$SCRIPT_DIR/config.json" > "$kv_file" 2>/dev/null
    # shellcheck source=/dev/null
    source "$kv_file"
    rm -f "$kv_file"
fi

# Cross-platform defaults aligned with the PowerShell scripts (fallbacks
# only — the values above are the canonical source)
LOG_DIR="${LOG_DIR:-$(dirname "$0")/logs}"
DEFAULT_TARGET="${TargetHost:-8.8.8.8}"
TIMESTAMP_FORMAT="${TimestampFormat:-%H:%M:%S}"

# Ping test
PING_COUNT="${PingCount:-4}"
PING_DELAY_MS="${PingDelayMs:-1000}"

# Bufferbloat / MTU discovery
BUFFER_START_SIZE="${BufferStartSize:-1500}"
MTU_STOP_SIZE="${MTUStopSize:-100}"
MTU_DECREMENT="${MTUDecrement:-20}"

# Paths for optional Windows fallbacks (useful when running under WSL/Git Bash)
SPEEDTEST_PATH="${SpeedtestPath:-/mnt/c/Tools/SpeedtestCLI}"
TRACERT_PATH="${TRACERT_PATH:-/mnt/c/Windows/System32}"

# Feature toggles
ENABLE_IP_GEO="${EnableIPGeo:-true}"
SUPPRESS_WARNINGS="${SuppressWarnings:-false}"
DEBUG_MODE="${DebugMode:-false}"
