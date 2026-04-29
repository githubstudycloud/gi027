---
name: ssh-manager
description: SSH 多服务器管理助手，帮助用户在多台服务器上执行命令、部署应用、监控状态、批量操作。当用户想要在服务器上执行命令、部署代码、查看服务器状态、批量管理服务器时自动激活。
allowed-tools: mcp__ssh-mcp-128__*, mcp__ssh-mcp-124__*, mcp__ssh-mcp-204__*, Bash
---

# SSH 多服务器管理助手 (SSH Manager)

## 概述
这个 skill 帮助你轻松管理多台 SSH 服务器，无需记忆服务器 IP 和端口，统一管理所有服务器操作。

## 服务器列表

当前配置的服务器：

| 别名 | 服务器 | 用途 | MCP 工具前缀 |
|------|--------|------|--------------|
| **web** | ssh-mcp-128 | Web 服务器 | `mcp__ssh-mcp-128__` |
| **db** | ssh-mcp-124 | 数据库服务器 | `mcp__ssh-mcp-124__` |
| **app** | ssh-mcp-204 | 应用服务器 | `mcp__ssh-mcp-204__` |

## 核心功能

### 1. 🖥️ 命令执行

#### 单服务器执行
**触发词**: "在XX服务器上执行"、"在web服务器运行"

**功能**:
- 在指定服务器执行单条命令
- 查看命令输出
- 处理命令错误

**使用示例**:
```
"在 web 服务器上执行：df -h"
"在数据库服务器查看磁盘使用情况"
"在 128 服务器上查看 nginx 状态"
```

**底层工具**:
- `mcp__ssh-mcp-128__exec`
- `mcp__ssh-mcp-124__exec`
- `mcp__ssh-mcp-204__exec`

#### 批量执行
**触发词**: "在所有服务器上执行"、"批量运行命令"

**功能**:
- 在多台服务器并行执行相同命令
- 汇总各服务器的执行结果
- 标记执行失败的服务器

**使用示例**:
```
"在所有服务器上查看内存使用情况"
"批量更新所有服务器的软件包"
"在 web 和 app 服务器上重启 nginx"
```

### 2. 🔐 Sudo 命令执行

#### 需要管理员权限的操作
**触发词**: "使用 sudo 执行"、"以管理员身份运行"

**功能**:
- 执行需要 root 权限的命令
- 自动处理 sudo 密码
- 安全的权限管理

**使用示例**:
```
"在 web 服务器使用 sudo 重启 nginx"
"在数据库服务器以 sudo 执行：systemctl restart mysql"
"在所有服务器上 sudo 更新系统"
```

**底层工具**:
- `mcp__ssh-mcp-128__sudo-exec`
- `mcp__ssh-mcp-124__sudo-exec`
- `mcp__ssh-mcp-204__sudo-exec`

### 3. 📊 服务器监控

#### 系统状态检查
**触发词**: "检查服务器状态"、"查看服务器健康度"

**功能**:
- CPU 使用率
- 内存使用情况
- 磁盘空间
- 网络连接
- 进程状态
- 服务运行状态

**使用示例**:
```
"检查所有服务器的状态"
"查看 web 服务器的资源使用情况"
"监控数据库服务器的性能"
"显示 app 服务器的运行进程"
```

**执行的命令**:
```bash
# CPU 和内存
top -bn1 | head -20

# 磁盘
df -h

# 网络
ss -tulpn | grep LISTEN

# 服务状态
systemctl status nginx
systemctl status mysql
```

#### 日志查看
**触发词**: "查看服务器日志"、"显示错误日志"

**功能**:
- 查看系统日志
- 查看应用日志
- 实时查看日志
- 过滤和搜索日志

**使用示例**:
```
"查看 web 服务器的 nginx 错误日志"
"显示数据库服务器的最近 50 条日志"
"查看 app 服务器的应用日志中的错误"
"实时查看所有服务器的系统日志"
```

### 4. 🚀 应用部署

#### 代码部署
**触发词**: "部署到XX服务器"、"更新应用"

