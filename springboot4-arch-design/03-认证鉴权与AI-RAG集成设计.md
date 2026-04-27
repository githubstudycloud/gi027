# 03 - 认证鉴权 与 AI / RAG 集成设计

> 版本：v1.0 | 日期：2026-04-27 | 状态：草稿

---

## 1. 认证鉴权（IAM）

### 1.1 模型

- **认证（AuthN）**：你是谁——多渠道（账密 / 短信 / 扫码 / OAuth2 / OIDC / 企业微信 / 飞书 / 钉钉 / SAML）。
- **鉴权（AuthZ）**：你能做什么——RBAC + ABAC 混合（角色给基础权限，属性补充细粒度）。
- **会话（Session）**：JWT（无状态，跨服务）+ Redis 黑名单（可吊销）。

### 1.2 模块拆分

```
security-api          // 抽象：UserPrincipal、Permission、AuthProvider SPI
security-core         // Spring Security 6 集成、过滤器链
security-jwt          // JWT 签发 / 校验
security-oauth2       // 三方登录（Google / GitHub / 微信 / 企微 / 飞书 / 钉钉）
security-saml         // 企业 SSO
security-mfa          // TOTP / WebAuthn
security-rbac         // 角色/权限模型 + 公共库表
security-abac         // 表达式（SpEL）策略引擎
security-audit        // 登录、越权、敏感操作审计
```

### 1.3 三方认证集成

| 渠道 | 协议 | 备注 |
|------|------|------|
| 微信开放平台 / 企业微信 | OAuth2 自定义 | 需 access_token 缓存 |
| 飞书 / 钉钉 | OAuth2 + 自定义 | 通讯录同步独立模块 |
| Google / GitHub / Microsoft | OIDC | 标准 |
| 企业 IdP（Okta / Azure AD） | SAML 2.0 / OIDC | 默认 OIDC |
| LDAP / AD | LDAP | 兼容老系统 |

> 所有三方登录走 `AuthProvider` SPI；新增渠道只需实现接口 + 配置启用，不改主流程。

### 1.4 鉴权决策点

```
请求 → Gateway(粗粒度: URL 白名单) → 业务服务 Filter(JWT 解析)
     → MethodInterceptor(@PreAuthorize)
     → 业务方法内显式 PolicyEngine.check(action, resource)  ← 数据级
```

### 1.5 关键约定

- 不在业务代码中使用 `SecurityContextHolder.getContext()`，统一用 `CurrentUser.get()` 封装；便于测试与替换。
- 所有越权 / 鉴权失败必须落审计表 `t_security_audit`。

---

## 2. AI 集成

### 2.1 总体定位

AI 能力作为**独立 starter**（`enterprise-ai-*`），业务项目按需引入；不污染业务核心模块。

```
enterprise-ai/
├── ai-api          // 抽象：ChatClient、EmbeddingClient、Tool、Agent
├── ai-llm          // 多模型：OpenAI / Azure OpenAI / 通义 / DeepSeek / 本地 Ollama
├── ai-rag          // 文档解析、切块、向量化、检索、Rerank
├── ai-agent        // 工具调用、Plan-Execute
├── ai-vectorstore  // PgVector / Milvus / Redis-Vector / Elasticsearch
├── ai-guardrail    // 输入/输出过滤、PII 脱敏、敏感词
└── ai-observability // Token / 成本 / 延迟监控
```

### 2.2 框架选型

| 选项 | 优点 | 缺点 | 选用 |
|------|------|------|------|
| Spring AI 1.1 / 2.0 | Spring 原生、生态接入快 | 仍在演进 | ✅ 主选 |
| LangChain4j | 功能更全、Agent 强 | 与 Spring 集成需手动 | ⚠️ 备选（复杂 Agent 场景） |
| 自研薄封装 | 灵活 | 维护成本 | ❌ |

> 主选 Spring AI，但通过 `ai-api` 抽象层屏蔽，未来可平滑替换。

### 2.3 多模型路由

```
ChatRequest ──► ModelRouter ──┐
                              ├─► OpenAI（外网）
                              ├─► Azure OpenAI（合规）
                              ├─► 通义千问 / DeepSeek（国内）
                              └─► Ollama（本地，敏感场景）
路由依据：场景标签 + 成本预算 + 内容敏感度 + 可用性
```

### 2.4 RAG 流水线

```
[原始文档] → [解析(Tika/PDFBox)] → [清洗] → [切块(语义/固定/递归)]
          → [Embedding] → [VectorStore]
查询：
[Query] → [Query 改写] → [Embedding] → [向量检索 topK]
       → [重排 Rerank] → [上下文组装] → [LLM 生成] → [引用回填] → [Guardrail]
```

### 2.5 向量库选型

| 库 | 适用 | 备注 |
|----|------|------|
| **PgVector** | 中小规模（< 1000 万向量）、已用 PG | ✅ 默认 |
| **Milvus** | 大规模、专用向量场景 | 大数据量切换 |
| **Redis-Vector** | 缓存型、低延迟 | 二级缓存 |
| **Elasticsearch 8 (kNN)** | 已用 ES、混合检索 | 候选 |

> 通过 `VectorStore` 接口抽象，迁移只换实现。

### 2.6 安全与合规（必做）

- **PII 脱敏**：入向量库前必须脱敏（手机号 / 身份证 / 邮箱）。
- **租户隔离**：向量集合 / 索引按 `tenantId` 分区，查询强制带 filter。
- **Prompt Injection 防御**：`ai-guardrail` 模块统一过滤。
- **成本控制**：每租户 / 每接口 token 配额，超限熔断。
- **审计**：所有 LLM 调用落 `t_ai_call_log`（脱敏后）。

### 2.7 Agent / Tool

- 工具注册：`@AiTool` 注解 + 自动生成 JSON Schema；
- 工具执行强制走 `ToolExecutor`，带超时 / 熔断 / 权限校验（Agent 调工具也要鉴权！）。

---

## 3. 自我修订记录

| 轮次 | 修订点 |
|------|--------|
| R1 | AI 与 IAM 拆为独立 starter，避免污染核心模块 |
| R2 | 增加 `AuthProvider` / `VectorStore` SPI，避免被单一供应商锁定 |
| R3 | 强制 Agent 工具调用走鉴权；强制 RAG 按租户隔离（高危盲区） |

---

## 4. 待确认

1. **AI 主要场景**？（决定 RAG / Agent / 简单问答的投入比例）
2. 是否有数据**出境合规**约束？（决定是否禁用海外模型）
3. 三方登录第一批接入清单？
4. 是否需要**统一身份中心（IDaaS）**作为单独服务？还是 starter 内置？
