import { useEffect, useRef } from 'react'
import type { LogEntry } from '@/api/types'
import styles from './AuditLog.module.css'

interface Props {
  entries: LogEntry[]
}

/**
 * AuditLog — terminal-style real-time agent trace.
 * Auto-scrolls to the newest entry.
 * Uses JetBrains Mono via CSS var(--font-mono).
 */
export function AuditLog({ entries }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [entries])

  return (
    <div
      className={styles.log}
      role="log"
      aria-live="polite"
      aria-label="Agent audit log — real-time agent actions"
      aria-atomic="false"
      tabIndex={0}
    >
      {entries.map((entry) => (
        <div key={entry.id} className={styles.entry}>
          <span className={styles.time}>[{entry.timestamp}]</span>{' '}
          <span className={styles.agent}>[{entry.agent}]</span>{' '}
          <span className={styles[`level_${entry.level}`]}>{entry.action}</span>
          {entry.details && (
            <span className={styles.details}> — {entry.details}</span>
          )}
        </div>
      ))}
      <div ref={bottomRef} aria-hidden="true" />
    </div>
  )
}
