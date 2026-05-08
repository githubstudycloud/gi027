param(
    [string]$OutputDir = "./tests/fixtures"
)

$ErrorActionPreference = "Stop"
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) { throw "Python runtime not found. Please install python3/python or use the Node launcher." }

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$coreScript = Join-Path $scriptDir "generate-test-data.py"
if ($python.Source -eq "py") {
    & py -3 $coreScript $OutputDir
} else {
    & $python.Source $coreScript $OutputDir
}
