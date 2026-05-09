param(
    [Parameter(Mandatory = $true)]
    [string[]]$InputFiles,
    [string]$OutputDir = "./reports/output",
    [string]$FieldMapPath,
    [string]$DimensionRulesPath,
    [string]$ReportLayoutPath,
    [string]$Locale = "en-US",
    [string]$LocaleFile
)

$ErrorActionPreference = "Stop"
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) { throw "Python runtime not found. Please install python3/python or use the Node launcher." }

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$coreScript = Join-Path $scriptDir "analyze-logs.py"
$args = @($coreScript, "analyze", "--input-files") + $InputFiles + @(
    "--output-dir", $OutputDir,
    "--locale", $Locale
)
if ($FieldMapPath) { $args += @("--field-map", $FieldMapPath) }
if ($DimensionRulesPath) { $args += @("--dimension-rules", $DimensionRulesPath) }
if ($ReportLayoutPath) { $args += @("--report-layout", $ReportLayoutPath) }
if ($LocaleFile) { $args += @("--locale-file", $LocaleFile) }
if ($python.Source -eq "py") {
    & py -3 @args
} else {
    & $python.Source @args
}
