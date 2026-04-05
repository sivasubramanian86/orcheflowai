import { useState, useCallback } from 'react'
import { runWorkflow } from '@/api/client'
import type { WorkflowRequest, WorkflowResult } from '@/api/client'
import type { PipelineStep, LogEntry, AgentState } from '@/api/types'
import { DEFAULT_PIPELINE } from '@/api/types'

const STAGES = [
  { id: 'orchestrator', label: 'Orchestrator',  action: 'PLANNING_PIPELINE' },
  { id: 'notes',        label: 'NotesAgent',    action: 'EXTRACTING_ACTION_ITEMS' },
  { id: 'task',         label: 'TaskAgent',     action: 'CREATING_TASKS' },
  { id: 'schedule',     label: 'ScheduleAgent', action: 'FINDING_CALENDAR_GAPS' },
  { id: 'workflow',     label: 'WorkflowAgent', action: 'COMPILING_SUMMARY' },
]

const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))
let logSeq = 0

function makeLog(agent: string, action: string, level: LogEntry['level'] = 'ok', details?: string): LogEntry {
  return {
    id: String(++logSeq),
    timestamp: new Date().toLocaleTimeString('en-GB', { hour12: false }),
    agent,
    action,
    level,
    details,
  }
}

/**
 * useWorkflow — manages the full orchestration lifecycle:
 * pipeline state, audit log, API call, result, and error handling.
 */
export function useWorkflow() {
  const [isRunning, setIsRunning]         = useState(false)
  const [pipeline, setPipeline]           = useState<PipelineStep[]>(DEFAULT_PIPELINE)
  const [logs, setLogs]                   = useState<LogEntry[]>([
    makeLog('System', 'DASHBOARD_READY', 'ok'),
  ])
  const [result, setResult]               = useState<WorkflowResult | null>(null)
  const [error, setError]                 = useState<string | null>(null)

  const setStepState = useCallback((id: string, state: AgentState) => {
    setPipeline(prev =>
      prev.map(s => s.id === id ? { ...s, state } : s)
    )
  }, [])

  const addLog = useCallback((entry: LogEntry) => {
    setLogs(prev => [...prev, entry])
  }, [])

  const resetPipeline = useCallback(() => {
    setPipeline(DEFAULT_PIPELINE.map(s => ({ ...s, state: 'idle' as AgentState })))
  }, [])

  const submit = useCallback(async (req: WorkflowRequest) => {
    setIsRunning(true)
    setResult(null)
    setError(null)
    resetPipeline()

    try {
      // Animate pipeline stages before API response
      for (let i = 0; i < STAGES.length - 1; i++) {
        const stage = STAGES[i]!
        setStepState(stage.id, 'active')
        addLog(makeLog(stage.label, stage.action, 'action'))
        await sleep(650)
        setStepState(stage.id, 'done')
      }
      const lastStage = STAGES[STAGES.length - 1]!
      setStepState(lastStage.id, 'active')
      addLog(makeLog(lastStage.label, lastStage.action, 'action'))

      // Real API call
      const data = await runWorkflow(req)
      setStepState(lastStage.id, 'done')

      addLog(makeLog('WorkflowAgent', 'ORCHESTRATION_COMPLETE', 'ok', `status=${data.status}`))

      // View Transitions API for smooth result reveal
      if (document.startViewTransition) {
        document.startViewTransition(() => setResult(data))
      } else {
        setResult(data)
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown error'
      setError(msg)
      STAGES.forEach(s => setStepState(s.id, 'idle'))
      addLog(makeLog('System', 'ERROR', 'error', msg))
    } finally {
      setIsRunning(false)
    }
  }, [resetPipeline, setStepState, addLog])

  return { isRunning, pipeline, logs, result, error, submit }
}
