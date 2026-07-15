const { contextBridge, ipcRenderer } = require('electron') as typeof import('electron')

contextBridge.exposeInMainWorld('qlu', {
  invoke: (method: string, params?: Record<string, unknown>) => ipcRenderer.invoke('bridge:invoke', method, params),
  onEvent: (callback: (name: string, payload: unknown) => void) => {
    const listener = (_event: unknown, name: string, payload: unknown) => callback(name, payload)
    ipcRenderer.on('bridge:event', listener)
    return () => ipcRenderer.removeListener('bridge:event', listener)
  },
  selectDirectory: (defaultPath?: string) => ipcRenderer.invoke('system:select-directory', defaultPath),
  openPath: (target: string) => ipcRenderer.invoke('system:open-path', target),
  showItem: (target: string) => ipcRenderer.invoke('system:show-item', target),
  openExternal: (url: string) => ipcRenderer.invoke('system:open-external', url),
  checkUpdate: (currentVersion: string) => ipcRenderer.invoke('system:check-update', currentVersion),
  windowAction: (action: 'minimize' | 'maximize' | 'close') => ipcRenderer.send('window:action', action),
})
