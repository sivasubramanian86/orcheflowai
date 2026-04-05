import React from 'react'
import styles from './FAQ.module.css'

export const FAQ: React.FC = () => {
  const faqs = [
    {
      q: "What is an 'Agentic Mesh'?",
      a: "An Agentic Mesh is a distributed network of specialized AI agents that can reason about complex tasks, share context, and execute tools autonomously. In OrcheFlowAI, this mesh is coordinated by a central Orchestrator that uses Gemini 2.5 Flash as its brain."
    },
    {
      q: "How does OrcheFlowAI access my data?",
      a: "We use the Model Context Protocol (MCP) to securely connect to your tools (Calendar, Tasks, Notes). The agents only access the data you explicitly authorize, and all sensitive operations require your final approval."
    },
    {
      q: "What is Google ADK?",
      a: "The Agent Development Kit (ADK) is the framework we use to manage the lifecycle, security, and communication of our agents. It ensures that every agent follows strict safety policies and operates within the bounds of your intent."
    },
    {
      q: "Is my data stored or used for training?",
      a: "No. OrcheFlowAI leverages Vertex AI which ensures that your data is never used to train foundational models. Your workflows and meeting notes remain private to your enterprise instance."
    },
    {
      q: "Can I add my own custom tools?",
      a: "Yes! Because we follow the MCP standard, any tool that implements the MCP server protocol can be plugged into OrcheFlowAI. You can extend the system's capabilities to include your own internal databases or APIs."
    }
  ]

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>Frequently Asked Questions</h1>
        <p className={styles.subtitle}>Everything you need to know about the OrcheFlowAI ecosystem.</p>
      </header>

      <div className={styles.list}>
        {faqs.map((faq, idx) => (
          <details key={idx} className={styles.item}>
            <summary className={styles.question}>
              {faq.q}
              <span className={styles.chevron}>↓</span>
            </summary>
            <div className={styles.answer}>
              <p>{faq.a}</p>
            </div>
          </details>
        ))}
      </div>

      <footer className={styles.cta}>
         <p>Still have questions? Reach out to the <a href="mailto:support@orcheflow.ai">OrcheFlowAI Dev Team</a>.</p>
      </footer>
    </div>
  )
}
