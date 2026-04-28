---
name: example-workflow
description: 示例工作流 Skill - 演示 Git Commit 助手的标准编写形态。当用户说"提交代码"、"写commit"、"commit信息"时自动激活。
argument-hint: "[简要描述]"
---

# Git Commit 助手（示例）

> 这是研究目录中的 **工作流型 Skill 示例**，展示标准的多步骤工作流写法。

## 何时使用
- 用户要求生成符合 Conventional Commits 的提交信息
- 用户希望基于当前 git diff 智能撰写 commit message

## 参数说明
- `$ARGUMENTS`：用户对本次改动的简要描述（可选）

## 工作流程

### 第一步：检查工作区状态
```bash
git status --short
git diff --stat
```

如果工作区干净 → 提示用户"无变更可提交"并停止。

### 第二步：识别变更类型
依据改动内容判断 type：

| 类型 | 触发条件 |
|------|---------|
| `feat` | 新增 .ts/.py 业务文件，含新 export |
| `fix` | 改动文件含"bug"、"修复"等注释 |
| `docs` | 仅 .md 文件改动 |
| `refactor` | 代码改动但无功能变化 |
| `test` | 仅测试目录改动 |
| `chore` | 仅配置/依赖文件改动 |

### 第三步：生成 Commit Message
按 [模板](./assets/commit-template.md) 填空生成：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 第四步：让用户确认
展示生成结果，等待用户回复"确认提交"或"修改：xxx"。

### 第五步：执行提交
```bash
git commit -m "<type>(<scope>): <subject>" -m "<body>"
```

## 输出格式
```markdown
**建议的 Commit Message：**

```
feat(auth): 新增 OAuth2 登录支持

- 集成 Google/GitHub OAuth 提供方
- 增加 token 刷新逻辑

Refs: #123
```

是否提交？(确认 / 修改)
```
