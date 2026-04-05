import type { WorkflowResult } from '@/api/client'
import type { Task, CalendarBlock } from '@/api/types'
import styles from './ResultsPanel.module.css'

interface Props {
  result: WorkflowResult
}

/** ResultsPanel — displays confidence, summary, tasks, and calendar blocks */
export function ResultsPanel({ result }: Props) {
  const confidence = result.confidence != null ? Math.round(result.confidence * 100) : null
  const tasks: Task[] = result.tasks_created ?? []
  const blocks: CalendarBlock[] = result.calendar_blocks ?? []

  const fmt = (iso?: string) =>
    iso ? new Date(iso).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }) : ''

  return (
    <section className={styles.panel} aria-label="Workflow results" aria-live="polite">
      <div className={styles.header}>
        <div className={styles.headerIcon} aria-hidden="true">✨</div>
        <div>
          <h3 className={styles.title}>Workflow Results</h3>
          {result.run_id && (
            <p className={styles.subtitle}>Run #{result.run_id.slice(0, 8)}</p>
          )}
        </div>
      </div>

      {confidence !== null && (
        <div className={styles.confidenceRow}>
          <span className={styles.confLabel}>AI Confidence</span>
          <div className={styles.confBar} aria-label={`Confidence: ${confidence}%`} role="meter"
            aria-valuenow={confidence} aria-valuemin={0} aria-valuemax={100}>
            <div className={styles.confFill} style={{ width: `${confidence}%` }} />
          </div>
          <span className={styles.confValue}>{confidence}%</span>
        </div>
      )}

      <div className={styles.section}>
        <div className={styles.sectionLabel}>Executive Summary</div>
        <p className={styles.summaryBox}>{result.summary ?? 'Workflow completed.'}</p>
      </div>

      <div className={styles.section}>
        <div className={styles.sectionLabel}>Tasks Created ({tasks.length})</div>
        {tasks.length === 0 ? (
          <EmptyState icon="✅" message="No tasks extracted." />
        ) : (
          <ul className={styles.taskList} role="list" aria-label="Created tasks">
            {tasks.map((t, i) => <TaskItem key={t.id ?? i} task={t} />)}
          </ul>
        )}
      </div>

      <div className={styles.section}>
        <div className={styles.sectionLabel}>Calendar Blocks ({blocks.length})</div>
        {blocks.length === 0 ? (
          <EmptyState icon="📅" message="No calendar blocks created." />
        ) : (
          <ul className={styles.blockList} aria-label="Calendar blocks">
            {blocks.map((b, i) => (
              <li key={i} className={styles.calBlock}>
                <span className={styles.calIcon} aria-hidden="true">📅</span>
                <div>
                  <div className={styles.calTime}>{fmt(b.start)} – {fmt(b.end)}</div>
                  <div className={styles.calTitle}>{b.title ?? 'Focus Block'}</div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}

function TaskItem({ task }: { task: Task }) {
  const p = Math.min(Number(task.priority) || 3, 3) as 1 | 2 | 3
  return (
    <li className={styles.taskItem} role="listitem">
      <div className={`${styles.badge} ${styles[`p${p}`]}`} aria-label={`Priority ${p}`}>
        P{p}
      </div>
      <span className={styles.taskTitle}>{task.title ?? 'Untitled task'}</span>
      {task.due_date && <span className={styles.taskDue}>{task.due_date}</span>}
    </li>
  )
}

function EmptyState({ icon, message }: { icon: string; message: string }) {
  return (
    <div className={styles.empty} role="status">
      <span aria-hidden="true" style={{ fontSize: '1.5rem', opacity: 0.35 }}>{icon}</span>
      <span>{message}</span>
    </div>
  )
}
