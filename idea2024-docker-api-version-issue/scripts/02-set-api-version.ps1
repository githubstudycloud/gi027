<#
.SYNOPSIS
    设置 DOCKER_API_VERSION 环境变量，并校验。

.PARAMETER Version
    目标 API 版本，默认 1.44。可设置为 1.47 等更高版本。

.PARAMETER Scope
    User (默认) / Machine。Machine 需要管理员权限。

.EXAMPLE
    .\02-set-api-version.ps1
    .\02-set-api-version.ps1 -Version 1.47
    .\02-set-api-version.ps1 -Version 1.44 -Scope Machine
#>
[CmdletBinding()]
param(
    [ValidatePattern('^\d+\.\d+$')]
    [string]$Version = '1.44',

    [ValidateSet('User','Machine')]
    [string]$Scope = 'User'
)

$ErrorActionPreference = 'Stop'

if ($Scope -eq 'Machine') {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator
    )
    if (-not $isAdmin) {
        Write-Error "设置 Machine 级变量需以管理员身份运行 PowerShell。"
        return
    }
}

Write-Host "正在设置 DOCKER_API_VERSION=$Version  (Scope=$Scope) ..." -ForegroundColor Cyan
[Environment]::SetEnvironmentVariable('DOCKER_API_VERSION', $Version, $Scope)

# 同步当前进程，方便立即测试
$env:DOCKER_API_VERSION = $Version

Write-Host "完成。" -ForegroundColor Green
Write-Host ""
Write-Host "校验：" -ForegroundColor Cyan
'  Process: ' + $env:DOCKER_API_VERSION
'  User   : ' + [Environment]::GetEnvironmentVariable('DOCKER_API_VERSION','User')
'  Machine: ' + [Environment]::GetEnvironmentVariable('DOCKER_API_VERSION','Machine')

Write-Host ""
Write-Host "⚠️  请运行 .\04-restart-idea.ps1 让 IDEA 重新读取环境变量。" -ForegroundColor Yellow
Write-Host "    （若由 JetBrains Toolbox 启动，需先退出 Toolbox 再重启）" -ForegroundColor Yellow
