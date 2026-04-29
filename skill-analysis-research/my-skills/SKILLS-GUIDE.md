# Skills 使用指南 - 飞书助手 & SSH 管理器

> **版本**: 1.0
> **创建日期**: 2025-12-21
> **适用**: 飞书集成 + 多服务器运维

---

## 📋 已安装的 Skills

| Skill | 功能 | 状态 | 位置 |
|-------|------|------|------|
| **feishu-helper** | 飞书操作助手 | ✅ 已安装 | `~/.claude/skills/feishu-helper/` |
| **ssh-manager** | SSH 多服务器管理 | ✅ 已安装 | `~/.claude/skills/ssh-manager/` |
| **qa-manager** | 问答知识管理 | ✅ 已安装 | `~/.claude/skills/qa-manager/` |

---

## 🎯 快速开始

### 飞书助手 (Feishu Helper)

#### 测试安装
```
# 启动 Claude Code
claude

# 测试 1: 查看群组
列出我的飞书群

# 测试 2: 搜索文档
搜索飞书中关于"技术方案"的文档

# 测试 3: 查询用户
查找邮箱为 test@company.com 的用户
```

#### 常用操作
```bash
# 📨 消息
"给张三发飞书消息：会议时间改为下午3点"
"在技术群发消息：代码已部署"

# 👥 群组
"创建飞书群：项目讨论组"
"查看开发群的成员"

# 📄 文档
"创建飞书文档：周会纪要"
"搜索飞书文档：API设计"

# 📊 Base
"创建飞书表格：任务管理"
"在任务表添加记录：优化性能"
"查询所有未完成的任务"
```

### SSH 管理器 (SSH Manager)

#### 测试安装
```
# 测试 1: 检查服务器状态
检查所有服务器的状态

# 测试 2: 执行命令
在 web 服务器上执行：uptime

# 测试 3: 查看日志
查看 web 服务器的 nginx 日志
```

#### 常用操作
```bash
# 🖥️ 单服务器
"在 web 服务器上查看磁盘使用情况"
"在数据库服务器重启 mysql"
"在 128 上执行：free -h"

# 🔄 批量操作
"在所有服务器上查看内存"
"批量更新所有服务器的系统"

# 🚀 部署
"部署最新代码到 web 服务器"
"重启所有后端服务器的应用"

# 📊 监控
"检查所有服务器的健康状况"
"诊断 web 服务器的性能问题"
```

---

## 💡 实际应用场景

### 场景 1: 应用部署 + 飞书通知

```
# 步骤 1: 部署应用
你: "部署最新代码到生产环境"

SSH Manager 执行:
✅ web 服务器: 代码已更新，nginx 已重启
✅ app 服务器: 应用已更新，pm2 已重启
✅ db 服务器: 数据库迁移完成

# 步骤 2: 发送通知
你: "发送飞书通知到项目组：生产环境已部署新版本 v1.2.0"

Feishu Helper 执行:
✅ 消息已发送到"项目组"群
   内容: 🚀 生产环境已部署新版本 v1.2.0
         部署时间: 2025-12-21 14:30
         变更内容: 性能优化、Bug修复
```

### 场景 2: 服务器监控 + 飞书告警

```
# 步骤 1: 检查服务器
你: "检查所有服务器的状态"

SSH Manager 返回:
✅ web (128): 正常 - CPU 25%, Memory 45%
⚠️ db (124): 警告 - CPU 15%, Memory 90% (高)
✅ app (204): 正常 - CPU 30%, Memory 55%

# 步骤 2: 发送告警
你: "发送飞书告警：数据库服务器内存使用率过高"

Feishu Helper 执行:
✅ 告警已发送到"运维群"
   ⚠️ 数据库服务器内存告警
   服务器: db (192.168.1.124)
   当前使用率: 90%
   建议: 立即检查并优化
```

### 场景 3: 创建部署文档

