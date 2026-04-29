# my-skills · 本仓库 Skill 备份与样本库

> 来源：`C:\Users\John\.claude\skills\`（Claude Code 全局 Skills 目录）
> 复制日期：2026-04-29
> 用途：作为本研究目录的**真实样本库**，配合前 7 篇文档练习"5 步阅读法"、"30 项打分"、"跨工具适配"等流程
>
> ⚠️ 原 `README.md` 与 `SKILLS-GUIDE.md` 是本地 skills 目录自带的内容，未改动。本文件是研究目录的索引，请优先看本文件。

---

## 📦 包含的 Skill 列表（共 36+ 个）

按使用场景分组：

### 🔧 开发工作流
- `dev-flow` - 软件开发全流程导航
- `new-feature` - 新功能完整工作流（**编排型**）
- `requirements`、`design`、`api-spec`、`db-schema`
- `gen-tests`、`bug-fix`、`review-pr`、`check-standards`、`refactor`

### 📋 项目管理
- `adr`、`sprint-plan`、`tech-debt`、`release`、`incident`
- `onboard`、`doc-update`、`qa-manager`、`security-audit`

### 🛢 数据库/中间件管理
- `mysql-manager`、`pg-manager`、`mongo-manager`、`redis-manager`
- `kafka-manager`、`ssh-manager`、`ftp-manager`
- `feishu-helper`、`workspace-manager`

### ✍️ 写作系列
- `writer` - 智能审核编排器（**编排型**，调度 7 个 sub-expert）
- `write-academic`、`write-business`、`write-creative`
- `write-marketing`、`write-news`、`write-social`、`write-tech`

---

## 🎯 推荐练习路径

按研究目录前 7 章学习，每章挑一个真实 Skill 实操：

| 章节 | 推荐练习的 Skill | 理由 |
|------|----------------|------|
| [01-如何阅读别人的Skill.md](../01-如何阅读别人的Skill.md) | `bug-fix` | 单文件型，简单入门 |
| [02-Skill互相调用分析.md](../02-Skill互相调用分析.md) | `new-feature`、`writer` | 编排型，复杂调用关系 |
| [03-Skill质量评估清单.md](../03-Skill质量评估清单.md) | 任选 3 个对比打分 | 看分数差异 |
| [04-跨工具适配指南.md](../04-跨工具适配指南.md) | `api-spec` | frontmatter 字段清晰 |
| [05-借助AI理解Skill.md](../05-借助AI理解Skill.md) | `incident` | 内容多、复杂度合适 |
| [06-调试与优化实战.md](../06-调试与优化实战.md) | `gen-tests` | 易于发现优化点 |
| [07-完整案例分析.md](../07-完整案例分析.md) | `requirements`、`onboard` | 走完整流程 |

---

## 🛠 批量分析命令

### 给所有 Skill 打分

```powershell
Get-ChildItem .\my-skills -Directory | ForEach-Object {
    $skillFile = Join-Path $_.FullName "SKILL.md"
    if (Test-Path $skillFile) {
        Write-Host "`n========== $($_.Name) =========="
        & ..\examples\score-skill.ps1 -Path $skillFile | Select-Object -Last 3
    }
}
```

### 找出所有编排型 Skill

```powershell
Select-String -Path ".\my-skills\*\SKILL.md" -Pattern "sub-?agent|调用.*agent|writer-.*-expert|orchestrat" |
    Select-Object Path, LineNumber, Line
```

### 抽取所有触发关键词

```powershell
Get-ChildItem .\my-skills -Directory | ForEach-Object {
    $skillFile = Join-Path $_.FullName "SKILL.md"
    if (Test-Path $skillFile) {
        $content = Get-Content $skillFile -Raw
        if ($content -match '(?ms)description:\s*(.+?)(?=\n[a-z\-]+:|---)') {
            "[$($_.Name)] $($matches[1].Trim())"
        }
    }
}
```

---

## ⚠️ 使用须知

1. **只读样本**：副本仅供学习分析，**不要直接修改**——改动请复制到 `my-skills-fork/`
2. **不会自动同步**：原 `~/.claude/skills/` 后续更新，本副本需手动重新拷贝
3. **隐私**：复制前请人工确认 Skill 内容不含 token/密钥/私钥（建议 grep 一次 `sk-`、`ghp_`、`AKIA`）
4. **顶层的 `README.md`、`SKILLS-GUIDE.md`** 是 skills 目录自带的元文档，不是本研究撰写
