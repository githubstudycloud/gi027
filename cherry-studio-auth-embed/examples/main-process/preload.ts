/**
 * preload.ts
 * ------------------------------------------------------------------
 * 给渲染进程暴露安全的 cookie 查询接口。
 * 在 BrowserWindow.webPreferences.preload 里指向编译后的 preload.js。
 * ------------------------------------------------------------------
 */
import { contextBridge, ipcRenderer } from 'electron'

export interface GetCookiesArgs {
  partition: string
  domain?: string
  name?: string
  url?: string
}

contextBridge.exposeInMainWorld('api', {
  getCookies: (args: GetCookiesArgs) => ipcRenderer.invoke('corp:get-cookies', args),
})

declare global {
  interface Window {
    api: {
      getCookies: (args: GetCookiesArgs) => Promise<Electron.Cookie[]>
    }
  }
}
