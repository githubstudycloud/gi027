# Claude Code Skills 集合

> **安装位置**: `~/.claude/skills/`
> **安装日期**: 2025-12-21
> **状态**: ✅ 全部已安装并可用

---

## 📦 已安装的 Skills

### 1. QA Manager - 问答知识管理器 ✅

**功能**: 保存、搜索、管理技术问答知识库

**触发词**: "保存问答"、"搜索问答"、"显示问答统计"

**核心能力**:
- 💾 保存问答（自动标签、时间戳）
- 🔍 智能搜索（语义搜索、标签过滤）
- ✏️ 更新编辑（版本控制）
- 📊 统计分析（分类、标签、图谱）
- 🏢 企业级（RBAC 权限、审计日志）

**快速开始**:
```
保存这个问答：
问题：如何使用 Git rebase？
答案：用于重写提交历史...
```

**文档**:
- 📖 [README.md](./qa-manager/README.md) - 项目概览
- 🚀 [QUICKSTART.md](./qa-manager/QUICKSTART.md) - 5分钟入门
- 💡 [examples.md](./qa-manager/examples.md) - 详细示例
- 📦 [DEPLOYMENT.md](./qa-manager/DEPLOYMENT.md) - 完整部署
- 🏢 [ENTERPRISE.md](./qa-manager/ENTERPRISE.md) - 企业配置
- 🧪 [TEST-REPORT.md](./qa-manager/TEST-REPORT.md) - 测试报告

---

### 2. Feishu Helper - 飞书操作助手 ✅

**功能**: 快速使用飞书的消息、文档、Base、群组等功能

**触发词**: "发飞书消息"、"创建飞书文档"、"查询飞书表格"

**核心能力**:
- 📨 消息管理（发送、查看、批量）
- 👥 群组管理（创建、查询、成员）
- 📄 文档操作（创建、搜索、编辑）
- 📊 Base 操作（表格、记录、查询）
- 📚 Wiki 搜索（知识库）
- 👤 通讯录（查找用户）
- 🔐 权限管理（共享、协作）

**快速开始**:
```
# 发送消息
给张三发飞书消息：会议时间改为下午3点

# 创建文档
创建飞书文档：技术方案

# 查询 Base
查询任务表中所有未完成的任务
```

**配置要求**:
```json
{
  "mcp": {
    "feishu": {
      "appId": "cli_xxxxxxxxxxxx",
      "appSecret": "xxxxxxxxxxxxxxxx"
    }
  }
}
```

**文档**:
- 📖 [SKILL.md](./feishu-helper/SKILL.md) - 完整功能说明

---

### 3. SSH Manager - SSH 多服务器管理助手 ✅

**功能**: 统一管理多台 SSH 服务器，批量执行命令

**触发词**: "在XX服务器上执行"、"检查所有服务器"、"部署到生产"

**核心能力**:
- 🖥️ 命令执行（单服务器、批量）
- 🔐 Sudo 执行（管理员权限）
- 📊 服务器监控（CPU、内存、磁盘）
- 🚀 应用部署（代码更新、重启）
- 📦 软件管理（安装、更新）
- 🔍 问题诊断（性能分析）
- 🔄 批量操作（文件同步、配置）

**服务器配置**:
```json
{
  "servers": {
    "web": {
      "mcp": "ssh-mcp-128",
      "description": "Web 服务器 (Nginx)",
      "ip": "192.168.1.128"
    },
    "db": {
      "mcp": "ssh-mcp-124",
      "description": "数据库服务器 (MySQL)",
      "ip": "192.168.1.124"
    },
    "app": {
      "mcp": "ssh-mcp-204",
      "description": "应用服务器 (Node.js)",
      "ip": "192.168.1.204"
    }
  }
}
```

**快速开始**:
```
# 检查状态
检查所有服务器的状态

# 执行命令
在 web 服务器上执行：df -h

# 批量操作
在所有服务器上查看内存使用情况

# 部署
部署最新代码到生产环境
```

**文档**:
- 📖 [SKILL.md](./ssh-manager/SKILL.md) - 完整功能说明
- ⚙️ [servers.json](./ssh-manager/servers.json) - 服务器配置

---

## 🔗 Skills 组合使用

### 组合场景 1: 完整的部署流程

```
1. SSH Manager: 部署代码到服务器
2. SSH Manager: 检查服务状态
3. Feishu Helper: 创建部署记录文档
4. Feishu Helper: 发送通知到项目组
5. QA Manager: 保存部署经验
```

### 组合场景 2: 监控告警系统

