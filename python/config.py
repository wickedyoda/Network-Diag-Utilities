import os
from pathlib import Path


BASE_DIR = Path(__file__).parent

# Default configuration settings aligned with the PowerShell version
config = {
    "Defaults": {
        "TargetHost": "8.8.8.8",
        "LogDirectory": str(BASE_DIR / "logs"),
        "TimestampFormat": "%H:%M:%S",
        # Ping Test
        "PingCount": 4,
        "PingDelay": 1000,  # milliseconds
        # Bufferbloat / MTU discovery
        "BufferStartSize": 1500,
        "MTUStopSize": 100,
        "MTUDecrement": 20,
        # Speedtest CLI
        "SpeedtestPath": str(Path.home() / "AppData" / "Local" / "Speedtest"),
        # Optional features
        "EnableIPGeo": True,
    }
}
