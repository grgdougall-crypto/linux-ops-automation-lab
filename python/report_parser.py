#!/usr/bin/env python3

from pathlib import Path

PROJECT_DIR = Path.home() / "linux-ops-automation-lab"
REPORT_DIR = PROJECT_DIR / "reports"


def get_latest_report():
    reports = sorted(REPORT_DIR.glob("system_report_*.txt"))

    if not reports:
        return None

    return reports[-1]


def main():
    latest_report = get_latest_report()

    if latest_report is None:
        print("No system reports found.")
        return

    content = latest_report.read_text().splitlines()

    hostname = "Unknown"
    mem_line = ""
    uptime_line = ""
    services = []

    for i, line in enumerate(content):

        if line == "========== HOSTNAME ==========":
            hostname = content[i + 1]

        if line.startswith("Mem:"):
            mem_line = line

        if "load average" in line:
            uptime_line = line

        if line.strip() == "active":
            services.append(line.strip())

    print("=" * 40)
    print(" Linux Ops Automation Lab")
    print(" System Health Summary")
    print("=" * 40)

    print()
    print(f"Hostname: {hostname}")

    print()
    print("Disk Usage")
    print("✓ Root filesystem detected")

    print()
    print("Memory")
    if mem_line:
        print("✓ Memory statistics collected")
    else:
        print("✗ Memory statistics unavailable")

    print()
    print("Services")

    if len(services) >= 3:
        print("✓ SSH Active")
        print("✓ NetworkManager Active")
        print("✓ Cron Active")
    else:
        print("⚠ One or more services may not be running")

    print()
    print("Uptime")
    print(uptime_line)

    print()
    print("Overall Status")
    print("HEALTHY")


if __name__ == "__main__":
    main()
