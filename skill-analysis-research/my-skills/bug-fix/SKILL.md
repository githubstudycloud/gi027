---
name: bug-fix
description: Bug分析修复助手 - 深度分析Bug根因，定位代码，给出修复方案。当用户说"修复bug"、"排查问题"、"报错了"、"fix"时自动激活。
argument-hint: "[错误信息 或 Bug描述]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
context: fork
agent: bug-analyzer
---

# Bug 分析修复助手

系统性地定位并修复 Bug，确保修复有测试保障，不引入新问题。

## 参数
- `$ARGUMENTS`：错误信息、堆栈、Bug 描述或复现步骤

## 工作流程

### 阶段 1：信息收集

**收集现场信息：**
```bash
# 最近的 git 改动（Bug 可能在这里）
git log --oneline -10
git diff HEAD~5 HEAD --stat

# 查看日志文件（如果存在）
ls logs/ 2>/dev/null
```

分析 `$ARGUMENTS` 中的：
- 错误类型（NPE / 404 / 500 / 业务逻辑错误）
- 堆栈信息（哪一行报错）
- 复现条件（什么操作触发）

### 阶段 2：定位根因

**根据错误类型定向搜索：**

```bash
# 搜索报错的类/方法名
grep -r "{ClassName}" src/ --include="*.java"

# 搜索相关 SQL
grep -r "SELECT.*{table}" src/

# 搜索最近修改的相关文件
git log --all --full-history -- "*{filename}*"
```

**执行链路追踪：**

1. 从报错入口（Controller/Route）开始
2. 逐层向下追踪调用链
3. 检查每一层的输入/输出假设
4. 找到"期望值"和"实际值"的偏差点

**常见根因模式：**

| 错误类型 | 常见根因 | 检查位置 |
|---------|---------|---------|
| NullPointerException | 未做 null 检查，Optional 未处理 | Service 层 |
| 404 Not Found | 路由配置错误，资源不存在 | Controller/Router |
| 500 Internal Error | 未捕获异常，DB 连接失败 | GlobalExceptionHandler |
| 数据不正确 | 事务边界问题，缓存过期 | Service/Repository |
| 并发问题 | 竞态条件，锁粒度不当 | Service 并发逻辑 |
| 权限错误 | RBAC 配置，JWT 过期 | Security 层 |

### 阶段 3：输出诊断报告

```markdown
## Bug 诊断报告

**Bug ID：** #{自增}
**严重程度：** 🔴 Critical / 🟠 Major / 🟡 Minor
**影响范围：** {受影响的功能/用户}

### 根因分析
{清晰描述为什么会出现这个问题}

### 执行链路
```
请求 → Controller:行号 → Service:行号 → Repository:行号
                              ↑ 问题出在这里
```

### 修复方案
**方案 A（推荐）：** {描述} | 风险：低 | 工作量：1h
**方案 B：** {描述} | 风险：中 | 工作量：3h
```

### 阶段 4：执行修复

获得用户确认后：

1. **应用代码修复**（使用 Edit 工具精确修改，不大范围重写）
2. **添加/更新测试**（必须有测试覆盖这个 Bug 场景，防止回归）
3. **验证修复**（描述如何验证）

修复代码原则：
- 只改必要的代码，不顺手重构
- 修复要有防御性（加 null 检查、边界判断）
- 注释说明为何这样修复（`// Fix: TICKET-xxx - reason`）

### 阶段 5：预防建议

```markdown
## 预防建议

1. **立即**：{能马上做的防范措施}
2. **本次 Sprint**：{建议加入到当前迭代的改进}
3. **技术债**：{记录到 /tech-debt}
```

提交建议：
```
fix({scope}): {一句话描述修复内容}

Root cause: {根因}
Fix: {修复方式}
Test: {测试验证方式}

Fixes #{issue-number}
```
