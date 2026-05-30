from flask import Flask, render_template, request
from pathlib import Path
import socket
import sys

app = Flask(__name__)

PERSONA_LABELS = {
    "operations": "Operations Manager",
    "security": "Security Analyst",
    "reliability": "Reliability Engineer"
}

PROJECT_DIR = Path.home() / "linux-ops-automation-lab"
REPORT_DIR = PROJECT_DIR / "reports"
AUTOMATION_LOG = REPORT_DIR / "daily_automation.log"

sys.path.append(str(PROJECT_DIR / "python"))

from ai_ops_summary import (
    get_latest_report,
    extract_report_data,
    generate_local_ai_summary
)


def extract_time(timestamp):
    try:
        return timestamp.split()[3][:5]
    except Exception:
        return "--:--"


def get_recent_activity():
    activities = []

    if not AUTOMATION_LOG.exists():
        return ["--:-- ✓ No automation activity found"]

    log_lines = AUTOMATION_LOG.read_text().splitlines()
    latest_time = "--:--"

    for line in log_lines:
        if "Workflow completed:" in line:
            timestamp = line.replace("Workflow completed:", "").strip()
            latest_time = extract_time(timestamp)

    for line in reversed(log_lines):
        if "Workflow completed:" in line:
            time_only = extract_time(line.replace("Workflow completed:", "").strip())
            activities.append(f"{time_only} ✓ Automation Workflow Completed")
        elif "Workflow started:" in line:
            time_only = extract_time(line.replace("Workflow started:", "").strip())
            activities.append(f"{time_only} ✓ Automation Workflow Started")
        elif "System report created:" in line:
            activities.append(f"{latest_time} ✓ System Report Generated")
        elif "Overall Score:" in line:
            score = line.replace("Overall Score:", "").strip()
            activities.append(f"{latest_time} ✓ Health Score Updated ({score})")
        elif "Status:" in line:
            status = line.replace("Status:", "").strip()
            activities.append(f"{latest_time} ✓ System Status Evaluated ({status})")
        elif "Trend Analysis" in line:
            activities.append(f"{latest_time} ✓ Trend Analysis Completed")
        elif "Report Retention Cleanup" in line:
            activities.append(f"{latest_time} ✓ Cleanup Review Completed")
        elif "No cleanup needed." in line:
            activities.append(f"{latest_time} ✓ No Cleanup Required")

    cleaned = []
    for activity in activities:
        if activity not in cleaned:
            cleaned.append(activity)

    return cleaned[:8]


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

    except Exception:
        return "status-warning"


def get_disk_health(percent_text):
    try:
        percent = int(percent_text.replace("%", ""))

        if percent >= 90:
            return "CRITICAL"
        if percent >= 70:
            return "WARNING"
        return "NORMAL"

    except Exception:
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


def calculate_advisor_risk(report_data, insight):
    score = report_data["current_health_score"]

    try:
        disk_percent = int(report_data["disk_usage"].replace("%", ""))
    except Exception:
        disk_percent = 0

    if disk_percent >= 90 or score < 60:
        return {"impact": "HIGH", "confidence": insight["confidence"], "priority": "P1"}

    if disk_percent >= 70 or score < 90:
        return {"impact": "MEDIUM", "confidence": insight["confidence"], "priority": "P3"}

    return {"impact": "LOW", "confidence": insight["confidence"], "priority": "P4"}


def get_advisor_response(question_type, persona, report_data, ai_summary, insight):
    persona_name = PERSONA_LABELS.get(persona, "Operations Manager")
    risk = calculate_advisor_risk(report_data, insight)

    if question_type == "health":
        if persona == "security":
            assessment = (
                f"No abnormal resource indicators are detected. Current health score is "
                f"{report_data['current_health_score']}/100, system status is "
                f"{report_data['status']}, and risk remains {risk['impact']}."
            )
        elif persona == "reliability":
            assessment = (
                f"Current service indicators show stable operating conditions. Health score is "
                f"{report_data['current_health_score']}/100 and operational status is "
                f"{report_data['status']}."
            )
        else:
            assessment = (
                f"System health remains strong. Current health score is "
                f"{report_data['current_health_score']}/100 and operational status is "
                f"{report_data['status']}."
            )

        return {
            "title": f"{persona_name}: System Health Assessment",
            "assessment": assessment,
            "impact": risk["impact"],
            "confidence": risk["confidence"],
            "priority": risk["priority"]
        }

    if question_type == "memory":
        if persona == "security":
            assessment = (
                f"Memory usage is currently {report_data['memory_used']}. "
                f"{insight['insight']} No suspicious memory-related behavior is indicated by the current dashboard data."
            )
        elif persona == "reliability":
            assessment = (
                f"Memory usage is currently {report_data['memory_used']}. "
                f"{insight['insight']} Resource pressure appears manageable under current conditions."
            )
        else:
            assessment = (
                f"Current memory usage is {report_data['memory_used']}. "
                f"{insight['insight']}"
            )

        return {
            "title": f"{persona_name}: Memory Trend Assessment",
            "assessment": assessment,
            "impact": risk["impact"],
            "confidence": risk["confidence"],
            "priority": risk["priority"]
        }

    if question_type == "disk":
        if persona == "security":
            assessment = (
                f"Disk utilization is {report_data['disk_usage']} with disk health marked as "
                f"{report_data['disk_health']}. No storage-related anomaly is indicated."
            )
        elif persona == "reliability":
            assessment = (
                f"Disk capacity remains stable at {report_data['disk_usage']}. "
                f"Disk health is {report_data['disk_health']}, so no reliability concern is present."
            )
        else:
            assessment = (
                f"Disk utilization is currently {report_data['disk_usage']} and disk health is "
                f"{report_data['disk_health']}. No immediate disk-related concern is detected."
            )

        return {
            "title": f"{persona_name}: Disk Utilization Assessment",
            "assessment": assessment,
            "impact": risk["impact"],
            "confidence": risk["confidence"],
            "priority": risk["priority"]
        }

    if question_type == "review":
        if persona == "security":
            assessment = (
                f"Review automation completion, report retention, and resource trends. "
                f"Suggested review: {insight['review']}"
            )
        elif persona == "reliability":
            assessment = (
                f"Focus review on trend stability, service health, and resource capacity. "
                f"Suggested review: {insight['review']}"
            )
        else:
            assessment = (
                f"Suggested review: {insight['review']} "
                f"Recommended action: {ai_summary['recommendation']}"
            )

        return {
            "title": f"{persona_name}: Recommended Review Plan",
            "assessment": assessment,
            "impact": risk["impact"],
            "confidence": risk["confidence"],
            "priority": risk["priority"]
        }

    return {
        "title": f"{persona_name}: Operations Advisor",
        "assessment": "Select a question to generate an operational assessment.",
        "impact": "UNKNOWN",
        "confidence": "LOW",
        "priority": "P3"
    }


