#!/bin/bash

echo "================================="
echo " Linux Ops Automation Lab"
echo " Failed Login Report"
echo "================================="
echo

if [ -f /var/log/auth.log ]; then
    FAILED_LOGINS=$(sudo grep -i "failed password" /var/log/auth.log | tail -10)

    if [ -z "$FAILED_LOGINS" ]; then
        echo "No failed SSH password attempts found in /var/log/auth.log."
    else
        echo "$FAILED_LOGINS"
    fi
else
    echo "Authentication log file not found at /var/log/auth.log."
    echo "This system may use journalctl instead of auth.log."
fi
