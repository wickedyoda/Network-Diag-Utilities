from pathlib import Path

import requests
from colorama import Fore

from config import config
from custom_logging import write_log_entry


FALLBACK_IP_ENDPOINTS = [
    "https://api.ipify.org?format=json",
    "https://ipinfo.io/json",
    "https://ifconfig.me/ip",
]


def _resolve_external_ip(log_file: Path) -> str | None:
    for url in FALLBACK_IP_ENDPOINTS:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json() if "json" in response.headers.get("Content-Type", "") else response.text
            ip_value = data.get("ip") if isinstance(data, dict) else data
            if ip_value:
                write_log_entry(f"Detected external IP: {ip_value}", str(log_file), Fore.GREEN)
                return str(ip_value).strip()
        except Exception as exc:
            write_log_entry(f"Failed to retrieve IP from {url}: {exc}", str(log_file), Fore.YELLOW)
    return None


def run_ip_geolocation_test(log_path: str | None = None):
    if not config["Defaults"].get("EnableIPGeo", True):
        return None

    log_file = Path(log_path or Path(config["Defaults"]["LogDirectory"]) / "ip_geolocation.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)

    write_log_entry("--- IP Geolocation Test ---", str(log_file), Fore.CYAN)

    external_ip = _resolve_external_ip(log_file)
    if not external_ip:
        write_log_entry("Unable to determine external IP address.", str(log_file), Fore.RED)
        return None

    try:
        geo_response = requests.get(f"http://ip-api.com/json/{external_ip}", timeout=8)
        geo_response.raise_for_status()
        geo_json = geo_response.json()
    except Exception as exc:
        write_log_entry(f"Geolocation lookup failed: {exc}", str(log_file), Fore.RED)
        return None

    if geo_json.get("status") != "success":
        write_log_entry(f"Geolocation lookup failed for {external_ip}", str(log_file), Fore.RED)
        return None

    summary = {
        "ISP": geo_json.get("isp", "Unknown"),
        "City": geo_json.get("city", "Unknown"),
        "Region": geo_json.get("regionName", "Unknown"),
        "Country": geo_json.get("country", "Unknown"),
        "Timezone": geo_json.get("timezone", "Unknown"),
        "IP": external_ip,
    }

    details = ", ".join(
        [
            f"ISP: {summary['ISP']}",
            f"City: {summary['City']}",
            f"Region: {summary['Region']}",
            f"Country: {summary['Country']}",
            f"Timezone: {summary['Timezone']}",
        ]
    )
    write_log_entry(details, str(log_file), Fore.GRAY)
    return summary

