# 06 - 依赖治理与本地 Lib 封装设计

> 版本：v1.0 | 日期：2026-04-27 | 状态：草稿
> 对应你的关注点：4 年期窗口、超期包缓退、工具类自包装、流水线只校验 Maven 拉取

---

## 1. 依赖治理目标

1. **新鲜度**：默认依赖**首发版本在最近 4 年内**；
2. **单一版本**：任一构件全仓库唯一版本（BOM 强制）；
3. **可替换**：所有第三方库通过封装层暴露，业务不直接依赖；
4. **可缓退**：超期但暂无替代品的库不立刻爆破，进入"缓退区"；
5. **可审计**：依赖变更必须 MR + 流水线校验。

---

## 2. BOM 与版本统一

```
enterprise-bom/pom.xml
  ├─ 引入 spring-boot-dependencies
  ├─ 引入 spring-cloud-dependencies
  ├─ 引入 spring-ai-bom
  └─ 自定义企业版本（覆盖 + 新增）
```

- 所有业务项目 `<parent>` 或 `<dependencyManagement><scope>import</import>` 引入 BOM；
- 业务模块内**禁止写 `<version>`**（Enforcer 插件强制）。

---

## 3. 4 年期窗口策略

### 3.1 校验方式

CI 阶段执行：

```
1. mvn dependency:tree → 抽取所有 GAV
2. 调用 Maven Central / 内网镜像 API 查询每个 artifact 的"首次符合策略版本"发布时间
3. if releaseDate < now - 4y → 失败（除非在白名单 enterprise-legacy-allowlist.yml）
4. 报告：哪些依赖临近 4 年（< 90 天）→ 提早预警
```

- 工具：`versions-maven-plugin` + 自研脚本 + OWASP Dependency-Check（顺带做安全扫描）。

### 3.2 例外白名单

`enterprise-legacy-allowlist.yml`：

```yaml
- gav: org.example:legacy-foo:1.2.3
  releaseDate: 2019-06-01
  reason: "暂无替代，已纳入缓退区"
  ownedBy: team-a
  expireBy: 2026-12-31      # 必须设过期日
  replacementPlan: "切换到 com.example:foo-next，预计 Q4"
```

- 例外必须有：原因、负责人、强制过期日、替代计划；
- CI 接近过期日会持续骚扰提醒。

---

## 4. 超期包"缓退区"——本地 Lib 方案（呼应你的设计）

### 4.1 总体思路

```
[第三方仓库] ──正常 Maven 依赖──► [业务模块]   ← 流水线检查这里
                                       ▲
[已超期但仍需用的 jar]                   │
        │                              │
        ▼                              │
[enterprise-legacy-lib/]  ──system scope──┘   ← 流水线豁免
        │
        └─ 本地 jar 文件 + 元数据文件（来源、原版本、引入时间、负责人）
```

- 本地 lib 以 `system` scope + `<systemPath>` 引入；
- 也可方案 B：发布到**内网私服的 `enterprise-internal-legacy` 仓库**，与公网仓库分离，校验脚本只扫描公共仓库 GAV，对该仓库豁免（**推荐**，比 system scope 更规范）。

### 4.2 推荐落地：私服分仓 + 校验白名单

```
私服 Nexus
├── public-proxy        ← 代理 Maven Central（CI 校验范围）
├── enterprise-release  ← 自研构件
└── enterprise-legacy   ← 缓退区（CI 校验豁免）
```

业务 pom 中显式声明 legacy 依赖时，CI 检查到来源 = `enterprise-legacy` 即跳过 4 年期检查，但必须存在白名单条目。

### 4.3 缓退治理

- 每季度一次"缓退区盘点会"，强制缩减；
- 任何新增缓退依赖必须架构组评审；
- 缓退依赖**不允许在新业务项目**中出现（archetype 默认禁用）。

---

## 5. 工具类自包装（呼应"工具类要包装"）

### 5.1 原则

业务代码**禁止直接 import** 以下任何包：

- `cn.hutool.*`
- `com.google.common.*`
- `org.apache.commons.*`
- `com.fasterxml.jackson.*`
- `org.springframework.util.*`（除明确许可的）
- 任何加解密 / Base64 / 日期 / JSON 库

### 5.2 封装层

```
enterprise-common-utils/
├── Strings        // 字符串
├── Collections    // 集合
├── Json           // JSON 序列化（默认 Jackson，可换 Fastjson2）
├── DateTimes      // 日期
├── Crypto         // 加解密（默认 BC，可换国密）
├── Codecs         // Base64 / Hex
├── Ids            // 雪花 / UUID v7 / NanoId
├── Files          // 文件
├── Http           // HTTP（默认 RestClient）
└── Validates      // 校验
```

- 接口稳定，实现可换；
- 通过 ArchUnit 规则强制：业务模块若 import 黑名单包，编译失败。

### 5.3 升级流程

替换底层实现（例：Hutool → 自研）：
1. 新增实现，灰度切换 `enterprise.utils.impl=hutool|inhouse`；
2. 跑全量回归；
3. 默认值切换；
4. 移除老实现。

---

## 6. CVE 与许可证

- OWASP Dependency-Check：CVE 严重级以上**阻断合并**；
- License Maven Plugin：禁用 GPL / AGPL（除非明确豁免）；
- 每周生成依赖健康报告（CVE / 过期 / 许可证）发送负责人。

---

## 7. 自我修订记录

| 轮次 | 修订点 |
|------|--------|
| R1 | 把 system scope 升级为"私服分仓 + 校验白名单"，比 systemPath 更规范、可审计 |
| R2 | 强制例外白名单必须有过期日，避免缓退变成永久豁免 |
| R3 | 工具类封装加 ArchUnit 规则，从"约定"变成"强制" |

---

## 8. 待确认

1. 是否已有 Nexus / Artifactory 私服？决定 4.2 节方案 |
2. 4 年窗口是否对**所有依赖**一刀切？建议对 `org.springframework.*` 等核心放宽到"GA 生命周期内"；
3. ArchUnit 规则是否一并强制 `samples/` 和已有遗留项目？建议遗留项目分阶段。
