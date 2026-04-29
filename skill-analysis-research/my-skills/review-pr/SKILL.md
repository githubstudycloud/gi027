---
name: review-pr
description: PR代码审查 - 深度审查Pull Request，检查安全、质量、规范、测试覆盖。当用户说"review PR"、"代码审查"、"帮我看看这个PR"时自动激活。
argument-hint: "[PR号 或 分支名，留空则审查当前分支]"
allowed-tools: Read, Glob, Grep, Bash
context: fork
agent: code-reviewer
---

# PR 代码审查助手

对标 `D:/gi021/project-standards/` 全套规范，输出专业的 Code Review 报告。

## 参数
- `$ARGUMENTS`：PR 编号（如 `123`）或分支名（如 `feature/user-auth`），留空则审查当前分支与 develop 的差异

## 工作流程

### 阶段 1：获取变更内容

```bash
# 如果有 PR 号
gh pr view $ARGUMENTS --json title,body,additions,deletions,changedFiles
gh pr diff $ARGUMENTS

# 如果是分支名或当前分支
git log develop..HEAD --oneline
git diff develop...HEAD --stat
git diff develop...HEAD
```

扫描变更文件类型，确定需要对照哪些规范文档。

### 阶段 2：多维度审查

对每个变更文件执行以下检查维度：

---

#### 2.1 安全审查（最高优先级）

参考：`D:/gi021/project-standards/security/security-standards.md`

```
OWASP Top 10 逐项检查：
🔍 A01 访问控制 - 每个端点是否做了对象级权限检查？
🔍 A02 加密 - 密码是否 Bcrypt/Argon2？Token 是否安全存储？
🔍 A03 注入 - SQL 是否参数化？无字符串拼接？
🔍 A05 配置 - 密钥是否从环境变量读取？无硬编码？
🔍 A07 认证 - JWT 验证是否完整（iss/aud/exp）？
```

#### 2.2 代码质量

```
架构层面：
□ 是否违反了单一职责原则？
□ Controller 是否包含业务逻辑（应在 Service 层）？
□ 是否存在循环依赖？
□ 异常处理是否完整（不吞异常，不过度 try-catch）？

代码逻辑：
□ 是否存在 N+1 查询？
□ 边界条件是否处理（null、空列表、极端值）？
□ 并发场景是否安全？
□ 资源是否正确释放（连接、流、锁）？
```

#### 2.3 API 规范

参考：`D:/gi021/project-standards/api-design.md`

```
□ URL 命名：小写复数名词，无动词？
□ HTTP 状态码正确？（201 创建，204 删除，400 校验失败）
□ 响应格式统一？（遵循 ApiResponse 包装）
□ 错误响应 RFC 7807 格式？
□ 是否有 @Valid 输入校验？
```

#### 2.4 数据库变更

参考：`D:/gi021/project-standards/database/database-standards.md`

```
□ 迁移文件是否使用 TIMESTAMPTZ（不是 TIMESTAMP）？
□ 外键是否建了索引？
□ 表/列命名是否 snake_case？
□ 迁移是否幂等（可重复执行）？
□ 是否有对应的 downgrade 方法？
```

#### 2.5 测试覆盖

参考：`D:/gi021/project-standards/testing/testing-standards.md`

```
□ 新增功能是否有对应单元测试？
□ 关键流程是否有集成测试？
□ 是否使用 Testcontainers（不用 H2）？
□ 测试是否真正有效（不只是测了 happy path）？
□ 前端是否用 data-test 属性作为选择器？
```

#### 2.6 可维护性

```
□ 变量/方法命名是否清晰表达意图？
□ 复杂逻辑是否有注释？
□ 魔法数字是否提取为常量？
□ PR 大小是否合理（< 400 行）？如超出建议如何拆分。
```

### 阶段 3：输出 Review 报告

```markdown
## Code Review 报告

**PR：** {标题} | **分支：** {branch} → develop
**变更量：** +{添加行} / -{删除行} | **文件数：** {N}
**总体评级：** ✅ 可合并 / ⚠️ 小修后合并 / ❌ 需要大改

---

### 🔴 BLOCKER（{N}个，必须修复才能合并）

#### [安全] 硬编码 JWT Secret
📍 `src/config/SecurityConfig.java:42`
```java
// 当前代码（危险！）
private String secret = "hardcoded-secret-key";

// 修复为
@Value("${app.security.jwt-secret}")
private String secret;
```

---

### 🟠 REQUIRED（{N}个，强烈建议修复）

#### [质量] OrderService 存在 N+1 查询
📍 `src/order/OrderService.java:67`
问题：循环内执行 `userRepository.findById()` 导致 N+1
修复：使用 `JOIN FETCH` 或批量查询

---

### 🟡 SUGGESTION（{N}个，可在后续 PR 中处理）

#### [规范] 响应状态码不准确
📍 `src/user/UserController.java:23`
问题：POST 接口返回 200，应返回 201
修复：`@ResponseStatus(HttpStatus.CREATED)`

---

### ✅ 做得好的地方
- 测试覆盖完整，包含边界场景
- Flyway 迁移脚本规范，包含 downgrade
- 异常处理统一走 GlobalExceptionHandler

---

### 📝 Review 建议
{总体评价和主要改进方向}

**合并建议：** {Wait for fixes / Approve with comments / Request changes}
```
