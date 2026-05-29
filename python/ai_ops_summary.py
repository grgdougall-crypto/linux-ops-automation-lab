#!/usr/bin/env python3

from pathlib import Path

PROJECT_DIR = Path.home() / "linux-ops-automation-lab"
REPORT_DIR = PROJECT_DIR / "reports"
AUTOMATION_LOG = REPORT_DIR / "daily_automation.log"


def get_latest_report():
    reports = sorted(REPORT_DIR.glob("system_report_*.txt"))
    return reports[-1] if reports else None


def extract_report_data(report_file):
    data = {
        "disk_usage": "Unavailable",
        "memory_used": "Unavailable",
        "automation_status": "UNKNOWN"
    }

    if report_file is None:
        return data

    lines = report_file.read_text().splitlines()

    for line in lines:
        if line.startswith("/dev/") and line.strip().endswith("/"):
            parts = line.split()
            if len(parts) >= 5:
                data["disk_usage"] = parts[4]

        if line.startswith("Mem:"):
            parts = line.split()
            if len(parts) >= 3:
                data["memory_used"] = parts[2]

    if AUTOMATION_LOG.exists():
        log_text = AUTOMATION_LOG.read_text()
        if "Workflow completed" in log_text:
            data["automation_status"] = "SUCCESS"
        else:
            data["automation_status"] = "CHECK LOG"

    return data


def get_disk_risk(disk_usage):
    try:
        percent = int(disk_usage.replace("%", ""))

        if percent >= 90:
            return "HIGH"
        if percent >= 70:
            return "MEDIUM"
        return "LOW"

    except ValueError:
        return "UNKNOWN"


def generate_local_ai_summary(data):
    disk_risk = get_disk_risk(data["disk_usage"])

    if disk_risk == "LOW" and data["automation_status"] == "SUCCESS":
        summary = (
            "System health appears stable. Disk usage is within normal limits, "
            "memory usage is available for review, and the daily automation workflow "
            "completed successfully."
        )
        recommendation = "Continue normal monitoring. No immediate remediation is required."
        risk_level = "LOW"

    elif disk_risk == "MEDIUM":
        summary = (
            "System health is generally stable, but disk usage is trending toward a "
            "level that should be monitored."
        )
        recommendation = "Review older reports, backups, logs, and unnecessary files."
        risk_level = "MEDIUM"

    elif disk_risk == "HIGH":
        summary = (
            "System health requires attention. Disk usage has reached a critical level "
            "and may affect system stability if not addressed."
        )
        recommendation = "Investigate disk usage immediately and remove unnecessary files or expand storage."
        risk_level = "HIGH"

    else:
        summary = (
            "System health could not be fully evaluated because some report data was unavailable."
        )
        recommendation = "Verify that system reports are being generated correctly."
        risk_level = "UNKNOWN"

    return {
        "provider": "Local Simulation",
        "summary": summary,
        "risk_level": risk_level,
        "recommendation": recommendation
    }


def main():
    latest_report = get_latest_report()
    data = extract_report_data(latest_report)
    ai_summary = generate_local_ai_summary(data)

    print("=" * 40)
    print(" Linux Ops Automation Lab")
    print(" AI Operations Summary")
    print("=" * 40)
    print()
    print(f"Provider: {ai_summary['provider']}")
    print(f"Risk Level: {ai_summary['risk_level']}")
    print()
    print("Summary:")
    print(ai_summary["summary"])
    print()
    print("Recommended Action:")
    print(ai_summary["recommendation"])


if __name__ == "__main__":
    main()
