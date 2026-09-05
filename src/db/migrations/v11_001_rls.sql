-- ==============================================================================
-- ULTRON V11: Row-Level Security (RLS) & Multi-Tenant Data Isolation
-- Migration: v11_001_rls.sql
-- ==============================================================================

-- 1. Enable RLS on core opportunity & economic tables
ALTER TABLE IF EXISTS recovery_opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS allocation_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS execution_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ledger_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS double_entry_ledger ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS audit_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS agent_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS outreach_drafts ENABLE ROW LEVEL SECURITY;

-- 2. Tenant isolation policies with service-role bypass
-- Service role key / superuser has full access. Standard tenant requests must match current tenant.

-- Helper function to extract current tenant context
CREATE OR REPLACE FUNCTION current_app_tenant_id() RETURNS TEXT AS $$
BEGIN
    RETURN NULLIF(current_setting('app.current_tenant_id', true), '');
END;
$$ LANGUAGE plpgsql STABLE;

-- Recovery Opportunities Policy
DROP POLICY IF EXISTS tenant_isolation_recovery_opportunities ON recovery_opportunities;
CREATE POLICY tenant_isolation_recovery_opportunities ON recovery_opportunities
    FOR ALL
    USING (
        current_app_tenant_id() IS NULL 
        OR tenant_id = current_app_tenant_id()
    )
    WITH CHECK (
        current_app_tenant_id() IS NULL 
        OR tenant_id = current_app_tenant_id()
    );

-- Audit Records Policy
DROP POLICY IF EXISTS tenant_isolation_audit_records ON audit_records;
CREATE POLICY tenant_isolation_audit_records ON audit_records
    FOR ALL
    USING (
        current_app_tenant_id() IS NULL 
        OR tenant_id = current_app_tenant_id()
    )
    WITH CHECK (
        current_app_tenant_id() IS NULL 
        OR tenant_id = current_app_tenant_id()
    );

-- Outreach Drafts Policy
DROP POLICY IF EXISTS tenant_isolation_outreach_drafts ON outreach_drafts;
CREATE POLICY tenant_isolation_outreach_drafts ON outreach_drafts
    FOR ALL
    USING (
        current_app_tenant_id() IS NULL 
        OR tenant_id = current_app_tenant_id()
    )
    WITH CHECK (
        current_app_tenant_id() IS NULL 
        OR tenant_id = current_app_tenant_id()
    );
