import React from 'react';
import styles from './RunExplorer.module.css';

/**
 * RunExplorer — Agent Observability.
 * Shows each workflow run and the breakdown of agent/tool calls.
 */
export const RunExplorer: React.FC = () => {
  const mockRuns = [
    { id: '1', name: 'Morning Plan 2026-04-06', status: 'COMPLETED', duration: '12s' },
    { id: '2', name: 'AlloyDB Task Sync', status: 'COMPLETED', duration: '4.5s' },
    { id: '3', name: 'YouTube Learning Cycle', status: 'RUNNING', duration: '2.1s' }
  ];

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Agent Run / Trace Explorer</h1>
      </header>

      <div className={styles.splitView}>
        <aside className={styles.runList}>
          {mockRuns.map(run => (
            <div key={run.id} className={styles.runItem}>
              <div className={styles.runName}>{run.name}</div>
              <div className={styles.runMeta}>{run.status} • {run.duration}</div>
            </div>
          ))}
        </aside>

        <main className={styles.traceDetail}>
          <div className={styles.step}>
            <div className={styles.stepHeader}>
              <div className={styles.stepIcon}>🤖</div>
              <div className={styles.stepTitle}>Orchestrator: Plan Daily Intent</div>
              <div className={styles.stepStatus}>SUCCESS</div>
            </div>
            <div className={styles.stepContext}>
              Input: "Plan my tomorrow focusing on deep work."
            </div>
          </div>

          <div className={styles.step}>
            <div className={styles.stepHeader}>
              <div className={styles.stepIcon}>📆</div>
              <div className={styles.stepTitle}>ScheduleAgent: listEvents (Google Calendar)</div>
              <div className={styles.stepStatus}>SUCCESS</div>
            </div>
            <div className={styles.stepContext}>
              Tool: `calendar.listEvents` → 5 found
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};