```
# 步骤 1: 执行部署
你: "部署新版本并记录部署过程"

SSH Manager 执行部署...

# 步骤 2: 创建文档
你: "创建飞书文档：部署记录 2025-12-21，内容如下：
# 部署记录

## 部署信息
- 版本: v1.2.0
- 时间: 2025-12-21 14:30
- 部署人: 张三

## 部署步骤
1. ✅ 拉取最新代码
2. ✅ 构建应用
3. ✅ 重启服务
4. ✅ 验证部署

## 服务器状态
- web: 正常
- app: 正常
- db: 正常
"

Feishu Helper 执行:
✅ 文档已创建
   标题: 部署记录 2025-12-21
   链接: https://feishu.cn/docs/xxx
```

### 场景 4: 问题排查 + 保存经验

```
# 步骤 1: 问题诊断
你: "web 服务器响应慢，帮我诊断"

SSH Manager 执行:
问题分析:
- CPU 正常: 20%
- 内存偏高: 75%
- 发现大量 TIME_WAIT 连接
- nginx error.log 有 502 错误

建议:
1. 检查后端应用连接
2. 优化 nginx upstream
3. 考虑增加内存

# 步骤 2: 解决问题
你: "优化 nginx upstream 配置并重启"

SSH Manager 执行:
✅ 配置已更新
✅ nginx 已重启
✅ 502 错误已消失

# 步骤 3: 保存经验
你: "保存这个问答：
问题：nginx 大量 502 错误如何排查？
答案：检查 upstream 连接，查看 TIME_WAIT 状态，优化连接池配置"

QA Manager 执行:
✅ 问答已保存
   标签: #nginx #502错误 #运维
```

### 场景 5: 创建任务管理系统

```
# 步骤 1: 创建飞书 Base
你: "创建飞书 Base：运维任务管理，包含任务表"

Feishu Helper 执行:
✅ Base 已创建
✅ 任务表已创建，包含字段：
   - 任务名称 (文本)
   - 服务器 (单选)
   - 状态 (单选)
   - 优先级 (单选)
   - 负责人 (人员)
   - 截止日期 (日期)

# 步骤 2: 添加任务
你: "在任务表添加：
- 任务：升级 web 服务器 nginx 版本
- 服务器：web
- 优先级：高
- 负责人：张三"

Feishu Helper 执行:
✅ 任务已添加

# 步骤 3: 执行任务
你: "在 web 服务器上执行：nginx -v"

SSH Manager 返回:
nginx version: nginx/1.18.0

你: "升级 nginx 到最新版本"

SSH Manager 执行:
✅ 正在升级...
✅ nginx 已升级到 1.24.0
✅ 服务已重启

# 步骤 4: 更新任务状态
你: "更新任务状态为已完成"

Feishu Helper 执行:
✅ 任务状态已更新
```

---

## 🔗 Skills 组合使用

### 组合 1: 部署流水线

```bash
# 完整的部署流程
"执行以下部署流程：
1. 在所有服务器上拉取最新代码
2. 构建和重启服务
3. 检查服务状态
4. 创建部署记录文档
5. 发送飞书通知
6. 保存部署经验为问答"

# 自动化执行
SSH Manager: 部署中...
Feishu Helper: 创建文档...
Feishu Helper: 发送通知...
QA Manager: 保存问答...

✅ 部署完成！
```

### 组合 2: 监控告警系统

```bash
# 定期检查并告警
"设置定时任务：
- 每小时检查服务器状态
- 如果 CPU/内存超过 80%，发送飞书告警
- 记录异常到飞书 Base"

# Hook 实现 (伪代码)
every 1 hour:
  status = ssh_manager.check_all_servers()
  for server in status:
    if server.cpu > 80% or server.memory > 80%:
      feishu.send_alert(server)
      feishu.add_to_base("告警记录", server)
```

### 组合 3: 知识库建设

```bash
# 积累运维经验
"当解决服务器问题后，自动：
1. 将问题和解决方案保存为问答
2. 创建详细的飞书文档
3. 共享文档给团队"

Example:
问题解决 → QA Manager 保存
         → Feishu Helper 创建文档
         → Feishu Helper 共享给团队
```

---

## ⚙️ 配置说明

### 飞书配置

**文件**: `~/.claude/settings.json`

```json
{
  "mcp": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxxxxxxxxxxx",
      "appSecret": "xxxxxxxxxxxxxxxx",
      "endpoint": "https://open.feishu.cn"
    }
  }
}
```

