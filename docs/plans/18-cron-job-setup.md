# Cron Job Setup for Nightly Scans

This document outlines the plan to set up a nightly cron job for the Techno-Quantamental Analyzer.

## Objective
Run a series of scanning commands every night at 5:00 PM (17:00) and log the output.

## Proposed Changes

### 1. New Directory: `scripts/`
Create a `scripts/` directory to hold the automation scripts.

### 2. New Script: `scripts/nightly_scan.sh`
This script will execute the following commands:
- `uv run main.py scan --config master_analyst_usa.json`
- `uv run main.py scan --config master_analyst_china.json`
- `uv run main.py scan --config institutional_accumulator_usa.json`
- `uv run main.py scan --config institutional_accumulator_china.json`
- `uv run main.py scan --config can_slim_usa.json`
- `uv run main.py scan --config can_slim_china.json`

The script will:
- Change directory to the project root.
- Use the full path to `uv` to ensure it works in the cron environment.
- Log both stdout and stderr to `logs/cron_scans.log`.
- Include timestamps for each run.

### 3. Cron Configuration
The cron job will be scheduled as:
```cron
0 17 * * * /bin/bash /home/vince/repos/techno-quantamental-analyzer/scripts/nightly_scan.sh >> /home/vince/repos/techno-quantamental-analyzer/logs/cron_scans.log 2>&1
```

## Implementation Steps

1.  **Identify `uv` path**: Run `which uv` to get the absolute path.
2.  **Create Directory**: `mkdir -p scripts`
3.  **Create Script**: Write the shell script with proper environment setup.
4.  **Set Permissions**: `chmod +x scripts/nightly_scan.sh`
5.  **Configure Cron**: Use `crontab -e` or a temporary file to add the entry.

## Verification
- Manually run the script once to ensure it works.
- Check `crontab -l` to confirm the entry.
