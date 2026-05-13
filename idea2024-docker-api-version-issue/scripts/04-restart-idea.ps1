<#
.SYNOPSIS
    安全地关闭并重启 IDEA，使其继承最新的环境变量。

.DESCRIPTION
    1) 关闭所有 idea64 / idea / fsnotifier 进程
    2) 可选关闭 jetbrains-toolbox（-IncludeToolbox）
    3) 通过指定路径或自动探测来启动 IDEA

.PARAMETER IdeaPath
    idea64.exe 完整路径。不传则自动在常见位置寻找。

.PARAMETER IncludeToolbox
    同时关闭 Toolbox。若你是通过 Toolbox 启动 IDEA，强烈建议加该参数。

.PARAMETER NoLaunch
    只关闭不重启。

.EXAMPLE
    .\04-restart-idea.ps1
    .\04-restart-idea.ps1 -IncludeToolbox
    .\04-restart-idea.ps1 -IdeaPath "C:\Program Files\JetBrains\IntelliJ IDEA 2024.3\bin\idea64.exe"
#>
[CmdletBinding()]
param(
    [string]$IdeaPath,
    [switch]$IncludeToolbox,
    [switch]$NoLaunch
)

$ErrorActionPreference = 'Continue'

$targets = @('idea64','idea','fsnotifier')
if ($IncludeToolbox) { $targets += 'jetbrains-toolbox' }

foreach ($name in $targets) {
    $ps = Get-Process -Name $name -ErrorAction SilentlyContinue
    if ($ps) {
        Write-Host "关闭 $name (PID: $($ps.Id -join ','))" -ForegroundColor Yellow
        $ps | Stop-Process -Force -ErrorAction SilentlyContinue
    }
}

Start-Sleep -Seconds 1

if ($NoLaunch) {
    Write-Host "已关闭，未启动。" -ForegroundColor Green
    return
}

# 自动探测 idea64.exe
if (-not $IdeaPath) {
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\IntelliJ IDEA Ultimate*\bin\idea64.exe",
        "$env:LOCALAPPDATA\JetBrains\Toolbox\apps\intellij-idea-ultimate\*\bin\idea64.exe",
        "$env:LOCALAPPDATA\JetBrains\Toolbox\apps\IDEA-U\*\bin\idea64.exe",
        "$env:LOCALAPPDATA\JetBrains\Toolbox\apps\intellij-idea-community\*\bin\idea64.exe",
        "C:\Program Files\JetBrains\IntelliJ IDEA*\bin\idea64.exe",
        "C:\Program Files (x86)\JetBrains\IntelliJ IDEA*\bin\idea64.exe"
    )
    foreach ($pattern in $candidates) {
        $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($found) { $IdeaPath = $found.FullName; break }
    }
}

if (-not $IdeaPath -or -not (Test-Path $IdeaPath)) {
    Write-Warning "未找到 idea64.exe，请手动启动 IDEA，或重新执行并传入 -IdeaPath。"
    return
}

Write-Host "启动 IDEA: $IdeaPath" -ForegroundColor Cyan
Write-Host "  继承的 DOCKER_API_VERSION = $env:DOCKER_API_VERSION" -ForegroundColor DarkGray
Start-Process -FilePath $IdeaPath
Write-Host "✅ 已启动。" -ForegroundColor Green
