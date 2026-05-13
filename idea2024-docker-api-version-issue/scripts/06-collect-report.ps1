<#
.SYNOPSIS
    Package diagnose output + idea.log + docker info into a zip.

.PARAMETER OutDir
    Output directory for the zip (default: current dir).
#>
[CmdletBinding()]
param(
    [string]$OutDir = (Get-Location).Path
)

$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$work = Join-Path $env:TEMP "idea-docker-report-$ts"
New-Item -ItemType Directory -Path $work -Force | Out-Null

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

& (Join-Path $scriptDir '01-diagnose.ps1') -OutFile (Join-Path $work 'diagnose.txt') | Out-Null

$logRoots = @("$env:APPDATA\JetBrains", "$env:LOCALAPPDATA\JetBrains")
$idx = 0
foreach ($root in $logRoots) {
    if (-not (Test-Path $root)) { continue }
    $logs = Get-ChildItem -Path $root -Recurse -Filter 'idea.log' -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 3
    foreach ($log in $logs) {
        $idx++
        $dest = Join-Path $work ("idea-{0:D2}-{1}.log" -f $idx, $log.Directory.Name)
        Copy-Item -Path $log.FullName -Destination $dest -Force -ErrorAction SilentlyContinue
    }
}

try {
    docker info 2>&1 | Out-File -FilePath (Join-Path $work 'docker-info.txt') -Encoding UTF8
} catch {}

$zip = Join-Path $OutDir "idea-docker-report-$ts.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path (Join-Path $work '*') -DestinationPath $zip -Force

Write-Host "`n[OK] Generated: $zip" -ForegroundColor Green
Write-Host "  Temp dir (safe to delete): $work" -ForegroundColor DarkGray
