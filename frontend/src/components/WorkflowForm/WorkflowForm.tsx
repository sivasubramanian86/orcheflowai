import { useState } from 'react'
import type { WorkflowRequest } from '@/api/client'
import { AgentPipeline } from '@/components/AgentPipeline/AgentPipeline'
import type { PipelineStep } from '@/api/types'
import styles from './WorkflowForm.module.css'

interface Props {
  onSubmit: (req: WorkflowRequest) => Promise<void>
  isRunning: boolean
  pipeline: PipelineStep[]
}

/**
 * WorkflowForm — intent input, notes textarea, date picker,
 * agent pipeline visualizer, and the run button.
 */
export function WorkflowForm({ onSubmit, isRunning, pipeline }: Props) {
  const today = new Date().toISOString().split('T')[0]
  const [intent, setIntent] = useState('')
  const [notes, setNotes]   = useState('')
  const [date, setDate]     = useState(today)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!intent.trim()) return
    await onSubmit({
      intent: intent.trim(),
      payload: { notes_content: notes.trim() || undefined, date_context: date },
    })
  }

  return (
    <form onSubmit={handleSubmit} aria-labelledby="workflow-heading" noValidate>
      <div className={styles.cardHeader}>
        <div className={styles.cardIcon} aria-hidden="true">🧠</div>
        <div>
          <h2 className={styles.cardTitle} id="workflow-heading">Run Workflow</h2>
          <p className={styles.cardSubtitle}>Paste notes or describe your intent</p>
        </div>
      </div>

      <div className={styles.field}>
        <label className={styles.label} htmlFor="intent-input">Intent</label>
        <input
          id="intent-input"
          className={styles.input}
          type="text"
          value={intent}
          onChange={e => setIntent(e.target.value)}
          placeholder="e.g. Convert Q2 planning notes into tasks and block focus time"
          aria-label="Workflow intent — describe what you want the agents to do"
          aria-required="true"
          maxLength={2000}
          disabled={isRunning}
        />
      </div>

      <div className={styles.field}>
        <label className={styles.label} htmlFor="notes-input">Meeting Notes / Content</label>
        <textarea
          id="notes-input"
          className={styles.textarea}
          value={notes}
          onChange={e => setNotes(e.target.value)}
          placeholder="Paste raw meeting notes, brain dump, or any unstructured content..."
          aria-label="Raw notes or content to process"
          aria-describedby="notes-hint"
          disabled={isRunning}
        />
        <p id="notes-hint" className={styles.hint}>
          The Notes Agent extracts action items, deadlines, and decisions from this content.
        </p>
      </div>

      <div className={styles.field}>
        <label className={styles.label} htmlFor="date-input">Date Context</label>
        <input
          id="date-input"
          className={styles.input}
          type="date"
          value={date}
          onChange={e => setDate(e.target.value)}
          aria-label="Date context for deadline inference and calendar blocking"
          disabled={isRunning}
        />
      </div>

      <div className={styles.pipelineLabel} aria-hidden="true">
        Agent Execution Pipeline
      </div>
      <AgentPipeline steps={pipeline} />

      <button
        type="submit"
        className={styles.btnPrimary}
        disabled={isRunning || !intent.trim()}
        aria-label={isRunning ? 'Agents are working...' : 'Run multi-agent workflow'}
        aria-busy={isRunning}
      >
        {isRunning ? (
          <><span className={styles.spinner} aria-hidden="true" /> Agents working...</>
        ) : (
          <><span aria-hidden="true">⚡</span> Run Workflow</>
        )}
      </button>
    </form>
  )
}
