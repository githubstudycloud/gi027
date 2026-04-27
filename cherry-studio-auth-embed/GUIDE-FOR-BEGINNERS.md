# 新手友好版：在 Cherry Studio 里嵌入「先登录，再提交问题」的完整教学

> 这份文档是**写给完全零基础的同学**的。我会把每一个名词、每一行代码都讲清楚。
> 读完你应该能：
> 1. 明白 Cherry Studio 是怎么跑起来的；
> 2. 明白「为什么两个网页能共享登录」；
> 3. 跟着一步步把功能写到自己 fork 的 Cherry Studio 里。

---

## 第 0 章 先建立几个最基本的认知

### 0.1 Cherry Studio 是什么？

Cherry Studio 是一个 **桌面应用**（你双击图标就能打开的那种程序），它用的技术叫 **Electron**。

> Electron = Chrome 浏览器内核 + Node.js
> 简单说：**它就是把一个网页打包成桌面 App**。

所以 Cherry Studio 内部其实有**两个世界**：

| 世界 | 别名 | 它能做什么 | 类比 |
|---|---|---|---|
| 主进程 (main) | "后台" | 开窗口、读文件、访问操作系统、管 Cookie | 一个 Node.js 程序 |
| 渲染进程 (renderer) | "前台" | 显示界面、按钮、表单 | 一个 Chrome 网页 |

它们之间通过 **IPC（进程间通信）** 说话，就像两个房间通过一根电话线对话。

### 0.2 几个核心英文名词翻译

- **BrowserWindow**：一个"窗口"对象。每打开一扇桌面窗口就是 new 一个它。
- **webview**：一个 HTML 标签 `<webview>`，长得像 `<iframe>`，**用来在你的 App 里嵌入第三方网页**。
- **WebContentsView**：跟 webview 类似，但写在主进程里，更可控。
- **session**：浏览器的"会话"。**Cookie、登录态、缓存都存在这里**。⭐ 我们整篇文章的核心。
- **partition**：session 的"分区名字"。同名分区 = 同一个 session = 同一份 Cookie。
- **preload**：在网页加载前先跑的一段脚本，用来给前台开"特权小窗口"调用主进程能力。
- **IPC**：Inter-Process Communication，进程间通信，也就是前台和后台聊天。

### 0.3 你的需求翻译成"人话"

你想做的事：

> 在 Cherry Studio 里开一个标签页，里面先弹出公司 SSO 登录页，登录完成后自动跳到"问题提交"页，且**不要让我重新登录一次**。

技术上的核心难点只有一个：

> ❓ 怎么让"问题提交页"知道我已经在"登录页"登录过了？

**答案：让它们用同一个 Cookie 罐子。**

而 Electron 里的"Cookie 罐子" = `session`，给它起个名字就叫 **partition**。
两个 webview 的 `partition` **写一样的字符串**，它们就共用 Cookie。就这么简单。

---

## 第 1 章 准备工作：把 Cherry Studio 跑起来

> 如果你已经能跑了，跳到第 2 章。

### 1.1 装环境

