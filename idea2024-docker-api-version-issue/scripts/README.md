# IDEA 2024 / Docker 客户端版本不兼容诊断 & 修复脚本集

> 本目录提供 PowerShell 脚本，一键诊断、设置环境变量、切换连接方式、生成日志报告。
> 所有脚本均**幂等**，可重复执行。需要 PowerShell 5.1+ 或 PowerShell 7+。

## 脚本列表

| 脚本 | 作用 | 是否需要管理员 |
|------|------|---------------|
| `01-diagnose.ps1`           | 一键采集 Docker / IDEA / 环境变量 / 日志关键行 | 否 |
| `02-set-api-version.ps1`    | 设置 `DOCKER_API_VERSION` 环境变量（用户级 / 机器级） | 机器级需要 |
| `03-unset-api-version.ps1`  | 移除上述环境变量 | 机器级需要 |
| `04-restart-idea.ps1`       | 安全退出 IDEA / Toolbox / fsnotifier，并重启 IDEA | 否 |
| `05-enable-tcp.ps1`         | 提示并校验 Docker Desktop TCP 2375 是否启用 | 否 |
| `06-collect-report.ps1`     | 把诊断结果打包成 zip 便于反馈 | 否 |
| `start-idea-with-env.bat`   | 仅对单次 IDEA 进程注入 `DOCKER_API_VERSION` 启动 | 否 |

## 推荐使用顺序

```powershell
# 1. 先采集现状
.\01-diagnose.ps1

# 2. 设置环境变量（默认 1.44，可传入其它）
.\02-set-api-version.ps1 -Version 1.44 -Scope User

# 3. 重启 IDEA（一定要全退！）
.\04-restart-idea.ps1 -IdeaPath "C:\Program Files\JetBrains\IntelliJ IDEA 2024.3\bin\idea64.exe"

# 4. 若仍报错，启用 TCP 连接并在 IDEA 里切换
.\05-enable-tcp.ps1

# 5. 把诊断包发出来
.\06-collect-report.ps1
```

## 关键背景

- Docker Engine **25.0+**（含 27.x，API 1.47）将 `MinAPIVersion` 提升到 `1.44`。
- IDEA 内置 / 插件捆绑的 `docker-java` 在未协商时默认走 `1.24`，导致 HTTP 400。
- 设置进程级环境变量 `DOCKER_API_VERSION=1.44`（或更高如 `1.47`）即可让 docker-java 跳过默认值。
- **必须**完全退出 IDEA 及 Toolbox 后由继承新环境的进程重新拉起，否则无效。

详见同级 [README.md](../README.md) / [analysis.md](../analysis.md)。
