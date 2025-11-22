#!/bin/bash

# Cross-platform defaults aligned with the PowerShell scripts
LOG_DIR="$(dirname "$0")/logs"
DEFAULT_TARGET="8.8.8.8"
TIMESTAMP_FORMAT="%H:%M:%S"

# Ping test
PING_COUNT=4
PING_DELAY_MS=1000

# Bufferbloat / MTU discovery
BUFFER_START_SIZE=1500
MTU_STOP_SIZE=100
MTU_DECREMENT=20

# Paths for optional Windows fallbacks (useful when running under WSL/Git Bash)
SPEEDTEST_PATH="/mnt/c/Tools/SpeedtestCLI"
TRACERT_PATH="/mnt/c/Windows/System32"

# Feature toggles
ENABLE_IP_GEO=true
SUPPRESS_WARNINGS=false
DEBUG_MODE=false
