-- ====================================================================
-- ULTRON: Supabase PostgreSQL Enterprise Schema
-- Run this in your Supabase Dashboard -> SQL Editor
-- ====================================================================

-- 1. Tenants Table
CREATE TABLE IF NOT EXISTS tenants (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  environment TEXT NOT NULL DEFAULT 'test' CHECK(environment IN ('test', 'live')),
  status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'SUSPENDED', 'REVOKED')),
  capacity_limit INTEGER NOT NULL DEFAULT 5,
  kill_switch_active BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Users Table
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
  mfa_secret TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Tenant Memberships
CREATE TABLE IF NOT EXISTS tenant_memberships (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK(role IN ('Owner', 'Admin', 'Operator', 'Analyst', 'Viewer')),
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_memberships_tenant ON tenant_memberships(tenant_id);
CREATE INDEX IF NOT EXISTS idx_memberships_user ON tenant_memberships(user_id);

-- 4. Tenant Credentials (Encrypted via AES-256-GCM)
CREATE TABLE IF NOT EXISTS tenant_credentials (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  provider TEXT NOT NULL,
  environment TEXT NOT NULL CHECK(environment IN ('test', 'live')),
  credential_reference TEXT NOT NULL,
  encrypted_blob TEXT NOT NULL,
  iv TEXT NOT NULL,
  auth_tag TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, credential_reference)
);

CREATE INDEX IF NOT EXISTS idx_credentials_tenant ON tenant_credentials(tenant_id);

-- 5. API Keys
CREATE TABLE IF NOT EXISTS api_keys (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  key_prefix TEXT NOT NULL,
  key_hash TEXT NOT NULL,
  scopes JSONB NOT NULL DEFAULT '["events:write", "opportunities:read"]'::jsonb,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  last_used_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_api_keys_tenant ON api_keys(tenant_id);

-- 6. Customers Table
CREATE TABLE IF NOT EXISTS customers (
  id TEXT PRIMARY KEY,
  merchant_id TEXT NOT NULL DEFAULT 'merchant_default',
  trust_score REAL NOT NULL DEFAULT 0.65,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Recovery Opportunities Table
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
  customer_id TEXT NOT NULL,
  customer_trust_score REAL NOT NULL DEFAULT 0.65,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status TEXT NOT NULL CHECK(status IN (
    'pending', 'scored', 'allocated', 'authorized', 'deferred', 'blocked', 'abstained', 'executing', 'recovered', 'not_recovered'
  )),
  razorpay_event_id TEXT UNIQUE,
  raw_payload_ref TEXT
);

CREATE INDEX IF NOT EXISTS idx_opps_tenant ON recovery_opportunities(tenant_id);
CREATE INDEX IF NOT EXISTS idx_opps_status ON recovery_opportunities(status);
CREATE INDEX IF NOT EXISTS idx_opps_created ON recovery_opportunities(created_at DESC);

-- 8. Scores Table
CREATE TABLE IF NOT EXISTS scores (
  opportunity_id TEXT PRIMARY KEY REFERENCES recovery_opportunities(id) ON DELETE CASCADE,
  natural_recovery_prob REAL NOT NULL,
  intervention_recovery_prob REAL NOT NULL,
  incremental_prob REAL NOT NULL,
  operational_cost_paise BIGINT NOT NULL,
  fatigue_cost_paise BIGINT NOT NULL,
  expected_incremental_value_paise BIGINT NOT NULL,
  confidence TEXT NOT NULL CHECK(confidence IN ('low', 'medium', 'high'))
);

-- 9. Allocation Decisions Table
CREATE TABLE IF NOT EXISTS allocation_decisions (
  opportunity_id TEXT PRIMARY KEY REFERENCES recovery_opportunities(id) ON DELETE CASCADE,
  decision TEXT NOT NULL CHECK(decision IN ('ACT', 'WAIT', 'ABSTAIN')),
  rank_in_batch INTEGER NOT NULL,
  shadow_price_paise_at_decision BIGINT NOT NULL,
  reason TEXT NOT NULL
);

-- 10. Authority Checks Table
CREATE TABLE IF NOT EXISTS authority_checks (
  id BIGSERIAL PRIMARY KEY,
  opportunity_id TEXT NOT NULL REFERENCES recovery_opportunities(id) ON DELETE CASCADE,
  check_name TEXT NOT NULL,
  passed BOOLEAN NOT NULL,
  reason TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_authority_opp ON authority_checks(opportunity_id);

-- 11. Execution Records Table
CREATE TABLE IF NOT EXISTS execution_records (
  opportunity_id TEXT PRIMARY KEY REFERENCES recovery_opportunities(id) ON DELETE CASCADE,
  razorpay_payment_link_id TEXT NOT NULL,
  link_url TEXT NOT NULL,
  status TEXT NOT NULL,
  idempotency_key TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 12. Ledger Entries Table
CREATE TABLE IF NOT EXISTS ledger_entries (
  id TEXT PRIMARY KEY,
  opportunity_id TEXT NOT NULL REFERENCES recovery_opportunities(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL CHECK(event_type IN (
    'webhook_received', 'reconciled', 'recovered', 'not_recovered'
  )),
  amount_paise BIGINT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  raw_payload_ref TEXT
);

CREATE INDEX IF NOT EXISTS idx_ledger_opp ON ledger_entries(opportunity_id);

-- 13. Audit Records Table
CREATE TABLE IF NOT EXISTS audit_records (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL DEFAULT 'tenant_system_default',
  actor_id TEXT NOT NULL,
  actor_type TEXT NOT NULL CHECK(actor_type IN ('USER', 'API_KEY', 'SYSTEM')),
  action TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  resource_id TEXT NOT NULL,
  payload JSONB,
  ip_address TEXT,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_tenant ON audit_records(tenant_id);

-- 14. Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  token_hash TEXT NOT NULL,
  role TEXT NOT NULL,
  ip_address TEXT,
  user_agent TEXT,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  revoked_at TIMESTAMPTZ
);

-- Enable Supabase Realtime for live dashboard updates
ALTER PUBLICATION supabase_realtime ADD TABLE recovery_opportunities;
ALTER PUBLICATION supabase_realtime ADD TABLE ledger_entries;
