from flask import Flask, render_template
from pathlib import Path
import socket
import sys

app = Flask(__name__)

PROJECT_DIR = Path.home() / "linux-ops-automation-lab"
REPORT_DIR = PROJECT_DIR / "reports"
AUTOMATION_LOG = REPORT_DIR / "daily_automation.log"

sys.path.append(str(PROJECT_DIR / "python"))

from ai_ops_summary import (
    get_latest_report,
    extract_report_data,
    generate_local_ai_summary
)


def get_automation_info():
    if not AUTOMATION_LOG.exists():
        return {"status": "NO LOG FOUND", "last_run": "Unknown", "class": "status-warning"}

    log_content = AUTOMATION_LOG.read_text().splitlines()

    for line in reversed(log_content):
        if "Workflow completed:" in line:
            return {
                "status": "SUCCESS",
                "last_run": line.replace("Workflow completed:", "").strip(),
                "class": "status-good"
            }

    return {"status": "CHECK LOG", "last_run": "Unknown", "class": "status-warning"}


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


def get_status_class_from_score(score):
    if score >= 90:
        return "status-good"
    if score >= 60:
        return "status-warning"
    return "status-critical"


def get_status_class_from_percent(percent_text):
    try:
        percent = int(percent_text.replace("%", ""))

        if percent >= 90:
            return "status-critical"
        if percent >= 70:
            return "status-warning"
        return "status-good"

    except ValueError:
        return "status-warning"


def get_disk_health(percent_text):
    try:
        percent = int(percent_text.replace("%", ""))

        if percent >= 90:
            return "CRITICAL"
        if percent >= 70:
            return "WARNING"
        return "NORMAL"

    except ValueError:
        return "UNKNOWN"


def get_ai_summary():
    latest_report = get_latest_report()
    report_data = extract_report_data(latest_report)
    return generate_local_ai_summary(report_data)


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
            "disk_health": "UNKNOWN",
            "memory_used": "Unavailable",
            "trend_status": "UNKNOWN",
            "chart_labels": [],
            "chart_scores": [],
            "current_health_score": 0,
            "health_class": "status-warning",
            "disk_class": "status-warning",
            "status": "UNKNOWN",
            "status_class": "status-warning"
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

    health_class = get_status_class_from_score(current_health_score)
    disk_class = get_status_class_from_percent(disk_usage)
    disk_health = get_disk_health(disk_usage)

    if current_health_score >= 90:
        status = "HEALTHY"
    elif current_health_score >= 60:
        status = "NEEDS REVIEW"
    else:
        status = "AT RISK"

    return {
        "latest_report": latest_report.name,
        "report_count": len(reports),
        "disk_usage": disk_usage,
        "disk_health": disk_health,
        "memory_used": memory_used,
        "trend_status": "STABLE",
        "chart_labels": chart_labels,
        "chart_scores": chart_scores,
        "current_health_score": current_health_score,
        "health_class": health_class,
        "disk_class": disk_class,
        "status": status,
        "status_class": health_class
    }


@app.route("/")
def home():
    report_data = get_latest_report_data()
    automation_data = get_automation_info()
    ai_summary = get_ai_summary()
    insight = ai_summary["operational_insight"]

    return render_template(
        "index.html",
        hostname=socket.gethostname(),
        latest_report=report_data["latest_report"],
        report_count=report_data["report_count"],
        disk_usage=report_data["disk_usage"],
        disk_health=report_data["disk_health"],
        memory_used=report_data["memory_used"],
        trend_status=report_data["trend_status"],
        automation_status=automation_data["status"],
        automation_class=automation_data["class"],
        last_run=automation_data["last_run"],
        chart_labels=report_data["chart_labels"],
        chart_scores=report_data["chart_scores"],
        health_score=f"{report_data['current_health_score']}/100",
        health_class=report_data["health_class"],
        disk_class=report_data["disk_class"],
        status=report_data["status"],
        status_class=report_data["status_class"],
        ai_provider=ai_summary["provider"],
        ai_risk_level=ai_summary["risk_level"],
        ai_summary=ai_summary["summary"],
        ai_findings=ai_summary["findings"],
        ai_recommendation=ai_summary["recommendation"],
        operational_insight=insight["insight"],
        insight_impact=insight["impact"],
        insight_confidence=insight["confidence"],
        insight_priority=insight["priority"],
        insight_review=insight["review"]
    )


if __name__ == "__main__":
    app.run(debug=True)
