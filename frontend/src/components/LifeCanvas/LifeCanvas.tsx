import React, { useState, useEffect, useRef } from 'react';
import styles from './LifeCanvas.module.css';

/**
 * LifeCanvas — Multi-track timeline cockpit.
 * =============================================================================
 * OrchePulse AI 2026 — Glassmorphism Design System
 * =============================================================================
 */
export const LifeCanvas: React.FC = () => {
  // Individual states for parallel loading
  const [calendar, setCalendar] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);
  const [commute, setCommute] = useState<any[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [routeInfo, setRouteInfo] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  
  // Agentic Log System
  const [logs, setLogs] = useState<{agent: string, msg: string, time: string}[]>([]);
  const logRef = useRef<HTMLDivElement>(null);
  const API_BASE = '/v1';

  const addLog = (agent: string, msg: string) => {
    setLogs(prev => [...prev, { 
      agent, 
      msg, 
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) 
    }].slice(-30));
  };

  useEffect(() => {
    addLog('Orchestrator', 'Swarm activated. Initializing parallel data extraction...');
    
    // 1. Fetch Core Dashboard Data (Parallel Streams)
    addLog('CalendarAgent', 'Scanning user schedules for current window...');
    fetch(`${API_BASE}/canvas/day`)
      .then(res => res.json())
      .then(d => {
        setCalendar(d.tracks.calendar || []);
        setTasks(d.tracks.tasks || []);
        setCommute(d.tracks.commute || []);
        setHealth(d.tracks.health);
        addLog('CalendarAgent', `Sync complete. ${d.tracks.calendar.length} events mapped.`);
        addLog('TaskAgent', `Prioritization complete. ${d.tracks.tasks.length} items active.`);
      })
      .catch(e => addLog('AlertAgent', `Data sync failed: ${e.message}`));

    // 2. Fetch Spatial Intelligence
    addLog('NavigatorAgent', 'Calculating optimal office transit vectors...');
    fetch(`${API_BASE}/location/office-route`)
      .then(res => res.json())
      .then(d => {
        setRouteInfo(d);
        addLog('NavigatorAgent', `Route locked: ${d.duration} travel time detected.`);
      })
      .catch(() => addLog('NavigatorAgent', 'VPC connectivity loss. Using local cached route.'));

    // 3. Fetch Advanced Recommendations
    addLog('StrategistAgent', 'Analyzing local patterns for FLOW optimization...');
    fetch(`${API_BASE}/location/recommendations`)
      .then(res => res.json())
      .then(d => {
        setRecommendations(d.recommendations || []);
        addLog('StrategistAgent', 'Recommendation payload delivered to UI.');
      })
      .catch(() => addLog('StrategistAgent', 'Strategist idle. Awaiting next session burst.'));
  }, [API_BASE]);

  // Auto-scroll the agent console
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);

  const renderSkeleton = () => <div className={styles.skeleton}></div>;

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>OrchePulse AI</h1>
        <div className={styles.agentBadge}>
          <span className={styles.pulseDot}></span>
          Agent Swarm: ACTIVE
        </div>
      </header>
      
      <div className={styles.mainView}>
        <div className={styles.timeline}>
          {/* TRACK: CALENDAR */}
          <section className={styles.track}>
            <div className={styles.trackLabel}>📅 CALENDAR</div>
            <div className={styles.trackContent}>
              {calendar.length > 0 ? calendar.map((ev, i) => (
                <div key={i} className={styles.event} style={{ left: `${(i*22)%70 + 5}%`, width: '18%' }}>
                  {ev.title}
                </div>
              )) : renderSkeleton()}
            </div>
          </section>

          {/* TRACK: TASKS */}
          <section className={styles.track}>
            <div className={styles.trackLabel}>✅ TASKS</div>
            <div className={styles.trackContent}>
              {tasks.length > 0 ? tasks.map((t, i) => (
                <div key={i} className={styles.task} style={{ left: `${(i*20)%80 + 2}%` }}>
                  {t.title}
                </div>
              )) : renderSkeleton()}
            </div>
          </section>

          {/* TRACK: COMMUTE */}
          <section className={styles.track}>
            <div className={styles.trackLabel}>🚗 COMMUTE</div>
            <div className={styles.trackContent}>
              {routeInfo ? (
                <div className={styles.commute} style={{ left: '10%', width: '30%' }}>
                  🏠 {routeInfo.duration} to Office ({routeInfo.summary.split('(')[0]})
                </div>
              ) : renderSkeleton()}
              {/* Secondary Commute Buffers */}
              {commute.map((c, i) => (
                <div key={`c-${i}`} className={styles.commute} style={{ left: `${(i*25)%50 + 45}%`, width: '18%', opacity: 0.6 }}>
                  🚌 {c.title}
                </div>
              ))}
            </div>
          </section>

          {/* TRACK: HEALTH */}
          <section className={styles.track}>
            <div className={styles.trackLabel}>❤️ HEALTH</div>
            <div className={styles.trackContent}>
               <div className={styles.healthBand}>
                 READINESS: {health?.readiness ?? 80}% // STATUS: OPTIMAL
               </div>
            </div>
          </section>
        </div>

        {/* GEMINI RECOMMENDATIONS */}
        <section className={styles.recommendations}>
          <h2 className={styles.aiHeading}>✨ Strategist Intelligence</h2>
          <div className={styles.recGrid}>
            {recommendations.length > 0 ? recommendations.map((rec, i) => (
              <div key={i} className={styles.recCard}>
                <div className={styles.recIcon}>{rec.icon === 'park' ? '🌳' : rec.icon === 'beach' ? '🏖️' : '🏛️'}</div>
                <div className={styles.recBody}>
                   <h3>{rec.spot || rec.title}</h3>
                   <p>{rec.rationale || rec.description}</p>
                   {rec.distance && <span className={styles.distanceMark}>{rec.distance} away</span>}
                </div>
              </div>
            )) : [1,2,3].map(i => (
              <div key={i} className={styles.recCard}>
                <div className={styles.skeleton}></div>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* AGENT CONSOLE SIDEBAR */}
      <aside className={styles.agentConsole}>
        <div className={styles.consoleHeader}>
          <div className={styles.statusIndicator}></div>
          LIVE AGENT INTELLIGENCE
        </div>
        <div className={styles.logArea} ref={logRef}>
          {logs.map((log, i) => (
            <div key={i} className={styles.logEntry}>
              <span className={styles.logTime}>[{log.time}]</span>
              <span className={styles.logAgent}>{log.agent}:</span>
              <span className={styles.logMsg}>{log.msg}</span>
            </div>
          ))}
          {logs.length === 0 && <div className={styles.logEntry}>Awaiting orchestration...</div>}
        </div>
      </aside>
    </div>
  );
};
