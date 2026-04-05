import React from 'react'
import { ThemeToggle } from '@/components/ThemeToggle/ThemeToggle'
import styles from './Settings.module.css'

export const Settings: React.FC = () => {
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>System Settings</h1>
        <p className={styles.subtitle}>Configure your OrcheFlowAI experience.</p>
      </header>

      <section className={styles.group}>
        <h2 className={styles.h2}>Interface Appearance</h2>
        <div className={styles.row}>
           <div className={styles.info}>
              <div className={styles.label}>Theme Mode</div>
              <div className={styles.description}>Switch between light and dark mode manually or sync with system.</div>
           </div>
           <ThemeToggle />
        </div>
      </section>

      <section className={styles.group}>
        <h2 className={styles.h2}>AI Model Configuration</h2>
        <div className={styles.row}>
           <div className={styles.info}>
              <div className={styles.label}>Model Selection</div>
              <div className={styles.description}>The orchestrator uses Gemini 2.5 Flash by default for high speed.</div>
           </div>
           <select className={styles.select} disabled>
              <option>Gemini 2.5 Flash (Recommended)</option>
              <option>Gemini 1.5 Pro (Precision Mode)</option>
              <option>Claude 3.5 Sonnet (External Bridge)</option>
           </select>
        </div>
      </section>

      <section className={styles.group}>
        <h2 className={styles.h2}>MCP Integrations</h2>
        <div className={styles.row}>
           <div className={styles.info}>
              <div className={styles.label}>Tool Connectivity</div>
              <div className={styles.description}>Manage connected services like Google Workspace, GitHub, and JIRA.</div>
           </div>
           <button className={styles.button} disabled>Manager Connections</button>
        </div>
      </section>

      <footer className={styles.footer}>
         <p>Settings are stored locally for the demo instance.</p>
      </footer>
    </div>
  )
}
