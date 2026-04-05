import type { PipelineStep } from '@/api/types'
import styles from './AgentPipeline.module.css'

interface Props {
  steps: PipelineStep[]
}

/**
 * AgentPipeline — animated multi-agent pipeline visualizer.
 * Each step renders a bubble with CSS data-state transitions.
 * Connected by animated fill lines (CSS ::after).
 */
export function AgentPipeline({ steps }: Props) {
  return (
    <ol className={styles.pipeline} aria-label="Multi-agent execution pipeline">
      {steps.map((step, idx) => (
        <li key={step.id} className={styles.pipelineItem}>
          <div
            className={styles.step}
            data-state={step.state}
            id={`step-${step.id}`}
          >
            <div
              className={styles.bubble}
              aria-label={`${step.label} — ${step.state}`}
            >
              <span aria-hidden="true">{step.icon}</span>
            </div>
            <span className={styles.label}>{step.label}</span>
          </div>
          {idx < steps.length - 1 && (
            <div
              className={styles.connector}
              data-prev-done={step.state === 'done' ? 'true' : 'false'}
              aria-hidden="true"
            />
          )}
        </li>
      ))}
    </ol>
  )
}
