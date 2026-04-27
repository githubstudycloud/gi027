# Spring Boot 4.x 企业级框架设计文档

## 1. 文档目标

本文档描述 `springboot4-enterprise-framework` 的设计原则、模块边界、技术选型、AI 能力集成方式、运行治理策略与后续扩展路线，作为项目初始化、团队协作和架构演进的统一基线。

## 2. 建设目标

- 建立符合企业规范的 `Spring Boot 4.x` 多模块基线工程
- 提供可直接运行、可直接二次开发的企业级骨架
- 统一接口响应、异常治理、安全策略、链路追踪与可观测性能力
- 将 `Spring AI` 作为平台一级能力接入，而不是零散嵌入某个单点业务
- 为数据库、缓存、消息队列、配置中心、向量数据库、MCP 工具生态预留清晰扩展点
- 降低团队从 0 到 1 的初始化成本，并形成长期可演进的架构基线

## 3. 设计原则

- 分层清晰：公共层、核心层、AI 契约层、启动装配层职责明确
- 低耦合：`core` 与 `ai` 只表达契约，不依赖具体 Web 或基础设施实现
- 高内聚：通用响应、错误码、异常、AI 模型契约统一收敛
- 约定优先：统一目录结构、配置命名、接口格式和扩展方式
- 先可用再增强：优先提供可跑通的企业级最小骨架，再逐步增强治理能力
- 安全默认：默认仅开放最小匿名接口，AI 能力默认纳入鉴权边界
- AI 原生：将对话、结构化输出、RAG、工具调用视为平台能力而非 Demo 代码

## 4. 技术基线

- JDK：21 作为推荐 LTS 基线
- 构建工具：Maven 3.9+
- 核心框架：Spring Boot 4.0.4
- 兼容体系：Spring Framework 7.x、Jakarta EE 11
- Web：Spring MVC
- 安全：Spring Security
- 校验：Bean Validation
- 可观测性：Spring Boot Actuator
- AI 框架：Spring AI 2.0.0-M2
- AI 模型接入：OpenAI Compatible Starter
- 测试：Spring Boot Test、MockMvc、Spring Security Test

## 5. 工程结构

```text
springboot4-enterprise-framework/
├─ docs/
│  └─ design.md
├─ enterprise-common/
├─ enterprise-core/
├─ enterprise-ai/
├─ enterprise-boot/
├─ pom.xml
└─ README.md
```

### 5.1 模块职责

#### enterprise-common

定位：承载跨模块公共能力。

职责：

- 统一响应对象 `ApiResponse`
- 统一错误码 `ErrorCode`
- 统一业务异常 `BusinessException`

约束：

- 不依赖具体业务
- 不耦合 Web 控制器和基础设施实现

#### enterprise-core

定位：承载核心业务契约和领域模型抽象。

职责：

- 定义系统级门面接口 `SystemFacade`
- 定义核心模型 `SystemStatus`

约束：

- 只表达业务能力和领域语义
- 不放置 Controller、配置类、数据库适配代码

#### enterprise-ai

定位：承载 AI 能力契约和模型，作为平台 AI 能力的稳定抽象层。

职责：

- 定义 AI 请求/响应模型 `AiApiModels`
- 定义统一 AI 门面 `EnterpriseAiFacade`
- 隔离启动层对具体 AI 实现的依赖

约束：

- 不直接依赖 Web 层与第三方模型供应商实现
- 只沉淀跨业务可复用的 AI 契约

#### enterprise-boot

定位：承载启动装配、交付入口和 AI 运行时实现。

职责：

- 应用启动
- Web API 暴露
- Spring Security 安全配置
- 全局异常处理
- TraceId 过滤器
- 配置文件与 Actuator 暴露
- Spring AI 运行时实现、工具定义与 RAG 存储

约束：

- 允许依赖 `common`、`core`、`ai`
- 作为最终可运行模块

