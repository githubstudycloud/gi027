# Cherry Studio 内嵌「公司内部鉴权 + 问题提交」页面方案

## 一、原始提问

> 当我通过 Cherry Studio 源码修改一个公司内部用的服务时，我需要嵌套一个问题提交页面，但这个页面还要先打开一个公司内部鉴权网页登录，不然直接打开问题提交页面会报错。在 Cherry Studio 这个框架上我要怎么写这个呢？两个页面间怎么继承第一个页面的登录信息呢？

---

## 二、背景与关键点

Cherry Studio 是基于 **Electron + React (Vite) + TypeScript** 的桌面应用，主进程使用 Electron 的 `BrowserWindow` / `session` / `WebContentsView` 管理窗口，渲染进程用 React 渲染 UI；嵌入第三方 Web 页面通常使用 `<webview>` 标签或 `BrowserView` / `WebContentsView`。

要在两个嵌入页面之间「继承登录信息」，本质就是 **共享同一个 Electron `session`（即同一个 cookie / localStorage / 存储分区）**。这样：

1. 用户在「鉴权登录页」完成登录后，公司 SSO 写入的 Cookie（通常是 `JSESSIONID` / `SSO_TOKEN` / `Authorization` 等）会落到这个 session 的 cookie jar。
2. 后续打开「问题提交页」时，只要使用 **同一个 partition**，Electron 会自动带上这些 Cookie，业务后端就认为已登录。

> ❗ 常见错误：第一个页面用 `partition="persist:auth"`，第二个页面没写 partition 或写成 `persist:other` —— 两者 cookie 隔离，必然 401/302。

---

## 三、整体方案

```
┌─────────────────────────────────────────────────────────┐
│ Cherry Studio 主窗口 (React)                            │
│                                                         │
│  ┌──────────────┐   登录成功(检测到目标Cookie)         │
│  │ Step 1       │ ───────────────┐                      │
│  │ 鉴权登录页   │                │                      │
│  │ <webview>    │                ▼                      │
│  │ partition=   │   ┌──────────────────────────┐       │
│  │ persist:corp │   │ Step 2                    │      │
│  └──────────────┘   │ 问题提交页                │      │
│         共享        │ <webview>                 │      │
│         同一 ───────┤ partition=persist:corp    │      │
│         session     │ (自动带上 SSO Cookie)     │      │
│                     └──────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

### 选择一：渲染层 `<webview>`（推荐，改动最小）

- 在 React 组件里放两个 `<webview>`，**partition 必须一致**（如 `persist:corp-sso`）。
- 用 `did-navigate` / `dom-ready` / `did-finish-load` 事件监听跳转，判断是否已登录。
- 也可以监听 cookie：在主进程通过 `session.fromPartition('persist:corp-sso').cookies.on('changed', ...)` 通知渲染进程切换。

### 选择二：主进程 `WebContentsView` + IPC（更可控）

- 在主进程为同一个 `BrowserWindow` 添加两个 `WebContentsView`，都用 `session.fromPartition('persist:corp-sso')`。
- 通过 IPC 控制显示/隐藏哪个 view。
- 适合需要拦截请求、注入 header、做单点登录代理的场景。

---

## 四、示例代码

> 见同目录下：
> - [examples/renderer-webview/AuthEmbed.tsx](examples/renderer-webview/AuthEmbed.tsx) — 渲染层 webview 方案
> - [examples/main-process/authWindow.ts](examples/main-process/authWindow.ts) — 主进程 WebContentsView 方案
> - [examples/main-process/preload.ts](examples/main-process/preload.ts) — preload 桥接
> - [examples/main-process/ipc-handlers.ts](examples/main-process/ipc-handlers.ts) — IPC 注册

### 4.1 关键点速查

| 关键点 | 写法 |
|---|---|
| 共享登录态 | 两个页面使用同一个 `partition`（如 `persist:corp-sso`） |
| 持久化 | partition 必须以 `persist:` 开头，否则关闭即失效 |
| 判断登录成功 | 监听目标 Cookie（推荐）或 URL 跳转或 DOM 元素出现 |
| 注入公共 header | `session.webRequest.onBeforeSendHeaders` |
| 跨域问题 | Electron 内嵌页本身不受浏览器同源限制，但业务接口的 CORS 仍需后端配合 |
| 证书问题（公司内网自签） | `app.on('certificate-error', ...)` 白名单放行，或导入 CA |

---

## 五、常见坑

1. **`<webview>` 标签不生效**：需要在创建 `BrowserWindow` 时设 `webPreferences.webviewTag: true`。
2. **partition 不持久**：忘记加 `persist:` 前缀，每次重启都要重新登录。
3. **Cookie 是 HttpOnly + SameSite=Lax**：在 Electron 嵌入场景下也能正常带上，无需特殊处理；但若公司 SSO 设置了 `SameSite=Strict` 且跨域跳转，可能需要在主进程用 `cookies.set` 复制一份。
4. **公司 SSO 检测 UA**：可在 `webview` 上设 `useragent` 属性，或在主进程 `session.setUserAgent`。
5. **重复登录**：检查是否多个 `BrowserWindow` 用了不同 partition；统一管理。
6. **关闭后下次启动还要登录**：通常是 SSO 的 token 过期，不是 Electron 问题；可在 `did-fail-load` 时把 webview 切回登录页。

---

## 六、在 Cherry Studio 源码中的落点

Cherry Studio 仓库的典型结构（以官方 `CherryHQ/cherry-studio` 为例）：

- `src/main/`：Electron 主进程
- `src/renderer/src/`：React 渲染进程
- `src/preload/`：preload 脚本

**建议落点**：

1. 在 `src/renderer/src/pages/` 下新增 `CorpServicePage.tsx`，使用方案一的 `AuthEmbed` 组件。
2. 在路由（一般在 `src/renderer/src/App.tsx` 或 `routes.tsx`）中注册一个新路由，例如 `/corp/issue`。
3. 在侧边栏或菜单（`src/renderer/src/components/app/Sidebar.tsx` 之类）加入入口。
4. 如果需要主进程能力（注入 header、放行证书），在 `src/main/services/` 下新增 `CorpSsoService.ts` 注册到现有的 service 启动流程，并在 `src/main/ipc.ts` 注册 IPC handler。

> 由于 Cherry Studio 版本迭代较快，具体目录以你 fork 的 commit 为准；上面的命名只是示意。
