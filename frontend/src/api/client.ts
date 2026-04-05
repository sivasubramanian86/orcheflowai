/**
 * OrcheFlowAI API client
 * All FastAPI backend calls are centralised here.
 * The Vite dev proxy rewrites /v1 → http://localhost:8000/v1
 */
import type { Task, CalendarBlock } from './types'
export type { Task, CalendarBlock }

const BASE = '/v1'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'Bearer demo-token',
      ...init?.headers,
    },
    ...init,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API ${res.status}: ${text.slice(0, 200)}`)
  }
  return res.json() as Promise<T>
}

// ── Workflow ────────────────────────────────────────────────────────
export interface WorkflowRequest {
  intent: string
  payload: {
    notes_content?: string
    date_context?: string
  }
}

export interface WorkflowResult {
  run_id: string
  status: string
  summary?: string
  confidence?: number
  tasks_created?: Task[]
  calendar_blocks?: CalendarBlock[]
  plan_executed?: string[]
}

export function runWorkflow(body: WorkflowRequest): Promise<WorkflowResult> {
  return request<WorkflowResult>('/workflow/run', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export interface WorkflowRun {
  run_id: string
  status: string
  created_at: string
}

export function listWorkflowRuns(): Promise<{ runs: WorkflowRun[]; total: number }> {
  return request('/workflow/runs')
}

// ── Tasks ────────────────────────────────────────────────────────────

export function listTasks(status = 'TODO', limit = 20): Promise<{ tasks: Task[]; total: number }> {
  return request(`/tasks?status=${status}&limit=${limit}`)
}

// ── Health ────────────────────────────────────────────────────────────
export interface HealthResponse {
  status: 'ok' | 'healthy' | 'degraded'
  service: string
  version: string
}

export function checkHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health')
}
