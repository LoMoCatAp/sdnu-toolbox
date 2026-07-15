import { computed, reactive, watch } from 'vue'
import type { BootstrapData, GradeEvent, PageName, Settings, TaskRecord } from './types'

const state = reactive({
  boot: null as BootstrapData | null,
  page: 'home' as PageName,
  loading: true,
  error: '',
  toast: null as null | { message: string; tone: 'success' | 'error' | 'info' },
  grade: {
    running: false,
    taskId: '',
    stage: 'environment',
    status: '准备就绪',
    logs: [] as string[],
    resultPath: '',
    failed: false,
  },
})

let toastTimer: number | undefined
function notify(message: string, tone: 'success' | 'error' | 'info' = 'info') {
  state.toast = { message, tone }
  window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => { state.toast = null }, 3500)
}

function applyTheme(theme: Settings['theme']) {
  const dark = theme === 'dark' || (theme === 'system' && matchMedia('(prefers-color-scheme: dark)').matches)
  document.documentElement.dataset.theme = dark ? 'dark' : 'light'
}

async function refreshTasks() {
  if (!state.boot) return
  state.boot.tasks = await window.qlu.invoke<TaskRecord[]>('listTasks', { limit: 200 })
}

async function saveSettings(patch: Partial<Settings>) {
  if (!state.boot) return
  state.boot.settings = await window.qlu.invoke<Settings>('saveSettings', patch as Record<string, unknown>)
  applyTheme(state.boot.settings.theme)
  notify('设置已保存', 'success')
}

async function initialize() {
  try {
    state.boot = await window.qlu.invoke<BootstrapData>('bootstrap')
    applyTheme(state.boot.settings.theme)
    window.qlu.onEvent((name, payload) => {
      if (name !== 'gradeExport') return
      const message = payload as { taskId: string; event: GradeEvent }
      const event = message.event
      if (event.type === 'status') {
        state.grade.stage = event.stage || state.grade.stage
        state.grade.status = event.message || '正在处理…'
      } else if (event.type === 'log') {
        state.grade.logs.push(event.message || '')
      } else if (event.type === 'success') {
        state.grade.running = false
        state.grade.resultPath = event.path || ''
        state.grade.status = '导出完成'
        state.grade.stage = 'success'
        notify('成绩文件已成功导出', 'success')
        void refreshTasks()
      } else if (event.type === 'cancelled') {
        state.grade.running = false
        state.grade.status = event.message || '操作已取消'
        state.grade.stage = 'cancelled'
        void refreshTasks()
      } else if (event.type === 'error') {
        state.grade.running = false
        state.grade.failed = true
        state.grade.status = event.message || '导出失败'
        state.grade.stage = 'error'
        notify(state.grade.status, 'error')
        void refreshTasks()
      }
    })
  } catch (error) {
    state.error = error instanceof Error ? error.message : String(error)
  } finally {
    state.loading = false
  }
}

watch(() => state.page, (page) => { if (page === 'tasks' || page === 'home') void refreshTasks() })

export const appStore = {
  state,
  boot: computed(() => state.boot),
  initialize,
  notify,
  refreshTasks,
  saveSettings,
  navigate(page: PageName) { state.page = page },
}
