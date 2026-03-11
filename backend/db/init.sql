-- Intelli-Credit PostgreSQL Schema
-- Run this once on a fresh database

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── Sessions ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions (
    session_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    borrower_name   VARCHAR(255),
    cin             VARCHAR(50),
    gstin           VARCHAR(20),
    loan_amount_cr  NUMERIC(10, 2),
    loan_type       VARCHAR(100),
    status          VARCHAR(50) DEFAULT 'INITIATED',
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- ─── Risk Flags (Module 1 → all downstream) ──────────────────────────────────
CREATE TABLE IF NOT EXISTS risk_flags (
    flag_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    flag_type       VARCHAR(100) NOT NULL,
    severity        VARCHAR(10) CHECK (severity IN ('HIGH', 'MEDIUM', 'LOW')),
    source_document VARCHAR(255),
    evidence_snippet TEXT,
    page_reference  VARCHAR(50),
    source_module   VARCHAR(50) CHECK (source_module IN ('STRUCTURED', 'RAG', 'RESEARCH', 'QUALITATIVE')),
    five_c_pillar   VARCHAR(5),   -- C1..C5
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_risk_flags_session ON risk_flags(session_id);
CREATE INDEX IF NOT EXISTS idx_risk_flags_severity ON risk_flags(severity);

-- ─── Research Flags (Module 2) ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS research_flags (
    flag_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    source          VARCHAR(100),     -- MCA21, e-Courts, NCLT, Web
    finding         TEXT NOT NULL,
    severity        VARCHAR(10) CHECK (severity IN ('HIGH', 'MEDIUM', 'LOW')),
    date_discovered DATE DEFAULT CURRENT_DATE,
    url             TEXT,
    raw_data        JSONB,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_research_flags_session ON research_flags(session_id);

-- ─── Qualitative Inputs (Human-in-the-Loop) ──────────────────────────────────
CREATE TABLE IF NOT EXISTS qualitative_inputs (
    input_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id            UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    officer_id            VARCHAR(100),
    factory_utilisation   INTEGER,       -- 0-100
    management_impression VARCHAR(50),   -- Confident/Mixed/Evasive
    promoter_reputation   VARCHAR(50),   -- Strong/Neutral/Concerning
    site_visit_notes      TEXT,
    other_observations    TEXT,
    parsed_adjustments    JSONB,         -- LLM-parsed score deltas
    total_score_delta     NUMERIC(5, 2),
    created_at            TIMESTAMP DEFAULT NOW()
);

-- ─── Jury Results ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jury_results (
    result_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id              UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    base_score              NUMERIC(5, 2),
    jury_score              NUMERIC(5, 2),
    c1_score                NUMERIC(5, 2),
    c2_score                NUMERIC(5, 2),
    c3_score                NUMERIC(5, 2),
    c4_score                NUMERIC(5, 2),
    c5_score                NUMERIC(5, 2),
    prosecution_findings    JSONB,
    defence_findings        JSONB,
    adjudication            JSONB,
    final_recommendation    VARCHAR(20),  -- APPROVE/CONDITIONAL/REJECT
    recommended_amount_cr   NUMERIC(10, 2),
    interest_rate_pct       NUMERIC(5, 2),
    loan_tenor_months       INTEGER,
    created_at              TIMESTAMP DEFAULT NOW()
);
