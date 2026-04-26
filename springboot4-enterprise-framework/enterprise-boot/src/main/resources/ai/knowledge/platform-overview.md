# Enterprise Platform Knowledge Base

该知识文件用于演示 `Spring AI + RAG` 在企业框架中的接入方式。

## 平台能力

- 应用基于 `Spring Boot 4.x` 构建
- 默认包含 `Web`、`Security`、`Validation`、`Actuator`、`TraceId`
- AI 能力包含 `Chat`、`Structured Output`、`Tool Calling`、`RAG`、`Embedding`
- 可扩展到 `Image`、`Transcription`、`Text-to-Speech`、`Moderation`、`MCP`

## 安全约束

- 匿名接口仅开放系统探活和 AI 能力探测
- 其余 AI 接口默认要求身份认证
- AI 回答应优先基于知识库和工具返回结果，不得伪造系统状态

## 运行建议

- 本地开发通过 `OPENAI_API_KEY` 提供真实密钥
- 生产环境通过密钥管理系统注入
- 向量数据默认落盘到 `data/ai/vector-store.json`
