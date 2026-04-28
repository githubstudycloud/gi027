# 01 - 什么是 Skill

## 1.1 定义

**Skill（技能）= Agent 按需加载的工作流文件夹**，包含：
- `SKILL.md`（必需，文件夹同名）
- `scripts/`（可选，可执行脚本）
- `references/`（可选，按需读取的扩展文档）
- `assets/`（可选，模板、样板代码）

> 引自官方文档：*"Folders of instructions, scripts, and resources that agents load on-demand for specialized tasks."*

## 1.2 三层渐进加载机制

| 层级 | 加载内容 | Token 消耗 | 触发时机 |
|------|---------|-----------|---------|
| **Discovery** | `name` + `description` | ~100 | 启动时全部 Skill 都加载这一层 |
| **Body** | `SKILL.md` 正文 | < 5000 | 用户输入命中描述时 |
| **Resources** | `references/*.md`、脚本等 | 按需 | 正文中通过 `[link](./xxx)` 显式引用时 |

**关键含义**：写好 `description` 是 Skill 能否被发现的唯一入口。

## 1.3 Skill 与其他自定义文件的区别

| 类型 | 文件 | 何时用 |
|------|------|--------|
| **agent instructions** | `copilot-instructions.md` / `AGENTS.md` | 永远生效的项目级规则 |
| **File Instructions** | `*.instructions.md` | 命中 `applyTo` glob 或描述时加载 |
| **Prompts** | `*.prompt.md` | 单任务 + 参数化输入（斜杠命令） |
| **Custom Agents** | `*.agent.md` | 子 agent，需要上下文隔离/工具限制 |
| **Skills** | `SKILL.md` | **多步骤工作流 + 捆绑脚本/模板** |
| **Hooks** | `*.json` | 生命周期钩子，确定性 shell 命令 |

### 核心选择树

```
要做一件事 ────┐
              │
   是工作流（多步骤）吗？───否──→ 用 Prompt
              │是
              ▼
   需要捆绑脚本/模板/参考资料吗？──否──→ Prompt 也行
              │是
              ▼
   需要上下文隔离或限制工具吗？──是──→ 用 Custom Agent
              │否
              ▼
            用 Skill ✓
```

## 1.4 Skill 的两个变体

| 变体 | `user-invocable` | `disable-model-invocation` | 行为 |
|------|------------------|---------------------------|------|
| **默认** | true | false | 既可斜杠手动调，也会被 Agent 自动发现 |
| **隐式工作流** | false | false | 不在斜杠列表，但 Agent 会自动加载 |
| **纯手动** | true | true | 只能斜杠调用，不会自动加载 |
| **完全静默** | false | true | 仅作为模板/资料目录存放（罕见） |

## 1.5 安装路径

| 路径 | 作用域 |
|------|--------|
| `.github/skills/<name>/` | 项目级（Copilot） |
| `.agents/skills/<name>/` | 项目级（通用） |
| `.claude/skills/<name>/` | 项目级（Claude） |
| `~/.claude/skills/<name>/` | 用户级（跨项目） |
| `~/.copilot/skills/<name>/` | 用户级（Copilot） |
| `~/.agents/skills/<name>/` | 用户级 |

> Windows 下 `~` 对应 `C:\Users\<用户名>\`。
