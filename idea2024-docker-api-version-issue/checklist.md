# 排查清单

按顺序勾选：

- [ ] 执行 `docker version`，记录 `Server.APIVersion` 与 `MinAPIVersion`
- [ ] 确认 `MinAPIVersion >= 1.44`（命中本问题的前提）
- [ ] 查看 `Help → About` 确认 IDEA 构建号
- [ ] `Settings → Plugins → Installed`，查看 Docker 插件版本
- [ ] 打开 `idea.log`，搜索 `client version 1.24 is too old`
- [ ] 尝试方案 A：升级 IDEA 到 2024.1.4+ 或 2024.2+
- [ ] 尝试方案 B：升级 Docker 插件
- [ ] 若仍报错，设置环境变量 `DOCKER_API_VERSION=1.44` 并重启 IDEA
- [ ] 自研 Java 程序：升级 docker-java 至 3.4.0+
- [ ] 仍无法解决：在 JetBrains YouTrack 提交 issue，附 `idea.log` 与 `docker version` 输出

## 一键诊断命令（PowerShell）

```powershell
Write-Host "=== Docker ===" -ForegroundColor Cyan
docker version

Write-Host "`n=== IDEA 进程 ===" -ForegroundColor Cyan
Get-Process idea64 -ErrorAction SilentlyContinue | Select-Object Id, Path, StartTime

Write-Host "`n=== DOCKER_API_VERSION ===" -ForegroundColor Cyan
[Environment]::GetEnvironmentVariable("DOCKER_API_VERSION", "User")
[Environment]::GetEnvironmentVariable("DOCKER_API_VERSION", "Machine")
```
