---
name: api-spec
description: API规范生成助手 - 生成符合OpenAPI 3.1标准的API设计文档。当用户说"生成API"、"设计接口"、"写OpenAPI"、"定义API规范"时自动激活。
argument-hint: "[资源名称 或 功能描述]"
allowed-tools: Read, Write, Glob, Grep
---

# API 规范生成助手

遵循 `D:/gi021/project-standards/api-design.md` 规范，生成 OpenAPI 3.1 格式的 API 设计文档。

## 参数说明
- `$ARGUMENTS`：要设计的资源名称或功能描述（如 "用户管理"、"订单"）

## 工作流程

### 第一步：读取规范和现有代码

1. 读取 `D:/gi021/project-standards/api-design.md` 了解规范要求
2. 扫描现有 API 文件（如 `src/*/router.py`、`*Controller.java`）避免重复

### 第二步：确认设计细节

根据 `$ARGUMENTS` 判断需要哪些接口，如不清晰则询问：
- 资源的主要属性有哪些？
- 需要哪些操作（CRUD 全部还是部分）？
- 是否需要嵌套资源？
- 是否有特殊的权限要求？

### 第三步：生成 OpenAPI 规范片段

输出标准 OpenAPI 3.1 YAML，严格遵循以下规范：
- URL：`/api/v1/{资源复数名}` 格式
- HTTP 方法语义正确（GET/POST/PUT/PATCH/DELETE）
- 错误响应遵循 RFC 7807 Problem Details
- 必须包含 security 声明
- 所有字段有 example 值

```yaml
# 生成的 OpenAPI 片段示例结构：
paths:
  /api/v1/{resource}:
    get: ...
    post: ...
  /api/v1/{resource}/{id}:
    get: ...
    patch: ...
    delete: ...

components:
  schemas:
    {Resource}Response: ...
    Create{Resource}Request: ...
    Update{Resource}Request: ...
```

### 第四步：生成对应的代码骨架

根据项目技术栈（检测 pom.xml / pyproject.toml）生成对应骨架：

**Spring Boot：**
```java
@RestController
@RequestMapping("/api/v1/{resources}")
public class {Resource}Controller { ... }
```

**FastAPI：**
```python
router = APIRouter(prefix="/{resources}", tags=["{Resource}"])

@router.get("/", response_model=list[{Resource}Response])
async def list_{resources}(): ...
```

### 第五步：说明后续步骤

- 将规范保存到 `docs/api/openapi.yaml`
- 建议配套的数据库表设计（/db-schema）
- 建议同步更新 CHANGELOG
