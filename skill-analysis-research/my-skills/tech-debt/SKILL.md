---
name: tech-debt
description: 技术债管理助手 - 扫描并量化代码中的技术债，生成优先级矩阵和偿还计划。当用户说"技术债"、"代码质量分析"、"重构计划"时自动激活。
argument-hint: "[模块路径 或 留空全量扫描]"
allowed-tools: Read, Write, Glob, Grep, Bash
context: fork
agent: Explore
---

# 技术债管理助手

系统扫描代码库，量化技术债，输出可执行的偿还计划。

## 参数
- `$ARGUMENTS`：要分析的模块路径（留空则全量扫描）

## 工作流程

### 阶段 1：多维度扫描

```bash
# 代码规模统计
find src -name "*.java" -o -name "*.py" -o -name "*.ts" | xargs wc -l 2>/dev/null | sort -rn | head -20

# 最复杂的文件（行数过多 = 违反单一职责）
find src -type f \( -name "*.java" -o -name "*.py" \) | xargs wc -l | sort -rn | head -10

# TODO/FIXME/HACK 注释
grep -rn "TODO\|FIXME\|HACK\|XXX\|WORKAROUND" src/ --include="*.java" --include="*.py" --include="*.ts" | head -30

# 重复代码（相似方法名）
grep -rn "private\|def \|function " src/ | awk -F: '{print $NF}' | sort | uniq -d | head -20

# 过期依赖（需要 npm/maven 命令）
npm outdated 2>/dev/null | head -10 || ./gradlew dependencyUpdates 2>/dev/null | grep -E "\->" | head -10
```

### 阶段 2：技术债分类

按 **影响度 × 修复成本** 矩阵分类：

```
影响度高
    │  Q1：立即处理          │  Q2：计划处理
    │  (高影响·低成本)        │  (高影响·高成本)
    ├──────────────────────────
    │  Q3：顺手处理          │  Q4：暂缓处理
    │  (低影响·低成本)        │  (低影响·高成本)
    └─────────────────────────── 修复成本高
```

**技术债类型清单：**

| 类型 | 扫描方式 | 常见表现 |
|------|---------|---------|
| 架构债 | 手动 | 上帝类、循环依赖、分层违规 |
| 测试债 | 覆盖率 | 覆盖率 < 60%、无集成测试 |
| 安全债 | grep | 硬编码密钥、未验证输入 |
| 依赖债 | outdated | 依赖 > 2 年未更新 |
| 文档债 | 文档对比 | README 过期、无 API 文档 |
| 性能债 | 代码分析 | N+1 查询、无索引、无缓存 |

### 阶段 3：输出技术债报告

```markdown
# 技术债分析报告

> 日期：{今天} | 扫描范围：{模块}

## 总览仪表盘

| 维度 | 债务量 | 严重程度 | 趋势 |
|------|--------|---------|------|
| 架构债 | {N} 处 | 🔴 高 | ↑ 增加 |
| 测试债 | 覆盖率 {N}% | 🟠 中 | → 持平 |
| 安全债 | {N} 处 | 🔴 高 | ↓ 减少 |
| 依赖债 | {N} 个过期 | 🟡 低 | ↑ 增加 |
| 文档债 | {N} 处 | 🟡 低 | → 持平 |

**技术债总评分：{N}/100（越低越好）**

---

## Q1：立即处理（高影响·低成本）

### TD-001：OrderService 中存在硬编码密钥
- **位置：** `src/order/OrderService.java:45`
- **类型：** 安全债
- **影响：** 生产密钥泄露风险
- **修复：** 改用 `@Value("${}")` 读取环境变量
- **预估工时：** 0.5h
- **负责人：** -

---

## Q2：计划处理（高影响·高成本）

### TD-002：用户模块缺乏集成测试
- **位置：** `src/user/`
- **类型：** 测试债
- **影响：** 发布风险高，回归 Bug 频率高
- **修复：** 补充 Testcontainers 集成测试
- **预估工时：** 3 天
- **建议加入：** Sprint 3

---

## Q3：顺手处理（低影响·低成本）

{列表...}

---

## 偿还计划

| Sprint | 待处理债务 | 预估工时 | 目标 |
|--------|----------|---------|------|
| 本 Sprint | TD-001, TD-005 | 4h | 消除安全债 |
| Sprint+1 | TD-002, TD-003 | 3天 | 测试覆盖率 > 75% |
| Sprint+2 | TD-004 | 2天 | 清理过期依赖 |

**建议：每个 Sprint 分配 20% 时间偿还技术债（"Boy Scout Rule"）**

---

## 防止技术债积累的机制

1. PR Review 中禁止合入引入新 TODO 的代码
2. CI 中加入覆盖率门控（< 80% 不能合并）
3. 每月执行一次 /tech-debt 扫描并追踪趋势
```

### 阶段 4：询问是否生成任务

询问用户是否将 Q1 技术债自动创建为 GitHub Issues（`gh issue create`）或 Sprint 任务。