@app.route("/")
def home():
    report_data = get_latest_report_data()
    automation_data = get_automation_info()
    activity_feed = get_recent_activity()

    ai_summary = get_ai_summary()
    insight = ai_summary["operational_insight"]

    advisor_question = request.args.get("advisor", "health")
    advisor_persona = request.args.get("persona", "operations")

    advisor_persona_label = PERSONA_LABELS.get(advisor_persona, "Operations Manager")

    advisor_response = get_advisor_response(
        advisor_question,
        advisor_persona,
        report_data,
        ai_summary,
        insight
    )

    recommendations = []

    health_score = report_data["current_health_score"]

    try:
        disk_usage = int(str(report_data["disk_usage"]).replace("%", ""))
    except Exception:
        disk_usage = 0

    try:
        memory_used = float(str(report_data["memory_used"]).replace("Gi", ""))
    except Exception:
        memory_used = 0

    if health_score < 80:
        recommendations.append({
            "action": "Investigate Health Score Degradation",
            "priority": "P1",
            "owner": "Security",
            "status": "Open"
        })

    if disk_usage > 80:
        recommendations.append({
            "action": "Review Disk Capacity",
            "priority": "P2",
            "owner": "Operations",
            "status": "Open"
        })

    if memory_used > 8:
        recommendations.append({
            "action": "Investigate Memory Consumption",
            "priority": "P2",
            "owner": "Reliability",
            "status": "Open"
        })

    if automation_data["status"] != "SUCCESS":
        recommendations.append({
            "action": "Investigate Automation Failure",
            "priority": "P1",
            "owner": "Operations",
            "status": "Open"
        })

    if len(recommendations) == 0:
        recommendations.append({
            "action": "Continue Monitoring",
            "priority": "P4",
            "owner": "Operations",
            "status": "Active"
        })

        recommendations.append({
            "action": "Review Memory Trends",
            "priority": "P4",
            "owner": "Reliability",
            "status": "Scheduled"
        })

        recommendations.append({
            "action": "Validate Report Retention",
            "priority": "P4",
            "owner": "Security",
            "status": "Scheduled"
        })

    last_analysis_time = automation_data["last_run"]

    if len(last_analysis_time.split()) >= 5:
        last_analysis_time = last_analysis_time.split()[3]

    advisor_observations = [
        {
            "time": last_analysis_time,
            "message": f"{advisor_persona_label} reviewed {advisor_question} data"
        },
        {
            "time": last_analysis_time,
            "message": f"Risk level evaluated as {advisor_response['impact']}"
        },
        {
            "time": last_analysis_time,
            "message": f"Priority assigned as {advisor_response['priority']}"
        },
        {
            "time": last_analysis_time,
            "message": "Automation workflow completed successfully"
        }
    ]

    executive_summary = (
        f"System status is {report_data['status']} with a health score of "
        f"{report_data['current_health_score']}/100. Current risk is "
        f"{advisor_response['impact']}. Recommended action: {ai_summary['recommendation']}"
    )

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
        last_run=last_analysis_time,
        activity_feed=activity_feed,
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
        advisor_question=advisor_question,
        advisor_persona=advisor_persona_label,
        advisor_title=advisor_response["title"],
        advisor_assessment=advisor_response["assessment"],
        advisor_impact=advisor_response["impact"],
        advisor_confidence=advisor_response["confidence"],
        advisor_priority=advisor_response["priority"],
        advisor_observations=advisor_observations,
        recommendations=recommendations,
        executive_summary=executive_summary,
        operational_insight=insight["insight"],
        insight_impact=insight["impact"],
        insight_confidence=insight["confidence"],
        insight_priority=insight["priority"],
        insight_review=insight["review"]
    )


if __name__ == "__main__":
    app.run(debug=True)
