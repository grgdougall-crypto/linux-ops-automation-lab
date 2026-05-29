#!/usr/bin/env python3

from pathlib import Path
import re

PROJECT_DIR = Path.home() / "linux-ops-automation-lab"
REPORT_DIR = PROJECT_DIR / "reports"


def get_reports():
    return sorted(REPORT_DIR.glob("system_report_*.txt"))


def extract_root_disk_usage(report_text):
    for line in report_text.splitlines():
        if " /" in line and "%" in line and line.startswith("/dev/"):
            match = re.search(r"(\d+)%", line)
            if match:
                return int(match.group(1))
    return None


def extract_memory_used(report_text):
    for line in report_text.splitlines():
        if line.startswith("Mem:"):
            parts = line.split()
            if len(parts) >= 3:
                return parts[2]
    return None


def main():
    reports = get_reports()

    print("=" * 40)
    print(" Linux Ops Automation Lab")
    print(" Trend Analysis")
    print("=" * 40)
    print()

    if len(reports) < 2:
        print("Not enough reports for trend analysis.")
        print("Generate at least two system reports first.")
        return

    oldest_report = reports[0]
    newest_report = reports[-1]

    oldest_text = oldest_report.read_text()
    newest_text = newest_report.read_text()

    old_disk = extract_root_disk_usage(oldest_text)
    new_disk = extract_root_disk_usage(newest_text)

    old_memory = extract_memory_used(oldest_text)
    new_memory = extract_memory_used(newest_text)

    print(f"Reports analyzed: {len(reports)}")
    print(f"Oldest report: {oldest_report.name}")
    print(f"Newest report: {newest_report.name}")
    print()

    print("Disk Usage Trend")
    if old_disk is not None and new_disk is not None:
        change = new_disk - old_disk
        print(f"Root filesystem: {old_disk}% → {new_disk}%")
        print(f"Change: {change:+d}%")
    else:
        print("Disk usage data unavailable.")
    print()

    print("Memory Usage Trend")
    if old_memory and new_memory:
        print(f"Used memory: {old_memory} → {new_memory}")
    else:
        print("Memory usage data unavailable.")
    print()

    print("Status")
    if old_disk is not None and new_disk is not None:
        if new_disk >= 90:
            print("AT RISK: Disk usage is critically high.")
        elif new_disk >= 75:
            print("NEEDS REVIEW: Disk usage is elevated.")
        elif new_disk > old_disk:
            print("STABLE: Disk usage increased slightly but remains healthy.")
        else:
            print("HEALTHY: Disk usage is stable.")
    else:
        print("UNKNOWN: Unable to determine disk trend.")


if __name__ == "__main__":
    main()
