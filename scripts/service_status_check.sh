#!/bin/bash

echo "================================="
echo " Linux Ops Automation Lab"
echo " Service Status Check"
echo "================================="
echo

echo "Checking SSH service:"
systemctl is-active ssh

echo
echo "Checking NetworkManager service:"
systemctl is-active NetworkManager

echo
echo "Checking cron service:"
systemctl is-active cron
