import json
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent  # repo root, not python/
CONFIG_PATH = BASE_DIR / "config.json"

# Shared schema as defined in config.json (scalar keys under Defaults).
_SHARED_DEFAULTS = {
    "TargetHost": "8.8.8.8",
    "LogDirectory": "logs",
    "TimestampFormat": "%H:%M:%S",
    "PingCount": 4,
    "PingDelayMs": 1000,
    "BufferStartSize": 1500,
    "MTUStopSize": 100,
    "MTUDecrement": 20,
    "SpeedtestPath": "",
    "EnableIPGeo": True,
    "DebugMode": False,
    "WarningsSuppression": False,
}

# Build config with guaranteed Defaults and all original keys, thanks to
# cached defaults when config.json is missing, unreadable, or malformed.
try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as _f:
        _shared = json.load(_f)
    if not isinstance(_shared, dict):
        raise ValueError("config.json top level is not an object")
except (OSError, ValueError, json.JSONDecodeError) as _exc:
    _shared = {}

config = {"Defaults": dict(_SHARED_DEFAULTS)}
for section, values in _shared.items():
    if isinstance(values, dict):
        config[section] = {**_SHARED_DEFAULTS, **values}
    else:
        config[section] = values

# Normalize the shared key to the original name so all Python callers match.
if isinstance(config.get("Defaults"), dict):
    _delay_ms = config["Defaults"].pop("PingDelayMs", None)
    if _delay_ms is not None:
        config["Defaults"]["PingDelay"] = _delay_ms