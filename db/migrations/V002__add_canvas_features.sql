-- OrcheFlowAI — V002: Add Canvas features
-- Adds support for UserModes, HealthSnapshots, LearningCapsules, and CommuteSegments.

-- 1. USER MODES (Personality configuration)
CREATE TABLE user_modes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    active_mode     TEXT CHECK (active_mode IN ('FOCUS','SOCIAL','RECOVERY')) DEFAULT 'FOCUS',
    constraints     JSONB DEFAULT '{}',
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- 2. HEALTH SNAPSHOTS (Google Fit Integration)
CREATE TABLE health_snapshots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    timestamp       TIMESTAMPTZ DEFAULT NOW(),
    steps           INTEGER DEFAULT 0,
    calories        INTEGER DEFAULT 0,
    heart_rate_avg  INTEGER,
    sleep_minutes   INTEGER,
    activity_score  INTEGER CHECK (activity_score BETWEEN 0 AND 100),
    metadata        JSONB DEFAULT '{}'
);
CREATE INDEX idx_health_user_time ON health_snapshots(user_id, timestamp DESC);

-- 3. LEARNING CAPSULES (YouTube Research Integration)
CREATE TABLE learning_capsules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    video_id        TEXT NOT NULL,
    title           TEXT NOT NULL,
    url             TEXT NOT NULL,
    topic           TEXT,
    duration_minutes INTEGER DEFAULT 30,
    status          TEXT CHECK (status IN ('PLANNED','COMPLETED','SKIPPED')) DEFAULT 'PLANNED',
    scheduled_event_id UUID REFERENCES calendar_events(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 4. COMMUTE SEGMENTS (Maps Predictive Integration)
CREATE TABLE commute_segments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    event_id        UUID REFERENCES calendar_events(id),
    origin          JSONB, -- { "lat": ..., "lng": ..., "name": ... }
    destination     JSONB,
    mode            TEXT CHECK (mode IN ('DRIVING','TRANSIT','WALKING','BICYCLING')) DEFAULT 'DRIVING',
    distance_meters INTEGER,
    duration_seconds INTEGER,
    predicted_delay INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Insert Demo User if not exists
INSERT INTO users (id, email, display_name) 
VALUES ('01948576-a3b2-7c6d-9e0f-1a2b3c4d5e6f', 'sivasubramanian86@hotmail.com', 'Sivasubramanian')
ON CONFLICT (email) DO NOTHING;

-- Initial Mode for Demo User
INSERT INTO user_modes (user_id, active_mode)
VALUES ('01948576-a3b2-7c6d-9e0f-1a2b3c4d5e6f', 'FOCUS')
ON CONFLICT (user_id) DO NOTHING;
