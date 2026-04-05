import { useState } from 'react'
import { useWorkflow } from '@/hooks/useWorkflow'
import { Sidebar, ViewType } from '@/components/Sidebar/Sidebar'
import { Dashboard } from '@/components/Dashboard/Dashboard'
import { About }     from '@/components/About/About'
import { FAQ }       from '@/components/FAQ/FAQ'
import { Settings }  from '@/components/Settings/Settings'
import styles from './App.module.css'

/**
 * App — Root Orchestrator. 
 * Manages the top-level navigation, sidebar layout, and view switching.
 */
export function App() {
  const [activeView, setActiveView] = useState<ViewType>('dashboard')
  const { isRunning, pipeline, logs, result, error, submit } = useWorkflow()

  const renderView = () => {
    switch (activeView) {
      case 'dashboard':
        return (
          <Dashboard 
            isRunning={isRunning} 
            pipeline={pipeline} 
            logs={logs} 
            result={result} 
            error={error} 
            onSubmit={submit} 
          />
        )
      case 'about':
        return <About />
      case 'faq':
        return <FAQ />
      case 'settings':
        return <Settings />
      default:
        return <Dashboard 
          isRunning={isRunning} 
          pipeline={pipeline} 
          logs={logs} 
          result={result} 
          error={error} 
          onSubmit={submit} 
        />
    }
  }

  return (
    <div className={styles.appShell}>
      <a href="#main-content" className="skip-nav">Skip to content</a>
      
      <Sidebar activeView={activeView} onViewChange={setActiveView} />

      <main id="main-content" className={styles.stage}>
        {renderView()}
      </main>
    </div>
  )
}
