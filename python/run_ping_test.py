import platform
import re
import subprocess
from pathlib import Path

from colorama import Fore, Style

from config import config
from custom_logging import write_log_entry


def _ping_command(target: str, count: int, delay_ms: int) -> list[str]:
    system = platform.system().lower()
    if system == "windows":
        return ["ping", target, "-n", str(count), "-w", str(delay_ms)]
    interval = max(1, int(delay_ms / 1000))
    return ["ping", "-c", str(count), "-i", str(interval), target]


def _parse_ping_output(output: str) -> tuple[list[float], float]:
    latencies: list[float] = []
    loss_percent = 0.0

    # Capture per-reply times
    for match in re.finditer(r"time[=<]([0-9.]+) ?ms", output):
        try:
            latencies.append(float(match.group(1)))
        except ValueError:
            continue

    # Capture loss from summary
    loss_match = re.search(r"(\d+)%\s+packet loss|Lost = \d+ \((\d+)%\)", output, re.IGNORECASE)
    if loss_match:
        percent = next((g for g in loss_match.groups() if g), None)
        if percent is not None:
            loss_percent = float(percent)

    return latencies, loss_percent


def run_ping_test(target: str, count: int | None = None, delay_ms: int | None = None, log_path: str | None = None):
    count = count or config["Defaults"]["PingCount"]
    delay_ms = delay_ms or config["Defaults"]["PingDelay"]
    log_file = Path(log_path or Path(config["Defaults"]["LogDirectory"]) / "ping.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)

    write_log_entry("--- Ping Test ---", str(log_file), "Cyan")
    write_log_entry(f"Pinging {target} {count} times...", str(log_file), "Gray")

    cmd = _ping_command(target, count, delay_ms)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        write_log_entry("Ping command not available on this system.", str(log_file), "Red")
        return None

    output = result.stdout or result.stderr or ""
    with open(log_file, "a", encoding="utf-8") as handle:
        handle.write(output + "\n")

    latencies, loss_percent = _parse_ping_output(output)
    jitter = 0.0
    if len(latencies) > 1:
        diffs = [abs(latencies[i] - latencies[i - 1]) for i in range(1, len(latencies))]
        jitter = sum(diffs) / len(diffs)

    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    min_latency = min(latencies) if latencies else 0.0
    max_latency = max(latencies) if latencies else 0.0

    print(Fore.CYAN + "\nPing statistics" + Style.RESET_ALL)
    print(Fore.LIGHTBLACK_EX + output + Style.RESET_ALL)

    return {
        "Target": target,
        "Sent": count,
        "Received": count - int((loss_percent / 100) * count),
        "Lost": int((loss_percent / 100) * count),
        "LossPercent": loss_percent,
        "AverageLatency": round(avg_latency, 2),
        "Jitter": round(jitter, 2),
        "MinLatency": round(min_latency, 2),
        "MaxLatency": round(max_latency, 2),
    }

