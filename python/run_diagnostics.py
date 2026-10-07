import os
import sys
import subprocess
import datetime
import platform
import shutil
import socket

# Defensive imports
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

try:
    from colorama import init, Fore, Style
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
    from colorama import init, Fore, Style

try:
    import speedtest
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "speedtest-cli"])
    import speedtest

init(autoreset=True)

# Local modules
from config import config
from ip_geolocation import run_ip_geolocation_test
from get_validated_int_input import get_validated_int
from custom_logging import write_log_entry

# ----------------------------
# Utility
# ----------------------------
def ensure_log_dir():
    os.makedirs(config["Defaults"]["LogDirectory"], exist_ok=True)

def log_file(name):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(config["Defaults"]["LogDirectory"], f"{name}_{ts}.log")

def is_command_available(cmd):
    return shutil.which(cmd) is not None

# ----------------------------
# Tests
# ----------------------------
def run_ping_test(target, count, delay_ms, logpath, verbose=True):
    delay_sec = max(1, delay_ms // 1000)
    system = platform.system().lower()

    if system == "windows":
        cmd = ["ping", target, "-n", str(count), "-w", str(delay_ms)]
    else:
        cmd = ["ping", "-c", str(count), "-i", str(delay_sec), target]

    if not is_command_available("ping"):
        try:
            r = requests.get(f"http://{target}", timeout=3)
            write_log_entry(f"Ping fallback: HTTP status {r.status_code}", logpath)
            return {"Target": target, "AverageLatency": 0, "Jitter": 0, "LossPercent": 0}
        except Exception as e:
            write_log_entry(f"Ping not available. HTTP fallback failed: {e}", logpath)
            return None

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = result.stdout

        # Log to file
        with open(logpath, "a", encoding="utf-8") as f:
            f.write("\n--- Ping Test ---\n")
            f.write(output + "\n")

        # Echo to console if verbose
        if verbose:
            print(Fore.LIGHTBLACK_EX + "\n--- Ping Results ---" + Style.RESET_ALL)
            print(output)

        # Parse summary
        avg_latency, jitter, loss = None, None, None
        import re
        if "Average" in output:  # Windows
            match = re.search(r"Average = (\d+)ms", output)
            if match:
                avg_latency = int(match.group(1))
        else:  # Linux/macOS
            match = re.search(r"rtt .* = .*?/([\d\.]+)/", output)
            if match:
                avg_latency = float(match.group(1))

        if "Lost =" in output:
            match = re.search(r"Lost = (\d+)", output)
            if match:
                loss = int(match.group(1))
        elif "packet loss" in output:
            match = re.search(r"(\d+)% packet loss", output)
            if match:
                loss = int(match.group(1))

        return {
            "Target": target,
            "AverageLatency": avg_latency or -1,
            "Jitter": jitter or 0,
            "LossPercent": loss or 0,
        }

    except Exception as e:
        write_log_entry(f"Ping failed: {e}", logpath)
        return None

def run_traceroute_test(target, logpath, verbose=True):
    system = platform.system().lower()

    # Resolve domain to IP
    try:
        resolved_ip = socket.gethostbyname(target)
    except Exception as e:
        msg = f"DNS resolution failed: {e}"
        write_log_entry(msg, logpath)
        if verbose:
            print(Fore.RED + msg + Style.RESET_ALL)
        return False

    # Choose command
    cmd = ["tracert", resolved_ip] if system == "windows" else ["traceroute", resolved_ip]

    # Check if command is available
    if not is_command_available(cmd[0]):
        msg = f"{cmd[0]} not available on this system."
        write_log_entry(msg, logpath)
        if verbose:
            print(Fore.RED + msg + Style.RESET_ALL)
        return False

    try:
        # Start process
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        if verbose:
            print(Fore.LIGHTBLACK_EX + "\n--- Traceroute Results ---" + Style.RESET_ALL)

        with open(logpath, "a", encoding="utf-8") as f:
            f.write("\n--- Traceroute Test ---\n")

            # Stream output line by line
            for line in process.stdout:
                f.write(line)
                if verbose:
                    print(line.strip())

        # Wait for process to finish with timeout
        process.wait(timeout=30)
        return True

    except subprocess.TimeoutExpired:
        msg = f"Traceroute failed: Command '{cmd[0]}' timed out after 30 seconds"
        write_log_entry(msg, logpath)
        if verbose:
            print(Fore.RED + msg + Style.RESET_ALL)
        return False

    except Exception as e:
        msg = f"Traceroute failed: {e}"
        write_log_entry(msg, logpath)
        if verbose:
            print(Fore.RED + msg + Style.RESET_ALL)
        return False

def run_speed_test(logpath):
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download = round(st.download() / 1_000_000, 2)
        upload = round(st.upload() / 1_000_000, 2)
        ping = st.results.ping
        server = st.results.server.get("sponsor", "Unknown")
        isp = st.results.client.get("isp", "Unknown")
        summary = {
            "Download": download,
            "Upload": upload,
            "Ping": ping,
            "Server": server,
            "ISP": isp,
        }
        with open(logpath, "a", encoding="utf-8") as f:
            f.write(str(summary) + "\n")
        return summary
    except Exception as e:
        fallback = {"Download": -1, "Upload": -1, "Ping": -1, "Server": "N/A", "ISP": "N/A"}
        write_log_entry(f"Speedtest failed, using fallback: {e}", logpath)
        return fallback

    print(Fore.LIGHTBLUE_EX + "\n--- Bufferbloat MTU Discovery ---" + Style.RESET_ALL)
    write_log_entry(f"Starting bufferbloat test to {target} with DF flag", logpath)
    mtu_value = run_bufferbloat_test(target, start_size=1500, logpath=logpath, verbose=True)
    write_log_entry(f"Bufferbloat result: {mtu_value}", logpath, Fore.LIGHTBLACK_EX)
    print(Fore.LIGHTBLACK_EX + f"Bufferbloat result: {mtu_value}", Style.RESET_ALL)


def run_bufferbloat_test(target, start_size=None, logpath=None, verbose=True):
    """Bufferbloat / MTU discovery test using IP fragmentation probing.

    Sends ICMP echo packets with the Don't Fragment (DF) flag set and reduces
    the payload until a non-fragmented reply is received. Cross-platform:
    - Windows:      ping -f -l <size>
    - Linux:        ping -M do -s <size - 28>
    - macOS:        ping -D -s <size - 28>
    """
    import platform
    import subprocess
    from pathlib import Path

    from colorama import Fore, Style

    from config import config
    from custom_logging import write_log_entry

    defaults = config["Defaults"]
    if start_size is not None:
        packet_size = start_size
    else:
        packet_size = defaults["BufferStartSize"]
    min_size = defaults["MTUStopSize"]
    step = defaults["MTUDecrement"]

    log_file = Path(logpath or Path(defaults["LogDirectory"]) / "bufferbloat.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)

    write_log_entry("--- Bufferbloat / MTU Discovery ---", str(log_file), Fore.CYAN)
    write_log_entry(f"Target: {target}", str(log_file), Fore.GRAY)

    system = platform.system().lower()
    if system == "windows":
        def build_ping_args(tgt, sz):
            return ["ping", tgt, "-f", "-l", str(sz), "-n", "1"]
    elif system == "linux":
        def build_ping_args(tgt, sz):
            payload = max(0, sz - 28)
            args = ["ping", "-c", "1", "-s", str(payload), tgt]
            args.insert(3, "-M")
            args.insert(4, "do")
            return args
    else:
        # macOS (and others)
        def build_ping_args(tgt, sz):
            payload = max(0, sz - 28)
            return ["ping", "-c", "1", "-D", "-s", str(payload), tgt]

    while packet_size >= min_size:
        write_log_entry(f"Testing with packet size: {packet_size} bytes", str(log_file), Fore.YELLOW)
        cmd = build_ping_args(target, packet_size)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        except FileNotFoundError:
            write_log_entry("Ping command not available for MTU discovery.", str(log_file), Fore.RED)
            return False
        except subprocess.TimeoutExpired:
            write_log_entry(f"Timeout at {packet_size} bytes", str(log_file), Fore.RED)
            packet_size -= step
            continue

        output = (result.stdout or "") + (result.stderr or "")
        with open(log_file, "a", encoding="utf-8") as handle:
            handle.write(output + "\n")

        fragmented = any(
            phrase in output
            for phrase in [
                "Packet needs to be fragmented",
                "message too long",
                "Frag needed",
                "DF set",
            ]
        )

        if fragmented or result.returncode != 0:
            write_log_entry(
                f"Fragmentation detected at {packet_size} bytes. Reducing size...",
                str(log_file),
                Fore.RED,
            )
            packet_size -= step
            continue

        write_log_entry(
            f"Non-fragmented response at {packet_size} bytes. Bufferbloat unlikely at this size.",
            str(log_file),
            Fore.GREEN,
        )
        if verbose:
            print(Fore.GREEN + f"Maximum non-fragmented packet size: {packet_size} bytes" + Style.RESET_ALL)
        return packet_size

    write_log_entry(
        f"Unable to find non-fragmented size above {min_size} bytes.",
        str(log_file),
        Fore.RED,
    )
    if verbose:
        print(Fore.RED + f"Unable to find non-fragmented size above {min_size} bytes." + Style.RESET_ALL)
    return None


def run_all_tests(target, logpath):
    print(Fore.LIGHTBLACK_EX + f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting diagnostics..." + Style.RESET_ALL)
    write_log_entry(f"Running full diagnostics on {target}", logpath, Fore.CYAN)

    # IP Geolocation
    print(Fore.LIGHTBLUE_EX + "\n--- IP Geolocation ---" + Style.RESET_ALL)
    geo_summary = run_ip_geolocation_test(logpath)

    # Ping Test
    print(Fore.LIGHTBLUE_EX + "\n--- Ping Test ---" + Style.RESET_ALL)
    ping_summary = run_ping_test(target, config["Defaults"]["PingCount"], config["Defaults"]["PingDelay"], logpath, verbose=True)

    # Traceroute
    print(Fore.LIGHTBLUE_EX + "\n--- Traceroute ---" + Style.RESET_ALL)
    traceroute_ok = run_traceroute_test(target, logpath, verbose=True)
    if traceroute_ok:
        print(Fore.LIGHTBLACK_EX + "Traceroute completed." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Traceroute failed or blocked by target (common with CDNs)." + Style.RESET_ALL)

    # Bufferbloat / MTU Discovery
    print(Fore.LIGHTBLUE_EX + "\n--- Bufferbloat Test (MTU Discovery) ---" + Style.RESET_ALL)
    mtu_success = run_bufferbloat_test(target, start_size=1500, logpath=logpath, verbose=True)
    if mtu_success:
        print(Fore.LIGHTBLACK_EX + "Bufferbloat test completed." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Bufferbloat test failed or unsupported on this platform." + Style.RESET_ALL)

    # Speed Test
    print(Fore.LIGHTBLUE_EX + "\n--- Speed Test ---" + Style.RESET_ALL)
    speed_summary = run_speed_test(logpath)

    # Summary Dashboard
    print(Fore.CYAN + "\n--- Summary Dashboard ---" + Style.RESET_ALL)
    with open(logpath, "a", encoding="utf-8") as f:
        f.write("\n--- Summary Dashboard ---\n")

        if geo_summary:
            line = f"GeoIP: {geo_summary.get('City')}, {geo_summary.get('Country')} (ISP: {geo_summary.get('ISP')})"
            print(Fore.LIGHTBLACK_EX + line + Style.RESET_ALL)
            f.write(line + "\n")

        if ping_summary:
            latency = ping_summary['AverageLatency']
            loss = ping_summary['LossPercent']
            color = Fore.GREEN if loss == 0 and latency < 50 else Fore.YELLOW if loss < 10 else Fore.RED
            line = (f"Ping to {ping_summary['Target']}: "
                    f"{latency}ms avg, "
                    f"{ping_summary['Jitter']}ms jitter, "
                    f"{loss}% loss")
            print(color + line + Style.RESET_ALL)
            f.write(line + "\n")

        if speed_summary:
            print(Fore.GREEN + "\n--- Speedtest Results ---" + Style.RESET_ALL)
            print(Fore.YELLOW + f"Download: {speed_summary['Download']} Mbps" + Style.RESET_ALL)
            print(Fore.YELLOW + f"Upload:   {speed_summary['Upload']} Mbps" + Style.RESET_ALL)
            print(Fore.YELLOW + f"Ping:     {speed_summary['Ping']} ms" + Style.RESET_ALL)
            print(Fore.LIGHTBLACK_EX + f"Server:   {speed_summary['Server']}" + Style.RESET_ALL)
            print(Fore.LIGHTBLACK_EX + f"ISP:      {speed_summary['ISP']}" + Style.RESET_ALL)

            f.write(f"\n--- Speedtest Results ---\n")
            f.write(f"Download: {speed_summary['Download']} Mbps\n")
            f.write(f"Upload:   {speed_summary['Upload']} Mbps\n")
            f.write(f"Ping:     {speed_summary['Ping']} ms\n")
            f.write(f"Server:   {speed_summary['Server']}\n")
            f.write(f"ISP:      {speed_summary['ISP']}\n")

    # Optional: persist MTU result to config
   # if mtu_success:
    #    try:
     #       with open("mtu_result.txt", "w") as mtu_file:
      #          mtu_file.write(f"MTU discovered for {target}: #{config['Defaults'].get('LastMTU', 'unknown')} bytes\n")
      #  except Exception as e:
       #     print(Fore.RED + f"Failed to write MTU result: {e}" + Style.RESET_ALL)

    write_log_entry("Traceroute and bufferbloat results logged to file.", logpath, Fore.LIGHTBLACK_EX)
    print(Fore.GREEN + "\nDiagnostics complete. Results saved to log file." + Style.RESET_ALL)
def main_menu():
    ensure_log_dir()
    print(Fore.CYAN + "\nNetwork Diagnostics Menu" + Style.RESET_ALL)
    print("1. Run full diagnostics")
    print("2. Run ping test")
    print("3. Run traceroute")
    print("4. Run speed test")
    print("5. Run bufferbloat test")
    print("6. Run IP geolocation")
    print("0. Exit")

    choice = get_validated_int("Select an option", 1, 0, 6, "menu choice")

    default_target = config["Defaults"]["TargetHost"]
    target = input(f"Enter target IP or URL (default: {default_target}): ").strip()
    if not target:
        target = default_target

    logpath = log_file("Diagnostics")

    if choice == 1:
        run_all_tests(target, logpath)
    elif choice == 2:
        run_ping_test(target, config["Defaults"]["PingCount"], config["Defaults"]["PingDelay"], logpath)
    elif choice == 3:
        run_traceroute_test(target, logpath)
    elif choice == 4:
        run_speed_test(logpath)
    elif choice == 5:
        mtu_success = run_bufferbloat_test(target, start_size=1500, logpath=logpath, verbose=True)
        if mtu_success:
            print(Fore.LIGHTBLACK_EX + "Bufferbloat test completed." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Bufferbloat test failed or unsupported on this platform." + Style.RESET_ALL)
    elif choice == 6:
        run_ip_geolocation_test(logpath)
    else:
        print(Fore.LIGHTBLACK_EX + "Exiting diagnostics." + Style.RESET_ALL)

    print(Fore.GREEN + "\nDone. You can find results in your log file." + Style.RESET_ALL)

# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    main_menu()
