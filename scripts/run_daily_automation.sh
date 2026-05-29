#!/bin/bash

echo "================================="
echo " Linux Ops Automation Lab"
echo " Daily Automation Workflow"
echo "================================="
echo

PROJECT_DIR="$HOME/linux-ops-automation-lab"
LOG_FILE="$PROJECT_DIR/reports/daily_automation.log"

echo "Workflow started: $(date)" >> "$LOG_FILE"

echo
echo "Step 1: Generating system report..."
"$PROJECT_DIR/scripts/generate_system_report.sh" >> "$LOG_FILE" 2>&1

echo
echo "Step 2: Running health score assessment..."
python3 "$PROJECT_DIR/python/health_score.py" >> "$LOG_FILE" 2>&1

echo
echo "Step 3: Running trend analysis..."
python3 "$PROJECT_DIR/python/trend_analysis.py" >> "$LOG_FILE" 2>&1

echo
echo "Step 4: Cleaning up old reports..."
"$PROJECT_DIR/scripts/cleanup_old_reports.sh" >> "$LOG_FILE" 2>&1

echo "Workflow completed: $(date)" >> "$LOG_FILE"
echo "---------------------------------" >> "$LOG_FILE"

echo
echo "Daily automation workflow completed."
echo "Log file:"
echo "$LOG_FILE"
