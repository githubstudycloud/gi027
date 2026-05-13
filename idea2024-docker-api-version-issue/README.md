# IDEA 2024 Docker 插件报错分析

## 一、问题现象

在 IntelliJ IDEA 2024 中使用 Docker 插件（或依赖 docker-java 客户端的插件，如 Spring Boot Docker 集成、JIB、TestContainers 等）连接 Docker 守护进程时，抛出如下异常：

```
com.github.dockerjava.api.exception.DockerException:
  Status 400: client version 1.24 is too old.
  Minimum supported API version is 1.44,
  please upgrade your client to a newer version.
```

> 注：原文中的 `com.github.docker.java.api.exception.DockerException` 实际包名为
> `com.github.dockerjava.api.exception.DockerException`（docker-java 库）。

---

## 二、根因分析

### 2.1 Docker Engine API 版本协商机制

Docker 客户端与服务端之间通过 HTTP 协商 API 版本：

| 角色 | 行为 |
|------|------|
| Server (dockerd) | 声明自己支持的最低/最高 API 版本，例如 `MinAPIVersion=1.44` |
| Client (docker-java) | 在 URL 中携带版本号，如 `/v1.24/containers/json` |
| 协商 | 若 client 版本 < server 最低支持版本 ⇒ 返回 HTTP 400 |

### 2.2 各版本对照

| Docker Engine 版本 | API 版本 | 最低支持客户端 API |
|--------------------|----------|---------------------|
| 20.10.x            | 1.41     | 1.24                |
| 23.0.x             | 1.42     | 1.24                |
| 24.0.x             | 1.43     | 1.24                |
| **25.0.x**         | **1.44** | **1.44** ✅ 重大变更 |
| 26.x / 27.x        | 1.45+    | 1.44                |

**Docker Engine 25.0（2024-01 发布）首次将最低客户端版本提升到 1.44**，导致旧版客户端报错。

### 2.3 为什么 IDEA 2024 仍在用 1.24

- IDEA 内置或插件依赖的 `docker-java` 版本较旧（≤ 3.2.x），默认 `RemoteApiVersion.VERSION_1_24`。
- 在 `DefaultDockerClientConfig` 中若未显式 `withApiVersion(...)`，且未启用版本协商，就会回落到硬编码的 1.24。
- Docker Desktop / Engine 自动升级到 25.x 后，客户端未跟进 ⇒ 报错。

---

## 三、定位步骤

### 3.1 确认 Docker Engine 版本

```powershell
docker version
docker version --format '{{.Server.APIVersion}} / min={{.Server.MinAPIVersion}}'
```

若 `MinAPIVersion >= 1.44`，即命中本问题。

### 3.2 确认 IDEA 插件使用的 docker-java 版本

在 IDEA 中：

1. `Help → Show Log in Explorer` 打开 `idea.log`
2. 搜索关键字：`docker-java`、`DockerException`、`client version`
3. 或在 `Help → About → Copy` 查看构建号，对照 [JetBrains Release Notes](https://www.jetbrains.com/idea/whatsnew/) 判断捆绑版本

### 3.3 复现最小用例

参考 `samples/MinimalRepro.java`（见同目录）。

---

## 四、解决方案（按推荐优先级）

### ✅ 方案 A：升级 IDEA 到最新版（首选）

- IntelliJ IDEA **2024.1.4 / 2024.2+** 已升级内置 docker-java，支持 API 1.44。
- 操作：`Help → Check for Updates`。

### ✅ 方案 B：升级 Docker 插件

- `Settings → Plugins → Marketplace`，搜索 `Docker`，更新到最新版本。
- 重启 IDEA。

### ✅ 方案 C：降级 Docker Engine（临时绕过）

仅当无法升级 IDEA 时使用：

- Docker Desktop：在设置中安装 24.0.x 版本。
- Linux：`apt install docker-ce=5:24.0.9-1~*`

> ⚠️ 不推荐长期降级，存在安全补丁缺失风险。

### ✅ 方案 D：自定义代码中升级 docker-java（针对自研插件 / Java 程序）

在 `pom.xml` / `build.gradle` 中：

```xml
<dependency>
    <groupId>com.github.docker-java</groupId>
    <artifactId>docker-java-core</artifactId>
    <version>3.4.0</version>
</dependency>
<dependency>
    <groupId>com.github.docker-java</groupId>
    <artifactId>docker-java-transport-httpclient5</artifactId>
    <version>3.4.0</version>
</dependency>
```

并显式声明 API 版本：

```java
DefaultDockerClientConfig config = DefaultDockerClientConfig.createDefaultConfigBuilder()
    .withDockerHost("npipe:////./pipe/docker_engine")  // Windows
    .withApiVersion(RemoteApiVersion.VERSION_1_44)
    .build();
```

### ✅ 方案 E：设置环境变量强制版本

```powershell
# Windows PowerShell（用户级）
[Environment]::SetEnvironmentVariable("DOCKER_API_VERSION", "1.44", "User")
```

重启 IDEA 后生效。docker-java 会读取该变量覆盖默认 1.24。

---

## 五、验证

升级后再次运行：

```powershell
docker version
# 在 IDEA 中：Services → Docker → Connect
```

确认 IDEA 状态栏显示 `Connected`，且 `idea.log` 中无 `DockerException`。

---

## 六、参考资料

- Docker Engine 25.0 Release Notes: <https://docs.docker.com/engine/release-notes/25.0/>
- docker-java Releases: <https://github.com/docker-java/docker-java/releases>
- JetBrains YouTrack 相关 issue: 搜索 `IDEA-348xxx docker api 1.44`

---

## 七、目录结构

```
idea2024-docker-api-version-issue/
├── README.md                    # 本文件
├── analysis.md                  # 详细根因与堆栈分析
├── checklist.md                 # 排查清单
└── samples/
    └── MinimalRepro.java        # 最小复现代码
```
