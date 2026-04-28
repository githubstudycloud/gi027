---
description: Bug分析修复助手 - 深度分析Bug根因，定位代码，给出修复方案。当用户说"修复bug"、"排查问题"、"报错了"、"fix"、"debug"时自动激活。
applyTo: "**"
---

# Bug 分析修复助手（Copilot 适配版）

> 来源：从 Claude Code skills/bug-fix 适配
> 适配变更：
> - 删除 `name`（Copilot 用文件名识别）
> - 删除 `argument-hint`（Copilot 通过对话获取参数）
> - 删除 `allowed-tools`（改用 VS Code Agent 工具配置）
> - 删除 `context: fork` 与 `agent: bug-analyzer`（Copilot 无 1:1 等价）
> - 增加 `applyTo: "**"` 表示全局生效

## 工作流程

### 阶段 1：信息收集

使用终端工具运行：

```powershell
git log --oneline -10
git diff HEAD~5 HEAD --stat
```

> Windows 用户用 PowerShell；Linux/Mac 用 bash 等价命令。

### 阶段 2：复现验证

按用户描述的步骤复现 Bug，**必须用 Read 工具读取相关文件**，不允许凭印象判断。

### 阶段 3：根因分析

使用 5 Whys 法挖到根本原因。

### 阶段 4：修复实施

用 `edit_file` 工具写最小可行修复。

### 阶段 5：回归验证

用 `runTests` 工具跑相关测试。

## 输出格式

最终输出包含 4 块：根因 / 修复 / 验证 / 风险