**获取凭证**:
1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 配置权限：消息、文档、通讯录、云文档等

### SSH 配置

**服务器别名**: `~/.claude/skills/ssh-manager/servers.json`

```json
{
  "servers": {
    "web": {
      "mcp": "ssh-mcp-128",
      "description": "Web 服务器",
      "ip": "192.168.1.128",
      "tags": ["web", "nginx"]
    },
    "db": {
      "mcp": "ssh-mcp-124",
      "description": "数据库服务器",
      "ip": "192.168.1.124",
      "tags": ["database", "mysql"]
    },
    "app": {
      "mcp": "ssh-mcp-204",
      "description": "应用服务器",
      "ip": "192.168.1.204",
      "tags": ["app", "nodejs"]
    }
  }
}
```

**SSH 认证**:
```bash
# 方法 1: 密钥认证（推荐）
ssh-keygen -t rsa -b 4096
ssh-copy-id user@192.168.1.128
ssh-copy-id user@192.168.1.124
ssh-copy-id user@192.168.1.204

# 方法 2: 密码认证
# 在 MCP 配置中设置密码
```

---

## 📚 完整命令索引

### 飞书助手

```bash
# 消息
给[用户]发飞书消息：[内容]
在[群组]发消息：[内容]
查看[群组]的消息

# 群组
创建飞书群：[群名]
列出我的飞书群
查看[群组]的成员

# 文档
创建飞书文档：[标题]
搜索飞书文档：[关键词]
读取[文档]的内容
将[内容]导入到飞书文档

# Base
创建飞书 Base：[应用名]
在[表名]添加记录：[数据]
查询[表名]中的数据
更新[记录]的数据

# Wiki
搜索飞书知识库：[关键词]

# 用户
查找飞书用户：[邮箱/手机号]

# 权限
共享[文档]给[用户]
```

### SSH 管理器

```bash
# 命令执行
在[服务器]上执行：[命令]
在所有服务器上执行：[命令]
使用 sudo 在[服务器]执行：[命令]

# 监控
检查[服务器/所有服务器]的状态
查看[服务器]的[日志类型]日志
诊断[服务器]的[问题类型]问题

# 部署
部署[应用]到[服务器]
重启[服务器]的[服务]
更新[服务器/所有服务器]的系统

# 服务管理
重启[服务器]的[服务]
停止[服务器]的[服务]
查看[服务器]的服务状态

# 批量操作
同步[文件]到[服务器/所有服务器]
在[服务器组]上执行：[命令]
```

---

## 🔍 故障排查

### 飞书 Skill 不工作

```bash
# 检查 1: MCP 配置
cat ~/.claude/settings.json | grep -A 5 "feishu"

# 检查 2: 凭证是否正确
# 在飞书开放平台验证 App ID 和 Secret

# 检查 3: 权限是否足够
# 确保应用有所需的权限（消息、文档、通讯录等）

# 检查 4: Skill 是否加载
ls ~/.claude/skills/feishu-helper/
```

### SSH Skill 不工作

```bash
# 检查 1: MCP 是否运行
ps aux | grep mcp

# 检查 2: SSH 连接是否正常
ssh user@192.168.1.128 "echo test"

# 检查 3: 服务器配置
cat ~/.claude/skills/ssh-manager/servers.json

# 检查 4: 权限问题
# 确保有 SSH 密钥或密码认证
```

---

## 📖 扩展阅读

| 文档 | 路径 |
|------|------|
| 飞书助手完整文档 | `~/.claude/skills/feishu-helper/SKILL.md` |
| SSH 管理器完整文档 | `~/.claude/skills/ssh-manager/SKILL.md` |
| QA 管理器文档 | `~/.claude/skills/qa-manager/README.md` |
| 服务器配置 | `~/.claude/skills/ssh-manager/servers.json` |

---

## 🎉 开始使用

现在你已经了解了如何使用这两个强大的 Skills！

**立即尝试**:
```
1. 检查所有服务器状态
2. 搜索飞书中的技术文档
3. 保存一个有用的问答
```

**记住**: Skills 会自动激活，只需用自然语言描述你想做的事情！

---

**祝你使用愉快！** 🚀
