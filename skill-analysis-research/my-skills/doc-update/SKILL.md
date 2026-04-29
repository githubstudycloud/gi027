---
name: doc-update
description: 文档维护助手 - 扫描文档和代码的差异，自动更新过期的文档内容。当用户说"更新文档"、"文档同步"、"检查文档"、"文档维护"时自动激活。
argument-hint: "[文档路径 或 模块名，留空则全量扫描]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# 文档维护助手

自动发现并修复文档与代码之间的不一致，保持文档永远最新。

## 参数说明
- `$ARGUMENTS`：要维护的文档或模块（留空则全量扫描）

## 工作流程

### 第一步：发现文档 & 代码

```bash
# 扫描所有文档
find . -name "*.md" -not -path "*/node_modules/*" -not -path "*/.git/*"

# 扫描最近修改的代码
git log --oneline --since="30 days ago" --name-only
```

### 第二步：检查文档完整性

对每个找到的文档，检查以下方面：

#### README.md 检查
- [ ] 安装/启动步骤是否能跑通（依赖版本是否过期）？
- [ ] 环境变量列表是否和 `.env.example` 一致？
- [ ] API 端口、URL 是否和实际配置匹配？

#### OpenAPI 规范检查
- [ ] `docs/api/openapi.yaml` 中的路径是否和实际 Controller/Router 一致？
- [ ] 新增的 API 是否已写入规范？
- [ ] 已删除的 API 是否已从规范移除？

#### 变更日志检查
- [ ] `CHANGELOG.md` 是否反映了最近的 commits？
- [ ] 是否有 `[Unreleased]` 条目未整理？

#### ADR 检查
- [ ] `docs/adr/` 中的决策状态是否正确（已实施的是否标为 Accepted）？

### 第三步：发现差异

对比文档和代码，列出所有不一致：

```
差异类型：
- 文档存在但代码已删除 → 建议删除文档内容
- 代码存在但文档未记录 → 建议补充文档
- 文档描述过时 → 建议更新
- 链接失效 → 建议修复
```

### 第四步：交互式修复

对每个发现的差异，询问用户是否修复：

```
发现 3 处文档问题：

1. [README.md:25] Node.js 版本写的 16，但 package.json 要求 20
   → 自动修复？(Y/n)

2. [docs/api/openapi.yaml] 缺少 POST /api/v1/orders 接口定义
   → 根据代码生成并添加？(Y/n)

3. [CHANGELOG.md] 最近 5 个 feat/fix commits 未记录
   → 自动从 git log 生成条目？(Y/n)
```

获得确认后，使用 Edit 工具执行修复。

### 第五步：输出维护报告

```markdown
## 文档维护报告

**日期：** {今天}
**扫描范围：** {文件数} 个文档，{代码变更数} 个代码变更

### 修复项
- ✅ README.md 版本号更新（Node 16 → 20）
- ✅ openapi.yaml 新增 /orders 接口
- ✅ CHANGELOG.md 补充 5 条变更记录

### 待处理项（需人工决策）
- ⚠️ ADR-0003 状态仍为"草稿"，请确认是否已批准

### 建议
- 考虑在 CI 中添加文档检查步骤
- OpenAPI 规范建议使用 contract-first 开发方式
```