## 6. 总体架构

```text
Client
  |
  v
Controller Layer
  |- SystemController
  |- AiController
  |
  v
Facade Layer
  |- SystemFacade
  |- EnterpriseAiFacade
  |
  v
Runtime Services
  |- SecurityConfig
  |- TraceIdFilter
  |- GlobalExceptionHandler
  |- SpringAiEnterpriseFacade
  |- PlatformAiTools
  |
  v
External Providers / Storage
  |- OpenAI Chat / Embedding / Image / Audio / Moderation
  |- Local Vector Store JSON
  |- Knowledge Markdown Files
```

## 7. 分层设计

推荐按下列逻辑组织代码：

- `common`：通用模型、错误码、上下文对象
- `core`：领域模型、领域服务接口、业务契约
- `ai`：AI 协议模型、统一门面接口
- `boot`：配置类、控制器、过滤器、适配器实现、Spring AI 运行时装配

当前框架是最小企业级落地版本，后续可进一步细分为：

- `application`：应用服务编排
- `domain`：领域模型和领域规则
- `infrastructure`：数据库、缓存、MQ、外部服务、向量库适配
- `interfaces`：HTTP、RPC、事件订阅等对外入口

## 8. 核心基础治理

### 8.1 统一响应模型

所有接口优先使用统一返回结构：

- `timestamp`：响应生成时间
- `code`：业务码
- `message`：业务说明
- `traceId`：链路标识
- `data`：业务负载

设计价值：

- 降低前后端联调成本
- 支持灰度、问题追踪和统一错误展示
- 便于网关、日志平台和监控系统做结构化解析

### 8.2 异常治理

通过全局异常处理器统一捕获：

- 业务异常
- 参数校验异常
- 未预期系统异常

处理原则：

- 不向外暴露敏感堆栈
- 保留明确业务码和可追踪 `traceId`
- 错误日志面向运维，错误响应面向调用方

### 8.3 安全基线

当前版本采用 Basic Auth 作为最小安全样板，原因如下：

- 零额外基础设施即可运行
- 便于开发期联调
- 可以平滑迁移到 JWT、OAuth2 或企业 SSO

安全策略：

- `GET /actuator/health` 开放
- `GET /actuator/info` 开放
- `GET /api/v1/system/ping` 开放
- `GET /api/v1/ai/capabilities` 开放
- 其余接口默认鉴权
- 会话策略设为无状态
- 默认口令仅用于开发环境

后续建议增强：

- 接入 OAuth2 Resource Server
- 接入 API 网关统一鉴权
- 接入 RBAC / ABAC 权限模型
- 接入审计日志和操作留痕
- 对 AI 接口补充限流、熔断、配额和租户隔离

### 8.4 TraceId 传播

在 `TraceIdFilter` 中完成：

- 优先复用请求头中的 `X-Trace-Id`
- 若不存在则自动生成
- 回写到响应头
- 注入日志上下文 `MDC`

设计价值：

- 提升跨服务链路排障效率
- 为日志聚合平台、APM 和监控告警提供关联键
- 支撑 AI 调用链、工具调用和检索链路排查

### 8.5 可观测性

基于 Actuator 提供：

- 健康检查
- 应用基础信息

后续建议：

- 接入 Prometheus 指标
- 接入 Micrometer Tracing
- 接入 OpenTelemetry
- 建立 SLI/SLO 监控体系
- 对 AI 请求增加 token、耗时、模型、命中片段数等埋点

## 9. Spring AI 集成设计

### 9.1 设计目标

本框架中的 AI 集成不是简单增加依赖，而是提供企业级统一 AI 平台能力：

- 将模型接入与业务控制器解耦
- 统一 AI 请求/响应协议
- 在同一门面下收敛 Chat、Embedding、RAG、Image、Audio 等能力
- 为未来切换模型供应商、向量存储、MCP Server 留出稳定边界

