# 03 - Skill 质量评估清单（30 项打分）

> 拿到一个 Skill，按本表逐项打分。**60 分以下直接弃用，80 分以上才值得 fork**。

---

## 🧮 评分总览

| 维度 | 项数 | 满分 |
|------|-----|------|
| A. Frontmatter 元数据 | 6 | 20 |
| B. 描述与触发词 | 5 | 25 |
| C. 正文结构 | 6 | 20 |
| D. 引用与资源 | 5 | 15 |
| E. 安全与可移植 | 4 | 10 |
| F. 可维护性 | 4 | 10 |
| **合计** | **30** | **100** |

---

## A. Frontmatter 元数据（20 分）

| # | 检查项 | 分值 | 通过标准 |
|---|-------|------|---------|
| A1 | 有 YAML frontmatter | 3 | 文件顶部 `---` 包裹的 YAML 块 |
| A2 | `name` 与目录同名 | 3 | 严格相等、小写、短横线 |
| A3 | `description` 非空 | 4 | 至少 50 字符 |
| A4 | `description` < 1024 字符 | 3 | 太长 AI 加载会截断 |
| A5 | 工具权限显式声明 | 4 | 有 `allowed-tools` 或等价字段 |
| A6 | 没有锁死专属模型 | 3 | 不强制 `model: gpt-5` 这类 |

---

## B. 描述与触发词（25 分，最重要！）

| # | 检查项 | 分值 | 通过标准 |
|---|-------|------|---------|
| B1 | 一句话说清作用 | 5 | 第一句就讲清楚干啥 |
| B2 | 包含触发关键词 | 6 | "当用户说 X、Y、Z 时自动激活" |
| B3 | 关键词覆盖中英文 | 4 | 同时有中文+英文触发词 |
| B4 | 关键词数量 3-8 个 | 4 | 太少漏触发，太多误触发 |
| B5 | 排除场景说明 | 6 | 写明"以下情况不激活"（高级技巧） |

**B5 是大多数 Skill 缺的**。优秀例子：

```yaml
description: |
  ... 当用户说"修复bug"、"fix"时激活。
  
  不适用场景：
  - 用户只是问"这段代码什么意思"（用 explain skill）
  - 用户要新建功能而非修复（用 new-feature skill）
```

---

## C. 正文结构（20 分）

| # | 检查项 | 分值 | 通过标准 |
|---|-------|------|---------|
| C1 | 有"何时使用"章节 | 3 | `## When to Use` 或 `## 触发条件` |
| C2 | 有编号步骤 | 4 | `### Step 1:` `### Step 2:` |
| C3 | 步骤数 3-7 个 | 3 | 太少没价值，太多碎片化 |
| C4 | 每步有"输入/产出" | 4 | 明确上下游传递的内容 |
| C5 | 有具体示例 | 3 | 至少 1 个完整 Example |
| C6 | 主文件 < 500 行 | 3 | 超出应拆到 references/ |

---

## D. 引用与资源（15 分）

| # | 检查项 | 分值 | 通过标准 |
|---|-------|------|---------|
| D1 | 引用使用相对路径 | 3 | `./references/x.md` 而非绝对 |
| D2 | 引用文件真实存在 | 4 | 不会有断链 |
| D3 | references 命名清晰 | 2 | 见名知意 |
| D4 | 引用时机明确 | 3 | 写明何时读取 |
| D5 | 没有循环引用 | 3 | A 引 B，B 不引 A |

---

## E. 安全与可移植（10 分）

| # | 检查项 | 分值 | 通过标准 |
|---|-------|------|---------|
| E1 | 无 `Bash(*)` 全权限 | 3 | 显式列出可用命令 |
| E2 | 无远程脚本执行 | 3 | 没有 `curl ... \| bash` |
| E3 | 无硬编码密钥/路径 | 2 | 不写死 `/Users/john/...` |
| E4 | 跨 OS 兼容 | 2 | Windows + Mac/Linux 都能用 |

---

## F. 可维护性（10 分）

| # | 检查项 | 分值 | 通过标准 |
|---|-------|------|---------|
| F1 | 有版本号或日期 | 2 | frontmatter 含 `version` 或正文有 `Updated:` |
| F2 | 有作者/出处 | 2 | 知道找谁问、出 Bug 找谁 |
| F3 | 有变更日志 | 3 | `## Changelog` 章节 |
| F4 | 有 License | 3 | 明确许可证（MIT 等） |

---

## 📊 实战打分例子

### 例子 1：本仓库 `bug-fix` skill

打开 `c:\Users\John\.claude\skills\bug-fix\SKILL.md` 评估（伪打分）：

| 维度 | 得分 | 说明 |
|------|------|------|
| A | 17/20 | A6 没明确锁模型，加分 |
| B | 16/25 | B5 缺排除场景 -6，B3 中英文混合 ✓ |
| C | 16/20 | 步骤清晰，但示例偏少 -3 |
| D | 9/15 | 没有 references 子目录，单文件型 |
| E | 8/10 | E4 部分命令仅 Linux 友好 -2 |
| F | 4/10 | 没 changelog、没 license -6 |
| **总分** | **70/100** | **及格，可用，但建议本地化** |

### 例子 2：网上抓来的某 "magic-skill"

```yaml
---
description: A super powerful skill
---
# Do whatever the user wants

Use Bash to do things.
```

| 维度 | 得分 | 说明 |
|------|------|------|
| A | 5/20 | 缺 name、缺 allowed-tools |
| B | 3/25 | 没触发词、太短 |
| C | 2/20 | 几乎没结构 |
| D | 0/15 | 无引用 |
| E | 0/10 | `Use Bash` 等于 `Bash(*)` |
| F | 0/10 | 啥都没 |
| **总分** | **10/100** | **垃圾，丢弃** |

---

## 🎯 自动化打分脚本

放在 `examples/score-skill.ps1`（见配套示例）：

```powershell
# 用法: .\score-skill.ps1 -Path "C:\path\to\skill\SKILL.md"
param([string]$Path)

$content = Get-Content $Path -Raw
$score = 0
$report = @()

# A1: 有 frontmatter
if ($content -match '(?ms)^---\s*\n.*?\n---') {
    $score += 3; $report += "✓ A1: frontmatter present (+3)"
} else {
    $report += "✗ A1: missing frontmatter (0)"
}

# B2: 触发关键词
if ($content -match '当用户说|when\s+user|trigger') {
    $score += 6; $report += "✓ B2: trigger keywords (+6)"
} else {
    $report += "✗ B2: NO trigger keywords (0) ← FATAL"
}

# E1: 全权限 Bash
if ($content -match 'Bash\(\*\)|allowed-tools.*\*') {
    $report += "✗ E1: dangerous Bash(*) detected (-0/3)"
} else {
    $score += 3; $report += "✓ E1: no dangerous wildcards (+3)"
}

# ... 完整版见 examples/

Write-Host "Score: $score / 100"
$report | ForEach-Object { Write-Host $_ }
```

---

## 📝 小结

- **B 维度（描述与触发词）权重最高**——它直接决定 Skill 能否被发现
- **60 分是生死线**：低于 60 分的 Skill 别用，改它的成本超过自己写
- **80 分以上才值得 fork**：稍加本地化即可跑
- **95 分以上是稀有品**：直接照抄别的项目

下一章：跨工具适配，把高分 Skill 移植到 Codex / Gemini / OpenCode 等。
