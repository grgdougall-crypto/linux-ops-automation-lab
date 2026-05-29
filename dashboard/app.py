from flask import Flask, render_template
from pathlib import Path
import socket

app = Flask(__name__)

PROJECT_DIR = Path.home() / "linux-ops-automation-lab"
REPORT_DIR = PROJECT_DIR / "reports"


@app.route("/")
def home():

    reports = sorted(REPORT_DIR.glob("system_report_*.txt"))

    if reports:
        latest_report = reports[-1].name
    else:
        latest_report = "No reports found"

    report_count = len(reports)

    return render_template(
        "index.html",
        hostname=socket.gethostname(),
        latest_report=latest_report,
        report_count=report_count,
        health_score="100/100",
        status="HEALTHY"
    )


if __name__ == "__main__":
    app.run(debug=True)
