# OrcheFlowAI — Hackathon Demo Script (4-minute target)
# Based on skill-04: Hackathon Demo Pipeline
# Audience: Gen AI Academy APAC Judges

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[0:00 – 0:40] THE HOOK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPOKEN:
"The average knowledge worker switches context 23 times a day. By 9 AM, they already have
unread meeting notes, a backlog of tasks with no deadlines, and a calendar that has 0
breathing room.

We built OrcheFlowAI — a multi-agent AI system that takes your raw meeting notes and,
in seconds, extracts action items, creates prioritised tasks, and blocks your deep-work
time — without you writing a single to-do manually."

ON SCREEN: OrcheFlowAI logo + tagline: "Orchestrate your flow. Let agents do the rest."
GOAL: Establish the pain point before showing the solution.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[0:40 – 1:20] THE WOW MOMENT (show the result first)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPOKEN:
"Here's OrcheFlowAI completing a full Q2 planning workflow from a single API call.
I'm posting raw meeting notes — 15 lines of unstructured text — and watching four
specialist agents coordinate in real time."

ON SCREEN:
  Terminal showing:
    curl -X POST https://orcheflow-api-xxxxx-uc.a.run.app/v1/workflow/run \
      -d '{"intent": "Convert Q2 planning notes to tasks and block focus time", ...}'

  Live streaming response showing:
    "plan_executed": ["ingest_notes", "create_tasks", "find_calendar_gaps", "block_time"]
    "tasks_created": [ 5 tasks with priorities ]
    "calendar_blocks": [ 2-hour focus block tomorrow morning ]
    "status": "COMPLETED"

GOAL: Show the agent mesh working end-to-end within 30 seconds. Judges see real output.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1:20 – 2:45] ARCHITECTURE DEEP DIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPOKEN:
"Let me show you what's powering this. OrcheFlowAI uses a 3-tier microservices
architecture deployed on Google Cloud Run."

ON SCREEN: Architecture diagram —

  ┌─────────────────────────────────────────────────────────────────┐
  │                    OrcheFlowAI Architecture                     │
  ├─────────────────────────────────────────────────────────────────┤
  │  USER / CLIENT                                                  │
  │       │  POST /v1/workflow/run                                  │
  │       ▼                                                         │
  │  [API Service — FastAPI]  Cloud Run                             │
  │       │  dispatch                                               │
  │       ▼                                                         │
  │  [Agent Service — Google ADK]  Cloud Run                        │
  │       │                                                         │
  │       ├──[Orchestrator]──gemini-2.5-flash (Vertex AI)          │
  │       │        │ sub-agent delegation                           │
  │       │        ├──[Notes Agent]────gemini-2.0-flash            │
  │       │        ├──[Task Agent]─────gemini-2.0-flash            │
  │       │        ├──[Schedule Agent]─gemini-2.0-flash            │
  │       │        └──[Workflow Agent]─gemini-2.0-flash            │
  │       │                                                         │
  │       ▼  MCP Tool Protocol                                      │
  │  [MCP Server]  Cloud Run                                        │
  │       ├── notes_manager (create, extract, search)               │
  │       ├── task_manager (CRUD, prioritize)                       │
  │       └── calendar_manager (events, gaps, block)                │
  │                │                                                │
  │                ▼                                                │
  │  [AlloyDB / PostgreSQL + pgvector]                              │
  │  Tasks · Notes · Calendar Events · Audit Log · Agent Memory     │
  └─────────────────────────────────────────────────────────────────┘

SPOKEN (continued):
"The key innovation: every sub-agent is a proper Google ADK Agent with its own
system prompt and specialist tools. The orchestrator uses ADK's sub_agents delegation
pattern — the Gemini 2.5 Flash LLM decides, at runtime, which sub-agent to call
and in what order.

MCP (Model Context Protocol) is the tool layer — a standard protocol that lets any
agent call any tool without tight coupling. Today it's PostgreSQL; in production you
swap in Google Calendar API, Jira, Salesforce — same interface, same agent code.

All Gemini calls go through Vertex AI Model Garden under project genai-apac-2026-491004
using Application Default Credentials — no API keys anywhere in the system."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[2:45 – 3:45] LIVE DEMO — STEP BY STEP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPOKEN (narrate each action):
"Step 1: I'm posting raw Q2 meeting notes — straight copy-paste, no formatting."
[ACTION: Show sample_inputs/meeting_notes.txt in terminal]

"Step 2: Watch the audit trail — every agent action is logged in real time."
[ACTION: GET /v1/audit — show 8-10 log entries streaming in with agent_name, action, latency_ms]

"Step 3: Here are the 5 tasks created — with priorities automatically assigned
based on deadline proximity and explicit urgency signals in the notes."
[ACTION: GET /v1/tasks — show prioritised task list]

"Step 4: The Schedule Agent found a 2-hour gap tomorrow morning at 9 AM
and created a focus block labelled 'OrcheFlow Focus: Review API contract'."
[ACTION: GET /v1/schedule/gaps — show the blocked slot]

"Step 5: And the full workflow run — every step, every sub-agent call, every
tool invocation — is fully auditable."
[ACTION: GET /v1/workflow/runs/{id}/steps — show step-by-step trace]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[3:45 – 4:15] SCALING + CLOSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPOKEN:
"OrcheFlowAI is live on Cloud Run today. To scale this to enterprise:

  - Add async workflow execution via Pub/Sub for non-blocking processing
  - Swap mock calendar tools for live Google Calendar API via MCP
  - Enable pgvector semantic search in AlloyDB for AI-powered note retrieval
  - Rate-limit and monetize as an API-as-a-service at $X per 1,000 workflows

OrcheFlowAI is open for collaboration — full code at github.com/[your-handle]/orcheflow.
The architecture is intentionally MCP-first, which means any enterprise data source
becomes a plug-in. This is how AI-native productivity should work."

ON SCREEN: GitHub URL + Architecture one-pager
GOAL: Leave judges with a clear path to production and the mental model of MCP extensibility.

---

# Pre-Demo Checklist
- [ ] docker-compose up -d — all 3 services green
- [ ] Schema migrated — V001 applied, pgvector enabled
- [ ] GOOGLE_CLOUD_PROJECT=genai-apac-2026-491004 in .env
- [ ] gcloud auth application-default login completed
- [ ] sample_inputs/meeting_notes.txt ready in terminal
- [ ] Postman / curl aliases ready for each demo step
- [ ] Pre-recorded 60-second fallback video ready (skill-04 rule)

# One-Liner Pitch
"OrcheFlowAI uses Google ADK's multi-agent orchestration and Vertex AI's Gemini 2.5
to convert raw meeting notes into prioritised tasks and calendar blocks — fully
audited, MCP-extensible, and deployed on Cloud Run in under 4 minutes."
