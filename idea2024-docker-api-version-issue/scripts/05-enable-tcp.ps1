<#
.SYNOPSIS
    校验 Docker Desktop TCP 2375 端点是否可用；若不可用给出启用指引。

.DESCRIPTION
    很多 npipe 路径下的版本兼容问题可以通过 TCP 绕过。
    本脚本不会自动改动 Docker Desktop 配置（避免误开放未授权端口），
    只做检测和指引。

.EXAMPLE
    .\05-enable-tcp.ps1
#>

$ErrorActionPreference = 'Continue'

Write-Host "检测 tcp://localhost:2375 ..." -ForegroundColor Cyan
$test = Test-NetConnection -ComputerName 'localhost' -Port 2375 -WarningAction SilentlyContinue

if ($test.TcpTestSucceeded) {
    Write-Host "✅ TCP 2375 已开放。" -ForegroundColor Green

    Write-Host "`n尝试通过 TCP 调用 Docker API ..." -ForegroundColor Cyan
    try {
        $resp = Invoke-RestMethod -Uri 'http://localhost:2375/version' -TimeoutSec 5
        Write-Host "Server API: $($resp.ApiVersion)  /  Min: $($resp.MinAPIVersion)" -ForegroundColor Green
    } catch {
        Write-Warning "TCP 端口开放但 /version 调用失败: $_"
    }

    Write-Host @"

下一步在 IDEA 配置：
  Settings → Build, Execution, Deployment → Docker → +
  选 'TCP socket'，地址填: tcp://localhost:2375
  点 Test connection，看到 'Connection successful' 即可。
"@ -ForegroundColor Yellow

} else {
    Write-Warning "TCP 2375 未开放。"
    Write-Host @"

启用步骤：
  1. 打开 Docker Desktop
  2. Settings → General
  3. 勾选: ☑ Expose daemon on tcp://localhost:2375 without TLS
  4. Apply & Restart
  5. 重跑本脚本验证

⚠️  安全提醒：2375 未加密，仅在本机开发使用，切勿在公网暴露！
"@ -ForegroundColor Yellow
}
