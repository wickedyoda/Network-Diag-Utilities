from pathlib import Path

import speedtest
from colorama import Fore, Style

from config import config
from custom_logging import write_log_entry


def run_speed_test(log_path: str | None = None):
    log_file = Path(log_path or Path(config["Defaults"]["LogDirectory"]) / "speedtest.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)

    write_log_entry("--- Speed Test ---", str(log_file), Fore.CYAN)

    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download = round(st.download() / 1_000_000, 2)
        upload = round(st.upload() / 1_000_000, 2)
        ping = round(st.results.ping, 2)
        server = st.results.server.get("name", "Unknown")
        server_id = st.results.server.get("id", "N/A")
        isp = st.results.client.get("isp", "Unknown")
    except Exception as exc:
        write_log_entry(f"Speedtest failed: {exc}", str(log_file), Fore.RED)
        return None

    summary = {
        "Download": download,
        "Upload": upload,
        "Ping": ping,
        "Server": server,
        "ServerId": server_id,
        "ISP": isp,
    }

    with open(log_file, "a", encoding="utf-8") as handle:
        handle.write(f"Download: {download} Mbps\n")
        handle.write(f"Upload:   {upload} Mbps\n")
        handle.write(f"Ping:     {ping} ms\n")
        handle.write(f"Server:   {server} [ID: {server_id}]\n")
        handle.write(f"ISP:      {isp}\n")

    print(Fore.GREEN + "\n--- Speedtest Results ---" + Style.RESET_ALL)
    print(Fore.YELLOW + f"Download: {download} Mbps" + Style.RESET_ALL)
    print(Fore.YELLOW + f"Upload:   {upload} Mbps" + Style.RESET_ALL)
    print(Fore.YELLOW + f"Ping:     {ping} ms" + Style.RESET_ALL)
    print(Fore.LIGHTBLACK_EX + f"Server:   {server} [ID: {server_id}]" + Style.RESET_ALL)
    print(Fore.LIGHTBLACK_EX + f"ISP:      {isp}" + Style.RESET_ALL)

    return summary

