#!/bin/bash

REPORT_DIR="$HOME/linux-ops-automation-lab/reports"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
REPORT_FILE="$REPORT_DIR/system_report_$TIMESTAMP.txt"

mkdir -p "$REPORT_DIR"

{
echo "================================="
echo " Linux Ops Automation Lab"
echo " System Health Report"
echo "================================="
echo
echo "Generated: $(date)"
echo

echo "========== HOSTNAME =========="
hostname
echo

echo "========== DISK USAGE =========="
df -h
echo

echo "========== MEMORY USAGE =========="
free -h
echo

echo "========== UPTIME =========="
uptime
echo

echo "========== ACTIVE SERVICES =========="
systemctl is-active ssh
systemctl is-active NetworkManager
systemctl is-active cron
echo

} > "$REPORT_FILE"

echo "System report created:"
echo "$REPORT_FILE"
