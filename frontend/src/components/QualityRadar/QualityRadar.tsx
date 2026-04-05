import React from 'react';
import styles from './QualityRadar.module.css';

/**
 * QualityRadar — Weekly Productivity/Health Dashboard.
 */
export const QualityRadar: React.FC = () => {
  const metrics = [
    { label: 'Deep Work', score: 85, color: '#4F46E5', desc: 'Focus blocks used effectively' },
    { label: 'Sleep / Rest', score: 72, color: '#0EA5E9', desc: 'Average 7h 12m' },
    { label: 'Activity', score: 45, color: '#F43F5E', desc: 'Under steps target' },
    { label: 'Learning', score: 90, color: '#10B981', desc: 'YouTube Capsules: 4/5' },
    { label: 'Social Sync', score: 60, color: '#F59E0B', desc: 'Meeting load heavy' }
  ];

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Quality Time Radar</h1>
        <p>Insights derived from Google Fit & Calendar telemetry.</p>
      </header>

      <div className={styles.grid}>
        <div className={styles.radarPlaceholder}>
           <div className={styles.ring} style={{ width: '85%', borderColor: metrics[0].color }} />
           <div className={styles.ring} style={{ width: '60%', borderColor: metrics[4].color }} />
           <div className={styles.ring} style={{ width: '45%', borderColor: metrics[2].color }} />
           <div className={styles.centerText}>82%</div>
        </div>

        <div className={styles.metricsList}>
          {metrics.map(m => (
            <div key={m.label} className={styles.metricItem}>
              <div className={styles.metricName}>{m.label}</div>
              <div className={styles.progressBar}>
                <div 
                  className={styles.pFill} 
                  style={{ width: `${m.score}%`, backgroundColor: m.color }} 
                />
              </div>
              <div className={styles.metricDesc}>{m.desc}</div>
            </div>
          ))}
        </div>
      </div>

      <div className={styles.rec}>
         <h3>Orchestrator Recommendations:</h3>
         <p>"Protect 2 extra morning focus blocks next week to recover from high meeting load."</p>
      </div>
    </div>
  );
};
