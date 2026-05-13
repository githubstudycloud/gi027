# IDEA 2024 / Docker 客户端版本不兼容 — 脚本集

> PowerShell 脚本一键诊断、设置环境变量、切换连接方式、生成日志报告。
> 全部脚本使用 **ASCII / 英文输出**，可在 Windows PowerShell 5.1（默认 GBK 控制台）和 PowerShell 7+ 上无乱码运行。

## 脚本列表

| 脚本 | 作用 | 是否需要管理员 |
|------|------|---------------|
| [01-diagnose.ps1](01-diagnose.ps1)             | 一键采集 Docker / IDEA / 环境变量 / 日志关键行 | 否 |
| [02-set-api-version.ps1](02-set-api-version.ps1) | 设置 `DOCKER_API_VERSION` 环境变量（User / Machine） | Machine 需要 |
| [03-unset-api-version.ps1](03-unset-api-version.ps1) | 移除上述环境变量 | Machine 需要 |
| [04-restart-idea.ps1](04-restart-idea.ps1)     | 安全退出 IDEA / Toolbox / fsnotifier，并重启 IDEA | 否 |
| [05-enable-tcp.ps1](05-enable-tcp.ps1)         | 提示并校验 Docker Desktop TCP 2375 是否启用 | 否 |
| [06-collect-report.ps1](06-collect-report.ps1) | 把诊断结果打包成 zip 便于反馈 | 否 |
| [start-idea-with-env.bat](start-idea-with-env.bat) | 仅对单次 IDEA 进程注入 `DOCKER_API_VERSION` 启动 | 否 |
| [.idea-path.txt.sample](.idea-path.txt.sample)  | IDEA 路径配置文件模板 | — |

## IDEA 路径如何传入

`04-restart-idea.ps1` 与 `start-idea-with-env.bat` 都**不再硬编码** IDEA 路径，按下列优先级解析（先匹配先用）：

| 优先级 | PowerShell 脚本 | bat 脚本 |
|--------|-----------------|----------|
| 1 | `-IdeaPath` 参数 | 第一个命令行参数 `%1` |
| 2 | `-IdeaPathFile` 参数（读文件首行）| — |
| 3 | 环境变量 `IDEA_PATH` | 环境变量 `IDEA_PATH` |
| 4 | 同目录 `.idea-path.txt`（首行非 `#` 注释）| 同目录 `.idea-path.txt` |
| 5 | 缓存 `%LOCALAPPDATA%\idea-docker-fix\idea-path.txt`（上次成功路径，自动写入） | — |
| 6 | 自动探测常见安装位置 | — |

**推荐做法**：复制 `.idea-path.txt.sample` 为 `.idea-path.txt`，写入你的 `idea64.exe` 路径，**该文件已加入 .gitignore，不会被提交**。

```powershell
Copy-Item .\.idea-path.txt.sample .\.idea-path.txt
notepad .\.idea-path.txt
```

## 推荐使用顺序

```powershell
cd d:\20260422\idea2024-docker-api-version-issue\scripts

# 1. 先采集现状
.\01-diagnose.ps1 -OutFile .\diagnose.txt

# 2. 设置环境变量（默认 1.44，docker 客户端 1.47 也可指定 1.47）
.\02-set-api-version.ps1 -Version 1.44 -Scope User

# 3. 重启 IDEA —— 任选其一
.\04-restart-idea.ps1 -IdeaPath "C:\Program Files\JetBrains\IntelliJ IDEA 2024.3\bin\idea64.exe" -IncludeToolbox
# 或先配置 .idea-path.txt，再裸跑：
.\04-restart-idea.ps1 -IncludeToolbox

# 4. 若仍报错，启用 TCP 连接
.\05-enable-tcp.ps1

# 5. 仍无法解决，打包日志反馈
.\06-collect-report.ps1
```

## 关键背景

- Docker Engine **25.0+**（含 27.x / 29.x，API 1.47/1.52）将 `MinAPIVersion` 提升到 `1.44`。
- IDEA 内置 / 插件捆绑的 `docker-java` 在未协商时默认走 `1.24`，导致 HTTP 400。
- 设置进程级环境变量 `DOCKER_API_VERSION=1.44`（或更高）即可让 docker-java 跳过默认值。
- **必须**完全退出 IDEA 及 Toolbox 后由继承新环境的进程重新拉起，否则无效。

详见上级目录 [README.md](../README.md) 与 [analysis.md](../analysis.md)。

## 常见问题

**Q: PowerShell 报"方法调用中缺少右括号"或一堆乱码？**
A: 这是旧版本（含中文输出）在 GBK 控制台下的编码问题。当前脚本已全部改为英文输出，重新 `git pull` 即可。

**Q: 脚本提示 "running scripts is disabled on this system"?**
A: 执行策略限制。临时放开：
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**Q: 04-restart-idea.ps1 找不到 idea64.exe?**
A: 用 `-IdeaPath` 显式传入，或复制 `.idea-path.txt.sample` 为 `.idea-path.txt` 并填写路径。