### 9.2 能力矩阵

当前版本实现如下能力：

- `Chat`
- `Structured Output`
- `Tool Calling`
- `RAG`
- `Embedding`
- `Image Generation`
- `Moderation`
- `Text-to-Speech`
- `Transcription`
- `MCP Ready`

说明：

- `MCP Ready` 表示已经接入 `spring-ai-starter-mcp-client`，具备向企业 MCP 工具生态扩展的依赖基础
- 当前版本未内置具体外部 MCP Server 连接配置，避免演示工程耦合特定外部系统

### 9.3 核心组件

#### EnterpriseAiFacade

统一 AI 门面，屏蔽控制器对具体模型、提示词拼装和存储细节的感知。

能力包括：

- 对话
- 结构化抽取
- 向量化
- 文档入库
- RAG 问答
- 图像生成
- 审核
- 语音合成
- 音频转写

#### SpringAiEnterpriseFacade

平台 AI 运行时实现，负责：

- 延迟获取 `ChatClient.Builder`
- 延迟获取 `EmbeddingModel`、`ImageModel`、`ModerationModel`
- 统一系统提示词拼装
- 工具调用启用与关闭
- 文档切分和向量生成
- 本地向量库存储与检索

#### PlatformAiTools

通过 `@Tool` 暴露企业平台工具能力：

- 获取平台状态
- 获取当前时间
- 判断平台是否支持指定能力

设计价值：

- 演示如何将“平台内事实”注入模型
- 为后续扩展数据库查询、配置查询、审批辅助等工具模式提供样板

#### AiProperties

集中管理 AI 配置：

- 默认系统提示词
- RAG 检索数量
- 向量库存储路径
- 图像模型
- 转写模型
- 语音模型与默认音色

### 9.4 AI 请求处理流程

#### 标准对话流程

1. `AiController` 接收 `/api/v1/ai/chat`
2. 读取 `traceId`
3. 调用 `EnterpriseAiFacade.chat()`
4. `SpringAiEnterpriseFacade` 构建 `ChatClient`
5. 按请求参数决定是否启用工具调用和知识库增强
6. 调用模型并返回统一响应

#### 结构化输出流程

1. 接收自然语言文本
2. 使用 `BeanOutputConverter` 生成目标 JSON 格式说明
3. 将格式要求注入提示词
4. 模型返回结果后转换为强类型对象

#### RAG 入库流程

1. 接收文档内容和元数据
2. 使用 `TokenTextSplitter` 进行切块
3. 调用 `EmbeddingModel` 生成每个块的向量
4. 保存文本、元数据、向量到本地向量文件
5. 返回入库后的块信息

#### RAG 问答流程

1. 对用户问题生成查询向量
2. 从本地向量库中按余弦相似度检索 `topK`
3. 将命中的知识片段拼接到用户提示词
4. 由模型基于知识片段增强回答
5. 在响应中返回参考片段

### 9.5 为何采用本地向量存储

当前版本没有强绑定外部向量数据库，而是采用“`Spring AI Embedding + 本地 JSON 向量存储`”方案，原因如下：

- 让工程在无额外基础设施下即可运行和演示
- 避免样板工程与特定向量库厂商耦合
- 将重点放在 RAG 流程、能力抽象和企业扩展点设计上

该选择的边界：

- 适合本地开发、Demo、轻量知识库
- 不适合高并发、大规模语料和复杂过滤检索场景

生产环境替换建议：

- PostgreSQL + PGVector
- Elasticsearch Vector
- Redis Vector
- Milvus
- Weaviate

### 9.6 流式输出设计

`/api/v1/ai/chat/stream` 基于 `SseEmitter` 实现：

- 控制器将模型输出按事件流返回
- 事件负载仍包裹统一响应结构
- 保留 `traceId` 便于链路关联

适用场景：

- 聊天式前端
- 长文本生成
- 运维 Copilot 页面

