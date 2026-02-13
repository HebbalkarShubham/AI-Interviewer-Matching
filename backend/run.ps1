# Run backend from backend folder so "app" package is found
Set-Location $PSScriptRoot
& "$PSScriptRoot\venv\Scripts\python.exe" -m uvicorn app.main:app --reload --port 8000
