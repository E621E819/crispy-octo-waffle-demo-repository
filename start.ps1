param([int]$Port = 8000)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Python environment not found. Follow the installation steps in README.md first.'
}
Push-Location -LiteralPath (Join-Path $PSScriptRoot 'frontend')
try {
    & npm.cmd run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
} finally { Pop-Location }
Write-Host "Exam Radar is opening at http://127.0.0.1:$Port/"
Write-Host 'Keep this terminal running. Press Ctrl+C to stop.'
& $pythonPath -m uvicorn backend.app:app --host 127.0.0.1 --port $Port
