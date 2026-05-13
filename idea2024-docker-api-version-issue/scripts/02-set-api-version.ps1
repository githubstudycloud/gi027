<#
.SYNOPSIS
    Set DOCKER_API_VERSION environment variable.

.PARAMETER Version
    Target API version, default 1.44.

.PARAMETER Scope
    User (default) or Machine. Machine requires admin.

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
        Write-Error "Setting Machine scope requires administrator PowerShell."
        return
    }
}

Write-Host "Setting DOCKER_API_VERSION=$Version  (Scope=$Scope) ..." -ForegroundColor Cyan
[Environment]::SetEnvironmentVariable('DOCKER_API_VERSION', $Version, $Scope)
$env:DOCKER_API_VERSION = $Version

Write-Host "Done." -ForegroundColor Green
Write-Host ""
Write-Host "Verify:" -ForegroundColor Cyan
'  Process: ' + $env:DOCKER_API_VERSION
'  User   : ' + [Environment]::GetEnvironmentVariable('DOCKER_API_VERSION','User')
'  Machine: ' + [Environment]::GetEnvironmentVariable('DOCKER_API_VERSION','Machine')

Write-Host ""
Write-Host "[!] Run .\04-restart-idea.ps1 to let IDEA pick up the new env." -ForegroundColor Yellow
Write-Host "    If launched via JetBrains Toolbox, add -IncludeToolbox." -ForegroundColor Yellow
