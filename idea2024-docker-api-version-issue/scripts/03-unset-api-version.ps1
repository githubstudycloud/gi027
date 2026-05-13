<#
.SYNOPSIS
    Remove DOCKER_API_VERSION environment variable.

.PARAMETER Scope
    User (default) / Machine / All
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
            Write-Warning "Skipping Machine scope (admin required)."
            return
        }
    }
    [Environment]::SetEnvironmentVariable('DOCKER_API_VERSION', $null, $s)
    Write-Host "Removed $s scope DOCKER_API_VERSION" -ForegroundColor Green
}

if ($Scope -eq 'All') {
    Remove-One 'User'
    Remove-One 'Machine'
} else {
    Remove-One $Scope
}

Remove-Item Env:DOCKER_API_VERSION -ErrorAction SilentlyContinue
Write-Host "Current process env also cleared. Restart IDEA to take effect." -ForegroundColor Yellow
