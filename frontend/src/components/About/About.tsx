import React from 'react'
import styles from './About.module.css'

export const About: React.FC = () => {
  return (
    <div className={styles.container}>
      <header className={styles.hero}>
        <div className={styles.badge}>✦ THE VISION 2026</div>
        <h1 className={styles.title}>Unified Agent Orchestration</h1>
        <p className={styles.subtitle}>
          OrcheFlowAI is the next-generation productivity hub that transforms 
          the chaos of multi-channel communication into a streamlined, 
          prioritized workflow using an autonomous <strong>Agent Mesh</strong>.
        </p>
      </header>

      <section className={styles.grid}>
        <div className={styles.card}>
          <div className={styles.cardIcon}>🤖</div>
          <h3>Gemini-Powered Intelligence</h3>
          <p>Leveraging Vertex AI's Gemini 2.5 Flash for context-aware notes extraction and high-speed task generation.</p>
        </div>
        <div className={styles.card}>
          <div className={styles.cardIcon}>📐</div>
          <h3>Google ADK Native</h3>
          <p>Built with the Google Agent Development Kit for robust, sovereign agent lifecycle management and secure tool execution.</p>
        </div>
        <div className={styles.card}>
          <div className={styles.cardIcon}>🛠️</div>
          <h3>Universal MCP Integration</h3>
          <p>Connecting to your world via Model Context Protocol — from Google Calendar to enterprise task managers.</p>
        </div>
      </section>

      <section className={styles.imageSection}>
         <div className={styles.imageOverlay}>
            <h2>Orchestrate, don't just automate.</h2>
            <p>Our agentic mesh doesn't just run scripts; it observes, reasons, and acts across your ecosystem.</p>
         </div>
         {/* Using the generated high-end viz */}
         <img 
           src="/images/mesh-viz.png" 
           alt="Conceptual visualization of OrcheFlow agentic mesh" 
           className={styles.meshViz}
         />
      </section>

      <section className={styles.howItWorks}>
        <h2 className={styles.h2}>How it Works</h2>
        <div className={styles.steps}>
          <div className={styles.step}>
             <div className={styles.stepNum}>01</div>
             <p><strong>Ingest:</strong> Feed meeting transcripts, napkin sketches, or voice notes into the secure API.</p>
          </div>
          <div className={styles.step}>
             <div className={styles.stepNum}>02</div>
             <p><strong>Decompose:</strong> The Orchestrator agent breaks down the intent into parallel sub-tasks.</p>
          </div>
          <div className={styles.step}>
             <div className={styles.stepNum}>03</div>
             <p><strong>Execute:</strong> Specialized agents use MCP tools to update calendars, CRMs, or JIRA.</p>
          </div>
          <div className={styles.step}>
             <div className={styles.stepNum}>04</div>
             <p><strong>Review:</strong> Human-in-the-loop review ensures every automated action meets your quality bar.</p>
          </div>
        </div>
      </section>
    </div>
  )
}
