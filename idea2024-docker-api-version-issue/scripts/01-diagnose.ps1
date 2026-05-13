<#
.SYNOPSIS
    诊断 IDEA 2024 连接 Docker 报 "client version 1.24 is too old" 问题。

.DESCRIPTION
    采集以下信息：
      - Docker 客户端 / 服务端版本与 MinAPIVersion
      - DOCKER_API_VERSION 环境变量（进程 / 用户 / 机器三级）
      - IDEA / Toolbox 进程
      - 最近的 idea.log 中关键报错行

.PARAMETER OutFile
    把结果同时写入文件（默认仅打印）。

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

function Write-Section($title) {
    $sep = '=' * 60
    $lines.Add('')
    $lines.Add($sep)
    $lines.Add("  $title")
    $lines.Add($sep)
}

Write-Section "Docker 版本"
try {
    $dockerVer = docker version 2>&1
    $lines.Add(($dockerVer -join "`n"))

    $fmt = docker version --format 'Client: {{.Client.Version}} | ServerAPI: {{.Server.APIVersion}} | MinAPI: {{.Server.MinAPIVersion}}' 2>&1
    $lines.Add('')
    $lines.Add(">>> 摘要: $fmt")

    # 解析 Min API
    if ($fmt -match 'MinAPI:\s*([\d.]+)') {
        $minApi = [version]$Matches[1]
        if ($minApi -ge [version]'1.44') {
            $lines.Add(">>> ⚠️ 命中本问题：Server 最低要求 $minApi >= 1.44，旧 docker-java 客户端 (1.24) 会被拒绝。")
        } else {
            $lines.Add(">>> ✅ Server MinAPI=$minApi < 1.44，理论上不应报 1.24 too old。请检查 IDEA 插件是否硬编码错误版本。")
        }
    }
} catch {
    $lines.Add("docker 命令执行失败: $_")
}

Write-Section "DOCKER_API_VERSION 环境变量"
$envUser    = [Environment]::GetEnvironmentVariable('DOCKER_API_VERSION','User')
$envMachine = [Environment]::GetEnvironmentVariable('DOCKER_API_VERSION','Machine')
$envProc    = $env:DOCKER_API_VERSION
$lines.Add("Process: $envProc")
$lines.Add("User   : $envUser")
$lines.Add("Machine: $envMachine")

if (-not $envUser -and -not $envMachine) {
    $lines.Add(">>> 未设置；建议执行 .\02-set-api-version.ps1 -Version 1.44 -Scope User")
}

Write-Section "IDEA / Toolbox 进程"
$procs = Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -match '^(idea64|idea|jetbrains-toolbox|fsnotifier)$' } |
    Select-Object Id, ProcessName, StartTime, Path
if ($procs) {
    $lines.Add(($procs | Format-Table -AutoSize | Out-String).Trim())
} else {
    $lines.Add("(未发现 IDEA 相关进程)")
}

Write-Section "idea.log 最近的 DockerException"
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
    $lines.Add("(未找到 idea.log)")
} else {
    foreach ($log in $logs | Sort-Object LastWriteTime -Descending | Select-Object -First 3) {
        $lines.Add("--- $($log.FullName) (LastWrite=$($log.LastWriteTime)) ---")
        $hit = Select-String -Path $log.FullName -Pattern 'client version .* is too old|DockerException|Minimum supported API version' -SimpleMatch:$false -ErrorAction SilentlyContinue |
            Select-Object -Last 20
        if ($hit) {
            $lines.Add(($hit | ForEach-Object { "L$($_.LineNumber): $($_.Line.Trim())" }) -join "`n")
        } else {
            $lines.Add("  (无关键字命中)")
        }
    }
}

Write-Section "结论建议"
$lines.Add(@"
1) 优先升级 IDEA 到 2024.3.x 或 2025.1+（彻底修复内置 docker-java 版本）。
2) 临时绕过：.\02-set-api-version.ps1 -Version 1.44 -Scope User，然后 .\04-restart-idea.ps1。
3) 如仍报错，启用 Docker Desktop TCP 2375 并在 IDEA 中切换连接方式。
"@)

$output = $lines -join "`n"
Write-Output $output

if ($OutFile) {
    $output | Out-File -FilePath $OutFile -Encoding UTF8
    Write-Host "`n已写入 $OutFile" -ForegroundColor Green
}
