#!/bin/bash

echo "================================="
echo " Linux Ops Automation Lab"
echo " Report Retention Cleanup"
echo "================================="
echo

REPORT_DIR="$HOME/linux-ops-automation-lab/reports"
KEEP_COUNT=30

echo "Report directory: $REPORT_DIR"
echo "Keeping newest $KEEP_COUNT system reports."
echo

cd "$REPORT_DIR" || exit 1

REPORT_COUNT=$(ls -1 system_report_*.txt 2>/dev/null | wc -l)

echo "Current system report count: $REPORT_COUNT"

if [ "$REPORT_COUNT" -le "$KEEP_COUNT" ]; then
    echo "No cleanup needed."
else
    DELETE_COUNT=$((REPORT_COUNT - KEEP_COUNT))
    echo "Deleting $DELETE_COUNT old report(s)."

    ls -1t system_report_*.txt | tail -n "$DELETE_COUNT" | xargs rm -f

    echo "Cleanup complete."
fi
