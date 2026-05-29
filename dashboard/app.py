from flask import Flask, render_template
from pathlib import Path

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

    return render_template(
        "index.html",
        hostname="trickydeb",
        latest_report=latest_report,
        health_score="100/100",
        status="HEALTHY"
    )


if __name__ == "__main__":
    app.run(debug=True)
