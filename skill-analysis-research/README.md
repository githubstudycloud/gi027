# Skill 分析、调试与优化研究

> 创建日期：2026-04-28
> 适用：Claude Code / VS Code Copilot / Codex / Gemini CLI / OpenCode / Cursor / Trae 等所有支持 SKILL.md 协议或类 Skill 机制的工具
> 写给：**只想"看懂别人的 Skill 并改成自己能用的版本"的开发者**（包括"自认为智力低下"的我自己）

---

## 🤔 这个研究要解决什么问题？

你在 GitHub / X(Twitter) / 国内开源仓库捡到一个别人写的 Skill，长得像这样：

```
some-skill/
├── SKILL.md           ← 主入口
├── references/        ← 一堆 markdown
│   ├── api.md
│   └── examples.md
├── scripts/           ← 几个 .py / .sh
└── assets/            ← 模板文件
```

打开就懵了：

- ❓ 这玩意儿到底干啥的？描述写得云里雾里
- ❓ `SKILL.md` 里写了 `详见 references/api.md`，到底什么时候会去读？
- ❓ 它写的是 Claude 的格式，我用 Copilot / Codex / Gemini 能不能跑？
- ❓ 半成品没跑过，怎么知道它好不好？要不要抄？
- ❓ 我想改一部分，怎么不改坏其它部分？

**这套研究就是教你一步一步把上面 5 个问题解决，最后能自信地把别人的 Skill 拆开、看懂、改造、再装回自己工具链里跑起来。**

---

## 📂 目录结构

| 文件 | 你能学到什么 |
|------|-------------|
| [01-如何阅读别人的Skill.md](./01-如何阅读别人的Skill.md) | 5 步阅读法：从目录树→Frontmatter→正文→引用→脚本 |
| [02-Skill互相调用分析.md](./02-Skill互相调用分析.md) | 怎么判断 Skill A 会不会调用 Skill B？图谱怎么画？ |
| [03-Skill质量评估清单.md](./03-Skill质量评估清单.md) | 30 项打分清单，60 分以下别用 |
| [04-跨工具适配指南.md](./04-跨工具适配指南.md) | Claude/Copilot/Codex/Gemini/OpenCode/Cursor 差异对照表 |
| [05-借助AI理解Skill.md](./05-\u501f\u52a9AI\u7406\u89e3Skill.md) | 让 AI 帮你逆向解析 Skill 的 6 个 Prompt 模板 |
| [06-调试与优化实战.md](./06-调试与优化实战.md) | 不触发？慢？冲突？6 类常见问题排查手册 |
| [07-完整案例分析.md](./07-完整案例分析.md) | 拿本仓库 `bug-fix` skill 走一遍完整逆向→改造流程 |
| [examples/](./examples/) | 配套示例：一个"半成品 Skill"→ 修复后的版本 |

---

## 🎯 5 分钟核心结论（TL;DR）

1. **看 Skill 先看 `description`**：没有"当用户说 XXX 时"这种触发关键词的，质量基本不及格
2. **Skill 之间不能直接 `import`**：所谓"调用"其实是宿主 Agent 根据 description 同时加载多个 Skill，是**并行**不是**调用**
3. **跨工具兼容核心是 Frontmatter 字段名**：`description` 几乎所有工具都认；`allowed-tools`、`applyTo`、`model` 各家不一样
4. **质量看 3 个比例**：描述长度 / 正文长度 / 引用文件数，三者失衡的 Skill 多半是垃圾
5. **改别人的 Skill 永远先复制再改**，路径上加 `-fork` 后缀，不要直接覆盖原作者的目录

---

## 🚀 5 步快速上手流程

```
拿到一个陌生 Skill
   ↓
① 读 README + SKILL.md 的 frontmatter（30 秒）→ 决定要不要继续看
   ↓
② 用 tree 命令打印目录树 → 标出资源文件（30 秒）
   ↓
③ 用 03 章的清单打分（5 分钟）→ < 60 分直接弃用
   ↓
④ 用 05 章的 Prompt 让 AI 逆向解释一遍（2 分钟）→ 校对自己理解
   ↓
⑤ fork 一份，改 description 适配本地工具链 → 跑一次冒烟测试
```

---

## 📚 配套阅读

- 写 Skill：[../skill-authoring-research/](../skill-authoring-research/README.md)（同仓库已有）
- 本仓库已有的真实 Skill 集合：`C:\Users\<你>\.claude\skills\` 和 `c:\Users\<你>\.vscode\extensions\github.copilot-chat-*\assets\prompts\skills\`

---

## ⚠️ 心态建议

> "看不懂别人的 Skill 是正常的，作者自己一周后也看不懂自己的 Skill。"

Skill 本质是**别人浓缩自己工作经验后的提示词压缩包**，里面隐含了大量作者自己工作环境、语气、工具栈的偏见。**90% 的 Skill 不能直接用，必须本地化。**

不要因为看不懂就觉得自己笨，按本研究的 5 步法走，每一步都是机械流程。
