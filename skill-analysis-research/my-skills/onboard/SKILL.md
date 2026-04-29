---
name: onboard
description: 项目入驻助手 - 为新成员生成项目全景导览，或帮助快速理解陌生项目。当用户说"帮我了解项目"、"新人入驻"、"onboard"、"介绍一下这个项目"时自动激活。
argument-hint: "[新成员角色 如 backend/frontend/fullstack，留空则全栈]"
allowed-tools: Read, Glob, Grep, Bash
context: fork
agent: Explore
---

# 项目入驻助手

深度扫描项目，生成适合 `$ARGUMENTS` 角色的入驻文档。

## 参数
- `$ARGUMENTS`：角色（`backend` / `frontend` / `fullstack` / `devops`，默认 `fullstack`）

## 工作流程

### 阶段 1：全量项目探索

```bash
# 项目基本信息
ls -la
cat README.md 2>/dev/null | head -50

# 技术栈检测
cat package.json 2>/dev/null | python -c "import sys,json; d=json.load(sys.stdin); print(list(d.get('dependencies',{}).keys())[:10])"
cat pom.xml 2>/dev/null | grep -E "<artifactId>" | head -10
cat pyproject.toml 2>/dev/null | head -20

# 项目结构
find . -maxdepth 3 -type d \
  -not -path "*/.git/*" \
  -not -path "*/node_modules/*" \
  -not -path "*/.gradle/*" \
  -not -path "*/target/*" \
  -not -path "*/__pycache__/*" \
  | sort | head -40

# 入口文件
ls src/main/java/**/*Application.java 2>/dev/null || \
ls main.py app.py 2>/dev/null || \
cat package.json 2>/dev/null | grep '"main"\|"scripts"'

# API 端点总览
grep -rn "@GetMapping\|@PostMapping\|@PutMapping\|@DeleteMapping\|@PatchMapping\|@router\.\|@app\." src/ 2>/dev/null | grep -v test | head -30

# 数据库迁移（了解数据模型）
ls src/main/resources/db/migration/ 2>/dev/null | head -10 || ls alembic/versions/ 2>/dev/null | head -10

# Git 历史（了解开发节奏）
git log --oneline -15
git shortlog -sn --no-merges -10
```

### 阶段 2：生成入驻文档

根据角色（`$ARGUMENTS`）输出对应深度的文档：

```markdown
# {项目名} 项目入驻指南

> 角色：{角色} | 生成日期：{今天}

---

## 1. 项目一句话介绍
{从 README 或代码推断，用 1-2 句话描述这个项目是做什么的}

## 2. 技术栈总览

| 层级 | 技术 | 版本 | 备注 |
|------|------|------|------|
| 后端框架 | | | |
| 数据库 | | | |
| 缓存 | | | |
| 前端框架 | | | |
| 构建工具 | | | |
| 容器化 | | | |

## 3. 快速启动（5 分钟跑起来）

### 前置要求
- [ ] Java 21 / Node 20 / Python 3.12（按需）
- [ ] Docker Desktop 启动中
- [ ] 设置环境变量（复制 `.env.example` → `.env`）

### 启动步骤
```bash
# 1. 克隆项目
git clone {repo-url}

# 2. 启动依赖（DB、Redis、Kafka）
docker-compose up -d

# 3. 初始化数据库
./gradlew flywayMigrate  # 或 alembic upgrade head

# 4. 启动应用
./gradlew bootRun  # 或 uvicorn main:app --reload

# 5. 验证
curl http://localhost:8080/actuator/health
```

## 4. 项目结构导览

{根据扫描结果生成目录说明}

```
src/
├── auth/        ← 认证相关（JWT 登录、刷新）
├── user/        ← 用户管理
├── order/       ← 订单核心业务
└── config/      ← 全局配置
```

**关键文件：**
| 文件 | 作用 |
|------|------|
| `Application.java` | 启动入口 |
| `SecurityConfig.java` | 安全配置（JWT、CORS） |
| `GlobalExceptionHandler.java` | 统一异常处理 |

## 5. 数据模型概览

{根据迁移文件生成简要 ER 描述}

## 6. API 接口概览

{根据 Controller 扫描结果列出主要接口}

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/users | 用户列表 |
| POST | /api/v1/auth/login | 用户登录 |

完整 API 文档：`docs/api/openapi.yaml` 或 `http://localhost:8080/api/docs`

## 7. 开发工作流

```
1. 从 develop 切出功能分支：git checkout -b feature/PROJ-XXX-desc
2. 开发 + 测试（/new-feature 辅助）
3. PR 前自检：/check-standards
4. 创建 PR → 等待 2 个 Review (/review-pr)
5. CI 通过 → Squash Merge → 删除分支
```

## 8. 常用命令速查

```bash
# 开发
./gradlew test              # 运行单元测试
./gradlew integrationTest   # 运行集成测试
./gradlew spotlessApply     # 格式化代码

# 数据库
./gradlew flywayMigrate     # 执行迁移
./gradlew flywayInfo        # 查看迁移状态

# 查看日志
docker-compose logs -f app
```

## 9. 重要规范

| 规范文档 | 内容 |
|---------|------|
| 项目规范总览 | `D:/gi021/project-standards/README.md` |
| API 设计 | `D:/gi021/project-standards/api-design.md` |
| 提交规范 | Conventional Commits |
| 分支策略 | GitFlow |

## 10. 常见问题

**Q: 启动报数据库连接错误？**
A: 确认 docker-compose 中的 postgres 容器已启动：`docker ps`

**Q: 测试跑不起来？**
A: 确认 Docker 运行中（Testcontainers 需要 Docker）

**Q: 找不到某个功能的代码？**
A: 按领域分包，在 `src/{domain}/` 目录下查找

---

## 新人入职任务清单
- [ ] 成功本地启动项目
- [ ] 阅读规范文档（project-standards）
- [ ] 完成一个小 Bug 修复（熟悉工作流）
- [ ] 了解 CI/CD 流程
- [ ] 完成第一个功能开发

**有问题找：** {从 git shortlog 提取最活跃的贡献者}
```
