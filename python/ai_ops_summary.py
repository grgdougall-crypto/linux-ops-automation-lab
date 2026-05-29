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
    findings = []

    disk_risk = get_disk_risk(data["disk_usage"])

    if disk_risk == "LOW":
        findings.append(f"Disk utilization remains healthy at {data['disk_usage']}.")
    elif disk_risk == "MEDIUM":
        findings.append(
            f"Disk utilization is elevated at {data['disk_usage']} and should be monitored."
        )
    elif disk_risk == "HIGH":
        findings.append(
            f"Disk utilization is critically high at {data['disk_usage']}."
        )
    else:
        findings.append("Disk utilization could not be evaluated from the latest report.")

    if data["automation_status"] == "SUCCESS":
        findings.append("Daily automation workflow completed successfully.")
    else:
        findings.append("Automation workflow requires review.")

    if data["memory_used"] != "Unavailable":
        findings.append(f"Current memory usage is {data['memory_used']}.")
    else:
        findings.append("Memory usage data was unavailable in the latest report.")

    if disk_risk == "LOW" and data["automation_status"] == "SUCCESS":
        risk_level = "LOW"
        recommendation = "Continue normal monitoring. No immediate remediation is required."
    elif disk_risk == "MEDIUM":
        risk_level = "MEDIUM"
        recommendation = "Review backups, logs, and unused files to control storage growth."
    elif disk_risk == "HIGH":
        risk_level = "HIGH"
        recommendation = "Investigate disk usage immediately and review operational logs."
    else:
        risk_level = "UNKNOWN"
        recommendation = "Verify that reports and automation logs are being generated correctly."

    summary = " ".join(findings)

    return {
        "provider": "Local Simulation",
        "summary": summary,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "findings": findings
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
    print("Key Findings:")
    for finding in ai_summary["findings"]:
        print(f"- {finding}")
    print()
    print("Summary:")
    print(ai_summary["summary"])
    print()
    print("Recommended Action:")
    print(ai_summary["recommendation"])


if __name__ == "__main__":
    main()