### 9.7 可用性与降级策略

当前设计允许应用在没有真实 `OPENAI_API_KEY` 的情况下正常启动，原因如下：

- AI Bean 使用 `ObjectProvider` 延迟获取模型
- 非 AI 接口不依赖模型能力即可启动
- 只有真正调用具体 AI 能力时，才会校验模型是否已配置

这样可以实现：

- 非 AI 模块本地开发不被 AI 配置阻断
- 测试环境可先验证安全、路由、基础治理能力
- 后续可进一步细化为按能力自动装配与按 profile 启停

## 10. 配置设计

### 10.1 基础配置

当前使用 `application.yml` 管理默认配置，后续建议按环境拆分：

- `application-dev.yml`
- `application-test.yml`
- `application-prod.yml`

配置治理建议：

- 敏感配置不写死在仓库
- 优先通过环境变量、配置中心、密钥服务注入
- 明确应用端口、日志级别、超时配置、线程池参数

### 10.2 AI 配置项

`spring.ai.openai`：

- `api-key`：模型调用凭证
- `chat.options.model`：聊天模型
- `chat.options.temperature`：对话随机性
- `embedding.options.model`：向量模型
- `moderation.options.model`：审核模型

`platform.ai`：

- `default-system-prompt`：平台级默认提示词
- `rag-top-k`：默认检索片段数量
- `rag-store-file`：本地向量库存储路径
- `image-model`：图像模型
- `transcription-model`：转写模型
- `speech-model`：语音合成模型
- `speech-voice`：默认音色
- `governance.audit-enabled`：是否启用 AI 审计日志
- `governance.rate-limit-enabled`：是否启用 AI 接口限流
- `governance.requests-per-minute`：AI 接口每分钟请求阈值

### 10.3 配置治理建议

- 生产环境必须使用真实密钥中心，不允许提交真实 `api-key`
- 按环境区分模型选型，开发环境用轻量模型，生产环境按场景分配
- 对语音、图像等高成本能力增加额度配置
- 对知识库存储路径和数据目录做好备份与权限隔离

### 10.4 环境拆分策略

当前已提供以下配置文件：

- `application.yml`：公共默认配置
- `application-dev.yml`：开发环境配置
- `application-prod.yml`：生产环境配置

策略说明：

- 开发环境允许较宽松的限流阈值，便于联调
- 生产环境通过环境变量注入 `OPENAI_API_KEY` 和 Basic Auth 凭据
- 生产环境默认收敛健康检查暴露细节，并保留 AI 审计日志

## 11. API 设计规范

建议统一遵循以下约定：

- 路径前缀使用 `/api/v1`
- 对外接口统一返回 `ApiResponse`
- 错误码稳定，不随文案变化
- 控制器只做协议转换，不承载复杂业务
- AI 接口统一收口到 `/api/v1/ai`

### 11.1 系统接口

- `GET /api/v1/system/ping`：匿名探活
- `GET /api/v1/system/status`：鉴权后查看系统状态

### 11.2 AI 接口

- `GET /api/v1/ai/capabilities`：AI 能力探测
- `POST /api/v1/ai/chat`：对话
- `POST /api/v1/ai/chat/stream`：流式对话
- `POST /api/v1/ai/extract`：结构化抽取
- `POST /api/v1/ai/embedding`：文本向量化
- `POST /api/v1/ai/rag/ingest`：知识库入库
- `POST /api/v1/ai/rag/ask`：检索增强问答
- `POST /api/v1/ai/image`：图像生成
- `POST /api/v1/ai/moderation`：内容审核
- `POST /api/v1/ai/speech`：文本转语音
- `POST /api/v1/ai/transcription`：音频转写

## 12. 知识库与 RAG 设计

当前内置样例知识文件：

- `src/main/resources/ai/knowledge/platform-overview.md`

它的作用：

