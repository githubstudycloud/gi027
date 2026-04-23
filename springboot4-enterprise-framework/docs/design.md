# Spring Boot 4.x 企业级框架设计文档

## 1. 文档目标

本文档用于描述 `springboot4-enterprise-framework` 的设计原则、模块边界、技术选型、运行方式与后续扩展策略，作为项目初始化、团队协作和架构演进的统一基线。

## 2. 建设目标

- 建立符合企业应用规范的 `Spring Boot 4.x` 基线工程
- 提供可直接运行、可直接二次开发的多模块骨架
- 统一接口响应、异常治理、安全策略与链路追踪机制
- 为未来接入数据库、缓存、消息队列、任务调度、分布式治理预留清晰扩展点
- 降低新人上手成本，缩短项目从 0 到 1 的初始化周期

## 3. 设计原则

- 分层清晰：按公共层、核心层、启动层拆分职责
- 低耦合：`core` 不依赖 Web 实现，便于单测与后续服务化拆分
- 高内聚：通用响应、异常和错误码统一收敛到公共模块
- 约定优先：减少重复决策，统一工程目录、编码规范和配置模型
- 先可用再增强：先提供稳定骨架，再按业务接入数据与中间件
- 安全默认：默认关闭高风险暴露，保留最小公开接口

## 4. 技术基线

- JDK：21 作为推荐 LTS 基线
- 构建工具：Maven 3.9+
- 核心框架：Spring Boot 4.0.4
- 兼容体系：Spring Framework 7.x、Jakarta EE 11
- Web：Spring MVC
- 安全：Spring Security
- 校验：Bean Validation
- 可观测性：Spring Boot Actuator
- 测试：Spring Boot Test、MockMvc、Spring Security Test

## 5. 工程结构

```text
springboot4-enterprise-framework/
├─ docs/
│  └─ design.md
├─ enterprise-common/
├─ enterprise-core/
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

#### enterprise-boot

定位：承载启动装配与交付入口。

职责：

- 应用启动
- Web API 暴露
- Spring Security 安全配置
- 全局异常处理
- TraceId 过滤器
- 配置文件与 Actuator 暴露

约束：

- 允许依赖 `common` 和 `core`
- 作为最终可运行模块

## 6. 分层设计

推荐按下列逻辑组织代码：

- `common`：通用模型、工具、错误码、上下文对象
- `core`：领域模型、领域服务接口、应用服务接口、仓储接口
- `boot`：配置类、控制器、过滤器、事件监听、适配器实现

当前框架是最小企业级落地版本，后续可进一步细分为：

- `application`：应用服务编排
- `domain`：领域模型和领域规则
- `infrastructure`：数据库、缓存、MQ、第三方接口适配
- `interfaces`：HTTP、RPC、事件订阅等对外入口

## 7. 核心设计点

### 7.1 统一响应模型

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

### 7.2 异常治理

通过全局异常处理器统一捕获：

- 业务异常
- 参数校验异常
- 未预期系统异常

处理原则：

- 不向外暴露敏感堆栈
- 保留明确业务码和可追踪 `traceId`
- 错误日志面向运维，错误响应面向调用方

### 7.3 安全基线

当前版本采用 Basic Auth 作为最小安全样板，原因如下：

- 零额外基础设施即可运行
- 便于开发期联调
- 可以平滑迁移到 JWT、OAuth2 或企业 SSO

安全策略：

- `GET /actuator/health` 开放
- `GET /actuator/info` 开放
- `GET /api/v1/system/ping` 开放
- 其余接口默认鉴权
- 会话策略设为无状态
- 默认口令仅用于开发环境

后续建议增强：

- 接入 OAuth2 Resource Server
- 接入 API 网关统一鉴权
- 接入 RBAC / ABAC 权限模型
- 接入审计日志和操作留痕

### 7.4 TraceId 传播

在 `TraceIdFilter` 中完成：

- 优先复用请求头中的 `X-Trace-Id`
- 若不存在则自动生成
- 回写到响应头
- 注入日志上下文 `MDC`

设计价值：

- 提升跨服务链路排障效率
- 为日志聚合平台、APM 和监控告警提供关联键

### 7.5 可观测性

基于 Actuator 提供：

- 健康检查
- 应用基础信息

后续建议：

- 接入 Prometheus 指标
- 接入 Micrometer Tracing
- 接入 OpenTelemetry
- 建立 SLI/SLO 监控体系

## 8. 配置设计

当前使用 `application.yml` 管理默认配置，后续建议按环境拆分：

- `application-dev.yml`
- `application-test.yml`
- `application-prod.yml`

配置治理建议：

- 敏感配置不写死在仓库
- 优先通过环境变量、配置中心、密钥服务注入
- 明确应用端口、日志级别、超时配置、线程池参数

## 9. API 设计规范

建议统一遵循以下约定：

- 路径前缀使用 `/api/v1`
- 资源命名使用名词，不使用动词
- 对外接口必须返回统一响应结构
- 错误码稳定，不随文案变化
- 控制器只做协议转换，不承载复杂业务

示例接口：

- `GET /api/v1/system/ping`：匿名探活
- `GET /api/v1/system/status`：鉴权后查看系统状态

## 10. 开发规范

### 10.1 包结构建议

- `config`：配置类
- `web`：控制器
- `service`：应用服务实现
- `advice`：全局增强
- `filter`：过滤器

### 10.2 编码约束

- 控制器只做参数接收与结果返回
- 业务异常统一抛 `BusinessException`
- 新增业务码必须登记到 `ErrorCode`
- 日志中尽量打印 `traceId`
- 避免在 `common` 中加入业务逻辑

### 10.3 测试策略

- 单元测试验证核心业务规则
- Web 测试验证接口契约和安全策略
- 集成测试验证配置装配和基础设施适配

## 11. 扩展路线

建议按阶段演进：

### 第一阶段

- 接入数据库访问层
- 引入 Flyway 或 Liquibase 管理表结构
- 接入 Redis 缓存

### 第二阶段

- 接入 OpenAPI 文档
- 接入统一日志规范
- 接入审计与操作日志
- 建立统一线程池和异步任务模型

### 第三阶段

- 接入消息队列
- 接入分布式锁
- 接入灰度发布和动态配置
- 支持多租户与数据权限

## 12. 部署建议

- 容器化部署，镜像中只保留运行时依赖
- 通过环境变量注入安全配置
- 使用独立配置中心管理各环境参数
- 通过健康检查与滚动发布保障可用性

## 13. 风险与注意事项

- 默认 Basic Auth 仅适合开发和演示，不适合直接用于生产
- 当前未接入数据库与缓存，实现的是企业级骨架而非完整业务平台
- 若未来采用微服务拆分，应尽早规范 DTO、错误码和链路治理标准

## 14. 结论

本框架提供了 `Spring Boot 4.x` 企业项目常见的基础治理能力，适合作为中后台系统、平台型服务和新业务项目的初始化模板。它既能直接运行，也为后续接入数据库、缓存、消息队列、配置中心、鉴权中心等企业能力保留了清晰边界和扩展点。
