# 快速测试指引 / 一页纸 SOP

> 你说 IDEA 2024 全系仍报错、`docker.exe` 显示 1.47。按下面顺序跑一遍即可定位 + 修复。
> 全部脚本已改为英文输出，避免 PowerShell 5.1 中文乱码解析失败。

## Step 0：配置 IDEA 路径（一次性）

任选一种方式（推荐 A）：

```powershell
cd d:\20260422\idea2024-docker-api-version-issue\scripts

# A) 配置文件（推荐，已被 .gitignore 忽略，不会泄露个人路径）
Copy-Item .\.idea-path.txt.sample .\.idea-path.txt
notepad .\.idea-path.txt   # 写入: C:\Program Files\JetBrains\IntelliJ IDEA 2024.3\bin\idea64.exe

# B) 环境变量（持久）
[Environment]::SetEnvironmentVariable("IDEA_PATH", "C:\Program Files\JetBrains\IntelliJ IDEA 2024.3\bin\idea64.exe", "User")

# C) 每次显式传参
.\04-restart-idea.ps1 -IdeaPath "C:\Program Files\JetBrains\IntelliJ IDEA 2024.3\bin\idea64.exe"
```

## Step 1：确认服务端最低版本

```powershell
docker version --format 'Client: {{.Client.Version}} | ServerAPI: {{.Server.APIVersion}} | MinAPI: {{.Server.MinAPIVersion}}'
```

- `MinAPI >= 1.44` ⇒ 命中本问题，继续 Step 2。
- `MinAPI = 1.24` ⇒ IDEA 插件 bug，跳到 Step 5。

## Step 2：一键诊断

```powershell
cd d:\20260422\idea2024-docker-api-version-issue\scripts
.\01-diagnose.ps1 -OutFile .\diagnose.txt
```

## Step 3：设置环境变量

```powershell
.\02-set-api-version.ps1 -Version 1.44 -Scope User
# 若 docker.exe 是 1.47 想保持一致：
# .\02-set-api-version.ps1 -Version 1.47 -Scope User
```

## Step 4：彻底重启 IDEA（关键！）

```powershell
# Toolbox 启动的务必加 -IncludeToolbox
.\04-restart-idea.ps1 -IncludeToolbox
```

打开 IDEA → Services → Docker → **重新 Connect**。

## Step 5：仍报错 → 启用 TCP 通道

```powershell
.\05-enable-tcp.ps1
```

按提示在 Docker Desktop 勾选 `Expose daemon on tcp://localhost:2375 without TLS`，然后在 IDEA 新建一个 Docker 连接：

```
Type        : TCP socket
Engine API URL: tcp://localhost:2375
```

## Step 6：还不行 → 收集日志反馈

```powershell
.\06-collect-report.ps1
# 生成 idea-docker-report-yyyyMMdd-HHmmss.zip
```

---

## 各 IDEA 版本兼容速查

| IDEA 版本 | 是否需要 `DOCKER_API_VERSION` 绕过 |
|-----------|------------------------------------|
| 2023.x          | 必须 |
| 2024.1 / 2024.2 | 多数情况下需要 |
| 2024.3+         | 通常已修复，可不设置 |
| 2025.1+         | 已修复 |

## 常见陷阱

1. **设置完变量没退出 Toolbox** → 进程仍继承旧环境。务必加 `-IncludeToolbox`。
2. **在已开的 PowerShell 中 `set` 变量** → 只对该窗口有效，IDEA 读不到。必须用 `02-set-api-version.ps1`（写注册表）。
3. **WSL 后端** → 还需在 WSL 内 `export DOCKER_API_VERSION=1.44` 并写入 `~/.bashrc`。
4. **PowerShell 报中文乱码 / "缺少右括号"** → 旧脚本问题，已修复。重新 `git pull`。
5. **执行策略限制** → `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`。
