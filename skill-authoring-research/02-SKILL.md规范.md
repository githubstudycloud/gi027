# 02 - SKILL.md 规范

## 2.1 完整 Frontmatter 字段

```yaml
---
name: skill-name                  # 必需：1-64 字符，小写字母数字+连字符，必须与文件夹同名
description: '一句话说清做什么 + 触发关键词。最长 1024 字符。'  # 必需
argument-hint: '[参数提示]'         # 可选：斜杠调用时的提示文字
user-invocable: true              # 可选：默认 true，是否在 / 命令列表显示
disable-model-invocation: false   # 可选：默认 false，是否禁用 Agent 自动加载
allowed-tools: Read, Write, Bash  # 可选（Claude）：限制本 Skill 可用工具
---
```

### 字段细节

#### `name`（必需）
- 1-64 字符
- 仅小写字母、数字、连字符
- **必须与所在文件夹同名**，否则静默失败
- 示例：`api-spec`、`bug-fix`、`db-schema`

#### `description`（必需，最重要）
- 最长 1024 字符
- **决定 Skill 是否被发现**
- 必须包含：
  1. **做什么**（动宾短语）
  2. **何时使用**（触发关键词列表）
- 推荐"Use when..."模式 / 中文"当用户说……时自动激活"

✅ 好例子：
```
描述：架构决策记录助手 - 创建 ADR（Architecture Decision Record）。
当用户说"记录决策"、"写ADR"、"架构决策"时自动激活。
```

❌ 坏例子：
```
描述：一个有用的助手
```

#### `argument-hint`（可选）
- 仅斜杠调用时显示
- 例如 `argument-hint: "[决策标题]"`

#### `user-invocable` / `disable-model-invocation`
见 [01-什么是Skill.md#14-skill-的两个变体](./01-什么是Skill.md)。

## 2.2 文件结构规范

```
<skill-name>/
├── SKILL.md          # 必需，正文 < 500 行
├── scripts/          # 可选：可执行脚本
│   └── *.js / *.sh / *.py
├── references/       # 可选：扩展文档
│   └── *.md
└── assets/           # 可选：模板、样板代码
    └── template.*
```

**铁律**：所有从 SKILL.md 出发的资源引用 **只能一层深**。
- ✅ `[模板](./assets/template.md)`
- ❌ `[模板](./assets/sub/deep/template.md)` （Agent 不会自动追下去）

## 2.3 正文结构推荐

```markdown
# 标题（与 name 对应的中文/英文名）

> 一句话副标题（可选）

## 何时使用 / When to Use
- 场景 1
- 场景 2

## 参数说明（如果有 argument-hint）
- `$ARGUMENTS`：xxx

## 工作流程 / Procedure
### 第一步：xxx
### 第二步：xxx
### 第三步：xxx

## 输出格式 / Output Format
（如果有固定输出结构，给出模板）

## 参考资料
- [模板文件](./assets/template.md)
- [扩展说明](./references/details.md)
```

## 2.4 YAML 静默失败陷阱（必看）

以下问题都会导致 **Agent 完全识别不到 Skill，且无任何报错**：

| 错误 | 修复 |
|------|------|
| 描述含未转义冒号 `description: 用法: xxx` | 加引号 `description: "用法: xxx"` |
| 用 Tab 缩进 | 改用 2 个空格 |
| `name` 与文件夹名不一致 | 保持完全一致 |
| `name` 含大写字母 | 全部小写 |
| Frontmatter 前后 `---` 缺失或多余 | 严格三个连字符 |
| `applyTo` 等字段写错位置（Skill 不支持 applyTo） | 删除 |

**调试方法**：在 VS Code Chat 输入 `/`，查看你的 Skill 是否出现；不出现 = Frontmatter 有问题。
