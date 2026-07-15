/// <reference types="vite/client" />

interface Window {
  qlu: {
    invoke<T>(method: string, params?: Record<string, unknown>): Promise<T>
    onEvent(callback: (name: string, payload: unknown) => void): () => void
    selectDirectory(defaultPath?: string): Promise<string | null>
    openPath(target: string): Promise<string>
    showItem(target: string): Promise<void>
    openExternal(url: string): Promise<void>
    checkUpdate(currentVersion: string): Promise<UpdateInfo | null>
    windowAction(action: 'minimize' | 'maximize' | 'close'): void
  }
}

interface UpdateInfo { version: string; name: string; notes: string; url: string }
