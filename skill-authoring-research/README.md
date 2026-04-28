# Skill 编写技巧研究

> 创建日期：2026-04-28
> 目标：系统研究"如何编写高质量 Skill"，沉淀可复用的写作模板与最佳实践
> 适用范围：Claude Code Skills、VS Code Copilot Agent Skills（两者格式高度兼容）

---

## 📂 目录结构

| 文件 | 内容 |
|------|------|
| [01-什么是Skill.md](./01-什么是Skill.md) | Skill 的本质、与 Prompt/Agent/Instruction 的区别 |
| [02-SKILL.md规范.md](./02-SKILL.md规范.md) | 文件结构、Frontmatter 字段、命名规则 |
| [03-编写技巧与最佳实践.md](./03-编写技巧与最佳实践.md) | 描述写法、渐进加载、关键词触发、反模式 |
| [04-模板库.md](./04-模板库.md) | 5 类 Skill 的可复制模板（工作流/工具型/写作型/编排型/规范型） |
| [05-参考资料汇总.md](./05-参考资料汇总.md) | 官方文档、本地实例、外部参考链接 |
| [06-网络资料汇总.md](./06-网络资料汇总.md) | Twitter/GitHub/官方博客资料、高频成功模式、Linter 工具 |
| [examples/](./examples/) | 三个完整可运行的 Skill 示例 |

---

## 🎯 核心结论（TL;DR）

1. **Skill = 按需加载的工作流目录**，由 `SKILL.md` + 可选的 `scripts/`、`references/`、`assets/` 组成
2. **`description` 字段是发现入口**：必须包含触发关键词（"当用户说……时"），否则 Agent 永远不会主动加载
3. **渐进加载三层**：Discovery（~100 tokens 读 name+description）→ Body（<5000 tokens 读 SKILL.md）→ Resources（按需展开 references）
4. **SKILL.md 控制在 500 行以内**，长内容拆到 `references/` 里通过相对路径引用
5. **Skill vs Prompt vs Agent**：多步骤+捆绑资产 → Skill；单任务+参数化 → Prompt；需上下文隔离/工具限制 → Agent

---

## 🚀 快速开始

如果只想立即写一个 Skill，按这个最小流程：

```
~/.claude/skills/<your-skill-name>/
└── SKILL.md
```

`SKILL.md` 最小模板：

```markdown
---
name: your-skill-name
description: 一句话说清做什么 + 何时使用。当用户说"关键词1"、"关键词2"时自动激活。
argument-hint: "[可选参数提示]"
---

# 标题

## 何时使用
- 场景 1
- 场景 2

## 工作流程
1. 步骤一
2. 步骤二
3. 步骤三
```

详见 [04-模板库.md](./04-模板库.md)。
