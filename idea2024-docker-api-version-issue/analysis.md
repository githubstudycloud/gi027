# 详细根因与堆栈分析

## 1. 完整异常堆栈（典型）

```
com.github.dockerjava.api.exception.DockerException:
  Status 400: {"message":"client version 1.24 is too old.
  Minimum supported API version is 1.44,
  please upgrade your client to a newer version."}

  at com.github.dockerjava.core.DefaultInvocationBuilder.execute(DefaultInvocationBuilder.java:296)
  at com.github.dockerjava.core.DefaultInvocationBuilder.get(DefaultInvocationBuilder.java:81)
  at com.github.dockerjava.core.exec.VersionCmdExec.execute(VersionCmdExec.java:30)
  at com.github.dockerjava.core.command.AbstrDockerCmd.exec(AbstrDockerCmd.java:35)
  at com.intellij.docker.agent.impl.DockerAgentImpl.connect(DockerAgentImpl.kt:...)
```

## 2. 协议层抓包示例

请求行（旧客户端发起）：

```
GET /v1.24/version HTTP/1.1
Host: localhost
```

响应（Engine 25+ 返回）：

```
HTTP/1.1 400 Bad Request
Content-Type: application/json
{"message":"client version 1.24 is too old. ..."}
```

## 3. docker-java 默认版本来源

`com.github.dockerjava.core.RemoteApiVersion`：

```java
public static final RemoteApiVersion VERSION_1_24 = RemoteApiVersion.create(1, 24);
public static final RemoteApiVersion UNKNOWN_VERSION = VERSION_1_24;  // 默认回落
```

在 `DefaultDockerClientConfig`：

```java
public RemoteApiVersion getApiVersion() {
    return apiVersion == null ? RemoteApiVersion.unknown() : RemoteApiVersion.parseConfig(apiVersion);
}
```

⇒ 未配置 `DOCKER_API_VERSION` 时使用 1.24。

## 4. IDEA 内部链路

```
Services Tool Window
   └─> com.intellij.docker.DockerConnection
         └─> com.intellij.docker.agent.DockerAgent (远程进程)
               └─> docker-java 客户端
                     └─> HTTP/npipe → Docker Engine
```

IDEA 在远程 agent 进程中加载 docker-java；该 jar 随 Docker 插件 / IDEA 主程序发布，需通过升级才能更换。

## 5. 影响范围

| 工具 / 框架 | 是否受影响 | 说明 |
|------------|----------|------|
| IDEA Docker 插件（< 2024.1.4 内置） | ✅ | 需升级 |
| TestContainers 1.19.x | ⚠️ 部分 | 1.19.7+ 已修复 |
| Spring Boot Docker Compose 支持 | ✅ | 取决于 docker-java 传递依赖 |
| JIB / Fabric8 docker-maven-plugin | ❌ | 使用各自客户端实现 |
| `docker` CLI | ❌ | CLI 自身会协商版本 |

## 6. 与 Docker Desktop 4.27 行为变化的关联

Docker Desktop 4.27（2024-01）随 Engine 25.0 发布，部分用户升级后立即遭遇。
回滚 Desktop 到 4.26 可临时绕过，但同样不推荐。
