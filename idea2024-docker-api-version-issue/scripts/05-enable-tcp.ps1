<#
.SYNOPSIS
    Check if Docker Desktop TCP 2375 endpoint is available and give guidance.

.EXAMPLE
    .\05-enable-tcp.ps1
#>

$ErrorActionPreference = 'Continue'

Write-Host "Checking tcp://localhost:2375 ..." -ForegroundColor Cyan
$test = Test-NetConnection -ComputerName 'localhost' -Port 2375 -WarningAction SilentlyContinue

if ($test.TcpTestSucceeded) {
    Write-Host "[OK] TCP 2375 is open." -ForegroundColor Green

    Write-Host "`nCalling Docker API over TCP ..." -ForegroundColor Cyan
    try {
        $resp = Invoke-RestMethod -Uri 'http://localhost:2375/version' -TimeoutSec 5
        Write-Host "Server API: $($resp.ApiVersion)  /  Min: $($resp.MinAPIVersion)" -ForegroundColor Green
    } catch {
        Write-Warning "TCP open but /version call failed: $_"
    }

    Write-Host @"

Next step in IDEA:
  Settings -> Build, Execution, Deployment -> Docker -> +
  Choose 'TCP socket', set: tcp://localhost:2375
  Click 'Test connection' and look for 'Connection successful'.
"@ -ForegroundColor Yellow

} else {
    Write-Warning "TCP 2375 is NOT open."
    Write-Host @"

How to enable:
  1. Open Docker Desktop
  2. Settings -> General
  3. Check: [x] Expose daemon on tcp://localhost:2375 without TLS
  4. Apply & Restart
  5. Re-run this script to verify

[!] Security: 2375 is unencrypted. Use only on localhost during dev.
    Do NOT expose to the public network.
"@ -ForegroundColor Yellow
}
