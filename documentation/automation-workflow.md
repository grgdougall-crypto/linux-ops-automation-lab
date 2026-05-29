# Automation Workflow

## Overview

The Linux Ops Automation Lab follows a simple monitoring and reporting workflow designed to demonstrate Linux administration, Bash automation, and Python-based analysis.

## Workflow

```text
Bash Monitoring Scripts
        ↓
Generate System Report
        ↓
Store Report in reports/
        ↓
Python Report Parser
        ↓
Health Score Assessment
        ↓
Operational Summary
```

## Components

### Bash Monitoring Scripts

The Bash scripts collect information from the Linux operating system, including:

* Disk utilization
* Memory utilization
* Service status
* Authentication activity
* Backup operations

### System Report Generation

The `generate_system_report.sh` script consolidates system information into a single report file.

Example data collected:

* Hostname
* Disk usage
* Memory usage
* Uptime
* Service status

### Report Storage

Reports are stored in the `reports/` directory.

Generated reports are excluded from source control through `.gitignore`.

### Python Report Parser

The Python parser reads generated reports and extracts important operational information.

The parser converts raw report data into a simplified summary.

### Health Score Assessment

The health scoring engine evaluates report contents and assigns an overall health score.

Current evaluation categories include:

* Disk data availability
* Memory data availability
* Core service availability

### Future Enhancements

Planned improvements include:

* Scheduled execution through cron
* Historical trend analysis
* Web dashboard
* AI-assisted recommendations
* Executive reporting
