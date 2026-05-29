from flask import Flask, render_template
from pathlib import Path
import socket

app = Flask(__name__)

PROJECT_DIR = Path.home() / "linux-ops-automation-lab"
REPORT_DIR = PROJECT_DIR / "reports"
AUTOMATION_LOG = REPORT_DIR / "daily_automation.log"


def get_latest_report_data():
    reports = sorted(REPORT_DIR.glob("system_report_*.txt"))

    if not reports:
        return {
            "latest_report": "No reports found",
            "report_count": 0,
            "disk_usage": "Unavailable",
            "memory_used": "Unavailable",
            "trend_status": "UNKNOWN",
            "automation_status": "UNKNOWN"
        }

    latest_report = reports[-1]
    content = latest_report.read_text().splitlines()

    disk_usage = "Unavailable"
    memory_used = "Unavailable"

    for line in content:
        if line.startswith("/dev/") and line.strip().endswith("/"):
            parts = line.split()
            if len(parts) >= 5:
                disk_usage = parts[4]

        if line.startswith("Mem:"):
            parts = line.split()
            if len(parts) >= 3:
                memory_used = parts[2]

    trend_status = "STABLE"
    automation_status = get_automation_status()

    return {
        "latest_report": latest_report.name,
        "report_count": len(reports),
        "disk_usage": disk_usage,
        "memory_used": memory_used,
        "trend_status": trend_status,
        "automation_status": automation_status
    }


def get_automation_status():
    if not AUTOMATION_LOG.exists():
        return "NO LOG FOUND"

    log_content = AUTOMATION_LOG.read_text()

    if "Workflow completed" in log_content:
        return "SUCCESS"

    return "CHECK LOG"


@app.route("/")
def home():
    report_data = get_latest_report_data()

    return render_template(
        "index.html",
        hostname=socket.gethostname(),
        latest_report=report_data["latest_report"],
        report_count=report_data["report_count"],
        disk_usage=report_data["disk_usage"],
        memory_used=report_data["memory_used"],
        trend_status=report_data["trend_status"],
        automation_status=report_data["automation_status"],
        health_score="100/100",
        status="HEALTHY"
    )


if __name__ == "__main__":
    app.run(debug=True)