**功能**:
- 拉取最新代码
- 构建应用
- 重启服务
- 回滚版本

**使用示例**:
```
"部署最新代码到 web 服务器"
"更新 app 服务器的应用"
"在所有服务器上部署新版本"
"回滚 web 服务器到上一个版本"
```

**部署流程**:
```bash
# 1. 拉取代码
cd /var/www/app && git pull

# 2. 安装依赖
npm install

# 3. 构建
npm run build

# 4. 重启服务
pm2 restart app

# 5. 验证
curl http://localhost:3000/health
```

#### 服务管理
**触发词**: "重启XX服务"、"停止XX进程"

**功能**:
- 启动/停止/重启服务
- 查看服务状态
- 管理系统服务（systemd）
- 管理进程（pm2, supervisor）

**使用示例**:
```
"重启 web 服务器的 nginx"
"停止数据库服务器的 mysql"
"在 app 服务器启动 node 应用"
"查看所有服务器的服务状态"
```

### 5. 📦 软件包管理

#### 安装和更新
**触发词**: "安装软件"、"更新系统"

**功能**:
- 安装软件包（apt/yum）
- 更新系统
- 清理缓存
- 查看已安装软件

**使用示例**:
```
"在 web 服务器安装 htop"
"更新所有服务器的系统包"
"在 app 服务器安装 Node.js"
"查看数据库服务器安装的软件"
```

### 6. 🔍 问题诊断

#### 快速诊断
**触发词**: "诊断服务器问题"、"检查XX错误"

**功能**:
- 检查端口占用
- 查看错误日志
- 检查进程状态
- 网络连接测试
- 磁盘空间检查

**使用示例**:
```
"诊断 web 服务器的网络问题"
"检查数据库服务器为什么慢"
"查看 app 服务器的错误"
"检查 80 端口是否被占用"
```

**诊断脚本**:
```bash
# 综合诊断
echo "=== CPU & Memory ==="
top -bn1 | head -5

echo "=== Disk Usage ==="
df -h

echo "=== Network ==="
ss -tulpn | grep LISTEN

echo "=== Recent Errors ==="
journalctl -p err -n 20

echo "=== Top Processes ==="
ps aux --sort=-%mem | head -10
```

### 7. 🔄 批量操作

#### 文件同步
**触发词**: "同步文件到服务器"、"批量上传"

**功能**:
- 从本地上传文件到服务器
- 在服务器间同步文件
- 批量下载文件

**使用示例**:
```
"将配置文件同步到所有 web 服务器"
"上传部署脚本到 app 服务器"
"从数据库服务器下载备份文件"
```

**实现方式**:
```bash
# 通过 SSH 执行
cat local-file | ssh user@server 'cat > /remote/path/file'

# 或使用 base64 传输
base64 local-file | ssh user@server 'base64 -d > /remote/path/file'
```

#### 配置管理
**触发词**: "更新服务器配置"、"修改配置文件"

**功能**:
- 批量修改配置文件
- 备份配置
- 验证配置
- 回滚配置

**使用示例**:
```
"更新所有服务器的 nginx 配置"
"备份数据库配置文件"
"验证 app 服务器的配置"
```

## 服务器别名配置

### 配置文件

**文件**: `~/.claude/skills/ssh-manager/servers.json`

```json
{
  "servers": {
    "web": {
      "mcp": "ssh-mcp-128",
      "description": "Web 服务器 (Nginx)",
      "ip": "192.168.1.128",
      "tags": ["web", "frontend"],
      "services": ["nginx", "php-fpm"]
    },
    "db": {
      "mcp": "ssh-mcp-124",
      "description": "数据库服务器 (MySQL)",
      "ip": "192.168.1.124",
      "tags": ["database", "mysql"],
      "services": ["mysql"]
    },
    "app": {
      "mcp": "ssh-mcp-204",
      "description": "应用服务器 (Node.js)",
      "ip": "192.168.1.204",
      "tags": ["app", "nodejs"],
      "services": ["pm2", "node"]
    }
  },
  "groups": {
    "all": ["web", "db", "app"],
    "backend": ["db", "app"],
    "frontend": ["web"]
  }
}
```

