# Techno-Quantamental Analyzer Nightly Scan Script for Windows
# This script can be run via Windows Task Scheduler.

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
# If run directly, ensure we resolve to the parent/project root directory
if ($ScriptDir -match "scripts$") {
    $ProjectDir = Split-Path $ScriptDir
} else {
    $ProjectDir = $ScriptDir
}
Set-Location $ProjectDir

$LogFile = Join-Path $ProjectDir "logs\cron_scans.log"

# Ensure log directory exists
if (-not (Test-Path "$ProjectDir\logs")) {
    New-Item -ItemType Directory -Force -Path "$ProjectDir\logs" | Out-Null
}

$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $LogFile -Value "------------------------------------------------------------"
Add-Content -Path $LogFile -Value "Nightly Scan Started: $Timestamp"
Add-Content -Path $LogFile -Value "------------------------------------------------------------"

$Configs = @(
    "master_analyst_usa.json",
    "master_analyst_china.json",
    "institutional_accumulator_usa.json",
    "institutional_accumulator_china.json",
    "can_slim_usa.json",
    "can_slim_china.json"
)

foreach ($Config in $Configs) {
    Add-Content -Path $LogFile -Value "Running scan for config: $Config"
    
    # Run using the python virtual environment executable
    & "$ProjectDir\.venv\Scripts\python.exe" main.py scan --config $Config *>> $LogFile
    
    if ($LASTEXITCODE -eq 0) {
        Add-Content -Path $LogFile -Value "Successfully completed scan for $Config"
    } else {
        Add-Content -Path $LogFile -Value "FAILED scan for $Config"
    }
    Add-Content -Path $LogFile -Value "------------------------------------------------------------"
}

$EndTimestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $LogFile -Value "Nightly Scan Finished: $EndTimestamp"
Add-Content -Path $LogFile -Value "------------------------------------------------------------"
Add-Content -Path $LogFile -Value ""
