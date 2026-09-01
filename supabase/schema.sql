-- ==============================================================================
-- ULTRON: Master Supabase (PostgreSQL) Production Schema
-- Autonomous Economic Control Plane for Failed-Payment Recovery on Razorpay
-- ==============================================================================

-- Enable UUID extension if required
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Multi-Tenancy & Access Control
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    environment TEXT NOT NULL CHECK(environment IN ('live', 'test')),
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'SUSPENDED', 'PENDING')),
    capacity_limit INTEGER NOT NULL DEFAULT 5,
    kill_switch_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS organizations (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    mfa_secret TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS memberships (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK(role IN ('Viewer', 'Analyst', 'Operator', 'Admin', 'Owner')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, tenant_id)
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS api_keys (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    key_prefix TEXT NOT NULL,
    key_id TEXT NOT NULL UNIQUE,
    secret_hash TEXT NOT NULL,
    environment TEXT NOT NULL CHECK(environment IN ('live', 'test')),
    scopes TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS audit_records (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    actor_id TEXT NOT NULL,
    actor_type TEXT NOT NULL CHECK(actor_type IN ('USER', 'API_KEY', 'SYSTEM', 'AGENT')),
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    payload JSONB,
    ip_address TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tenant_credentials (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    environment TEXT NOT NULL CHECK(environment IN ('live', 'test')),
    credential_reference TEXT NOT NULL UNIQUE,
    encrypted_data TEXT NOT NULL,
    iv TEXT NOT NULL,
    auth_tag TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. Core Economic Recovery Pipeline
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL DEFAULT 'tenant_system_default',
    merchant_id TEXT NOT NULL DEFAULT 'merchant_default',
    trust_score NUMERIC(4, 3) NOT NULL DEFAULT 0.650,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS recovery_opportunities (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL DEFAULT 'tenant_system_default',
    merchant_id TEXT NOT NULL DEFAULT 'merchant_default',
    source TEXT NOT NULL CHECK(source IN ('real', 'synthetic')),
    amount_paise BIGINT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',
    reason_code TEXT NOT NULL,
    decline_type TEXT NOT NULL CHECK(decline_type IN ('hard', 'soft', 'unknown')),
    attempt_count INTEGER NOT NULL DEFAULT 1,
    customer_id TEXT NOT NULL REFERENCES customers(id),
    customer_trust_score NUMERIC(4, 3) NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'scored', 'allocated', 'deferred', 'blocked', 'abstained', 'executing', 'recovered', 'not_recovered')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS scores (
    opportunity_id TEXT PRIMARY KEY REFERENCES recovery_opportunities(id) ON DELETE CASCADE,
    tenant_id TEXT NOT NULL DEFAULT 'tenant_system_default',
    natural_recovery_prob NUMERIC(5, 4) NOT NULL,
    intervention_recovery_prob NUMERIC(5, 4) NOT NULL,
    incremental_prob NUMERIC(5, 4) NOT NULL,
    operational_cost_paise BIGINT NOT NULL,
    fatigue_cost_paise BIGINT NOT NULL,
    expected_incremental_value_paise BIGINT NOT NULL,
    confidence TEXT NOT NULL CHECK(confidence IN ('low', 'medium', 'high')),
    scored_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS allocation_decisions (
    opportunity_id TEXT PRIMARY KEY REFERENCES recovery_opportunities(id) ON DELETE CASCADE,
    tenant_id TEXT NOT NULL DEFAULT 'tenant_system_default',
    decision TEXT NOT NULL CHECK(decision IN ('ACT', 'WAIT', 'ABSTAIN')),
    rank_in_batch INTEGER NOT NULL,
    shadow_price_paise_at_decision BIGINT NOT NULL,
    reason TEXT NOT NULL,
    allocated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS authority_checks (
    id BIGSERIAL PRIMARY KEY,
    opportunity_id TEXT NOT NULL REFERENCES recovery_opportunities(id) ON DELETE CASCADE,
    tenant_id TEXT NOT NULL DEFAULT 'tenant_system_default',
    check_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    reason TEXT NOT NULL,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS execution_records (
    opportunity_id TEXT PRIMARY KEY REFERENCES recovery_opportunities(id) ON DELETE CASCADE,
    tenant_id TEXT NOT NULL DEFAULT 'tenant_system_default',
    razorpay_payment_link_id TEXT,
    link_url TEXT,
    status TEXT NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ledger_entries (
    id BIGSERIAL PRIMARY KEY,
    opportunity_id TEXT NOT NULL REFERENCES recovery_opportunities(id) ON DELETE CASCADE,
    tenant_id TEXT NOT NULL DEFAULT 'tenant_system_default',
    event_type TEXT NOT NULL CHECK(event_type IN ('webhook_received', 'reconciled', 'recovered', 'not_recovered', 'audit')),
    amount_paise BIGINT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    raw_payload_ref TEXT
);

CREATE TABLE IF NOT EXISTS double_entry_ledger (
    id BIGSERIAL PRIMARY KEY,
    opportunity_id TEXT NOT NULL REFERENCES recovery_opportunities(id) ON DELETE CASCADE,
    tenant_id TEXT NOT NULL DEFAULT 'tenant_system_default',
    debit_account TEXT NOT NULL,
    credit_account TEXT NOT NULL,
    amount_paise BIGINT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    description TEXT
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. AI Agent Specialist Subsystem
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS agent_runs (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL DEFAULT 'tenant_system_default',
    opportunity_id TEXT NOT NULL REFERENCES recovery_opportunities(id) ON DELETE CASCADE,
    mission_id TEXT,
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS agent_memories (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL DEFAULT 'tenant_system_default',
    key TEXT NOT NULL,
    value JSONB NOT NULL,
    agent_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS outreach_drafts (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL DEFAULT 'tenant_system_default',
    opportunity_id TEXT NOT NULL REFERENCES recovery_opportunities(id) ON DELETE CASCADE,
    channel TEXT NOT NULL CHECK(channel IN ('EMAIL', 'WHATSAPP', 'SMS')),
    subject TEXT,
    content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING_REVIEW' CHECK(status IN ('PENDING_REVIEW', 'APPROVED', 'REJECTED', 'DISPATCHED')),
    compliance_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS schema_migrations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    checksum TEXT NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    execution_time_ms INTEGER NOT NULL
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. Indexes for Performance & Partition Isolation
-- ─────────────────────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_tenants_slug ON tenants(slug);
CREATE INDEX IF NOT EXISTS idx_memberships_user ON memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_memberships_tenant ON memberships(tenant_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token_hash ON sessions(token_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_id ON api_keys(key_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_tenant ON api_keys(tenant_id);
CREATE INDEX IF NOT EXISTS idx_audit_tenant ON audit_records(tenant_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_records(timestamp);
CREATE INDEX IF NOT EXISTS idx_opportunities_tenant ON recovery_opportunities(tenant_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_status ON recovery_opportunities(status);
CREATE INDEX IF NOT EXISTS idx_scores_tenant ON scores(tenant_id);
CREATE INDEX IF NOT EXISTS idx_authority_opp ON authority_checks(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_ledger_opp ON ledger_entries(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_double_entry_opp ON double_entry_ledger(opportunity_id);
