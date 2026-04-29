---
name: check-standards
description: 代码规范检查 - 对照项目规范检查代码质量、结构、安全性。当用户说"检查规范"、"代码审查"、"规范检查"时自动激活。
argument-hint: "[文件路径 或 模块名称，留空则检查当前改动]"
allowed-tools: Read, Glob, Grep, Bash
---

# 代码规范检查助手

对照 `D:/gi021/project-standards/` 规范，全面审查代码质量。

## 参数说明
- `$ARGUMENTS`：要检查的文件/目录，留空则检查 `git diff --staged` 的改动

## 工作流程

### 第一步：确定检查范围

```bash
# 如果没有参数，检查 staged 改动
git diff --staged --name-only 2>/dev/null || echo "no git"
```

根据文件类型选择对应规范：
- `.java` → `D:/gi021/project-standards/backend/springboot.md`
- `.py` → `D:/gi021/project-standards/backend/python-fastapi.md`
- `.vue` → `D:/gi021/project-standards/frontend/vue3.md`
- `.tsx` / `.ts` → `D:/gi021/project-standards/frontend/react-nextjs.md`
- `.sql` → `D:/gi021/project-standards/database/database-standards.md`

### 第二步：执行分层检查

读取相关文件后，按以下维度逐一检查，对每个问题给出 **严重级别**：

```
🔴 Critical  - 安全漏洞、数据丢失风险，必须修复
🟠 Major     - 违反核心规范，强烈建议修复
🟡 Minor     - 代码质量问题，建议修复
🔵 Info      - 风格建议，可选优化
```

#### 安全检查（对照 security-standards.md）
- [ ] 是否有硬编码密钥/密码/Token？
- [ ] SQL 查询是否使用参数化？（无字符串拼接）
- [ ] 是否校验了用户输入？
- [ ] 是否做了对象级权限检查（防 BOLA）？
- [ ] 敏感信息是否会泄露到日志或响应体？

#### 架构检查（对照对应后端/前端规范）
- [ ] 是否符合分层规范（Controller 不含业务逻辑）？
- [ ] 是否存在循环依赖？
- [ ] 是否存在 N+1 查询问题？
- [ ] 异常处理是否完整？

#### API 规范检查（对照 api-design.md）
- [ ] URL 命名是否符合规范（小写复数名词）？
- [ ] HTTP 状态码使用是否正确？
- [ ] 响应体格式是否统一？
- [ ] 是否有 API 版本号？

#### 数据库检查（对照 database-standards.md）
- [ ] 表/列命名是否 snake_case？
- [ ] 是否使用了 `TIMESTAMPTZ`（不是 `TIMESTAMP`）？
- [ ] 外键是否建了索引？
- [ ] 是否有 `created_at`/`updated_at`？

#### 测试覆盖（对照 testing-standards.md）
- [ ] 新增功能是否有对应测试？
- [ ] 是否使用了 Testcontainers（不用 H2）？
- [ ] 测试选择器是否用 `data-test` 属性（前端）？

### 第三步：输出结构化报告

```markdown
## 规范检查报告

**检查范围：** {文件列表}
**检查时间：** {今天}
**总体评级：** ✅ 通过 / ⚠️ 有问题 / ❌ 需整改

---

### 🔴 Critical Issues（{n} 个）
1. **[安全] 硬编码密钥**
   - 文件：`src/config.java:15`
   - 问题：JWT_SECRET 被直接写入代码
   - 修复：使用 `${JWT_SECRET}` 环境变量

### 🟠 Major Issues（{n} 个）
...

### 🟡 Minor Issues（{n} 个）
...

### ✅ 通过项
- 所有 SQL 查询使用参数化
- 响应体格式符合规范
- ...

---

**建议优先修复 Critical + Major 问题再合并 PR。**
```
