@echo off
setlocal

set "SCRIPT_DIR=%~dp0"

for %%P in (py -3,py -3,python) do (
    if not defined PY_CMD (
        for /f %%I in ('where %%P 2^>nul') do set "PY_CMD=%%I"
    )
)

if not defined PY_CMD (
    echo Python 3.10+ is required to run ContentHub tooling.
    echo Install from https://www.python.org/downloads/windows/ or via winget:
    echo     winget install Python.Python.3.11
    echo After installing, re-open CMD and run: ch.bat setup
    exit /b 1
)

"%PY_CMD%" "%SCRIPT_DIR%ch.py" %*
