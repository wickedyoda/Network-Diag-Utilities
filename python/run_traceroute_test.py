import platform
import socket
import subprocess
from pathlib import Path

from colorama import Fore, Style

from config import config
from custom_logging import write_log_entry


def run_traceroute_test(target: str, log_path: str | None = None):
    log_file = Path(log_path or Path(config["Defaults"]["LogDirectory"]) / "traceroute.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)

    write_log_entry("--- Traceroute Test ---", str(log_file), Fore.CYAN)

    try:
        resolved_target = socket.gethostbyname(target)
    except Exception as exc:
        write_log_entry(f"DNS resolution failed: {exc}", str(log_file), Fore.RED)
        return False

    system = platform.system().lower()
    cmd = ["tracert", resolved_target] if system == "windows" else ["traceroute", resolved_target]

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    except FileNotFoundError:
        write_log_entry(f"{cmd[0]} command not available.", str(log_file), Fore.RED)
        return False

    with open(log_file, "a", encoding="utf-8") as handle:
        for line in process.stdout or []:
            handle.write(line)
            print(Fore.LIGHTBLACK_EX + line.strip() + Style.RESET_ALL)

    return process.wait() == 0