1. 装 [Node.js](https://nodejs.org/) **20 LTS** 或更新（下载 .msi 一路下一步）。
2. 装 [Git](https://git-scm.com/)。
3. 打开 PowerShell，输入下面命令验证：
   ```powershell
   node -v   # 应该显示 v20.x.x
   npm -v
   git --version
   ```

### 1.2 拿到 Cherry Studio 源码

```powershell
# 找一个你喜欢的目录，比如 D:\code
cd D:\code
git clone https://github.com/CherryHQ/cherry-studio.git
cd cherry-studio
```

### 1.3 装依赖、跑起来

```powershell
# 推荐用 yarn，Cherry Studio 官方用的就是 yarn
npm install -g yarn
yarn install
yarn dev
```

第一次会比较慢（要下载 Electron 二进制，约 200MB）。耐心等。
看到一个 Cherry Studio 窗口弹出来，就成功了。

### 1.4 认一下目录（重点）

打开仓库，你会看到几个文件夹。**只需要记住这三个**：

```
cherry-studio/
├─ src/
│  ├─ main/        ← "后台"代码（Electron 主进程）
│  ├─ preload/     ← "电话线"代码
│  └─ renderer/    ← "前台"代码（你看到的 React 界面）
└─ package.json
```

> 不同版本目录可能略有不同，但 main / preload / renderer 这三层一定有。

---

## 第 2 章 核心原理图（请认真看）

```
       ┌──────────────────────── 你的 Cherry Studio 窗口 ────────────────────────┐
       │                                                                          │
       │   ┌──────── 一个共享的 Cookie 罐子（partition = "persist:corp-sso"）─┐  │
       │   │                                                                  │  │
       │   │   网页A: 公司 SSO 登录页                                          │  │
       │   │   ┌────────────────────────┐                                     │  │
       │   │   │ 用户名: ___________    │   登录成功                          │  │
       │   │   │ 密码:   ***________    │   ↓                                 │  │
       │   │   │ [登录]                 │   写入 Cookie: SSO_TOKEN=abc123      │  │
       │   │   └────────────────────────┘                                     │  │
       │   │                                                                  │  │
       │   │   网页B: 问题提交页                                               │  │
       │   │   ┌────────────────────────┐                                     │  │
       │   │   │ 自动从同一个罐子里拿  │                                     │  │
       │   │   │ Cookie: SSO_TOKEN=abc123                                     │  │
       │   │   │ → 后端识别为已登录✅   │                                     │  │
       │   │   └────────────────────────┘                                     │  │
       │   │                                                                  │  │
       │   └──────────────────────────────────────────────────────────────────┘  │
       └──────────────────────────────────────────────────────────────────────────┘
```

**一句话总结：写一样的 partition，就共享登录态。**

⚠️ 三条铁律：

1. partition 必须以 `persist:` 开头（如 `persist:corp-sso`），不然关掉窗口就忘记登录。
2. 两个 `<webview>` 的 partition 字符串**一个字都不能差**。
3. 主进程的 `session.fromPartition('persist:corp-sso')` 必须和上面一致。

---

## 第 3 章 第一种做法（推荐新手）：只改前台

适合：你只想加个页面，不想动 Electron 主进程的复杂逻辑。

### 3.1 整体步骤

1. 在主进程的窗口配置里，**打开 webview 标签**（一次性，全局只改一处）。
2. 写一个 React 组件 `AuthEmbed.tsx`，里面放两个 `<webview>`。
3. 在 Cherry Studio 的路由/侧边栏里加个入口，指向这个组件。
4. （可选）让前台能问主进程"Cookie 在不在？"。

### 3.2 第 1 步：开 webview 标签

打开 `src/main/` 下创建窗口的文件（一般叫 `index.ts` 或 `window.ts`，搜 `new BrowserWindow` 就能找到）：

```ts
const mainWindow = new BrowserWindow({
  // ...其他原有配置...
  webPreferences: {
    // 👇 加这一行（如果已经有就不用动）
    webviewTag: true,

    contextIsolation: true,                        // 安全开关，保持 true
    preload: path.join(__dirname, '../preload/index.js'),
  },
})
```

> **为什么要这样？** Electron 出于安全考虑，默认禁用了 `<webview>` 标签。
> 你不加这一行，你写的 `<webview>` 就只是一个空的 HTML 元素，啥也加载不了。

### 3.3 第 2 步：写 React 组件

> 完整代码已放在仓库 [cherry-studio-auth-embed/examples/renderer-webview/AuthEmbed.tsx](examples/renderer-webview/AuthEmbed.tsx)。下面我**逐段拆给你看**。

#### 3.3.1 文件顶部：常量

```tsx
const SSO_COOKIE_NAME = 'CORP_SSO_TOKEN'   // ① 公司 SSO 登录成功后写到浏览器的 Cookie 名
const SSO_DOMAIN      = 'sso.your-corp.com'// ② 那个 Cookie 是哪个域名下的
const PARTITION       = 'persist:corp-sso' // ③ ⭐ 共享 Cookie 罐子的名字

const LOGIN_URL = 'https://sso.your-corp.com/login?redirect=https://issue.your-corp.com/'
const ISSUE_URL = 'https://issue.your-corp.com/submit'
```

> 这三个值你得**问后端同学/SSO 文档**拿。
> 怎么自己看？打开公司登录页，按 F12 → Application → Cookies，
> 登录前后多了哪个 Cookie，就是 ①；它的 Domain 列就是 ②。

#### 3.3.2 状态：现在该显示哪个页

```tsx
type Stage = 'login' | 'issue'
const [stage, setStage] = useState<Stage>('login')
```

简单理解：`stage === 'login'` 显示登录页，`stage === 'issue'` 显示问题页。
`useState` 是 React 里"会让界面自动刷新的变量"。

#### 3.3.3 怎么知道用户登录成功了？

最稳的办法是**问主进程**：那个 Cookie 罐子里有没有 `CORP_SSO_TOKEN`？

```tsx
const hasSsoCookie = async () => {
  const cookies = await window.api.getCookies({
    partition: PARTITION,
    domain:    SSO_DOMAIN,
    name:      SSO_COOKIE_NAME,
  })
  return cookies.length > 0   // 数组非空 = 有 Cookie = 登录成功
}
```

> `window.api` 是哪来的？是 preload 脚本"开"给前台的小窗口（见 3.5 节）。

#### 3.3.4 在登录页加载完之后检查

```tsx
const wv = loginRef.current   // 拿到 <webview> DOM 引用
wv.addEventListener('did-finish-load', async () => {
  if (await hasSsoCookie()) {
    setStage('issue')         // ⭐ 切到问题页
  }
})
```

`did-finish-load` 是 `<webview>` 自带的事件，**每次它加载完一个新页面就会触发一次**。
SSO 登录通常是这样：填账号密码 → 提交 → 跳转到回调页 → 回调页加载完 → 这个事件触发 → 我们检查 Cookie → 有就切页。

#### 3.3.5 渲染：两个 webview，但同时只显示一个

```tsx
<webview src={LOGIN_URL} partition={PARTITION}
         style={{ display: stage === 'login' ? 'flex' : 'none' }} />

{stage === 'issue' && (
  <webview src={ISSUE_URL} partition={PARTITION} />
)}
```

为什么问题页用 `{stage === 'issue' && ...}` 而不是 `display:none`？
**因为如果一开始就加载问题页，它会因为没登录而拿到 401，浏览器会缓存这个失败结果**。
我们让它**等到登录成功后才挂载**，加载时 Cookie 已经在了，请求就 200 了。

### 3.4 第 3 步：把这个组件挂到 Cherry Studio 的页面上

打开 `src/renderer/src/` 下的路由文件（搜 `<Route` 或 `createBrowserRouter`），加一行：

```tsx
import AuthEmbed from './pages/CorpServicePage/AuthEmbed'

// 路由表里加：
<Route path="/corp/issue" element={<AuthEmbed />} />
```

然后在侧边栏（搜 Sidebar）加一个菜单项跳到 `/corp/issue`。

### 3.5 第 4 步：让前台能问 Cookie（写两段桥接代码）

#### 主进程 IPC 注册（`src/main/ipc.ts` 或 `src/main/index.ts` 里调用一次）

```ts
import { ipcMain, session } from 'electron'

ipcMain.handle('corp:get-cookies', async (_evt, args) => {
  if (!args.partition.startsWith('persist:')) {
    throw new Error('only persist: partitions are allowed')   // 安全校验
  }
  const sess = session.fromPartition(args.partition)
  return sess.cookies.get({
    domain: args.domain,
    name:   args.name,
  })
})
```

> `ipcMain.handle('频道名', 处理函数)` = 前台喊一声 `'corp:get-cookies'`，后台接住并回话。

#### preload 暴露（`src/preload/index.ts`）

```ts
import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('api', {
  getCookies: (args) => ipcRenderer.invoke('corp:get-cookies', args),
})
```

> `contextBridge.exposeInMainWorld('api', { ... })` 的意思是：
> "在前台网页的全局 `window` 对象上，挂一个叫 `api` 的对象，里面有 `getCookies` 方法。"
> 所以前台才能 `window.api.getCookies(...)`。

完整文件见：
- [examples/main-process/preload.ts](examples/main-process/preload.ts)
- [examples/main-process/ipc-handlers.ts](examples/main-process/ipc-handlers.ts)

### 3.6 完事了，跑一下

```powershell
yarn dev
```

点你新加的菜单 → 看到登录页 → 输账号密码 → 自动切到问题提交页。✅

---

## 第 4 章 第二种做法：用主进程 WebContentsView（更专业）

适合：你需要做这些事情，前台 webview 搞不定：

- 注入自定义请求头（如 `X-Corp-App: cherry-studio`）；
- 公司内网用了**自签名 HTTPS 证书**，浏览器拒绝加载；
- 想要做更精细的拦截、代理、错误回退。

完整代码：[examples/main-process/authWindow.ts](examples/main-process/authWindow.ts)

我挑核心几行讲：

```ts
const sess = session.fromPartition('persist:corp-sso')   // ① 同样那个共享罐子

// ② 给所有走这个 session 的请求加一个 header
sess.webRequest.onBeforeSendHeaders((details, cb) => {
  details.requestHeaders['X-From'] = 'cherry-studio'
  cb({ requestHeaders: details.requestHeaders })
})

// ③ 在主窗口里塞两个"内嵌视图"，都用上面这个 session
const loginView = new WebContentsView({ webPreferences: { session: sess } })
const issueView = new WebContentsView({ webPreferences: { session: sess } })
parent.contentView.addChildView(loginView)
parent.contentView.addChildView(issueView)

// ④ 显示哪个就 setVisible(true)，另一个 false
```

证书放行（公司内网自签必备）：

```ts
app.on('certificate-error', (event, _wc, url, _err, _cert, callback) => {
  const host = new URL(url).hostname
  if (['sso.your-corp.com', 'issue.your-corp.com'].includes(host)) {
    event.preventDefault()
    callback(true)            // 我信任这个域名，放行
    return
  }
  callback(false)             // 其他域名按默认处理（拒绝）
})
```

⚠️ 这段不要复制到生产环境前不审 —— 放行证书 = 接受中间人攻击的风险，**一定只放行公司内网域名白名单**。

---

## 第 5 章 常见错误与排查清单

| 现象 | 多半是哪儿出了问题 | 怎么修 |
|---|---|---|
| 写了 `<webview>` 但是空白 | `webviewTag: true` 没开 | 见 3.2 |
| 登录后切过去还是 401 | 两个 partition 不一样 / 没写 `persist:` | 检查字符串完全一致 |
| 关掉重开又要登录 | partition 没加 `persist:` 前缀 | 改成 `persist:xxx` |
| `window.api is undefined` | preload 没挂上 / 路径错 | 检查 BrowserWindow 的 `webPreferences.preload` 路径，看主进程控制台 |
| 公司内网页面打不开，证书错误 | 自签证书没放行 | 见第 4 章证书段 |
| 登录页能开，但提交时报跨域 (CORS) | 前端 webview 同源策略仍在 | 让后端加 CORS，或主进程用 `webRequest` 改 header |
| `did-finish-load` 一直没触发 | webview 还没挂到 DOM 上 | 用 `useEffect` 在挂载后再 addEventListener |

### 排查神器：打开 webview 自己的 DevTools

```ts
loginRef.current?.openDevTools()   // 给 webview 单独开一个 F12
```

或在主进程方案里：

```ts
loginView.webContents.openDevTools({ mode: 'detach' })
```

---

## 第 6 章 推荐的学习路径（给你之后用）

1. **先读 React 官方教程（中文）**：https://zh-hans.react.dev/learn  ——只需读到"添加交互"那一节。
2. **再读 Electron 官方文档**：https://www.electronjs.org/zh/docs/latest/  —— 重点看：
   - "进程模型" → 弄清主/渲染进程
   - "IPC" → 弄清 ipcMain / ipcRenderer / contextBridge
   - `session` 与 `cookies` 这两个 API
3. **最后看 Cherry Studio 的 PR/Issue**：https://github.com/CherryHQ/cherry-studio  —— 看真实代码长什么样。

---

## 第 7 章 把所有文件对应起来

| 文件 | 作用 | 放在 Cherry Studio 哪里 |
|---|---|---|
| [examples/renderer-webview/AuthEmbed.tsx](examples/renderer-webview/AuthEmbed.tsx) | 前台 React 组件，两个 webview | `src/renderer/src/pages/CorpServicePage/AuthEmbed.tsx` |
| [examples/main-process/preload.ts](examples/main-process/preload.ts) | 前后台桥接 | 合并到现有 `src/preload/index.ts` |
| [examples/main-process/ipc-handlers.ts](examples/main-process/ipc-handlers.ts) | 后台处理 cookie 查询请求 | 在 `src/main/index.ts` 启动时调用 `registerCorpIpc()` |
| [examples/main-process/authWindow.ts](examples/main-process/authWindow.ts) | 第二种做法的主进程视图 | `src/main/services/CorpSsoService.ts`（按需） |

---

## 第 8 章 一图回顾全文

```
[问题] 两个嵌入页要共享登录
   │
   ▼
[原理] 共用同一个 partition  ← persist:corp-sso
   │
   ├── 方案A（推荐）: 渲染层 <webview> ×2
   │     ├ 1. 主进程开 webviewTag:true
   │     ├ 2. React 写 AuthEmbed.tsx
   │     └ 3. preload + IPC 用来查 cookie
   │
   └── 方案B（专业）: 主进程 WebContentsView ×2
         ├ 1. session.fromPartition(...)
         ├ 2. 注入 header / 放行证书
         └ 3. setVisible 切换显示

[判断登录成功] = 检查目标 cookie 在不在
[切换页面]    = setStage('issue') 或 setVisible 切换
```

---

## 结语

这套流程把"嵌入两个登录态共享的网页"讲明白了。**真正的核心其实只有一个词：partition**。
其他所有代码都是配套用的——监听事件、调 IPC、注入 header——都是围绕"让这两个页面共享同一个 Cookie 罐子"展开的。

如果你跟着改完跑通，就已经掌握了 Electron 应用里嵌入第三方网页 + 单点登录这一类问题的通用做法。下次再遇到类似需求（比如再加一个第三方系统），把 partition 名字再换一个就好。

加油 💪
