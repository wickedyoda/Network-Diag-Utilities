# Network-Diag-Utilities


## 🚀 Overview  
Network-Diag-Utilities is a lightweight collection of shell scripts designed for network diagnostics, troubleshooting, and performance benchmarking on Linux-based systems (particularly OpenWrt, Debian, or other embedded platforms). Whether you’re validating VPN throughput, testing router WiFi performance, or measuring bufferbloat, these tools help you quickly collect reliable data.

---

## 🔧 Features  
* **iPerf3 test wrappers** – simplified commands to benchmark throughput, upload/download, reverse tests.  
* **Bufferbloat script** – tests MTU fragmentation, checks for latency under load.  
* **Network path analysis** – tools to run traceroute, mtr, latency jitter checks.  
* **Router/Client automation** – deploy these scripts on embedded devices like GL.iNet, OpenWrt routers for consistent workflows.  
* **Minimal dependencies** – built for environments with BusyBox or limited space.

---

## 📝 Included Scripts  
| Script | Description |
|--------|-------------|
| `bufferbloat-test.sh` | Detects MTU issues and fragmentation, logs packet size where performance drops. |
| `iperf3-client.sh` | Runs iPerf3 download/upload tests, gathers results for reporting. |
| `mtr-latency.sh` | Conducts MTR/traceroute sessions and logs latency + hops for network path diagnosis. |
| `router-deploy.sh` | Automates deployment of diagnostics on GL.iNet/OpenWrt router environments. |

---

## 🖥️ Requirements  
* Linux or embedded system (Debian, OpenWrt, etc.)  
* `bash` or `sh` shell  
* `ping`, `traceroute`/`mtr`, `iperf3` installed for full feature set  
* Sufficient free space if running extended tests (especially on embedded)  

---

## 🧪 Quick Start  
1. Clone the repo:  
   ```bash
   git clone https://github.com/wickedyoda/Network-Diag-Utilities.git
   cd Network-Diag-Utilities
