#!/usr/bin/env python3

from pathlib import Path

PROJECT_DIR = Path.home() / "linux-ops-automation-lab"
REPORT_DIR = PROJECT_DIR / "reports"


def get_latest_report():
    reports = sorted(REPORT_DIR.glob("system_report_*.txt"))
    return reports[-1] if reports else None


def main():
    latest_report = get_latest_report()

    if latest_report is None:
        print("No system reports found.")
        print("Run ./scripts/generate_system_report.sh first.")
        return

    content = latest_report.read_text()

    score = 0
    max_score = 100

    print("=" * 40)
    print(" Linux Ops Automation Lab")
    print(" Health Score Assessment")
    print("=" * 40)
    print()
    print(f"Source report: {latest_report.name}")
    print()

    if "========== MEMORY USAGE ==========" in content and "Mem:" in content:
        score += 25
        print("Memory Data        +25")
    else:
        print("Memory Data         +0")

    if "========== DISK USAGE ==========" in content and "/dev/" in content:
        score += 25
        print("Disk Data          +25")
    else:
        print("Disk Data           +0")

    active_count = content.count("active")

    if active_count >= 3:
        score += 50
        print("Core Services      +50")
    elif active_count > 0:
        score += 25
        print("Core Services      +25")
    else:
        print("Core Services       +0")

    print()
    print("-" * 40)
    print(f"Overall Score: {score}/{max_score}")

    if score >= 90:
        status = "HEALTHY"
    elif score >= 60:
        status = "NEEDS REVIEW"
    else:
        status = "AT RISK"

    print(f"Status: {status}")
    print("-" * 40)


if __name__ == "__main__":
    main()
