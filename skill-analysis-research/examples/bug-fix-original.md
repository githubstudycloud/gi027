---
name: bug-fix
description: Bug分析修复助手 - 深度分析Bug根因，定位代码，给出修复方案。当用户说"修复bug"、"排查问题"、"报错了"、"fix"时自动激活。
argument-hint: "[错误信息 或 Bug描述]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
context: fork
agent: bug-analyzer
---

# Bug 分析修复助手

系统性地定位并修复 Bug，确保修复有测试保障。

## 参数
- `$ARGUMENTS`：错误信息、堆栈、Bug 描述或复现步骤

## 工作流程

### 阶段 1：信息收集

```bash
git log --oneline -10
git diff HEAD~5 HEAD --stat
```

### 阶段 2：复现验证

按用户描述的步骤复现 Bug，确认现象。

### 阶段 3：根因分析

使用 5 Whys 法挖到根本原因，不能停留在表面症状。

### 阶段 4：修复实施

写最小可行的修复，避免顺手重构。

### 阶段 5：回归验证

跑测试、跑相关 e2e，确认没引入回归。

## 输出格式

最终输出包含：根因 / 修复 / 验证 / 风险 四块。