### 使用别名

```bash
# 可以使用以下方式指定服务器：
- 别名: "web", "db", "app"
- IP: "128", "124", "204"
- 完整标识: "ssh-mcp-128"
- 分组: "backend", "all"
```

## 工作流示例

### 场景 1: 全栈应用部署

```
用户: "部署新版本到生产环境"

Skill 执行流程:
1. 在 web 服务器上:
   - 拉取前端代码
   - 构建前端资源
   - 重启 nginx

2. 在 app 服务器上:
   - 拉取后端代码
   - 安装依赖
   - 重启 Node.js 应用

3. 在 db 服务器上:
   - 执行数据库迁移脚本
   - 验证数据库状态

4. 验证部署:
   - 检查所有服务状态
   - 测试健康检查接口
   - 查看错误日志

5. 返回部署报告
```

### 场景 2: 服务器健康检查

```
用户: "检查所有服务器的健康状况"

Skill 执行:
1. 并行检查所有服务器:
   - CPU 使用率
   - 内存使用率
   - 磁盘空间
   - 关键服务状态

2. 生成健康报告:
   ✅ web (128): 正常
      CPU: 25%, Memory: 45%, Disk: 60%
      nginx: running

   ⚠️ db (124): 警告
      CPU: 15%, Memory: 85% (高), Disk: 75%
      mysql: running

   ✅ app (204): 正常
      CPU: 30%, Memory: 55%, Disk: 50%
      pm2: running

3. 建议:
   - db 服务器内存使用率高，建议优化
```

### 场景 3: 批量配置更新

```
用户: "更新所有服务器的时区为上海"

Skill 执行:
1. 在所有服务器上执行:
   sudo timedatectl set-timezone Asia/Shanghai

2. 验证更新:
   date

3. 返回结果:
   ✅ web: 时区已更新
   ✅ db: 时区已更新
   ✅ app: 时区已更新
```

### 场景 4: 问题排查

```
用户: "web 服务器响应很慢，帮我诊断"

Skill 执行:
1. 检查系统资源:
   - CPU: 查看高 CPU 进程
   - Memory: 查看内存使用
   - Disk I/O: 查看磁盘读写

2. 检查服务状态:
   - nginx: 是否正常运行
   - 连接数: 当前连接数量
   - 错误日志: 最近的错误

3. 网络检查:
   - 网络延迟
   - 带宽使用
   - 连接状态

4. 生成诊断报告:
   问题分析:
   - CPU 使用率正常: 20%
   - 内存使用率: 75% (偏高)
   - 发现大量 TIME_WAIT 连接
   - nginx error.log 有大量 502 错误

   建议:
   1. 检查后端应用服务器连接
   2. 优化 nginx upstream 配置
   3. 考虑增加内存
```

### 场景 5: 自动化运维脚本

```
用户: "每天凌晨 2 点备份数据库并清理日志"

Skill 生成 cron 任务:
# 在 db 服务器上添加定时任务
0 2 * * * /scripts/backup-database.sh
0 2 * * * find /var/log -name "*.log" -mtime +7 -delete

确认后在服务器上执行:
sudo crontab -e
# 添加任务...
```

## 智能服务器识别

Skill 会自动识别服务器：

```
# 通过别名
"在 web 服务器上..." → ssh-mcp-128

# 通过 IP 最后一段
"在 128 上..." → ssh-mcp-128
"在 .128 服务器..." → ssh-mcp-128

# 通过用途
"在数据库服务器上..." → ssh-mcp-124
"在 nginx 服务器上..." → ssh-mcp-128

# 通过分组
"在所有后端服务器..." → [db, app]
"在前端服务器..." → [web]
```

## 安全最佳实践

### 1. 密码管理
```bash
# 使用环境变量
export SSH_SUDO_PASSWORD="secure_password"

# 或使用密钥认证（推荐）
ssh-copy-id user@server
```

