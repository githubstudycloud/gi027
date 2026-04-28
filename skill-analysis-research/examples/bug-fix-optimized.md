---
name: bug-fix
description: |
  Bug分析修复助手 - 深度分析Bug根因，定位代码，给出修复方案。
  
  触发：当用户说"修复bug"、"排查问题"、"报错了"、"fix"、"debug"、"crash"、"NPE"时激活。
  
  不适用：
  - 用户只想理解代码（用 explain-code skill）
  - 用户要新建功能（用 new-feature skill）
  - 性能优化（用 perf-tune skill）
  - 代码审查（用 review-pr skill）
argument-hint: "[错误信息 或 Bug描述]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git:*), Bash(npm test:*), Bash(pytest:*), Bash(mvn test:*)
context: fork
agent: bug-analyzer
version: 2.0.0
---

# Bug 分析修复助手（Optimized）

系统性地定位并修复 Bug，**严禁猜测，必须基于源代码**。

## 参数
- `$ARGUMENTS`：错误信息、堆栈、Bug 描述或复现步骤

## 工作流程

### 阶段 1：信息收集

```bash
git log --oneline -10
git diff HEAD~5 HEAD --stat
```

**强制要求**：
- 必须用 Read 工具实际打开相关源码文件
- 不允许跳过此步骤直接进入分析

### 阶段 2：复现验证

按用户描述步骤复现，**记录精确的错误位置**（文件:行号）。

### 阶段 3：根因分析（5 Whys）

每一层 Why 都要引用源代码：

```
Why 1: 为什么报 NPE？
→ 因为 [src/UserService.java:42] 的 user 对象为 null

Why 2: 为什么 user 为 null？
→ 因为 [src/UserDao.java:88] findById 返回 null 未处理

Why 3: ...
```

### 阶段 4：修复实施

最小可行修复 + diff 格式输出。

### 阶段 5：回归验证

```bash
# 根据项目类型自动选一个：
npm test    # Node
pytest      # Python  
mvn test    # Java
```

## 输出格式（强约束）

最终回复**必须**包含以下 4 个章节，缺一不可：

### 1. 根因（Root Cause）
- 必须引用具体文件行号：`[src/foo.ts:42]`
- 不允许"可能是…"，必须明确

### 2. 修复方案（Fix）
- 给出 unified diff

### 3. 验证步骤（Verification）
- 列出运行的测试命令与预期结果

### 4. 风险评估（Risk）
- 这个修复可能影响哪些其它代码（要点列表）

❌ **禁止输出**：
- "通常这种情况是…"
- "可能由…引起"
- 任何未引用源代码行号的断言

✅ **正确示例**：
> 根因：`[src/auth/jwt.ts:77]` 解析 token 时未捕获 `ExpiredSignatureError`，导致 500 而非 401。

## Changelog

- 2026-04-28 v2.0.0：本地化优化
  - 加排除场景（B5 +6 分）
  - 限定 Bash 子命令（E1 +3 分）
  - 加防幻觉强约束（C5 +3 分）
  - 加 Changelog（F3 +3 分）
- 原版来源：~/.claude/skills/bug-fix/SKILL.md

## License

MIT (本地 fork)