```
1. SSH Manager: 定时检查服务器状态
2. Feishu Helper: 异常时发送告警消息
3. Feishu Helper: 记录到 Base 告警表
4. QA Manager: 保存问题解决方案
```

### 组合场景 3: 知识库建设

```
1. SSH Manager: 解决服务器问题
2. QA Manager: 保存问题和解决方案
3. Feishu Helper: 创建详细文档
4. Feishu Helper: 共享给团队
```

---

## 📖 快速参考

### 常用命令速查

#### QA Manager
```bash
# 保存
"保存这个问答：[问题和答案]"

# 搜索
"搜索关于 React 的问答"

# 统计
"显示我的问答统计"
```

#### Feishu Helper
```bash
# 消息
"给[用户]发飞书消息：[内容]"
"在[群组]发消息：[内容]"

# 文档
"创建飞书文档：[标题]"
"搜索飞书文档：[关键词]"

# Base
"在[表名]添加记录：[数据]"
"查询[表名]中的数据"
```

#### SSH Manager
```bash
# 命令
"在[服务器]上执行：[命令]"
"在所有服务器上执行：[命令]"

# 监控
"检查所有服务器的状态"
"诊断[服务器]的问题"

# 部署
"部署代码到[服务器]"
"重启[服务器]的[服务]"
```

---

## ⚙️ 配置文件位置

| 配置 | 路径 | 说明 |
|------|------|------|
| 全局配置 | `~/.claude/settings.json` | MCP、Hooks 等配置 |
| QA Manager | `~/.claude/skills/qa-manager/` | 问答管理配置 |
| Feishu Helper | `~/.claude/settings.json` | 飞书凭证配置 |
| SSH Manager | `~/.claude/skills/ssh-manager/servers.json` | 服务器别名配置 |

---

## 🚀 立即开始

### 测试 Skills 是否工作

```bash
# 启动 Claude Code
claude

# 测试 1: QA Manager
保存这个问答：Skill 测试

# 测试 2: SSH Manager
在 web 服务器上执行：uptime

# 测试 3: Feishu Helper
列出我的飞书群
```

### 查看完整文档

```bash
# 综合使用指南
cat ~/.claude/skills/SKILLS-GUIDE.md

# 各个 skill 详细文档
cat ~/.claude/skills/qa-manager/QUICKSTART.md
cat ~/.claude/skills/feishu-helper/SKILL.md
cat ~/.claude/skills/ssh-manager/SKILL.md
```

---

## 📊 Skills 总览

| Skill | 文件数 | 大小 | 状态 |
|-------|--------|------|------|
| **QA Manager** | 6 docs | ~140 KB | ✅ 完整 |
| **Feishu Helper** | 1 doc | ~25 KB | ✅ 完整 |
| **SSH Manager** | 2 files | ~20 KB | ✅ 完整 |
| **总计** | **9 files** | **~185 KB** | ✅ 可用 |

---

## 🎯 下一步

1. ✅ **熟悉基础功能**: 先测试每个 skill 的基本操作
2. ✅ **配置凭证**: 设置飞书 API 凭证（如果使用）
3. ✅ **自定义配置**: 编辑 `servers.json` 设置你的服务器
4. ✅ **组合使用**: 尝试多个 skills 组合的场景
5. ✅ **积累知识**: 持续保存有用的问答和文档

---

## 💡 使用技巧

1. **明确的触发词**: 使用清晰的关键词让 skill 自动激活
2. **服务器别名**: 用简短的别名（web、db、app）而不是 IP
3. **批量操作**: 一次性在多台服务器执行相同命令
4. **保存经验**: 解决问题后及时保存到 QA Manager
5. **团队协作**: 通过飞书分享知识和通知

---

## 🆘 获取帮助

### 在 Claude Code 中

```
# 查看 skill 帮助
qa-manager 怎么用？
feishu-helper 有哪些功能？
ssh-manager 如何管理服务器？

# 阅读文档
阅读 ~/.claude/skills/SKILLS-GUIDE.md
```

### 故障排查

```bash
# 检查 skills 是否加载
ls ~/.claude/skills/

# 检查配置
cat ~/.claude/settings.json

# 查看 MCP 状态
ps aux | grep mcp
```

---

## 📝 更新日志

- **2025-12-21**: 初始版本
  - ✅ QA Manager v1.0 (7 docs, 完整功能)
  - ✅ Feishu Helper v1.0 (消息、文档、Base)
  - ✅ SSH Manager v1.0 (多服务器管理)

---

**祝你使用愉快！有任何问题随时在 Claude Code 中询问。** 🚀✨
