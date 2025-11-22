#!/usr/bin/env python3

import datetime
import os
from pathlib import Path

from colorama import Fore, Style

from config import config
from custom_logging import write_log_entry
from get_validated_int_input import get_validated_int
from run_bufferbloat_test import run_bufferbloat_test
from run_ip_geolocation_test import run_ip_geolocation_test
from run_ping_test import run_ping_test
from run_speedtest import run_speed_test
from run_traceroute_test import run_traceroute_test


def _log_path(prefix: str) -> Path:
    base = Path(config["Defaults"]["LogDirectory"])
    base.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return base / f"{prefix}_{ts}.log"


def _run_all_tests(target: str):
    log_file = _log_path("FullDiagnostics")
    write_log_entry(f"Running full diagnostics on {target}", str(log_file), Fore.CYAN)

    geo_summary = run_ip_geolocation_test(str(log_file)) if config["Defaults"].get("EnableIPGeo", True) else None
    ping_summary = run_ping_test(target, log_path=str(log_file))
    traceroute_ok = run_traceroute_test(target, str(log_file))
    buffer_result = run_bufferbloat_test(target, log_path=str(log_file))
    speed_summary = run_speed_test(str(log_file))

    write_log_entry("\n--- Summary Dashboard ---", str(log_file), Fore.CYAN)
    if geo_summary:
        write_log_entry(
            f"GeoIP: {geo_summary['City']}, {geo_summary['Country']} (ISP: {geo_summary['ISP']})",
            str(log_file),
            Fore.LIGHTBLACK_EX,
        )
    if ping_summary:
        write_log_entry(
            (
                f"Ping to {ping_summary['Target']}: {ping_summary['AverageLatency']}ms avg, "
                f"{ping_summary['Jitter']}ms jitter, {ping_summary['LossPercent']}% loss"
            ),
            str(log_file),
            Fore.YELLOW,
        )
    if traceroute_ok:
        write_log_entry("Traceroute completed.", str(log_file), Fore.GREEN)
    if buffer_result:
        write_log_entry(f"MTU discovered: {buffer_result} bytes", str(log_file), Fore.GREEN)
    if speed_summary:
        write_log_entry(
            f"Download: {speed_summary['Download']} Mbps | Upload: {speed_summary['Upload']} Mbps | Ping: {speed_summary['Ping']} ms",
            str(log_file),
            Fore.YELLOW,
        )


def main():
    defaults = config["Defaults"]
    print(Fore.CYAN + "\n--- Network Diagnostics ---" + Style.RESET_ALL)
    print("1. Ping Test")
    print("2. Traceroute Test")
    print("3. Speed Test")
    print("4. Bufferbloat Test")
    print("5. IP Geolocation Test")
    print("6. Run All Tests")
    print("7. Exit")

    choice = get_validated_int("Enter your choice", default=7, min_value=1, max_value=7, label="menu choice")
    if choice == 7:
        print(Fore.LIGHTBLACK_EX + "Exiting diagnostics suite." + Style.RESET_ALL)
        return

    target = input(f"Enter target host (default: {defaults['TargetHost']}): ").strip() or defaults["TargetHost"]

    if choice == 1:
        log_path = _log_path("Ping")
        run_ping_test(target, log_path=str(log_path))
    elif choice == 2:
        log_path = _log_path("Traceroute")
        run_traceroute_test(target, str(log_path))
    elif choice == 3:
        log_path = _log_path("Speedtest")
        run_speed_test(str(log_path))
    elif choice == 4:
        log_path = _log_path("Bufferbloat")
        start_size = defaults["BufferStartSize"]
        run_bufferbloat_test(target, start_size=start_size, log_path=str(log_path))
    elif choice == 5:
        log_path = _log_path("IPGeo")
        run_ip_geolocation_test(str(log_path))
    elif choice == 6:
        _run_all_tests(target)


if __name__ == "__main__":
    main()

