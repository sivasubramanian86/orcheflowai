import React, { useState, useEffect } from 'react';
import styles from './AppHeader.module.css';

/**
 * AppHeader — Top navigation bar with Mode Switch and User Context.
 */
export const AppHeader: React.FC = () => {
  const [activeMode, setActiveMode] = useState<'FOCUS' | 'SOCIAL' | 'RECOVERY'>('FOCUS');
  const API_BASE = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

  // Sync mode with backend on load
  useEffect(() => {
    fetch(`${API_BASE}/v1/modes/`)
      .then(res => res.json())
      .then(data => setActiveMode(data.active_mode))
      .catch(() => console.log('Using default FOCUS mode'));
  }, [API_BASE]);

  const handleModeChange = async (newMode: 'FOCUS' | 'SOCIAL' | 'RECOVERY') => {
    setActiveMode(newMode);
    try {
      await fetch(`${API_BASE}/v1/modes/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: newMode })
      });
    } catch (e) {
      console.error('Failed to sync mode', e);
    }
  };

  return (
    <header className={styles.appHeader}>
      <div className={styles.left}>
        <span className={styles.breadcrumb}> APAC // 2026 // OrcheFlow </span>
      </div>

      <div className={styles.center}>
        <div className={styles.modeSwitch}>
          {(['FOCUS', 'SOCIAL', 'RECOVERY'] as const).map(m => (
            <button
              key={m}
              className={`${styles.modeBtn} ${activeMode === m ? styles.active : ''} ${styles[m.toLowerCase()]}`}
              onClick={() => handleModeChange(m)}
            >
               {m}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.right}>
        <div className={styles.userBadge}>
          <div className={styles.avatar}>S</div>
          <span>Sivasubramanian</span>
        </div>
      </div>
    </header>
  );
};
