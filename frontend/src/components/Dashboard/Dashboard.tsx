import React from 'react'
import { WorkflowForm } from '@/components/WorkflowForm/WorkflowForm'
import { ResultsPanel } from '@/components/ResultsPanel/ResultsPanel'
import { AuditLog } from '@/components/AuditLog/AuditLog'
import { WorkflowRequest } from '@/api/client'
import { Activity, CheckCircle, Zap } from 'lucide-react'
import styles from './Dashboard.module.css'

interface DashboardProps {
  isRunning: boolean;
  pipeline: any[];
  logs: any[];
  result: any;
  error: string | null;
  onSubmit: (req: WorkflowRequest) => Promise<void>;
}

export const Dashboard: React.FC<DashboardProps> = ({ 
  isRunning, pipeline, logs, result, error, onSubmit 
}) => {
  return (
    <div className={styles.container}>
      <header className={styles.hero}>
        <div className={styles.heroTag}>✦ GOOGLE ADK • VERTEX AI • MCP</div>
        <h1 className={styles.title}>Orchestrate your flow.</h1>
        <p className={styles.subtitle}>
          Multi-agent orchestration that converts raw notes into prioritised tasks.
        </p>
      </header>

      {/* DASHBOARD METRICS */}
      <div className={styles.metricsGrid}>
        <div className={styles.metricCard}>
          <div className={styles.metricIconWrap} style={{ color: '#10B981', background: 'rgba(16, 185, 129, 0.1)' }}>
            <Activity size={24} />
          </div>
          <div className={styles.metricData}>
            <div className={styles.metricLabel}>Total Extracted</div>
            <div className={styles.metricValue}>1,204 <span className={styles.metricUnit}>tasks</span></div>
          </div>
        </div>
        <div className={styles.metricCard}>
          <div className={styles.metricIconWrap} style={{ color: '#8B5CF6', background: 'rgba(139, 92, 246, 0.1)' }}>
            <Zap size={24} />
          </div>
          <div className={styles.metricData}>
            <div className={styles.metricLabel}>Avg. Agent Latency</div>
            <div className={styles.metricValue}>1.2 <span className={styles.metricUnit}>sec</span></div>
          </div>
        </div>
        <div className={styles.metricCard}>
          <div className={styles.metricIconWrap} style={{ color: '#3B82F6', background: 'rgba(59, 130, 246, 0.1)' }}>
            <CheckCircle size={24} />
          </div>
          <div className={styles.metricData}>
            <div className={styles.metricLabel}>Sync Accuracy</div>
            <div className={styles.metricValue}>99.8 <span className={styles.metricUnit}>%</span></div>
          </div>
        </div>
      </div>

      <div className={styles.mainGrid}>
        <div className={styles.leftCol}>
          <section className={styles.card}>
            <WorkflowForm
              onSubmit={onSubmit}
              isRunning={isRunning}
              pipeline={pipeline}
            />
          </section>

          {error && (
            <div className={styles.errorBanner} role="alert">
              <strong>Error:</strong> {error}
            </div>
          )}

          {result && (
            <section className={styles.card}>
              <ResultsPanel result={result} />
            </section>
          )}
        </div>

        <aside className={styles.rightCol} aria-label="Agent audit log">
          <section className={styles.card}>
            <div className={styles.panelHeader}>
              <div className={styles.panelIcon}>📡</div>
              <div>
                <div className={styles.panelTitle}>Agent Audit Log</div>
                <div className={styles.panelSub}>Real-time trace</div>
              </div>
            </div>
            <AuditLog entries={logs} />
          </section>
        </aside>
      </div>
    </div>
  )
}
