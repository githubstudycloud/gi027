/**
 * AuthEmbed.tsx
 * ------------------------------------------------------------------
 * 在 Cherry Studio 渲染进程中嵌入「公司鉴权页 → 问题提交页」的示例。
 *
 * 关键点：
 *  1. 两个 <webview> 使用同一个 partition="persist:corp-sso"，共享 cookie/localStorage。
 *  2. 通过监听目标 cookie 出现来判断登录成功，自动切到问题提交页。
 *  3. 不需要把 token 手动复制到第二个页面 —— Electron 会自动带上同 session 的 cookie。
 *
 * 前置条件（在主进程创建 BrowserWindow 时）：
 *    new BrowserWindow({
 *      webPreferences: {
 *        webviewTag: true,        // 必须开启
 *        contextIsolation: true,
 *        preload: path.join(__dirname, 'preload.js'),
 *      },
 *    })
 * ------------------------------------------------------------------
 */
import React, { useEffect, useRef, useState, useCallback } from 'react'

// 与公司 SSO 一致；登录成功后该 cookie 会被写入
const SSO_COOKIE_NAME = 'CORP_SSO_TOKEN'
const SSO_DOMAIN = 'sso.your-corp.com'

// 共享存储分区（必须 persist: 前缀才会持久化）
const PARTITION = 'persist:corp-sso'

const LOGIN_URL = 'https://sso.your-corp.com/login?redirect=https://issue.your-corp.com/'
const ISSUE_URL = 'https://issue.your-corp.com/submit'

type Stage = 'login' | 'issue'

export const AuthEmbed: React.FC = () => {
  const loginRef = useRef<Electron.WebviewTag | null>(null)
  const issueRef = useRef<Electron.WebviewTag | null>(null)
  const [stage, setStage] = useState<Stage>('login')
  const [errorMsg, setErrorMsg] = useState<string>('')

  /** 询问主进程：当前 partition 是否已存在 SSO cookie */
  const hasSsoCookie = useCallback(async (): Promise<boolean> => {
    // window.api 来自 preload，见 examples/main-process/preload.ts
    const cookies = await window.api.getCookies({
      partition: PARTITION,
      domain: SSO_DOMAIN,
      name: SSO_COOKIE_NAME,
    })
    return Array.isArray(cookies) && cookies.length > 0
  }, [])

  /** 启动时若已登录则直接进入问题页 */
  useEffect(() => {
    hasSsoCookie().then((ok) => ok && setStage('issue'))
  }, [hasSsoCookie])

  /** 监听登录 webview 的导航/加载事件 */
  useEffect(() => {
    const wv = loginRef.current
    if (!wv) return

    const onLoaded = async () => {
      if (await hasSsoCookie()) {
        setStage('issue')
      }
    }
    const onFail = (e: Electron.DidFailLoadEvent) => {
      // -3 = ABORTED（用户主动跳转），忽略
      if (e.errorCode !== -3) setErrorMsg(`登录页加载失败: ${e.errorDescription}`)
    }

    wv.addEventListener('did-finish-load', onLoaded)
    wv.addEventListener('did-navigate', onLoaded)
    wv.addEventListener('did-navigate-in-page', onLoaded)
    wv.addEventListener('did-fail-load', onFail)
    return () => {
      wv.removeEventListener('did-finish-load', onLoaded)
      wv.removeEventListener('did-navigate', onLoaded)
      wv.removeEventListener('did-navigate-in-page', onLoaded)
      wv.removeEventListener('did-fail-load', onFail)
    }
  }, [hasSsoCookie, stage])

  /** 问题页 401 时回退到登录页 */
  useEffect(() => {
    const wv = issueRef.current
    if (!wv || stage !== 'issue') return
    const onFail = async (e: Electron.DidFailLoadEvent) => {
      if (e.errorCode === -3) return
      // 401 时 Electron 通常仍会触发 did-finish-load，这里再二次校验
      if (!(await hasSsoCookie())) setStage('login')
    }
    wv.addEventListener('did-fail-load', onFail)
    return () => wv.removeEventListener('did-fail-load', onFail)
  }, [hasSsoCookie, stage])

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {errorMsg && <div style={{ color: '#c00', padding: 8 }}>{errorMsg}</div>}

      {/* 登录 webview：未登录时显示 */}
      <webview
        ref={loginRef as unknown as React.RefObject<HTMLElement>}
        src={LOGIN_URL}
        partition={PARTITION}
        // @ts-expect-error allowpopups 是 webview 标签属性
        allowpopups="true"
        style={{
          flex: 1,
          display: stage === 'login' ? 'flex' : 'none',
          border: 'none',
        }}
      />

      {/* 问题提交 webview：登录后才挂载，避免提前请求拿到 401 缓存 */}
      {stage === 'issue' && (
        <webview
          ref={issueRef as unknown as React.RefObject<HTMLElement>}
          src={ISSUE_URL}
          partition={PARTITION}
          // @ts-expect-error
          allowpopups="true"
          style={{ flex: 1, border: 'none' }}
        />
      )}
    </div>
  )
}

export default AuthEmbed
