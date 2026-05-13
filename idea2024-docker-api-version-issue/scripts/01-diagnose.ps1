<#
.SYNOPSIS
    Diagnose IDEA + Docker "client version 1.24 is too old" issue.

.DESCRIPTION
    Collects:
      - Docker client/server version and MinAPIVersion
      - DOCKER_API_VERSION env var (Process / User / Machine)
      - IDEA / Toolbox processes
      - Recent idea.log entries matching the known error

.PARAMETER OutFile
    Also write the report to this file (optional).

.EXAMPLE
    .\01-diagnose.ps1
    .\01-diagnose.ps1 -OutFile .\diagnose.txt
#>
[CmdletBinding()]
param(
    [string]$OutFile
)

$ErrorActionPreference = 'Continue'
$lines = New-Object System.Collections.Generic.List[string]

function Add-Section($title) {
    $sep = '=' * 60
    $lines.Add('')
    $lines.Add($sep)
    $lines.Add("  $title")
    $lines.Add($sep)
}

Add-Section "Docker Version"
try {
    $dockerVer = docker version 2>&1
    $lines.Add(($dockerVer -join "`n"))

    $fmt = docker version --format 'Client: {{.Client.Version}} | ServerAPI: {{.Server.APIVersion}} | MinAPI: {{.Server.MinAPIVersion}}' 2>&1
    $lines.Add('')
    $lines.Add(">>> Summary: $fmt")

    if ($fmt -match 'MinAPI:\s*([\d.]+)') {
        $minApi = [version]$Matches[1]
        if ($minApi -ge [version]'1.44') {
            $lines.Add(">>> [HIT] Server MinAPI = $minApi (>= 1.44). Old docker-java (1.24) will be rejected.")
        } else {
            $lines.Add(">>> [INFO] Server MinAPI = $minApi (< 1.44). Should not trigger '1.24 too old'. Check IDEA plugin.")
        }
    }
} catch {
    $lines.Add("docker command failed: $_")
}

Add-Section "DOCKER_API_VERSION Environment Variable"
$envUser    = [Environment]::GetEnvironmentVariable('DOCKER_API_VERSION','User')
$envMachine = [Environment]::GetEnvironmentVariable('DOCKER_API_VERSION','Machine')
$envProc    = $env:DOCKER_API_VERSION
$lines.Add("Process: $envProc")
$lines.Add("User   : $envUser")
$lines.Add("Machine: $envMachine")

if (-not $envUser -and -not $envMachine) {
    $lines.Add(">>> Not set. Suggest: .\02-set-api-version.ps1 -Version 1.44 -Scope User")
}

Add-Section "IDEA / Toolbox Processes"
$procs = Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -match '^(idea64|idea|jetbrains-toolbox|fsnotifier)$' } |
    Select-Object Id, ProcessName, StartTime, Path
if ($procs) {
    $lines.Add(($procs | Format-Table -AutoSize | Out-String).Trim())
} else {
    $lines.Add("(no IDEA-related processes found)")
}

Add-Section "Recent idea.log DockerException entries"
$logRoots = @(
    "$env:APPDATA\JetBrains",
    "$env:LOCALAPPDATA\JetBrains"
)
$logs = foreach ($root in $logRoots) {
    if (Test-Path $root) {
        Get-ChildItem -Path $root -Recurse -Filter 'idea.log' -ErrorAction SilentlyContinue
    }
}

if (-not $logs) {
    $lines.Add("(idea.log not found)")
} else {
    foreach ($log in $logs | Sort-Object LastWriteTime -Descending | Select-Object -First 3) {
        $lines.Add("--- $($log.FullName) (LastWrite=$($log.LastWriteTime)) ---")
        $hit = Select-String -Path $log.FullName -Pattern 'client version .* is too old|DockerException|Minimum supported API version' -ErrorAction SilentlyContinue |
            Select-Object -Last 20
        if ($hit) {
            $lines.Add(($hit | ForEach-Object { "L$($_.LineNumber): $($_.Line.Trim())" }) -join "`n")
        } else {
            $lines.Add("  (no matching lines)")
        }
    }
}

Add-Section "Recommendation"
$lines.Add(@"
1) Preferred: upgrade IDEA to 2024.3.x or 2025.1+.
2) Workaround: .\02-set-api-version.ps1 -Version 1.44 -Scope User; then .\04-restart-idea.ps1
3) If still failing: enable Docker Desktop TCP 2375 and switch IDEA connection.
"@)

$output = $lines -join "`n"
Write-Output $output

if ($OutFile) {
    $output | Out-File -FilePath $OutFile -Encoding UTF8
    Write-Host "`nReport written to: $OutFile" -ForegroundColor Green
}
