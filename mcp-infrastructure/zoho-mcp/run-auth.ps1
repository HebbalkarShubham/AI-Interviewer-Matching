# Run Zoho MCP auth with .env loaded from this folder
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"
py "$PSScriptRoot\run-auth.py"