### 2. 权限控制
```bash
# 限制可执行的命令
allowed_commands:
  - "systemctl status *"
  - "journalctl *"
  - "df -h"
  - "free -h"

# 禁止危险命令
blocked_commands:
  - "rm -rf /"
  - "dd if=/dev/zero"
  - ":(){ :|:& };:"  # fork bomb
```

### 3. 操作审计
```bash
# 记录所有操作
~/.claude/ssh-audit.log

# 格式
{
  "timestamp": "2025-12-21T12:00:00Z",
  "user": "john",
  "server": "web",
  "command": "systemctl restart nginx",
  "sudo": true,
  "exit_code": 0
}
```

### 4. 操作确认
```bash
# 危险操作需要确认
用户: "删除 web 服务器的所有日志"
Skill: ⚠️ 这是一个危险操作，将删除所有日志文件。确认？[是/否]
用户: "是"
Skill: 执行中...
```

## 常用命令模板

### 系统监控
```bash
# CPU 和进程
top -bn1 | head -20
ps aux --sort=-%cpu | head -10

# 内存
free -h
ps aux --sort=-%mem | head -10

# 磁盘
df -h
du -sh /var/* | sort -rh | head -10

# 网络
ss -tulpn | grep LISTEN
netstat -an | grep ESTABLISHED | wc -l

# 系统负载
uptime
w
```

### 服务管理
```bash
# systemd 服务
systemctl status SERVICE
systemctl start SERVICE
systemctl stop SERVICE
systemctl restart SERVICE
systemctl enable SERVICE
systemctl disable SERVICE

# pm2 (Node.js)
pm2 list
pm2 restart APP
pm2 logs APP
pm2 monit
```

### 日志查看
```bash
# 系统日志
journalctl -xe
journalctl -u SERVICE -n 50
journalctl -p err -n 20

# 应用日志
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
tail -f /var/log/app/error.log

# 搜索日志
grep "ERROR" /var/log/app/*.log
```

### 性能分析
```bash
# I/O 统计
iostat -x 1 5
iotop -o

# 网络流量
iftop
nethogs

# 进程监控
htop
glances
```

## 快捷命令

```bash
# 快速检查
"状态" → 检查所有服务器状态
"日志" → 查看最近的错误日志
"进程" → 显示占用资源最多的进程

# 快速操作
"重启" → 重启相关服务
"更新" → 更新系统包
"清理" → 清理日志和缓存

# 快速诊断
"慢" → 性能诊断
"错误" → 查看错误日志
"网络" → 网络连接检查
```

## 与其他 Skill 集成

### 与飞书集成
```bash
# 部署完成后通知
"部署完成后发送飞书通知到项目组"

# 服务器告警
"当服务器 CPU 超过 80% 时发送飞书告警"

# 定时报告
"每天早上 9 点发送服务器状态报告到飞书"
```

### 与 QA Manager 集成
```bash
# 保存运维经验
"将这次问题排查过程保存为问答"

# 查询历史问题
"搜索之前 nginx 502 错误的解决方案"
```

## 常见问题

**Q: 如何添加新服务器？**
A: 编辑 `~/.claude/skills/ssh-manager/servers.json`，添加新的服务器配置

**Q: sudo 命令需要密码？**
A: 配置 passwordless sudo 或设置 `SSH_SUDO_PASSWORD` 环境变量

**Q: 如何批量执行不同的命令？**
A: 使用脚本模板或分别在不同服务器执行

**Q: 执行超时怎么办？**
A: 长时间运行的命令建议使用 nohup 或 screen

**Q: 如何查看历史操作？**
A: 查看 `~/.claude/ssh-audit.log` 审计日志

## 参考资源

- SSH 最佳实践: https://www.ssh.com/academy/ssh/command
- 服务器配置文件: `~/.claude/skills/ssh-manager/servers.json`
- 使用示例: `~/.claude/skills/ssh-manager/examples.md`
