import platform
import subprocess
from pathlib import Path

from colorama import Fore, Style

from config import config
from custom_logging import write_log_entry


def _build_ping_args(target: str, size: int) -> list[str]:
    system = platform.system().lower()
    if system == "windows":
        return ["ping", target, "-f", "-l", str(size), "-n", "1"]
    # Linux and macOS
    payload = max(0, size - 28)
    args = ["ping", "-c", "1", "-s", str(payload), target]
    # Linux supports -M do; macOS will ignore the flag
    if system == "linux":
        args.insert(3, "-M")
        args.insert(4, "do")
    return args


def run_bufferbloat_test(target: str, start_size: int | None = None, log_path: str | None = None):
    defaults = config["Defaults"]
    packet_size = start_size or defaults["BufferStartSize"]
    min_size = defaults["MTUStopSize"]
    step = defaults["MTUDecrement"]

    log_file = Path(log_path or Path(defaults["LogDirectory"]) / "bufferbloat.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)

    write_log_entry("--- Bufferbloat / MTU Discovery ---", str(log_file), Fore.CYAN)
    write_log_entry(f"Target: {target}", str(log_file), Fore.GRAY)

    while packet_size >= min_size:
        write_log_entry(f"Testing with packet size: {packet_size} bytes", str(log_file), Fore.YELLOW)
        cmd = _build_ping_args(target, packet_size)

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
        print(Fore.GREEN + f"Maximum non-fragmented packet size: {packet_size} bytes" + Style.RESET_ALL)
        return packet_size

    write_log_entry(
        f"Unable to find non-fragmented size above {min_size} bytes.",
        str(log_file),
        Fore.RED,
    )
    return None

