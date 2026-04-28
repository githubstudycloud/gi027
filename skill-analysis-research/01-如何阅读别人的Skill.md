# 01 - 如何阅读别人的 Skill（5 步阅读法）

> 这一章教你**机械化**地拆解任何陌生 Skill，不需要"灵感"或"经验"

---

## 第 1 步：先看目录树（30 秒）

进入 Skill 目录，运行：

```powershell
# Windows PowerShell
Get-ChildItem -Recurse | Select-Object FullName
# 或者
tree /F
```

```bash
# Linux/Mac
tree -L 3
```

**判断 Skill 类型**：

| 目录形态 | Skill 类型 | 复杂度 |
|---------|-----------|-------|
| 仅 `SKILL.md` 一个文件 | **简单工作流型** | ⭐ |
| `SKILL.md` + `references/*.md` | **知识库型** | ⭐⭐ |
| `SKILL.md` + `scripts/*.{py,sh,js}` | **工具型**（会执行代码）| ⭐⭐⭐ |
| `SKILL.md` + `references/` + `scripts/` + `assets/` | **完整工程型** | ⭐⭐⭐⭐ |
| 多个子 Skill 互相 `@reference` | **编排型/Orchestrator** | ⭐⭐⭐⭐⭐ |

> 💡 **新手提示**：⭐⭐⭐ 以上的 Skill 不建议从陌生作者那里直接拿来用，安全风险（脚本可能执行任意代码）和理解成本都很高。

### 例子

本仓库 `c:\Users\John\.claude\skills\bug-fix\SKILL.md` 是单文件型；而 `writer/` 是编排型（会调度 7 个 sub-expert agents）。

---

## 第 2 步：解剖 SKILL.md 的 Frontmatter（1 分钟）

打开 SKILL.md，顶部的 YAML 块就是"身份证"：

```yaml
---
name: bug-fix
description: Bug分析修复助手 - 当用户说"修复bug"、"排错"、"报错了"、"fix"时自动激活
allowed-tools: Read, Grep, Bash(git:*)
model: claude-sonnet-4
---
```

**逐字段判断**：

| 字段 | 该问自己什么 | 红旗警告 🚩 |
|------|-------------|------------|
| `name` | 是否短横线小写、与目录名一致？ | 含中文、空格、大写字母 |
| `description` | 有没有触发关键词（"当用户说X时"）？ | 只有泛泛介绍如"这是个好工具" |
| `description` | 长度 50-200 字符之间？ | < 30 字符或 > 500 字符 |
| `allowed-tools` | 列了哪些工具？有没有 `Bash(*)` 这种全权限？ | `Bash(*)`、`*` 等通配符（安全风险）|
| `model` | 锁了特定模型吗？ | 锁了你没有的模型（如 `gpt-5`） |
| `applyTo` | 限定了文件 glob 吗？（VS Code 专属字段）| 写错的 glob 永远不会触发 |

### 实操例子

来看本仓库的 `bug-fix` skill：

```yaml
description: Bug分析修复助手 - 深度分析Bug根因，定位代码，给出修复方案。
             当用户说"修复bug"、"排查问题"、"报错了"、"fix"时自动激活。
```

**评分**：✅ 有作用说明 ✅ 有触发关键词 ✅ 中英文混合关键词覆盖度高 → **合格**

反例：

```yaml
description: A helpful skill
```

**评分**：🚩 没说干嘛、🚩 没触发词、🚩 太短 → **垃圾**

---

## 第 3 步：扫描正文章节标题（2 分钟）

不要逐字读 SKILL.md，先用工具抽取所有 `##` 一级标题：

```powershell
Select-String -Path "SKILL.md" -Pattern "^#{1,3} " | Select-Object Line
```

```bash
grep -n "^#\{1,3\} " SKILL.md
```

**好 Skill 的标题骨架**通常长这样：

```
# <Skill Name>
## 触发条件 / When to Use
## 工作流程 / Workflow
   ### Step 1: 收集上下文
   ### Step 2: 分析
   ### Step 3: 输出
## 输出格式 / Output Format
## 示例 / Examples
## 参考 / References
```

**坏 Skill 的特征**：

- 🚩 没有"触发条件"或"何时使用"章节
- 🚩 工作流没有编号步骤（变成大段散文）
- 🚩 没有任何示例
- 🚩 全文超过 800 行（应该拆到 references/）

---

## 第 4 步：追踪引用关系（3 分钟）

这是最关键的一步。**Skill 内部的"调用"全靠相对路径引用**，找出所有引用：

```powershell
# 找出所有 markdown 链接和 @ 引用
Select-String -Path "SKILL.md" -Pattern "\[.*\]\(.*\)|@\S+\.md|references/\S+"
```

把引用画成依赖图，例如：

```
SKILL.md
 ├─ 在第 50 行引用 → references/api-design.md
 ├─ 在第 80 行引用 → references/examples.md  
 ├─ 在第 120 行引用 → scripts/validate.py
 └─ 在第 200 行引用 → @other-skill（这是跨 Skill 引用！）
```

**渐进加载理解**：

- ✅ 引用是**惰性加载**——AI 只在执行到那个步骤时才会去读
- ✅ 因此 `references/` 里塞 5000 行也没事，不计入主 SKILL.md 的 token 预算
- 🚩 但如果在 SKILL.md 顶部就引用 10 个 references，那就是滥用，相当于全量加载

### 例子

```markdown
## Step 3: API 设计

完整字段命名规范见 [references/naming.md](./references/naming.md)，
执行此步骤前必须先读取它。
```

这种写法是**强制加载**——AI 看到"必须先读取"会立刻打开那个文件。

```markdown
## 进阶：复杂场景

如果遇到嵌套对象，可参考 [references/advanced.md](./references/advanced.md)。
```

这种写法是**条件加载**——AI 只在判断"遇到嵌套对象"时才会读。

---

## 第 5 步：审查脚本与资产（5 分钟，可选）

如果有 `scripts/` 目录，**逐个文件至少扫一眼**，特别注意：

```powershell
# 找危险操作
Select-String -Path "scripts\*" -Pattern "rm -rf|Remove-Item -Recurse|curl.*\|.*sh|eval|exec"
```

**红旗清单 🚩**：

- 🚩 `rm -rf /`、`Remove-Item -Recurse -Force`
- 🚩 `curl http://... | bash` （远程执行）
- 🚩 写入 `~/.ssh/`、`~/.aws/credentials`
- 🚩 `git push --force` 直接推送
- 🚩 调用未声明的 API_KEY 环境变量

如果有任何一项，**直接弃用**或者只在沙箱里跑。

---

## 📝 5 步阅读法总结表

| 步骤 | 时间 | 工具 | 输出 |
|------|------|------|------|
| 1. 目录树 | 30s | `tree` / `Get-ChildItem` | Skill 类型分类 |
| 2. Frontmatter | 1min | 文本编辑器 | 字段健康度评分 |
| 3. 章节骨架 | 2min | `grep -n "^#"` | 工作流是否清晰 |
| 4. 引用图 | 3min | `grep` 找链接 | 资源依赖关系图 |
| 5. 脚本审查 | 5min | 危险关键字搜索 | 安全风险报告 |

**总耗时：约 10 分钟**，比硬读半小时高效得多。

---

## 🎯 实战练习

打开本仓库已存在的 `c:\Users\John\.claude\skills\new-feature\SKILL.md`，按上面 5 步走一遍，写下你的判断：

- 类型：______
- description 触发词：______
- 主要章节数：______
- 引用文件数：______
- 评分（满分 100）：______

→ 答案见 [07-完整案例分析.md](./07-完整案例分析.md)
