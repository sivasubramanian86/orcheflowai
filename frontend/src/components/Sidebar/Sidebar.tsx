import React from 'react'
import styles from './Sidebar.module.css'

export type ViewType = 'life-canvas' | 'dashboard' | 'run-explorer' | 'quality-radar' | 'learning' | 'about' | 'faq' | 'settings';

interface SidebarProps {
  activeView: ViewType;
  onViewChange: (view: ViewType) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeView, onViewChange }) => {
  const menuItems = [
    { id: 'life-canvas', label: 'Life Canvas', icon: '🗓️' },
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'run-explorer', label: 'Run Explorer', icon: '🔍' },
    { id: 'quality-radar', label: 'Quality Radar', icon: '🎯' },
    { id: 'learning', label: 'Learning', icon: '📺' },
    { id: 'about', label: 'About', icon: '✨' },
    { id: 'faq', label: 'FAQ', icon: '❓' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
  ] as const;

  return (
    <nav className={styles.sidebar} aria-label="Main Navigation">
      <div className={styles.logoContainer}>
        <div className={styles.logoIcon}>⚡</div>
        <div className={styles.logoText}>OrcheFlow</div>
      </div>

      <ul className={styles.menu}>
        {menuItems.map((item) => (
          <li key={item.id}>
            <button
              className={`${styles.menuItem} ${activeView === item.id ? styles.active : ''}`}
              onClick={() => onViewChange(item.id)}
              aria-current={activeView === item.id ? 'page' : undefined}
            >
              <span className={styles.icon} aria-hidden="true">{item.icon}</span>
              <span className={styles.label}>{item.label}</span>
            </button>
          </li>
        ))}
      </ul>

      <div className={styles.footer}>
        <div className={styles.vTag}>v1.0.0-2026</div>
      </div>
    </nav>
  )
}
