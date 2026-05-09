param(
    [string]$SkillRoot = ".",
    [string]$Locale = "en-US"
)

$ErrorActionPreference = "Stop"
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) { throw "Python runtime not found. Please install python3/python or use the Node launcher." }

$skillRootPath = (Resolve-Path $SkillRoot).Path
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$coreScript = Join-Path $scriptDir "run-skill-tests.py"
if ($python.Source -eq "py") {
    & py -3 $coreScript $skillRootPath $Locale
} else {
    & $python.Source $coreScript $skillRootPath $Locale
}
