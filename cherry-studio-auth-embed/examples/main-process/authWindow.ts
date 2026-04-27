/**
 * authWindow.ts
 * ------------------------------------------------------------------
 * 主进程方案：在同一个 BrowserWindow 中用两个 WebContentsView，
 *           共用一个 partition session，实现登录态继承。
 *
 * 用法：
 *    import { openCorpService } from './authWindow'
 *    openCorpService(mainWindow)
 * ------------------------------------------------------------------
 */
import { BrowserWindow, WebContentsView, session, type Session } from 'electron'

const PARTITION = 'persist:corp-sso'
const SSO_DOMAIN = 'sso.your-corp.com'
const SSO_COOKIE_NAME = 'CORP_SSO_TOKEN'

const LOGIN_URL = 'https://sso.your-corp.com/login?redirect=https://issue.your-corp.com/'
const ISSUE_URL = 'https://issue.your-corp.com/submit'

/** 获取/初始化共享 session（注入公共 header、放行公司自签证书等） */
function getCorpSession(): Session {
  const sess = session.fromPartition(PARTITION)

  // 统一注入 UA / 公共 header（按需）
  sess.webRequest.onBeforeSendHeaders((details, cb) => {
    details.requestHeaders['X-From'] = 'cherry-studio'
    cb({ requestHeaders: details.requestHeaders })
  })

  return sess
}

/** 全局只注册一次：放行公司内网自签证书 */
let certHandlerInstalled = false
export function installCorpCertBypass(app: Electron.App, allowHosts: string[]): void {
  if (certHandlerInstalled) return
  certHandlerInstalled = true
  app.on('certificate-error', (event, _wc, url, _err, _cert, callback) => {
    try {
      const host = new URL(url).hostname
      if (allowHosts.includes(host)) {
        event.preventDefault()
        callback(true)
        return
      }
    } catch {
      /* ignore */
    }
    callback(false)
  })
}

async function hasSsoCookie(sess: Session): Promise<boolean> {
  const cookies = await sess.cookies.get({ domain: SSO_DOMAIN, name: SSO_COOKIE_NAME })
  return cookies.length > 0
}

/** 在父窗口里打开「登录 + 问题提交」嵌套视图 */
export async function openCorpService(parent: BrowserWindow): Promise<void> {
  const sess = getCorpSession()

  const loginView = new WebContentsView({ webPreferences: { session: sess, contextIsolation: true } })
  const issueView = new WebContentsView({ webPreferences: { session: sess, contextIsolation: true } })

  const layout = () => {
    const { width, height } = parent.getContentBounds()
    loginView.setBounds({ x: 0, y: 0, width, height })
    issueView.setBounds({ x: 0, y: 0, width, height })
  }

  parent.contentView.addChildView(loginView)
  parent.contentView.addChildView(issueView)
  layout()
  parent.on('resize', layout)

  const showLogin = () => {
    issueView.setVisible(false)
    loginView.setVisible(true)
  }
  const showIssue = () => {
    loginView.setVisible(false)
    issueView.setVisible(true)
    // 此时 session 中已有 SSO cookie，加载就会自动带上
    if (issueView.webContents.getURL() !== ISSUE_URL) {
      void issueView.webContents.loadURL(ISSUE_URL)
    }
  }

  // 初始：若已登录直接显示问题页
  if (await hasSsoCookie(sess)) {
    showIssue()
  } else {
    showLogin()
    void loginView.webContents.loadURL(LOGIN_URL)
  }

  // 登录页每次导航后检查
  loginView.webContents.on('did-finish-load', async () => {
    if (await hasSsoCookie(sess)) showIssue()
  })

  // 问题页加载失败 → 回退登录
  issueView.webContents.on('did-fail-load', async (_e, code) => {
    if (code === -3) return
    if (!(await hasSsoCookie(sess))) showLogin()
  })

  // 父窗口关闭时清理
  parent.once('closed', () => {
    loginView.webContents.close()
    issueView.webContents.close()
  })
}
