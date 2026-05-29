from flask import Flask, render_template
from pathlib import Path
import socket

app = Flask(__name__)

PROJECT_DIR = Path.home() / "linux-ops-automation-lab"
REPORT_DIR = PROJECT_DIR / "reports"
AUTOMATION_LOG = REPORT_DIR / "daily_automation.log"


def get_automation_info():
    if not AUTOMATION_LOG.exists():
        return {"status": "NO LOG FOUND", "last_run": "Unknown"}

    log_content = AUTOMATION_LOG.read_text().splitlines()

    for line in reversed(log_content):
        if "Workflow completed:" in line:
            return {
                "status": "SUCCESS",
                "last_run": line.replace("Workflow completed:", "").strip()
            }

    return {"status": "CHECK LOG", "last_run": "Unknown"}


def calculate_health_score(report_file):
    score = 0

    try:
        content = report_file.read_text().lower()

        if "mem:" in content:
            score += 25

        if "/dev/" in content:
            score += 25

        if "active" in content:
            score += 50

    except Exception:
        return 0

    return score


def format_chart_label(report):
    timestamp = report.stem.replace("system_report_", "")
    parts = timestamp.split("_")

    if len(parts) == 2:
        return parts[1][:5]

    return timestamp


def get_latest_report_data():
    reports = sorted(REPORT_DIR.glob("system_report_*.txt"))

    if not reports:
        return {
            "latest_report": "No reports found",
            "report_count": 0,
            "disk_usage": "Unavailable",
            "memory_used": "Unavailable",
            "trend_status": "UNKNOWN",
            "chart_labels": [],
            "chart_scores": [],
            "current_health_score": 0
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

    recent_reports = reports[-7:]
    chart_labels = [format_chart_label(report) for report in recent_reports]
    chart_scores = [calculate_health_score(report) for report in recent_reports]
    current_health_score = calculate_health_score(latest_report)

    return {
        "latest_report": latest_report.name,
        "report_count": len(reports),
        "disk_usage": disk_usage,
        "memory_used": memory_used,
        "trend_status": "STABLE",
        "chart_labels": chart_labels,
        "chart_scores": chart_scores,
        "current_health_score": current_health_score
    }


@app.route("/")
def home():
    report_data = get_latest_report_data()
    automation_data = get_automation_info()

    return render_template(
        "index.html",
        hostname=socket.gethostname(),
        latest_report=report_data["latest_report"],
        report_count=report_data["report_count"],
        disk_usage=report_data["disk_usage"],
        memory_used=report_data["memory_used"],
        trend_status=report_data["trend_status"],
        automation_status=automation_data["status"],
        last_run=automation_data["last_run"],
        chart_labels=report_data["chart_labels"],
        chart_scores=report_data["chart_scores"],
        health_score=f"{report_data['current_health_score']}/100",
        status="HEALTHY"
    )


if __name__ == "__main__":
    app.run(debug=True)
