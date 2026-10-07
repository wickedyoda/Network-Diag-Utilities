import json
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent  # repo root, not python/
CONFIG_PATH = BASE_DIR / "config.json"

# Load shared configuration from the single source of truth
with open(CONFIG_PATH, "r", encoding="utf-8") as _f:
    _shared = json.load(_f)

# Original defaults retained as fallback so nothing silently breaks on first run
_ORIGINAL_DEFAULTS = {
    "TargetHost": "8.8.8.8",
    "LogDirectory": str(BASE_DIR / "logs"),
    "TimestampFormat": "%H:%M:%S",
    "PingCount": 4,
    "PingDelay": 1000,
    "BufferStartSize": 1500,
    "MTUStopSize": 100,
    "MTUDecrement": 20,
    "SpeedtestPath": str(Path.home() / "AppData" / "Local" / "Speedtest"),
    "EnableIPGeo": True,
}

# Build config dict from shared config, layering original defaults back in
# so all original keys remain present regardless of the shared file's shape.
config = {}
for section, values in _shared.items():
    if section == "Paths" or section == "Notes":
        continue
    if isinstance(values, dict):
        config[section] = {**_ORIGINAL_DEFAULTS, **values}
    else:
        config[section] = values