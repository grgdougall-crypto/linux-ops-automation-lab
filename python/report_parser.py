#!/usr/bin/env python3

from pathlib import Path

PROJECT_DIR = Path.home() / "linux-ops-automation-lab"
REPORT_DIR = PROJECT_DIR / "reports"


def get_latest_report():
    reports = sorted(REPORT_DIR.glob("system_report_*.txt"))

    if not reports:
        return None

    return reports[-1]


def print_section(title):
    print()
    print("=" * 33)
    print(title)
    print("=" * 33)


def main():
    latest_report = get_latest_report()

    if latest_report is None:
        print("No system reports found.")
        print("Run ./scripts/generate_system_report.sh first.")
        return

    print_section("Linux Ops Automation Lab")
    print("Parsed System Report Summary")
    print(f"Source file: {latest_report.name}")

    content = latest_report.read_text()

    print_section("Report Preview")

    lines = content.splitlines()

    for line in lines:
        if "Generated:" in line:
            print(line)
        elif line == "trickydeb":
            print(f"Hostname: {line}")
        elif "/dev/nvme" in line and " /" in line:
            print(f"Root Disk: {line}")
        elif line.startswith("Mem:"):
            print(f"Memory: {line}")
        elif "load average" in line:
            print(f"Uptime: {line}")

    print_section("Summary")
    print("Report parsed successfully.")
    print("System health data is available for review.")


if __name__ == "__main__":
    main()
