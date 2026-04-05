/**
 * Shared TypeScript types not tied to the API layer.
 * Import from here for UI-specific models.
 */

/** Agent pipeline step states */
export type AgentState = 'idle' | 'active' | 'done' | 'error'

/** Log levels for the AuditLog component */
export type LogLevel = 'ok' | 'action' | 'warn' | 'error' | 'info'

/** Task entity (mirrors FastAPI Task schema) */
export interface Task {
  id?: string
  title: string
  priority?: number
  due_date?: string
  status?: string
  source_agent?: string
}

/** Calendar block entity */
export interface CalendarBlock {
  title?: string
  start?: string
  end?: string
}

export interface LogEntry {
  id: string
  timestamp: string
  agent: string
  action: string
  details?: string
  level: LogLevel
}

export interface CalendarBlock {
  title?: string
  start?: string
  end?: string
}

export interface PipelineStep {
  id: string
  label: string
  icon: string
  state: AgentState
}

export const DEFAULT_PIPELINE: PipelineStep[] = [
  { id: 'orchestrator', label: 'Orchestrator', icon: '🎯', state: 'idle' },
  { id: 'notes',        label: 'Notes',        icon: '📝', state: 'idle' },
  { id: 'task',         label: 'Tasks',         icon: '✅', state: 'idle' },
  { id: 'schedule',     label: 'Schedule',      icon: '📅', state: 'idle' },
  { id: 'workflow',     label: 'Workflow',       icon: '📋', state: 'idle' },
]
