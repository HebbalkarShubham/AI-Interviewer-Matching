# Run Zoho MCP server with .env loaded from this folder
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"
py "$PSScriptRoot\run-server.py"
