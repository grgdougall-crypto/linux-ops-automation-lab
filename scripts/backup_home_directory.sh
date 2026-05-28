#!/bin/bash

echo "================================="
echo " Linux Ops Automation Lab"
echo " Home Directory Backup"
echo "================================="
echo

BACKUP_DIR="$HOME/linux-ops-automation-lab/reports"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/home_backup_$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

tar -czf "$BACKUP_FILE" "$HOME/Documents" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "Backup created successfully:"
    echo "$BACKUP_FILE"
else
    echo "Backup failed."
    echo "Make sure your Documents folder exists."
fi
