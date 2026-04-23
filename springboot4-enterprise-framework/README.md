# Spring Boot 4.x Enterprise Framework

一个面向企业项目落地的 `Spring Boot 4.x` 参考框架，默认采用多模块 Maven 组织方式，兼顾以下目标：

- 快速启动：保留最小可运行骨架，避免一开始就引入过重基础设施
- 企业治理：统一响应体、异常处理、链路追踪、安全基线、Actuator 可观测性
- 分层解耦：通过 `common`、`core`、`boot` 分离公共能力、业务契约和启动装配
- 便于扩展：后续可平滑接入数据库、缓存、消息队列、分布式配置和多租户能力

## 模块说明

- `enterprise-common`：公共响应模型、错误码、业务异常等基础组件
- `enterprise-core`：领域服务契约与核心业务模型，不依赖 Web 层
- `enterprise-boot`：Spring Boot 启动模块，承载配置、安全、接口、异常处理、过滤器
- `docs`：完整设计文档

## 环境要求

- JDK 21+
- Maven 3.9+

## 快速启动

```bash
cd springboot4-enterprise-framework
mvn clean test
mvn -pl enterprise-boot spring-boot:run
```

## 默认访问

- 健康检查：`GET /actuator/health`
- 应用信息：`GET /actuator/info`
- 匿名探活：`GET /api/v1/system/ping`
- 鉴权状态：`GET /api/v1/system/status`

`/api/v1/system/status` 默认需要 Basic Auth：

- 用户名：`platform-admin`
- 密码：`changeit`

建议上线前通过配置中心、环境变量或密钥管理系统覆盖默认口令。

## 设计文档

详见 `docs/design.md`。
