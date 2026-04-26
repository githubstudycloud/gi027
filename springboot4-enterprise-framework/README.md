# Spring Boot 4.x Enterprise Framework

一个面向企业项目落地的 `Spring Boot 4.x` 参考框架，默认采用多模块 Maven 组织方式，并内置 `Spring AI` 企业集成能力，兼顾以下目标：

- 快速启动：保留最小可运行骨架，避免一开始就引入过重基础设施
- 企业治理：统一响应体、异常处理、链路追踪、安全基线、Actuator 可观测性
- 分层解耦：通过 `common`、`core`、`ai`、`boot` 分离公共能力、业务契约、AI 契约和启动装配
- AI 原生：内置 Chat、Structured Output、Tool Calling、RAG、Embedding、Image、Moderation、TTS、Transcription、MCP Ready
- 便于扩展：后续可平滑接入数据库、缓存、消息队列、分布式配置、多租户和外部向量数据库能力

## 模块说明

- `enterprise-common`：公共响应模型、错误码、业务异常等基础组件
- `enterprise-core`：领域服务契约与核心业务模型，不依赖 Web 层
- `enterprise-ai`：AI 请求/响应模型与统一 AI 门面接口
- `enterprise-boot`：Spring Boot 启动模块，承载配置、安全、接口、异常处理、过滤器和 AI 运行时实现
- `docs`：完整设计文档

## 环境要求

- JDK 21+
- Maven 3.9+
- OpenAI 兼容模型访问凭证

## 快速启动

```bash
cd springboot4-enterprise-framework
./mvnw clean test
./mvnw -pl enterprise-boot spring-boot:run
```

PowerShell：

```powershell
$env:OPENAI_API_KEY="your-api-key"
./mvnw -pl enterprise-boot spring-boot:run
```

## 默认访问

- 健康检查：`GET /actuator/health`
- 应用信息：`GET /actuator/info`
- 匿名探活：`GET /api/v1/system/ping`
- 鉴权状态：`GET /api/v1/system/status`
- AI 能力探测：`GET /api/v1/ai/capabilities`

`/api/v1/system/status` 默认需要 Basic Auth：

- 用户名：`platform-admin`
- 密码：`changeit`

建议上线前通过配置中心、环境变量或密钥管理系统覆盖默认口令。

除 `GET /api/v1/ai/capabilities` 外，其余 AI 接口默认也要求 Basic Auth。

## Spring AI 能力清单

当前框架已集成以下企业级 AI 能力：

- `Chat`：基于 `ChatClient` 的标准对话
- `Structured Output`：基于 `BeanOutputConverter` 的结构化抽取
- `Tool Calling`：通过 `@Tool` 暴露平台工具函数
- `RAG`：文档切分、Embedding、本地向量落盘、相似度检索增强问答
- `Embedding`：文本向量化
- `Image`：图像生成
- `Moderation`：内容审核
- `Text-to-Speech`：文本转语音
- `Transcription`：音频转写
- `MCP Ready`：已引入 MCP Client Starter，便于后续接入外部 MCP Server

## AI 配置说明

`application.yml` 提供了默认 AI 配置入口：

```yaml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY:demo-key}
      chat:
        options:
          model: gpt-4o-mini
      embedding:
        options:
          model: text-embedding-3-small
      moderation:
        options:
          model: text-moderation-latest

platform:
  ai:
    default-system-prompt: |
      你是企业级 Spring Boot 4.x 平台内置 AI 助手。
    rag-top-k: 4
    rag-store-file: data/ai/vector-store.json
    image-model: gpt-image-1
    transcription-model: gpt-4o-mini-transcribe
    speech-model: gpt-4o-mini-tts
    speech-voice: alloy
```

说明：

- `OPENAI_API_KEY` 未设置时，应用仍可启动，但真正调用模型能力会失败
- `platform.ai.rag-store-file` 为本地向量库存储路径
- `platform.ai.default-system-prompt` 控制平台级统一系统提示词

## AI 接口清单

- `GET /api/v1/ai/capabilities`：返回当前 AI 能力开关与可用性
- `POST /api/v1/ai/chat`：标准问答
- `POST /api/v1/ai/chat/stream`：SSE 流式输出
- `POST /api/v1/ai/extract`：结构化信息抽取
- `POST /api/v1/ai/embedding`：文本向量化
- `POST /api/v1/ai/rag/ingest`：知识库文档入库
- `POST /api/v1/ai/rag/ask`：检索增强问答
- `POST /api/v1/ai/image`：图像生成
- `POST /api/v1/ai/moderation`：审核文本内容
- `POST /api/v1/ai/speech`：文本转语音
- `POST /api/v1/ai/transcription`：音频转写

## AI 调用示例

能力探测：

```bash
curl http://localhost:8080/api/v1/ai/capabilities
```

标准对话：

```bash
curl -u platform-admin:changeit \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"总结这个平台的核心能力\",\"useTools\":true,\"useKnowledgeBase\":false,\"topK\":4}" \
  http://localhost:8080/api/v1/ai/chat
```

结构化抽取：

```bash
curl -u platform-admin:changeit \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"项目风险：接口文档缺失，联调延期 3 天，建议补齐测试用例和发布检查单。\"}" \
  http://localhost:8080/api/v1/ai/extract
```

知识库入库：

```bash
curl -u platform-admin:changeit \
  -H "Content-Type: application/json" \
  -d "{\"documentId\":\"kb-001\",\"title\":\"平台简介\",\"content\":\"该平台默认包含 Web、Security、Validation、Actuator、TraceId 与 AI 能力。\"}" \
  http://localhost:8080/api/v1/ai/rag/ingest
```

RAG 问答：

```bash
curl -u platform-admin:changeit \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"平台默认内置了哪些能力？\",\"topK\":4}" \
  http://localhost:8080/api/v1/ai/rag/ask
```

## RAG 实现说明

当前版本采用“`Spring AI Embedding + 框架本地向量存储`”方案：

- 入库时使用 `TokenTextSplitter` 分块
- 使用 `EmbeddingModel` 生成向量
- 将向量及元数据持久化到 `data/ai/vector-store.json`
- 查询时执行余弦相似度检索
- 命中片段会拼接到提示词中，供模型增强回答

该方案适合单体工程、演示环境和中小规模知识库。生产环境建议平滑替换为 PGVector、Milvus、Elasticsearch、Redis Vector 或其他企业级向量库。

## 设计与治理建议

- 将真实模型密钥放入环境变量、密钥中心或 KMS，不要提交到仓库
- 对 AI 接口增加限流、审计、超时和幂等保护
- 将提示词模板、知识库、工具定义与业务能力做版本化管理
- 对高风险输出场景叠加 `Moderation`、人工审核或规则兜底
- 将 MCP 能力接入限制在白名单服务器与受控工具域内

## 设计文档

详见 `docs/design.md`，其中补充了完整的 AI 架构、接口、配置、治理和演进设计。
