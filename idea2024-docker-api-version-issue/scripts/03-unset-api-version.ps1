<#
.SYNOPSIS
    移除 DOCKER_API_VERSION 环境变量。

.PARAMETER Scope
    User (默认) / Machine / All
#>
[CmdletBinding()]
param(
    [ValidateSet('User','Machine','All')]
    [string]$Scope = 'User'
)

function Remove-One([string]$s) {
    if ($s -eq 'Machine') {
        $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
            [Security.Principal.WindowsBuiltInRole]::Administrator
        )
        if (-not $isAdmin) {
            Write-Warning "跳过 Machine 级（需管理员）"
            return
        }
    }
    [Environment]::SetEnvironmentVariable('DOCKER_API_VERSION', $null, $s)
    Write-Host "已移除 $s 级 DOCKER_API_VERSION" -ForegroundColor Green
}

if ($Scope -eq 'All') {
    Remove-One 'User'
    Remove-One 'Machine'
} else {
    Remove-One $Scope
}

Remove-Item Env:DOCKER_API_VERSION -ErrorAction SilentlyContinue
Write-Host "当前进程也已清空。请重启 IDEA 生效。" -ForegroundColor Yellow
