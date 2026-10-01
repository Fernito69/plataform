# Free-threaded build (no GIL), where entity rendering actually runs in parallel.
# Set up with:
#   py -V:3.14t -m venv .venv314t
#   .venv314t\Scripts\python -m pip install pynput
Set-Location -Path $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv314t\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Error "No free-threaded venv at $python - see the setup comment above."
    exit 1
}

& $python main.py --threaded --render-workers 8 @args
