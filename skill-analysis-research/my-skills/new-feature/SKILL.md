---
name: new-feature
description: 新功能完整工作流 - 从需求到代码的一站式助手，串联需求→设计→API→数据库→代码→测试全流程。当用户说"做一个新功能"、"开发XXX"、"new feature"时自动激活。
argument-hint: "[功能描述]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# 新功能完整工作流

将 `$ARGUMENTS` 描述的功能，从零推进到可提交的完整实现。

## 参数
- `$ARGUMENTS`：要开发的功能描述

---

## 阶段 0：快速了解

扫描当前项目，了解：
1. 技术栈（`package.json` / `pom.xml` / `pyproject.toml`）
2. 现有代码结构（`src/` 目录）
3. 分支状态（`git status` + `git branch`）

然后**用 1-2 句话确认**你理解的功能范围，并询问用户：

> "我理解你想做的是：{总结}。是否需要完整走一遍需求→设计→实现流程，还是直接跳到编码？"

---

## 阶段 1：需求确认（5 分钟）

**最多问 3 个问题**，快速确认：
1. 核心用户场景是什么？
2. MVP 范围（本期做什么，不做什么）？
3. 有无特殊约束（性能、兼容性、安全）？

输出简版用户故事（不用完整 PRD）：
```
作为 [用户角色]，我希望 [功能]，以便 [价值]。

MVP 包含：
- ✅ ...
- ✅ ...

本期不做：
- ❌ ...
```

---

## 阶段 2：技术设计（快速版）

输出关键设计决策（不用完整设计文档）：

```
数据模型：{涉及哪些表/字段}
API：{几个关键接口}
核心流程：{一句话描述主流程}
潜在风险：{1-2 个关键风险}
```

询问：**"设计确认后开始编码？"**

---

## 阶段 3：生成代码骨架

根据检测到的技术栈，生成以下文件：

### 后端（Spring Boot）
按顺序创建：
1. `V{N}__{功能}.sql` - 数据库迁移（遵循 db-standards）
2. `{Entity}.java` - JPA Entity
3. `{Feature}Dto.java` - 请求/响应 DTO
4. `{Feature}Repository.java` - 数据访问
5. `{Feature}Service.java` - 业务逻辑
6. `{Feature}Controller.java` - REST 接口（遵循 api-design.md）

### 后端（FastAPI）
按顺序创建：
1. `alembic/versions/{N}_{功能}.py` - 数据库迁移
2. `src/{feature}/models.py` - SQLAlchemy 模型
3. `src/{feature}/schemas.py` - Pydantic 模型
4. `src/{feature}/service.py` - 业务逻辑
5. `src/{feature}/router.py` - API 路由

### 前端（Vue 3）
按顺序创建：
1. `src/services/{feature}Service.ts` - API 调用层
2. `src/stores/{feature}.ts` - Pinia Store
3. `src/views/{Feature}View.vue` - 页面组件
4. `src/components/{Feature}*.vue` - 子组件

### 前端（React/Next.js）
按顺序创建：
1. `src/services/{feature}Service.ts` - API 调用
2. `src/store/use{Feature}Store.ts` - Zustand Store
3. `src/app/{feature}/page.tsx` - Server Component 页面
4. `src/app/{feature}/_components/` - 私有组件

---

## 阶段 4：生成测试

生成对应测试文件：

**单元测试**（覆盖 Service 核心逻辑）
**集成测试**（Testcontainers / httpx）
**前端组件测试**（Vitest / Testing Library）

测试命名遵循：
```
正常场景：should_{动词}_{结果}_when_{条件}
异常场景：should_throw_{异常}_when_{错误条件}
```

---

## 阶段 5：代码自检

生成完成后，**自动执行规范检查**（等同于 /check-standards）：

- 安全：无硬编码密钥，SQL 参数化，对象级权限
- 规范：分层正确，命名符合约定
- 完整性：测试覆盖核心路径

输出：
```
✅ 生成了 {N} 个文件
⚠️ 注意：{如果有问题}
📝 下一步：git add → /commit → 创建 PR
```
