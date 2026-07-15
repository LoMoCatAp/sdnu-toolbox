export type PageName = 'home' | 'tools' | 'tasks' | 'settings' | 'about' | 'grade'
export type Theme = 'light' | 'dark' | 'system'

export interface Settings {
  schema_version: number
  welcome_accepted: boolean
  default_output_dir: string
  preferred_browser: 'auto' | 'edge' | 'chrome' | 'chromium'
  keep_login_state: boolean
  theme: Theme
  check_updates: boolean
}

export interface TaskRecord {
  id: string; tool_id: string; tool_name: string; tool_version: string
  status: 'running' | 'success' | 'failed' | 'cancelled' | 'interrupted'
  summary: string; result_path: string; error_message: string
  created_at: string; started_at: string; finished_at: string
}

export interface ToolManifest {
  id: string; name: string; description: string; category: string; version: string; icon_text: string
}

export interface BootstrapData {
  version: string
  settings: Settings
  tasks: TaskRecord[]
  defaultAcademicYear: string
  semesters: Record<string, string>
  tool: ToolManifest
  paths: Record<'settings' | 'tasks' | 'logs' | 'profiles' | 'data', string>
  metadata: Record<'author' | 'email' | 'github' | 'repository' | 'issues' | 'releases', string>
}

export interface GradeEvent {
  type: 'status' | 'log' | 'success' | 'error' | 'cancelled'
  stage?: string; message?: string; path?: string; code?: string
}
