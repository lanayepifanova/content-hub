#requires -version 5.0
Param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$python = $env:CH_PYTHON
if (-not $python) {
    foreach ($candidate in @("py.exe -3", "python3", "python")) {
        $cmd = $candidate.Split(" ")[0]
        $found = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($found) {
            $python = $candidate
            break
        }
    }
}

if (-not $python) {
    Write-Error "Python 3.10+ is required. Install from python.org, enable 'Add to PATH', then run `ch.ps1 setup`."
    exit 1
}

& $python (Join-Path $scriptDir "ch.py") @Args
