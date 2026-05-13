<#
.SYNOPSIS
    Safely stop IDEA / fsnotifier / Toolbox, then relaunch IDEA so it inherits
    the latest environment variables (e.g. DOCKER_API_VERSION).

.DESCRIPTION
    IDEA executable path resolution order (first match wins):
      1) -IdeaPath parameter
      2) -IdeaPathFile parameter (read first non-empty line as path)
      3) Environment variable IDEA_PATH
      4) File .idea-path.txt next to this script
      5) Saved cache file %LOCALAPPDATA%\idea-docker-fix\idea-path.txt
      6) Auto-detect common install locations

    On success the resolved path is cached so subsequent runs need no args.

.PARAMETER IdeaPath
    Full path to idea64.exe.

.PARAMETER IdeaPathFile
    Path to a text file whose first non-empty, non-# line is the idea64.exe path.

.PARAMETER IncludeToolbox
    Also kill jetbrains-toolbox.exe. Required if IDEA was launched via Toolbox.

.PARAMETER NoLaunch
    Only kill processes, do not relaunch.

.EXAMPLE
    .\04-restart-idea.ps1
    .\04-restart-idea.ps1 -IdeaPath "C:\Program Files\JetBrains\IntelliJ IDEA 2024.3\bin\idea64.exe"
    .\04-restart-idea.ps1 -IdeaPathFile .\.idea-path.txt -IncludeToolbox
    $env:IDEA_PATH = "D:\IDEA\bin\idea64.exe"; .\04-restart-idea.ps1
#>
[CmdletBinding()]
param(
    [string]$IdeaPath,
    [string]$IdeaPathFile,
    [switch]$IncludeToolbox,
    [switch]$NoLaunch
)

$ErrorActionPreference = 'Continue'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$cacheDir  = Join-Path $env:LOCALAPPDATA 'idea-docker-fix'
$cacheFile = Join-Path $cacheDir 'idea-path.txt'

function Read-FirstLine([string]$file) {
    if (-not $file -or -not (Test-Path $file)) { return $null }
    foreach ($l in Get-Content -Path $file -ErrorAction SilentlyContinue) {
        $t = $l.Trim()
        if ($t -and -not $t.StartsWith('#')) { return $t }
    }
    return $null
}

function Resolve-IdeaPath {
    if ($IdeaPath)     { return $IdeaPath }
    if ($IdeaPathFile) {
        $p = Read-FirstLine $IdeaPathFile
        if ($p) { return $p }
    }
    if ($env:IDEA_PATH) { return $env:IDEA_PATH }

    $sibling = Join-Path $scriptDir '.idea-path.txt'
    $p = Read-FirstLine $sibling
    if ($p) { return $p }

    $p = Read-FirstLine $cacheFile
    if ($p -and (Test-Path $p)) { return $p }

    $candidates = @(
        "$env:LOCALAPPDATA\Programs\IntelliJ IDEA Ultimate*\bin\idea64.exe",
        "$env:LOCALAPPDATA\JetBrains\Toolbox\apps\intellij-idea-ultimate\*\bin\idea64.exe",
        "$env:LOCALAPPDATA\JetBrains\Toolbox\apps\IDEA-U\*\bin\idea64.exe",
        "$env:LOCALAPPDATA\JetBrains\Toolbox\apps\intellij-idea-community\*\bin\idea64.exe",
        "$env:LOCALAPPDATA\JetBrains\Toolbox\apps\IDEA-C\*\bin\idea64.exe",
        "C:\Program Files\JetBrains\IntelliJ IDEA*\bin\idea64.exe",
        "C:\Program Files (x86)\JetBrains\IntelliJ IDEA*\bin\idea64.exe",
        "D:\Program Files\JetBrains\IntelliJ IDEA*\bin\idea64.exe",
        "D:\JetBrains\IntelliJ IDEA*\bin\idea64.exe"
    )
    foreach ($pattern in $candidates) {
        $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($found) { return $found.FullName }
    }
    return $null
}

# --- Kill phase ---
$targets = @('idea64','idea','fsnotifier')
if ($IncludeToolbox) { $targets += 'jetbrains-toolbox' }

foreach ($name in $targets) {
    $ps = Get-Process -Name $name -ErrorAction SilentlyContinue
    if ($ps) {
        Write-Host "Stopping $name (PID: $($ps.Id -join ','))" -ForegroundColor Yellow
        $ps | Stop-Process -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 1

if ($NoLaunch) {
    Write-Host "Stopped. Not relaunching (NoLaunch)." -ForegroundColor Green
    return
}

$resolved = Resolve-IdeaPath
if (-not $resolved -or -not (Test-Path $resolved)) {
    Write-Warning "Could not locate idea64.exe."
    Write-Host @"

Provide it one of these ways:
  -IdeaPath "C:\Path\to\idea64.exe"
  -IdeaPathFile .\.idea-path.txt
  `$env:IDEA_PATH = "C:\Path\to\idea64.exe"
  Copy .idea-path.txt.sample to .idea-path.txt and edit the path inside.

Then re-run:
  .\04-restart-idea.ps1
"@ -ForegroundColor Yellow
    return
}

Write-Host "Launching IDEA: $resolved" -ForegroundColor Cyan
Write-Host "  Inherited DOCKER_API_VERSION = $env:DOCKER_API_VERSION" -ForegroundColor DarkGray
Start-Process -FilePath $resolved

try {
    if (-not (Test-Path $cacheDir)) { New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null }
    Set-Content -Path $cacheFile -Value $resolved -Encoding UTF8
    Write-Host "Saved path to cache: $cacheFile" -ForegroundColor DarkGray
} catch {}

Write-Host "Started." -ForegroundColor Green
