-- OrcheFlowAI — Initial Database Schema
-- Compatible with AlloyDB (Postgres 15+) and Cloud SQL Postgres
-- Run pgvector extension first

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── USERS ─────────────────────────────────────────────────────────
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT UNIQUE NOT NULL,
    display_name    TEXT,
    timezone        TEXT DEFAULT 'UTC',
    preferences     JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── SESSIONS ──────────────────────────────────────────────────────
CREATE TABLE sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    jwt_jti         TEXT UNIQUE NOT NULL,
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── TASKS ─────────────────────────────────────────────────────────
CREATE TABLE tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    title           TEXT NOT NULL,
    description     TEXT,
    status          TEXT CHECK (status IN ('TODO','IN_PROGRESS','BLOCKED','DONE')) DEFAULT 'TODO',
    priority        INTEGER CHECK (priority BETWEEN 1 AND 5) DEFAULT 3,
    due_date        DATE,
    tags            TEXT[] DEFAULT '{}',
    source_note_id  UUID,
    source_event_id UUID,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- ─── NOTES ─────────────────────────────────────────────────────────
CREATE TABLE notes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    title           TEXT,
    content         TEXT NOT NULL,
    content_type    TEXT CHECK (content_type IN ('MEETING','IDEA','REFERENCE','JOURNAL')) DEFAULT 'REFERENCE',
    tags            TEXT[] DEFAULT '{}',
    embedding       VECTOR(768),
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notes_user ON notes(user_id);
CREATE INDEX idx_notes_embedding ON notes USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- ─── CALENDAR EVENTS ───────────────────────────────────────────────
CREATE TABLE calendar_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    external_id     TEXT,
    title           TEXT NOT NULL,
    start_time      TIMESTAMPTZ NOT NULL,
    end_time        TIMESTAMPTZ NOT NULL,
    event_type      TEXT CHECK (event_type IN ('MEETING','FOCUS_BLOCK','PERSONAL','DEADLINE')) DEFAULT 'MEETING',
    attendees       JSONB DEFAULT '[]',
    notes_id        UUID REFERENCES notes(id),
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_user_time ON calendar_events(user_id, start_time);

-- ─── WORKFLOW RUNS ──────────────────────────────────────────────────
CREATE TABLE workflow_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    idempotency_key TEXT UNIQUE,
    intent          TEXT NOT NULL,
    plan            JSONB,
    status          TEXT CHECK (status IN ('PENDING','RUNNING','COMPLETED','FAILED','PARTIAL')) DEFAULT 'PENDING',
    input_payload   JSONB DEFAULT '{}',
    output_summary  TEXT,
    error_details   JSONB,
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    total_tokens    INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_workflow_runs_user ON workflow_runs(user_id, created_at DESC);
CREATE INDEX idx_workflow_runs_idempotency ON workflow_runs(idempotency_key);

-- ─── WORKFLOW STEPS ─────────────────────────────────────────────────
CREATE TABLE workflow_steps (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID REFERENCES workflow_runs(id) ON DELETE CASCADE,
    step_index      INTEGER NOT NULL,
    step_name       TEXT NOT NULL,
    agent_name      TEXT NOT NULL,
    status          TEXT CHECK (status IN ('PENDING','RUNNING','DONE','FAILED','SKIPPED')) DEFAULT 'PENDING',
    input_context   JSONB,
    output_result   JSONB,
    error_message   TEXT,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    retry_count     INTEGER DEFAULT 0
);

CREATE INDEX idx_workflow_steps_run ON workflow_steps(run_id, step_index);

-- ─── AGENT AUDIT LOG (append-only) ─────────────────────────────────
CREATE TABLE agent_audit_log (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID REFERENCES workflow_runs(id),
    step_id         UUID REFERENCES workflow_steps(id),
    agent_name      TEXT NOT NULL,
    action          TEXT NOT NULL,
    details         JSONB,
    tokens_used     INTEGER,
    logged_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ─── TOOL CALL LOG ──────────────────────────────────────────────────
CREATE TABLE tool_call_log (
    id              BIGSERIAL PRIMARY KEY,
    step_id         UUID REFERENCES workflow_steps(id),
    tool_name       TEXT NOT NULL,
    tool_input      JSONB,
    tool_output     JSONB,
    success         BOOLEAN NOT NULL,
    error_code      TEXT,
    latency_ms      INTEGER,
    called_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ─── PLANS ──────────────────────────────────────────────────────────
CREATE TABLE plans (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    run_id          UUID REFERENCES workflow_runs(id),
    plan_type       TEXT CHECK (plan_type IN ('DAILY','WEEKLY','PROJECT','ADHOC')) DEFAULT 'ADHOC',
    title           TEXT,
    content         JSONB NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── MEMORY SNAPSHOTS ───────────────────────────────────────────────
CREATE TABLE memory_snapshots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    snapshot_type   TEXT CHECK (snapshot_type IN ('SESSION','DAILY','WEEKLY')) DEFAULT 'SESSION',
    summary         TEXT,
    raw_context     JSONB,
    embedding       VECTOR(768),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
