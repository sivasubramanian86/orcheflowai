import React from 'react';
import styles from './Learning.module.css';

/**
 * Learning — YouTube Learning Capsules viewer.
 */
export const Learning: React.FC = () => {
  const capsules = [
    { title: 'System Design: Designing for Scale', topic: 'AI Infrastructure', duration: '25m', status: 'PLANNED', date: 'Yesterday' },
    { title: 'Google Fit REST API Basics', topic: 'Google Ecosystem', duration: '15m', status: 'COMPLETED', date: 'Today' },
    { title: 'AlloyDB vs PostgreSQL: Benchmarks', topic: 'Databases', duration: '20m', status: 'PLANNED', date: 'Tomorrow' }
  ];

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>YouTube Learning Capsules</h1>
        <p>Guided learning time-boxed around your focus periods.</p>
      </header>

      <div className={styles.grid}>
        {capsules.map(c => (
          <div key={c.title} className={styles.capsuleCard}>
            <div className={styles.capsuleStatus}>{c.status}</div>
            <div className={styles.capsuleTopic}>{c.topic}</div>
            <h2 className={styles.capsuleTitle}>{c.title}</h2>
            <div className={styles.capsuleMeta}>{c.duration} • {c.date}</div>
            <div className={styles.capsuleActions}>
              <button className={styles.btnPrimary}>Start Learning</button>
              <button className={styles.btnSecondary}>Reschedule</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
