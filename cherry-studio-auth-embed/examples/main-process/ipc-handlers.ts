/**
 * ipc-handlers.ts
 * ------------------------------------------------------------------
 * 注册主进程 IPC，给渲染层 webview 方案提供 cookie 查询能力。
 * 在 app.whenReady() 里调用一次 registerCorpIpc()。
 * ------------------------------------------------------------------
 */
import { ipcMain, session } from 'electron'

export interface GetCookiesArgs {
  partition: string
  domain?: string
  name?: string
  url?: string
}

export function registerCorpIpc(): void {
  ipcMain.handle('corp:get-cookies', async (_evt, args: GetCookiesArgs) => {
    if (!args?.partition || typeof args.partition !== 'string') {
      throw new Error('partition is required')
    }
    // 仅允许查 persist: 开头的业务分区，避免越权读取默认 session
    if (!args.partition.startsWith('persist:')) {
      throw new Error('only persist: partitions are allowed')
    }
    const sess = session.fromPartition(args.partition)
    const filter: Electron.CookiesGetFilter = {}
    if (args.domain) filter.domain = args.domain
    if (args.name) filter.name = args.name
    if (args.url) filter.url = args.url
    return sess.cookies.get(filter)
  })
}
