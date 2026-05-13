<#
.SYNOPSIS
    打包诊断信息为 zip，便于反馈给同事或提 JetBrains issue。

.PARAMETER OutDir
    zip 输出目录，默认当前目录。
#>
[CmdletBinding()]
param(
    [string]$OutDir = (Get-Location).Path
)

$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$work = Join-Path $env:TEMP "idea-docker-report-$ts"
New-Item -ItemType Directory -Path $work -Force | Out-Null

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 运行诊断
& (Join-Path $scriptDir '01-diagnose.ps1') -OutFile (Join-Path $work 'diagnose.txt') | Out-Null

# 拷贝最近的 idea.log
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

# docker info 详细
try {
    docker info 2>&1 | Out-File -FilePath (Join-Path $work 'docker-info.txt') -Encoding UTF8
} catch {}

$zip = Join-Path $OutDir "idea-docker-report-$ts.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path (Join-Path $work '*') -DestinationPath $zip -Force

Write-Host "`n✅ 已生成: $zip" -ForegroundColor Green
Write-Host "   临时目录: $work (可手动删除)" -ForegroundColor DarkGray