- 作为平台 AI 能力说明的种子语料
- 演示知识库文件的组织方式
- 为后续自动入库或启动时预热提供样板

当前版本的知识库策略：

- 文档入库通过 API 显式触发
- 文本块和向量结果保存在本地文件
- 片段元数据中保存标题、文档 ID、入库时间等信息

后续建议增强：

- 启动时自动扫描并导入指定知识目录
- 支持租户隔离、标签过滤和来源追踪
- 支持异步重建索引
- 将向量库切换到企业级外部服务

## 13. MCP 设计说明

当前版本的 MCP 能力定位为“就绪而非完整交付”：

- 已引入 `spring-ai-starter-mcp-client`
- 已为后续接入外部 MCP Server 预留依赖基础
- 尚未强绑定具体 MCP Server 地址、工具集与权限模型

这样设计的原因：

- 保持模板工程中立
- 避免样板项目耦合特定外部系统
- 让接入方根据企业实际生态选择 MCP Server

后续接入建议：

- 对 MCP Server 做白名单控制
- 限制可调用工具域
- 引入操作审计与超时控制
- 对高风险工具加入审批和人工确认

## 14. 开发规范

### 14.1 包结构建议

- `config`：配置类
- `web`：控制器
- `service`：应用服务实现
- `advice`：全局增强
- `filter`：过滤器
- `tool`：AI 工具定义

### 14.2 编码约束

- 控制器只做参数接收与结果返回
- 业务异常统一抛 `BusinessException`
- 新增业务码必须登记到 `ErrorCode`
- 日志中尽量打印 `traceId`
- 避免在 `common` 中加入业务逻辑
- AI 提示词与工具定义要尽量显式、可审查、可版本化

### 14.3 测试策略

- 单元测试验证核心业务规则
- Web 测试验证接口契约和安全策略
- 集成测试验证配置装配和 AI 模块不影响基础启动
- 后续补充 AI 能力 Mock 测试，避免单测直接依赖外部模型

## 15. 运维与治理建议

- 对 AI 接口设置超时、重试和熔断策略
- 对高成本能力记录调用审计和额度消耗
- 对用户输入和模型输出增加脱敏与合规检查
- 对知识库内容建立版本管理和回滚机制
- 对工具调用结果做可观测性埋点
- 对 AI 接口启用基于主体或来源地址的限流策略
- 将 `AI_AUDIT` 日志接入集中日志平台进行审计检索和告警

## 16. 扩展路线

建议按阶段演进：

### 第一阶段

- 接入数据库访问层
- 引入 Flyway 或 Liquibase 管理表结构
- 接入 Redis 缓存
- 将知识库元数据从文件扩展到数据库

### 第二阶段

- 接入 OpenAPI 文档
- 接入统一日志规范
- 接入审计与操作日志
- 建立统一线程池和异步任务模型
- 引入外部向量数据库

### 第三阶段

- 接入消息队列
- 接入分布式锁
- 接入灰度发布和动态配置
- 支持多租户与数据权限
- 接入企业 MCP Server、Agent Workflow 与多工具编排

## 17. 风险与注意事项

- 默认 Basic Auth 仅适合开发和演示，不适合直接用于生产
- 当前本地 JSON 向量库存储不适合大规模生产知识库
- `MCP Ready` 不等于默认启用了完整 MCP 外部集成
- 未配置真实模型密钥时，AI 接口调用会失败，但应用仍可启动
- 图像、语音和审核能力可能带来额外成本与合规要求

## 18. 结论

本框架不仅提供了 `Spring Boot 4.x` 企业项目常见的基础治理能力，也将 `Spring AI` 以企业级平台能力的方式整合进来。它适合作为中后台系统、平台型服务、智能运营后台和 AI 增强业务系统的初始化模板，既可直接运行，也为后续接入数据库、缓存、消息队列、配置中心、向量数据库、MCP 工具生态等能力保留了清晰边界和扩展点。
