import React, { useState, useEffect } from 'react';
import styles from './LifeCanvas.module.css';

/**
 * LifeCanvas — Multi-track timeline cockpit.
 * Shows Calendar, Tasks, Commute, and Health data.
 */
export const LifeCanvas: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const API_BASE = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetch(`${API_BASE}/v1/canvas/`)
      .then(res => res.json())
      .then(d => setData(d))
      .catch(e => console.error('Canvas load failed', e));
  }, [API_BASE]);

  if (!data) return <div className={styles.loading}>Initializing Workspace...</div>;

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Life Canvas</h1>
        <div className={styles.controls}>
          <button className={styles.btn}>Today</button>
          <button className={styles.btn}>Week</button>
        </div>
      </header>
      
      <div className={styles.timeline}>
        {/* Track: Google Calendar */}
        <section className={styles.track} aria-label="Calendar Events">
          <div className={styles.trackLabel}>📅 Calendar</div>
          <div className={styles.trackContent}>
            {data.events.map((ev: any, i: number) => (
              <div key={i} className={styles.event} style={{ left: `${(i*20)%80 + 5}%`, width: '15%' }}>
                {ev.summary || 'Meeting'}
              </div>
            ))}
          </div>
        </section>

        {/* Track: Tasks */}
        <section className={styles.track} aria-label="Tasks">
          <div className={styles.trackLabel}>✅ Tasks</div>
          <div className={styles.trackContent}>
            {data.tasks.map((t: any, i: number) => (
              <div key={i} className={styles.task} style={{ left: `${(i*25)%75 + 10}%` }}>
                {t.title}
              </div>
            ))}
          </div>
        </section>

        {/* Track: Commute */}
        <section className={styles.track} aria-label="Commute">
          <div className={styles.trackLabel}>🚗 Commute</div>
          <div className={styles.trackContent}>
            {data.commute && (
              <div className={styles.commute} style={{ left: '40%', width: '15%' }}>
                {data.commute.summary}
              </div>
            )}
          </div>
        </section>

        {/* Track: Health (Google Fit) */}
        <section className={styles.track} aria-label="Health Indicators">
          <div className={styles.trackLabel}>❤️ Health</div>
          <div className={styles.trackContent}>
             <div className={styles.healthBand}>
               Activity Score: {data.health.activity_score}% // Steps: {data.health.steps}
             </div>
          </div>
        </section>
      </div>
    </div>
  );
};
