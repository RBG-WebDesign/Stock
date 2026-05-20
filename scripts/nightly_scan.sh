#!/bin/bash

# Techno-Quantamental Analyzer Nightly Scan Script
# This script is intended to be run via cron daily at 5:00 PM.

# Project Directory
PROJECT_DIR="/home/vince/repos/techno-quantamental-analyzer"
LOG_FILE="$PROJECT_DIR/logs/cron_scans.log"
UV_PATH="/snap/bin/uv"

# Ensure log directory exists
mkdir -p "$PROJECT_DIR/logs"

# Navigate to project directory
cd "$PROJECT_DIR" || exit 1

echo "------------------------------------------------------------" >> "$LOG_FILE"
echo "Nightly Scan Started: $(date)" >> "$LOG_FILE"
echo "------------------------------------------------------------" >> "$LOG_FILE"

# List of configurations to run
CONFIGS=(
    "master_analyst_usa.json"
    "master_analyst_china.json"
    "institutional_accumulator_usa.json"
    "institutional_accumulator_china.json"
    "can_slim_usa.json"
    "can_slim_china.json"
)

# Run each configuration
for config in "${CONFIGS[@]}"; do
    echo "Running scan for config: $config" >> "$LOG_FILE"
    $UV_PATH run main.py scan --config "$config" >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "Successfully completed scan for $config" >> "$LOG_FILE"
    else
        echo "FAILED scan for $config" >> "$LOG_FILE"
    fi
    echo "------------------------------------------------------------" >> "$LOG_FILE"
done

echo "Nightly Scan Finished: $(date)" >> "$LOG_FILE"
echo "------------------------------------------------------------" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
