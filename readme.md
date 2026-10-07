# Network-Diag-Utilities
Credits: Steve (Gl.iNet Discord) for the original scripts; WickedYoda for the
multi-language rewrite and maintenance.

## 🚀 Overview
Network-Diag-Utilities is a lightweight collection of shell scripts, PowerShell
modules, and Python scripts for network diagnostics, troubleshooting, and
performance benchmarking on Linux-based systems (particularly OpenWrt, Debian,
or other embedded platforms). Whether you're validating VPN throughput, testing
router WiFi performance, measuring bufferbloat, or running an MTU discovery, the
suite covers it.

## 🤖 Implementations
Three parallel implementations share a single configuration (see `config.json`).

| Implementation | Location | Status |
|---|---|---|
| **Bash** | `bash/` | Active — modular suite (`run_ping_test.sh`, `run_speedtest.sh`, `run_bufferbloat_test.sh`, `run_ip_geolocation.sh`, etc.) |
| **Python** | `python/` | Active — modular suite (`run_ping_test.py`, `run_speedtest.py`, `run_bufferbloat_test.py`, `run_ip_geolocation_test.py`, etc.) |
| **PowerShell** | `archived/version_2.0/`, `archived/version_3.0/` | Legacy — v2.0 modules and v3.0 parallel implementations, both superseded |

### Bash prerequisites
- `bash` or `sh`
- `ping` (with `-M do` on Linux for MTU discovery, or `-f -l` on Windows)
- `traceroute`/`mtr` for path analysis
- `speedtest-cli` (Python) or Ookla speedtest CLI for throughput
- `jq` and `bc` for speedtest JSON parsing and floating-point arithmetic
- Git Bash/WSL on Windows: `tracert.exe` and `speedtest.exe` fallbacks are
  configured in `config.sh`

### Python prerequisites
```bash
python3 -m pip install -r requirements.txt
```
Required packages: `colorama`, `requests`, `speedtest-cli`

## 📝 Included Scripts

### Bash
| Script | Description |
|---|---|
| `network_diagnostics.sh` | Main menu (7 options), dispatches to each test |
| `run_ping_test.sh` | Cross-platform ping with per-probe timing, loss %, and average |
| `run_traceroute.sh` | `traceroute` or Windows `tracert.exe` fallback |
| `run_speedtest.sh` | Auto-detects Ookla or Python speedtest CLI, logs Mbps |
| `run_bufferbloat_test.sh` | MTU discovery via `-M do` (Linux), `-D -s` (macOS), `-f -l` (Windows) |
| `run_ip_geolocation.sh` | `curl` + `jq` to ip-api.com |
| `config.sh` | Cross-platform defaults, sources `config.json` |
| `custom_logging.sh` | ANSI-coloured logging utility |

### Python
| Script | Description |
|---|---|
| `network_diagnostics.py` | Menu + entry point (modern runner) |
| `run_ping_test.py` | Cross-platform ping with per-probe latency, loss %, jitter, min/max |
| `run_traceroute_test.py` | Resolves hostnames via `socket.gethostbyname`, runs `traceroute`/`tracert` |
| `run_speedtest.py` | `speedtest-cli` integration with server/sponsor/ISP detail |
| `run_ip_geolocation_test.py` | Fallback IP endpoints + ip-api.com geolocation |
| `run_bufferbloat_test.py` | Modern MTU discovery with fragmentation-pattern detection |
| `config.py` | Loads shared `config.json` |
| `custom_logging.py` | Colour-mapped log writer |

## 🖥️ Requirements
* Linux, macOS, or Windows (via WSL/Git Bash)
* `bash` or `sh` shell for the Bash suite
* `python3` with `colorama`, `requests`, `speedtest-cli` for the Python suite
* `ping`, `traceroute`/`mtr` for path diagnostics
* Root/sudo for aggressive MTU probing (`ping -f` on Windows, `ping -M do` on Linux)

## 🧪 Quick Start

### Bash
```bash
git clone https://github.com/wickedyoda/Network-Diag-Utilities.git
cd Network-Diag-Utilities
chmod +x bash/*.sh
# Optional: install jq and bc (needed for speedtest parsing)
sudo apt install jq bc   # Debian/Ubuntu
sudo yum install jq bc   # RHEL/CentOS
# Run
./bash/network_diagnostics.sh
```

### Python
```python
git clone https://github.com/wickedyoda/Network-Diag-Utilities.git
cd Network-Diag-Utilities
python3 -m pip install -r requirements.txt
# Run (from the python/ directory)
cd python
python3 network_diagnostics.py
```

## ⚙️ Configuration
All implementations share `config.json`. The default settings are:

| Key | Default | Description |
|---|---|---|
| `TargetHost` | `8.8.8.8` | Host to test |
| `PingCount` | `4` | Ping probes per run |
| `PingDelayMs` | `1000` | Delay between probes (ms) |
| `BufferStartSize` | `1500` | Start packet size for MTU discovery |
| `MTUStopSize` | `100` | Minimum packet size to test |
| `MTUDecrement` | `20` | Step size when fragmentation is detected |
| `EnableIPGeo` | `true` | Enable geolocation test |
| `SpeedtestPath` | (OS-specific) | Path to Ookla speedtest CLI |

Notes:
- The shared config was migrated from `python/config.py` and `bash/config.sh`
  on 2026-10-06 to eliminate duplication.
- IP geolocation uses `http://ip-api.com` (plaintext). For secure deployments
  prefer a TLS-capable endpoint.
