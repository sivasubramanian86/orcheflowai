import React, { useState, useEffect } from 'react';
import styles from './AppHeader.module.css';

/**
 * AppHeader — Top navigation bar with Mode Switch and User Context.
 */
export const AppHeader: React.FC = () => {
  const [activeMode, setActiveMode] = useState<'FOCUS' | 'SOCIAL' | 'RECOVERY'>('FOCUS');
  const [user, setUser] = useState<{connected: boolean, name?: string, email?: string} | null>(null);
  const API_BASE = '/v1';
  
  // Sync mode and connection with backend on load
  useEffect(() => {
    fetch(`${API_BASE}/modes/`)
      .then(res => res.json())
      .then(data => setActiveMode(data.active_mode))
      .catch(() => console.log('Using default FOCUS mode'));

    fetch(`${API_BASE}/auth/google/status`)
       .then(res => res.json())
       .then(data => setUser(data))
       .catch(() => {});
  }, [API_BASE]);

  const handleModeChange = async (newMode: 'FOCUS' | 'SOCIAL' | 'RECOVERY') => {
    setActiveMode(newMode);
    try {
      await fetch(`${API_BASE}/modes/update`, {
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
        <div className={styles.logoContainer}>
          <div className={styles.logoIcon}>💓</div>
          <div className={styles.logoText}>OrcheFlowAI</div>
        </div>
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
        {user?.connected ? (
          <div className={styles.userBadge}>
            <div className={styles.avatar}>{user.name?.[0] || 'U'}</div>
            <span>{user.name || user.email}</span>
            <button 
              className={styles.miniBtn}
              onClick={() => window.location.href = `${API_BASE}/auth/google/login`}
            >
              Switch Account
            </button>
          </div>
        ) : (
          <button 
            className={styles.googleSync}
            onClick={() => window.location.href = `${API_BASE}/auth/google/login`}
          >
            <img src="https://www.gstatic.com/images/branding/product/1x/gsa_512dp.png" alt="G" style={{width:16, marginRight:8}} />
            Sign in with Google
          </button>
        )}
      </div>
    </header>
  );
};
