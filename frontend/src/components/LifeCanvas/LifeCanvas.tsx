import React, { useState, useEffect, useRef } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import { Activity, Battery, Target, Sparkles, Brain, Code, Dumbbell, Coffee } from 'lucide-react';
import styles from './LifeCanvas.module.css';

/**
 * LifeCanvas — Multi-track timeline cockpit.
 * =============================================================================
 * OrcheFlowAI 2026 — Immersive Glassmorphism Design System
 * =============================================================================
 */

const TRACE_DATA = [
  { time: '06:00', readiness: 45, focus: 20 },
  { time: '09:00', readiness: 95, focus: 80 },
  { time: '12:00', readiness: 85, focus: 90 },
  { time: '15:00', readiness: 60, focus: 75 },
  { time: '18:00', readiness: 40, focus: 45 },
  { time: '21:00', readiness: 20, focus: 15 },
];

const METRICS = [
  { name: 'Deep Work', value: 4.5, color: '#8B5CF6' },
  { name: 'Meetings', value: 2.5, color: '#3B82F6' },
  { name: 'Fitness', value: 1.5, color: '#10B981' },
];

export const LifeCanvas: React.FC = () => {
  const [calendar, setCalendar] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);
  const [commute, setCommute] = useState<any[]>([]);
  const [routeInfo] = useState<any>({ duration: '45 mins', summary: 'Hwy 101 N' });
  const [recommendations, setRecommendations] = useState<any[]>([]);
  
  const [logs, setLogs] = useState<{agent: string, msg: string, time: string}[]>([]);
  const logRef = useRef<HTMLDivElement>(null);

  const addLog = (agent: string, msg: string) => {
    setLogs(prev => [...prev, { 
      agent, 
      msg, 
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) 
    }].slice(-30));
  };


  useEffect(() => {
    addLog('Orchestrator', 'Swarm activated. Initializing parallel data extraction...');
    setTimeout(() => addLog('CalendarAgent', 'Scanning user schedules for current window...'), 500);
    setTimeout(() => {
      setCalendar([{ title: 'Hackathon Sync' }, { title: 'Code Review' }]);
      setTasks([{ title: 'Refactor Auth' }, { title: 'Implement GenUI' }]);
      setCommute([{ title: 'Return Trip' }]);
      addLog('CalendarAgent', `Sync complete. 2 events mapped.`);
      addLog('TaskAgent', `Prioritization complete. 2 items active.`);
    }, 1500);

    setTimeout(() => {
      addLog('NavigatorAgent', 'Calculating optimal office transit vectors...');
      addLog('NavigatorAgent', `Route locked: 45m travel time detected.`);
    }, 2500);

    setTimeout(() => {
      addLog('StrategistAgent', 'Analyzing local patterns for FLOW optimization...');
      setRecommendations([
        { title: 'Prime Coding Window', description: 'Your energy levels peak at 10 AM. Schedule the hardest Refactoring tasks then.', icon: 'Code', impact: 'High', score: 95 },
        { title: 'Afternoon Slump Mitigation', description: 'Take a 15m walk at 3 PM during the predicted cognitive dip before your next meeting.', icon: 'Coffee', impact: 'Medium', score: 82 },
        { title: 'Workout Re-routing', description: 'Traffic is heavy. Stop by the gym on Hwy 101 to let the congestion clear out.', icon: 'Dumbbell', impact: 'High', score: 88 }
      ]);
      addLog('StrategistAgent', 'Recommendation payload delivered to UI.');
    }, 3500);
  }, []);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);

  const renderSkeleton = () => <div className={styles.skeleton}></div>;

  const renderIcon = (name: string) => {
    switch (name) {
      case 'Code': return <Code size={24} color="#8B5CF6"/>;
      case 'Coffee': return <Coffee size={24} color="#F59E0B"/>;
      case 'Dumbbell': return <Dumbbell size={24} color="#10B981"/>;
      default: return <Brain size={24} color="#3B82F6"/>;
    }
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <h1>Life Canvas</h1>
          <div className={styles.headerPill}>OrcheFlow AI</div>
        </div>
        <div className={styles.agentBadge}>
          <span className={styles.pulseDot}></span>
          Agent Swarm: ACTIVE
        </div>
      </header>
      
      <div className={styles.mainView}>
        {/* TOP ROW: CHARTS */}
        <div className={styles.chartsGrid}>
          <div className={styles.chartCard}>
            <div className={styles.chartHeader}>
              <Battery size={18} />
              <span>Cognitive Readiness vs Focus</span>
            </div>
            <div className={styles.chartBody}>
              <ResponsiveContainer width="100%" height="100%" minHeight={0} minWidth={0}>
                <AreaChart data={TRACE_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorReadiness" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10B981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorFocus" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ background: '#111', border: '1px solid #333', borderRadius: '8px' }} />
                  <Area type="monotone" dataKey="readiness" stroke="#10B981" fillOpacity={1} fill="url(#colorReadiness)" strokeWidth={2} />
                  <Area type="monotone" dataKey="focus" stroke="#8B5CF6" fillOpacity={1} fill="url(#colorFocus)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className={styles.chartCard}>
            <div className={styles.chartHeader}>
              <Activity size={18} />
              <span>Activity Distribution (Hours)</span>
            </div>
            <div className={styles.chartBody}>
              <ResponsiveContainer width="100%" height="100%" minHeight={0} minWidth={0}>
                <BarChart data={METRICS} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} contentStyle={{ background: '#111', border: '1px solid #333', borderRadius: '8px' }} />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {METRICS.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* TIMELINE */}
        <div className={styles.timeline}>
          {/* TRACK: CALENDAR */}
          <section className={styles.track}>
            <div className={styles.trackLabel}>📅 CALENDAR</div>
            <div className={styles.trackContent}>
              {calendar.length > 0 ? calendar.map((ev, i) => (
                <div key={i} className={styles.event} style={{ left: `${(i*25)%70 + 5}%`, width: '18%' }}>
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
                <div key={i} className={styles.task} style={{ left: `${(i*22)%80 + 2}%` }}>
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
        </div>

        {/* GEMINI RECOMMENDATIONS */}
        <section className={styles.recommendations}>
          <h2 className={styles.aiHeading}>
            <Sparkles size={22} color="#8B5CF6"/>
            AI Synthesized Recommendations
          </h2>
          <div className={styles.recGrid}>
            {recommendations.length > 0 ? recommendations.map((rec, i) => (
              <div key={i} className={styles.recCard}>
                <div className={styles.recScore}>
                  <Target size={16} /> {rec.score}
                </div>
                <div className={styles.recIconWrap}>
                  {renderIcon(rec.icon)}
                </div>
                <div className={styles.recBody}>
                   <h3>{rec.title}</h3>
                   <p>{rec.description}</p>
                   <span className={styles.impactBadge} data-impact={rec.impact}>{rec.impact} Impact</span>
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
