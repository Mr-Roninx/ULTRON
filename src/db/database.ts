import { DatabaseSync } from 'node:sqlite';
import path from 'node:path';
import {
  RecoveryOpportunity,
  Score,
  AllocationDecision,
  AuthorityCheck,
  ExecutionRecord,
  LedgerEntry,
  Customer,
  OpportunityStatus,
} from '../types/index.js';
import {
  AgentRunRecord,
  AgentStateRecord,
  AgentStepRecord,
  AgentToolCallRecord,
  AgentPlanRecord,
  AgentHypothesisRecord,
  AgentProposalRecord,
  AgentMemoryItem,
  AgentOutcomeRecord,
  AgentAuthorityCheckRecord,
  LLMInvocationRecord,
  OutreachDraftRecord,
  PerceptionAnnotationRecord,
} from '../agents/types.js';

const DB_PATH = process.env.DATABASE_PATH || path.resolve(process.cwd(), 'ultron.db');

export const db = new DatabaseSync(DB_PATH);

export function initDatabase(): void {
  // Enable WAL mode & foreign keys
  db.exec(`
    PRAGMA journal_mode = WAL;
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS customers (
      id TEXT PRIMARY KEY,
      merchant_id TEXT NOT NULL DEFAULT 'merchant_default',
      trust_score REAL NOT NULL DEFAULT 0.65,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS recovery_opportunities (
      id TEXT PRIMARY KEY,
      merchant_id TEXT NOT NULL DEFAULT 'merchant_default',
      source TEXT NOT NULL CHECK(source IN ('real', 'synthetic')),
      amount_paise INTEGER NOT NULL,
      currency TEXT NOT NULL DEFAULT 'INR',
      reason_code TEXT NOT NULL,
      decline_type TEXT NOT NULL CHECK(decline_type IN ('hard', 'soft', 'unknown')),
      attempt_count INTEGER NOT NULL DEFAULT 1,
      customer_id TEXT NOT NULL,
      customer_trust_score REAL NOT NULL DEFAULT 0.65,
      created_at TEXT NOT NULL,
      status TEXT NOT NULL CHECK(status IN (
        'pending', 'scored', 'allocated', 'authorized', 'deferred', 'blocked', 'abstained', 'executing', 'recovered', 'not_recovered'
      )),
      razorpay_event_id TEXT UNIQUE,
      raw_payload_ref TEXT
    );
  `);

  try {
    db.exec(`ALTER TABLE customers ADD COLUMN merchant_id TEXT NOT NULL DEFAULT 'merchant_default';`);
  } catch (e) {
    // column exists
  }

  try {
    db.exec(`ALTER TABLE recovery_opportunities ADD COLUMN merchant_id TEXT NOT NULL DEFAULT 'merchant_default';`);
  } catch (e) {
    // column exists
  }

  db.exec(`

    CREATE INDEX IF NOT EXISTS idx_opportunities_source ON recovery_opportunities(source);
    CREATE INDEX IF NOT EXISTS idx_opportunities_status ON recovery_opportunities(status);
    CREATE INDEX IF NOT EXISTS idx_opportunities_customer ON recovery_opportunities(customer_id);
    CREATE INDEX IF NOT EXISTS idx_opportunities_rzp_event ON recovery_opportunities(razorpay_event_id);

    CREATE TABLE IF NOT EXISTS scores (
      opportunity_id TEXT PRIMARY KEY,
      natural_recovery_prob REAL NOT NULL,
      intervention_recovery_prob REAL NOT NULL,
      incremental_prob REAL NOT NULL,
      operational_cost_paise INTEGER NOT NULL,
      fatigue_cost_paise INTEGER NOT NULL,
      expected_incremental_value_paise INTEGER NOT NULL,
      confidence TEXT NOT NULL CHECK(confidence IN ('low', 'medium', 'high')),
      FOREIGN KEY (opportunity_id) REFERENCES recovery_opportunities(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS allocation_decisions (
      opportunity_id TEXT PRIMARY KEY,
      decision TEXT NOT NULL CHECK(decision IN ('ACT', 'WAIT', 'ABSTAIN')),
      rank_in_batch INTEGER NOT NULL,
      shadow_price_paise_at_decision INTEGER NOT NULL,
      reason TEXT NOT NULL,
      FOREIGN KEY (opportunity_id) REFERENCES recovery_opportunities(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS authority_checks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      opportunity_id TEXT NOT NULL,
      check_name TEXT NOT NULL,
      passed INTEGER NOT NULL CHECK(passed IN (0, 1)),
      reason TEXT NOT NULL,
      FOREIGN KEY (opportunity_id) REFERENCES recovery_opportunities(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_authority_opp_id ON authority_checks(opportunity_id);

    CREATE TABLE IF NOT EXISTS execution_records (
      opportunity_id TEXT PRIMARY KEY,
      razorpay_payment_link_id TEXT NOT NULL,
      link_url TEXT NOT NULL,
      status TEXT NOT NULL,
      idempotency_key TEXT NOT NULL UNIQUE,
      created_at TEXT NOT NULL,
      FOREIGN KEY (opportunity_id) REFERENCES recovery_opportunities(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS ledger_entries (
      id TEXT PRIMARY KEY,
      opportunity_id TEXT NOT NULL,
      event_type TEXT NOT NULL CHECK(event_type IN (
        'webhook_received', 'reconciled', 'recovered', 'not_recovered'
      )),
      amount_paise INTEGER NOT NULL,
      timestamp TEXT NOT NULL,
      raw_payload_ref TEXT,
      FOREIGN KEY (opportunity_id) REFERENCES recovery_opportunities(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_ledger_opp_id ON ledger_entries(opportunity_id);

    -- ========================================================
    -- AGENT SYSTEM TABLES
    -- ========================================================

    CREATE TABLE IF NOT EXISTS agent_runs (
      id TEXT PRIMARY KEY,
      mission_id TEXT NOT NULL,
      opportunity_id TEXT,
      goal_type TEXT NOT NULL,
      status TEXT NOT NULL CHECK(status IN ('running', 'completed', 'aborted', 'human_review')),
      start_time TEXT NOT NULL,
      end_time TEXT,
      total_steps INTEGER NOT NULL DEFAULT 0,
      llm_calls INTEGER NOT NULL DEFAULT 0,
      tool_calls INTEGER NOT NULL DEFAULT 0,
      replan_count INTEGER NOT NULL DEFAULT 0,
      total_tokens INTEGER NOT NULL DEFAULT 0,
      latency_ms INTEGER NOT NULL DEFAULT 0,
      termination_reason TEXT,
      created_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_agent_runs_opp ON agent_runs(opportunity_id);
    CREATE INDEX IF NOT EXISTS idx_agent_runs_status ON agent_runs(status);

    CREATE TABLE IF NOT EXISTS agent_states (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      run_id TEXT NOT NULL,
      state TEXT NOT NULL,
      previous_state TEXT,
      trigger TEXT NOT NULL,
      metadata TEXT,
      timestamp TEXT NOT NULL,
      FOREIGN KEY (run_id) REFERENCES agent_runs(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_agent_states_run ON agent_states(run_id);

    CREATE TABLE IF NOT EXISTS agent_steps (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      run_id TEXT NOT NULL,
      step_number INTEGER NOT NULL,
      state TEXT NOT NULL,
      observation TEXT,
      thought TEXT,
      action_type TEXT,
      action_payload TEXT,
      tool_name TEXT,
      tool_input TEXT,
      tool_output TEXT,
      timestamp TEXT NOT NULL,
      FOREIGN KEY (run_id) REFERENCES agent_runs(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_agent_steps_run ON agent_steps(run_id);

    CREATE TABLE IF NOT EXISTS agent_tool_calls (
      id TEXT PRIMARY KEY,
      run_id TEXT NOT NULL,
      tool_name TEXT NOT NULL,
      agent_name TEXT NOT NULL,
      input_payload TEXT NOT NULL,
      input_hash TEXT NOT NULL,
      output_payload TEXT NOT NULL,
      output_hash TEXT NOT NULL,
      status TEXT NOT NULL CHECK(status IN ('SUCCESS', 'DENIED', 'FAILED', 'TIMEOUT')),
      latency_ms INTEGER NOT NULL DEFAULT 0,
      error_message TEXT,
      permission_level TEXT NOT NULL,
      created_at TEXT NOT NULL,
      FOREIGN KEY (run_id) REFERENCES agent_runs(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_tool_calls_run ON agent_tool_calls(run_id);

    CREATE TABLE IF NOT EXISTS agent_plans (
      id TEXT PRIMARY KEY,
      run_id TEXT NOT NULL,
      plan_version INTEGER NOT NULL DEFAULT 1,
      goal TEXT NOT NULL,
      steps TEXT NOT NULL,
      validity_assumptions TEXT NOT NULL,
      candidate_actions TEXT NOT NULL,
      preferred_action TEXT NOT NULL,
      status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INVALIDATED', 'EXECUTED', 'SUPERSEDED')),
      invalidation_reason TEXT,
      created_at TEXT NOT NULL,
      FOREIGN KEY (run_id) REFERENCES agent_runs(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_agent_plans_run ON agent_plans(run_id);

    CREATE TABLE IF NOT EXISTS agent_hypotheses (
      id TEXT PRIMARY KEY,
      run_id TEXT NOT NULL,
      failure_category TEXT NOT NULL,
      root_cause_hypothesis TEXT NOT NULL,
      confidence REAL NOT NULL,
      supporting_evidence TEXT NOT NULL,
      created_at TEXT NOT NULL,
      FOREIGN KEY (run_id) REFERENCES agent_runs(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS agent_proposals (
      id TEXT PRIMARY KEY,
      run_id TEXT NOT NULL,
      opportunity_id TEXT NOT NULL,
      proposal_type TEXT NOT NULL,
      payload TEXT NOT NULL,
      status TEXT NOT NULL CHECK(status IN ('PENDING', 'ACCEPTED', 'REJECTED', 'SUPERSEDED')),
      review_notes TEXT,
      created_at TEXT NOT NULL,
      FOREIGN KEY (run_id) REFERENCES agent_runs(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_agent_proposals_opp ON agent_proposals(opportunity_id);

    CREATE TABLE IF NOT EXISTS agent_memories (
      id TEXT PRIMARY KEY,
      memory_type TEXT NOT NULL CHECK(memory_type IN ('working', 'episodic', 'semantic')),
      run_id TEXT,
      opportunity_id TEXT,
      failure_type TEXT,
      context_summary TEXT NOT NULL,
      action_taken TEXT,
      predicted_outcome TEXT,
      actual_outcome TEXT,
      prediction_error REAL,
      semantic_key TEXT,
      semantic_value TEXT,
      confidence REAL NOT NULL DEFAULT 0.8,
      provenance TEXT NOT NULL,
      created_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_agent_memories_type ON agent_memories(memory_type);
    CREATE INDEX IF NOT EXISTS idx_agent_memories_created ON agent_memories(created_at);
    CREATE INDEX IF NOT EXISTS idx_agent_memories_opp ON agent_memories(opportunity_id);

    CREATE TABLE IF NOT EXISTS agent_outcomes (
      id TEXT PRIMARY KEY,
      run_id TEXT NOT NULL,
      opportunity_id TEXT NOT NULL,
      predicted_recovery_prob REAL NOT NULL,
      actual_recovered INTEGER NOT NULL CHECK(actual_recovered IN (0, 1)),
      prediction_error REAL NOT NULL,
      actual_revenue_paise INTEGER NOT NULL,
      operational_cost_paise INTEGER NOT NULL,
      net_gain_paise INTEGER NOT NULL,
      customer_response TEXT,
      evaluated_at TEXT NOT NULL,
      FOREIGN KEY (run_id) REFERENCES agent_runs(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_agent_outcomes_opp ON agent_outcomes(opportunity_id);

    CREATE TABLE IF NOT EXISTS agent_authority_checks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      run_id TEXT NOT NULL,
      tool_name TEXT NOT NULL,
      agent_name TEXT NOT NULL,
      check_name TEXT NOT NULL,
      passed INTEGER NOT NULL CHECK(passed IN (0, 1)),
      reason TEXT NOT NULL,
      timestamp TEXT NOT NULL,
      FOREIGN KEY (run_id) REFERENCES agent_runs(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_agent_auth_run ON agent_authority_checks(run_id);

    CREATE TABLE IF NOT EXISTS llm_invocations (
      id TEXT PRIMARY KEY,
      run_id TEXT NOT NULL,
      model TEXT NOT NULL,
      provider TEXT NOT NULL,
      prompt_hash TEXT NOT NULL,
      prompt_preview TEXT NOT NULL,
      completion_hash TEXT NOT NULL,
      completion_preview TEXT NOT NULL,
      reasoning_preview TEXT,
      latency_ms INTEGER NOT NULL,
      prompt_tokens INTEGER NOT NULL DEFAULT 0,
      completion_tokens INTEGER NOT NULL DEFAULT 0,
      total_tokens INTEGER NOT NULL DEFAULT 0,
      error TEXT,
      created_at TEXT NOT NULL,
      FOREIGN KEY (run_id) REFERENCES agent_runs(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_llm_invocations_run ON llm_invocations(run_id);

    CREATE TABLE IF NOT EXISTS outreach_drafts (
      id TEXT PRIMARY KEY,
      run_id TEXT NOT NULL,
      opportunity_id TEXT NOT NULL,
      channel TEXT NOT NULL CHECK(channel IN ('SMS', 'WHATSAPP', 'EMAIL')),
      recipient TEXT NOT NULL,
      subject TEXT,
      body TEXT NOT NULL,
      compliance_footer TEXT NOT NULL,
      status TEXT NOT NULL CHECK(status IN ('PENDING_REVIEW', 'APPROVED', 'REJECTED')),
      review_feedback TEXT,
      created_at TEXT NOT NULL,
      FOREIGN KEY (run_id) REFERENCES agent_runs(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_outreach_drafts_opp ON outreach_drafts(opportunity_id);

    CREATE TABLE IF NOT EXISTS perception_annotations (
      id TEXT PRIMARY KEY,
      opportunity_id TEXT NOT NULL,
      failure_intent TEXT NOT NULL,
      customer_urgency_score REAL NOT NULL,
      merchant_risk_score REAL NOT NULL,
      semantic_notes TEXT NOT NULL,
      confidence REAL NOT NULL,
      created_at TEXT NOT NULL,
      FOREIGN KEY (opportunity_id) REFERENCES recovery_opportunities(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_perception_annotations_opp ON perception_annotations(opportunity_id);
  `);
}

// Initial execution
initDatabase();

// Customers queries
export function getCustomerById(id: string): Customer | undefined {
  const stmt = db.prepare('SELECT * FROM customers WHERE id = ?');
  return stmt.get(id) as unknown as Customer | undefined;
}

export function getOrCreateCustomer(id: string, defaultTrustScore: number = 0.65): Customer {
  const existing = getCustomerById(id);
  if (existing) {
    return existing;
  }

  const now = new Date().toISOString();
  const insertStmt = db.prepare(`
    INSERT INTO customers (id, trust_score, created_at, updated_at)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET updated_at = excluded.updated_at
  `);
  insertStmt.run(id, defaultTrustScore, now, now);

  return {
    id,
    trust_score: defaultTrustScore,
    created_at: now,
    updated_at: now,
  };
}

export function upsertCustomer(customer: Customer): void {
  const stmt = db.prepare(`
    INSERT INTO customers (id, trust_score, created_at, updated_at)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
      trust_score = excluded.trust_score,
      updated_at = excluded.updated_at
  `);
  stmt.run(customer.id, customer.trust_score, customer.created_at, customer.updated_at);
}

export function countPriorAttempts(customerId: string, rawPayloadSubstring?: string): number {
  if (rawPayloadSubstring) {
    const stmt = db.prepare(`
      SELECT COUNT(*) as count FROM recovery_opportunities 
      WHERE customer_id = ? OR raw_payload_ref LIKE ?
    `);
    const res = stmt.get(customerId, `%${rawPayloadSubstring}%`) as { count: number };
    return res?.count || 0;
  }

  const stmt = db.prepare('SELECT COUNT(*) as count FROM recovery_opportunities WHERE customer_id = ?');
  const res = stmt.get(customerId) as { count: number };
  return res?.count || 0;
}

// Opportunity queries
export function getOpportunityById(id: string): RecoveryOpportunity | undefined {
  const stmt = db.prepare('SELECT * FROM recovery_opportunities WHERE id = ?');
  return stmt.get(id) as unknown as RecoveryOpportunity | undefined;
}

export function getOpportunityByRazorpayEventId(eventId: string): RecoveryOpportunity | undefined {
  const stmt = db.prepare('SELECT * FROM recovery_opportunities WHERE razorpay_event_id = ?');
  return stmt.get(eventId) as unknown as RecoveryOpportunity | undefined;
}

export function getAllOpportunities(tenantId?: string): RecoveryOpportunity[] {
  if (tenantId) {
    const stmt = db.prepare('SELECT * FROM recovery_opportunities WHERE tenant_id = ? OR merchant_id = ? ORDER BY created_at DESC');
    return stmt.all(tenantId, tenantId) as unknown as RecoveryOpportunity[];
  }
  const stmt = db.prepare('SELECT * FROM recovery_opportunities ORDER BY created_at DESC');
  return stmt.all() as unknown as RecoveryOpportunity[];
}

export function insertOpportunity(opp: RecoveryOpportunity): void {
  const stmt = db.prepare(`
    INSERT INTO recovery_opportunities (
      id, source, amount_paise, currency, reason_code, decline_type,
      attempt_count, customer_id, customer_trust_score, created_at, status,
      tenant_id, razorpay_event_id, raw_payload_ref
    ) VALUES (
      ?, ?, ?, ?, ?, ?,
      ?, ?, ?, ?, ?,
      ?, ?, ?
    )
  `);
  stmt.run(
    opp.id,
    opp.source,
    opp.amount_paise,
    opp.currency || 'INR',
    opp.reason_code,
    opp.decline_type,
    opp.attempt_count ?? 1,
    opp.customer_id,
    opp.customer_trust_score ?? 0.65,
    opp.created_at || new Date().toISOString(),
    opp.status || 'pending',
    opp.tenant_id || 'tenant_default',
    opp.razorpay_event_id || null,
    opp.raw_payload_ref || null
  );
}

export function upsertOpportunity(opp: RecoveryOpportunity): void {
  const stmt = db.prepare(`
    INSERT INTO recovery_opportunities (
      id, source, amount_paise, currency, reason_code, decline_type,
      attempt_count, customer_id, customer_trust_score, created_at, status,
      razorpay_event_id, raw_payload_ref
    ) VALUES (
      ?, ?, ?, ?, ?, ?,
      ?, ?, ?, ?, ?,
      ?, ?
    )
    ON CONFLICT(id) DO UPDATE SET
      source = excluded.source,
      amount_paise = excluded.amount_paise,
      currency = excluded.currency,
      reason_code = excluded.reason_code,
      decline_type = excluded.decline_type,
      attempt_count = excluded.attempt_count,
      customer_id = excluded.customer_id,
      customer_trust_score = excluded.customer_trust_score,
      status = excluded.status,
      razorpay_event_id = excluded.razorpay_event_id,
      raw_payload_ref = excluded.raw_payload_ref
  `);
  stmt.run(
    opp.id,
    opp.source,
    opp.amount_paise,
    opp.currency || 'INR',
    opp.reason_code,
    opp.decline_type,
    opp.attempt_count ?? 1,
    opp.customer_id,
    opp.customer_trust_score ?? 0.65,
    opp.created_at || new Date().toISOString(),
    opp.status || 'pending',
    opp.razorpay_event_id || null,
    opp.raw_payload_ref || null
  );
}

export function updateOpportunityStatus(id: string, status: OpportunityStatus): void {
  const stmt = db.prepare('UPDATE recovery_opportunities SET status = ? WHERE id = ?');
  stmt.run(status, id);
}

// Scores queries
export function getScoreByOpportunityId(opportunityId: string): Score | undefined {
  const stmt = db.prepare('SELECT * FROM scores WHERE opportunity_id = ?');
  return stmt.get(opportunityId) as unknown as Score | undefined;
}

export function upsertScore(score: Score): void {
  const stmt = db.prepare(`
    INSERT INTO scores (
      opportunity_id, natural_recovery_prob, intervention_recovery_prob, incremental_prob,
      operational_cost_paise, fatigue_cost_paise, expected_incremental_value_paise, confidence
    ) VALUES (
      ?, ?, ?, ?,
      ?, ?, ?, ?
    )
    ON CONFLICT(opportunity_id) DO UPDATE SET
      natural_recovery_prob = excluded.natural_recovery_prob,
      intervention_recovery_prob = excluded.intervention_recovery_prob,
      incremental_prob = excluded.incremental_prob,
      operational_cost_paise = excluded.operational_cost_paise,
      fatigue_cost_paise = excluded.fatigue_cost_paise,
      expected_incremental_value_paise = excluded.expected_incremental_value_paise,
      confidence = excluded.confidence
  `);
  stmt.run(
    score.opportunity_id,
    score.natural_recovery_prob,
    score.intervention_recovery_prob,
    score.incremental_prob,
    score.operational_cost_paise,
    score.fatigue_cost_paise,
    score.expected_incremental_value_paise,
    score.confidence
  );
}

export function getAllScores(): (Score & { opportunity_id: string })[] {
  const stmt = db.prepare('SELECT * FROM scores');
  return stmt.all() as unknown as (Score & { opportunity_id: string })[];
}

// Allocation Decisions queries
export function getAllocationDecisionByOpportunityId(oppId: string): AllocationDecision | undefined {
  const stmt = db.prepare('SELECT * FROM allocation_decisions WHERE opportunity_id = ?');
  return stmt.get(oppId) as unknown as AllocationDecision | undefined;
}

export function upsertAllocationDecision(decision: AllocationDecision): void {
  const stmt = db.prepare(`
    INSERT INTO allocation_decisions (
      opportunity_id, decision, rank_in_batch, shadow_price_paise_at_decision, reason
    ) VALUES (
      ?, ?, ?, ?, ?
    )
    ON CONFLICT(opportunity_id) DO UPDATE SET
      decision = excluded.decision,
      rank_in_batch = excluded.rank_in_batch,
      shadow_price_paise_at_decision = excluded.shadow_price_paise_at_decision,
      reason = excluded.reason
  `);
  stmt.run(
    decision.opportunity_id,
    decision.decision,
    decision.rank_in_batch,
    decision.shadow_price_paise_at_decision,
    decision.reason
  );
}

export function getAllAllocationDecisions(tenantId?: string): AllocationDecision[] {
  if (tenantId) {
    const stmt = db.prepare(`
      SELECT ad.* FROM allocation_decisions ad
      JOIN recovery_opportunities ro ON ad.opportunity_id = ro.id
      WHERE ro.tenant_id = ? OR ro.merchant_id = ?
      ORDER BY ad.rank_in_batch ASC
    `);
    return stmt.all(tenantId, tenantId) as unknown as AllocationDecision[];
  }
  const stmt = db.prepare('SELECT * FROM allocation_decisions ORDER BY rank_in_batch ASC');
  return stmt.all() as unknown as AllocationDecision[];
}

// Authority Checks queries
export function ensureOpportunity(oppId: string): void {
  if (!oppId) return;
  const existing = getOpportunityById(oppId);
  if (!existing) {
    upsertOpportunity({
      id: oppId,
      source: 'synthetic',
      amount_paise: 100000,
      currency: 'INR',
      reason_code: 'generic_decline',
      decline_type: 'soft',
      attempt_count: 1,
      customer_id: `cust_${oppId}`,
      customer_trust_score: 0.65,
      created_at: new Date().toISOString(),
      status: 'pending',
    });
  }
}

export function insertAuthorityCheck(check: AuthorityCheck): void {
  ensureOpportunity(check.opportunity_id);
  const stmt = db.prepare(`
    INSERT INTO authority_checks (
      opportunity_id, check_name, passed, reason
    ) VALUES (
      ?, ?, ?, ?
    )
  `);
  stmt.run(
    check.opportunity_id,
    check.check_name,
    check.passed ? 1 : 0,
    check.reason
  );
}

export function getAuthorityChecksByOpportunityId(oppId: string): AuthorityCheck[] {
  const stmt = db.prepare('SELECT * FROM authority_checks WHERE opportunity_id = ? ORDER BY id ASC');
  const rows = stmt.all(oppId) as any[];
  return rows.map((r) => ({
    id: r.id,
    opportunity_id: r.opportunity_id,
    check_name: r.check_name,
    passed: Boolean(r.passed),
    reason: r.reason,
  }));
}

export function clearAuthorityChecksForOpportunity(oppId: string): void {
  const stmt = db.prepare('DELETE FROM authority_checks WHERE opportunity_id = ?');
  stmt.run(oppId);
}

export function clearAllAuthorityChecks(): void {
  db.exec('DELETE FROM authority_checks;');
}

// Execution Records queries
export function upsertExecutionRecord(record: ExecutionRecord): void {
  const stmt = db.prepare(`
    INSERT INTO execution_records (
      opportunity_id, razorpay_payment_link_id, link_url, status, idempotency_key, created_at
    ) VALUES (
      ?, ?, ?, ?, ?, ?
    )
    ON CONFLICT(opportunity_id) DO UPDATE SET
      razorpay_payment_link_id = excluded.razorpay_payment_link_id,
      link_url = excluded.link_url,
      status = excluded.status,
      idempotency_key = excluded.idempotency_key,
      created_at = excluded.created_at
  `);
  stmt.run(
    record.opportunity_id,
    record.razorpay_payment_link_id,
    record.link_url,
    record.status,
    record.idempotency_key,
    record.created_at || new Date().toISOString()
  );
}

export function getExecutionRecordByOpportunityId(oppId: string): ExecutionRecord | undefined {
  const stmt = db.prepare('SELECT * FROM execution_records WHERE opportunity_id = ?');
  return stmt.get(oppId) as unknown as ExecutionRecord | undefined;
}

export function getAllExecutionRecords(tenantId?: string): ExecutionRecord[] {
  if (tenantId) {
    const stmt = db.prepare(`
      SELECT er.* FROM execution_records er
      JOIN recovery_opportunities ro ON er.opportunity_id = ro.id
      WHERE ro.tenant_id = ? OR ro.merchant_id = ?
      ORDER BY er.created_at DESC
    `);
    return stmt.all(tenantId, tenantId) as unknown as ExecutionRecord[];
  }
  const stmt = db.prepare('SELECT * FROM execution_records ORDER BY created_at DESC');
  return stmt.all() as unknown as ExecutionRecord[];
}

// Ledger queries
export function insertLedgerEntry(entry: LedgerEntry): void {
  const stmt = db.prepare(`
    INSERT INTO ledger_entries (
      id, opportunity_id, event_type, amount_paise, timestamp, raw_payload_ref
    ) VALUES (
      ?, ?, ?, ?, ?, ?
    )
    ON CONFLICT(id) DO UPDATE SET
      opportunity_id = excluded.opportunity_id,
      event_type = excluded.event_type,
      amount_paise = excluded.amount_paise,
      timestamp = excluded.timestamp,
      raw_payload_ref = excluded.raw_payload_ref
  `);
  stmt.run(
    entry.id,
    entry.opportunity_id,
    entry.event_type,
    entry.amount_paise,
    entry.timestamp || new Date().toISOString(),
    entry.raw_payload_ref || null
  );
}

export function getLedgerEntriesByOpportunity(oppId: string): LedgerEntry[] {
  const stmt = db.prepare('SELECT * FROM ledger_entries WHERE opportunity_id = ? ORDER BY timestamp ASC');
  return stmt.all(oppId) as unknown as LedgerEntry[];
}

// ========================================================
// AGENT SYSTEM QUERIES
// ========================================================

// 1. Agent Runs
export function ensureAgentRun(runId: string, oppId?: string): void {
  if (!runId) return;
  const existing = getAgentRunById(runId);
  if (!existing) {
    insertAgentRun({
      id: runId,
      mission_id: `miss_${runId}`,
      opportunity_id: oppId || null,
      goal_type: 'RECOVER_PAYMENT',
      status: 'running',
      start_time: new Date().toISOString(),
      end_time: null,
      total_steps: 0,
      llm_calls: 0,
      tool_calls: 0,
      replan_count: 0,
      total_tokens: 0,
      latency_ms: 0,
      termination_reason: null,
      created_at: new Date().toISOString(),
    });
  }
}

export function insertAgentRun(run: AgentRunRecord): void {
  const stmt = db.prepare(`
    INSERT INTO agent_runs (
      id, mission_id, opportunity_id, goal_type, status,
      start_time, end_time, total_steps, llm_calls, tool_calls,
      replan_count, total_tokens, latency_ms, termination_reason, created_at
    ) VALUES (
      ?, ?, ?, ?, ?,
      ?, ?, ?, ?, ?,
      ?, ?, ?, ?, ?
    )
  `);
  stmt.run(
    run.id,
    run.mission_id,
    run.opportunity_id || null,
    run.goal_type,
    run.status,
    run.start_time,
    run.end_time || null,
    run.total_steps || 0,
    run.llm_calls || 0,
    run.tool_calls || 0,
    run.replan_count || 0,
    run.total_tokens || 0,
    run.latency_ms || 0,
    run.termination_reason || null,
    run.created_at || new Date().toISOString()
  );
}

export function updateAgentRun(run: Partial<AgentRunRecord> & { id: string }): void {
  const existing = getAgentRunById(run.id);
  if (!existing) return;

  const updated: AgentRunRecord = { ...existing, ...run };
  const stmt = db.prepare(`
    UPDATE agent_runs SET
      status = ?,
      end_time = ?,
      total_steps = ?,
      llm_calls = ?,
      tool_calls = ?,
      replan_count = ?,
      total_tokens = ?,
      latency_ms = ?,
      termination_reason = ?
    WHERE id = ?
  `);
  stmt.run(
    updated.status,
    updated.end_time,
    updated.total_steps,
    updated.llm_calls,
    updated.tool_calls,
    updated.replan_count,
    updated.total_tokens,
    updated.latency_ms,
    updated.termination_reason,
    updated.id
  );
}

export function getAgentRunById(id: string): AgentRunRecord | undefined {
  const stmt = db.prepare('SELECT * FROM agent_runs WHERE id = ?');
  return stmt.get(id) as unknown as AgentRunRecord | undefined;
}

export function getAllAgentRuns(): AgentRunRecord[] {
  const stmt = db.prepare('SELECT * FROM agent_runs ORDER BY created_at DESC');
  return stmt.all() as unknown as AgentRunRecord[];
}

export function getAgentRunsByOpportunityId(oppId: string): AgentRunRecord[] {
  const stmt = db.prepare('SELECT * FROM agent_runs WHERE opportunity_id = ? ORDER BY created_at DESC');
  return stmt.all(oppId) as unknown as AgentRunRecord[];
}

// 2. Agent States
export function insertAgentState(state: AgentStateRecord): void {
  ensureAgentRun(state.run_id);
  const stmt = db.prepare(`
    INSERT INTO agent_states (
      run_id, state, previous_state, trigger, metadata, timestamp
    ) VALUES (?, ?, ?, ?, ?, ?)
  `);
  stmt.run(
    state.run_id,
    state.state,
    state.previous_state || null,
    state.trigger,
    state.metadata || null,
    state.timestamp || new Date().toISOString()
  );
}

export function getAgentStatesByRunId(runId: string): AgentStateRecord[] {
  const stmt = db.prepare('SELECT * FROM agent_states WHERE run_id = ? ORDER BY id ASC');
  return stmt.all(runId) as unknown as AgentStateRecord[];
}

// 3. Agent Steps
export function insertAgentStep(step: AgentStepRecord): void {
  ensureAgentRun(step.run_id);
  const stmt = db.prepare(`
    INSERT INTO agent_steps (
      run_id, step_number, state, observation, thought,
      action_type, action_payload, tool_name, tool_input, tool_output, timestamp
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  stmt.run(
    step.run_id,
    step.step_number,
    step.state,
    step.observation || null,
    step.thought || null,
    step.action_type || null,
    step.action_payload || null,
    step.tool_name || null,
    step.tool_input || null,
    step.tool_output || null,
    step.timestamp || new Date().toISOString()
  );
}

export function getAgentStepsByRunId(runId: string): AgentStepRecord[] {
  const stmt = db.prepare('SELECT * FROM agent_steps WHERE run_id = ? ORDER BY step_number ASC');
  return stmt.all(runId) as unknown as AgentStepRecord[];
}

// 4. Agent Tool Calls
export function insertAgentToolCall(call: AgentToolCallRecord): void {
  ensureAgentRun(call.run_id);
  const stmt = db.prepare(`
    INSERT INTO agent_tool_calls (
      id, run_id, tool_name, agent_name, input_payload,
      input_hash, output_payload, output_hash, status,
      latency_ms, error_message, permission_level, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  stmt.run(
    call.id,
    call.run_id,
    call.tool_name,
    call.agent_name,
    call.input_payload,
    call.input_hash,
    call.output_payload,
    call.output_hash,
    call.status,
    call.latency_ms,
    call.error_message || null,
    call.permission_level,
    call.created_at || new Date().toISOString()
  );
}

export function getAgentToolCallsByRunId(runId: string): AgentToolCallRecord[] {
  const stmt = db.prepare('SELECT * FROM agent_tool_calls WHERE run_id = ? ORDER BY created_at ASC');
  return stmt.all(runId) as unknown as AgentToolCallRecord[];
}

export function getAllAgentToolCalls(): AgentToolCallRecord[] {
  const stmt = db.prepare('SELECT * FROM agent_tool_calls ORDER BY created_at DESC LIMIT 100');
  return stmt.all() as unknown as AgentToolCallRecord[];
}

// 5. Agent Plans
export function insertAgentPlan(plan: AgentPlanRecord): void {
  ensureAgentRun(plan.run_id);
  const stmt = db.prepare(`
    INSERT INTO agent_plans (
      id, run_id, plan_version, goal, steps,
      validity_assumptions, candidate_actions, preferred_action,
      status, invalidation_reason, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  stmt.run(
    plan.id,
    plan.run_id,
    plan.plan_version,
    plan.goal,
    JSON.stringify(plan.steps),
    JSON.stringify(plan.validity_assumptions),
    JSON.stringify(plan.candidate_actions),
    plan.preferred_action,
    plan.status,
    plan.invalidation_reason || null,
    plan.created_at || new Date().toISOString()
  );
}

export function updateAgentPlanStatus(planId: string, status: 'ACTIVE' | 'INVALIDATED' | 'EXECUTED' | 'SUPERSEDED', reason?: string): void {
  const stmt = db.prepare('UPDATE agent_plans SET status = ?, invalidation_reason = ? WHERE id = ?');
  stmt.run(status, reason || null, planId);
}

export function getAgentPlansByRunId(runId: string): AgentPlanRecord[] {
  const stmt = db.prepare('SELECT * FROM agent_plans WHERE run_id = ? ORDER BY plan_version ASC');
  const rows = stmt.all(runId) as any[];
  return rows.map((r) => ({
    ...r,
    steps: JSON.parse(r.steps || '[]'),
    validity_assumptions: JSON.parse(r.validity_assumptions || '[]'),
    candidate_actions: JSON.parse(r.candidate_actions || '[]'),
  }));
}

export function getActivePlanByRunId(runId: string): AgentPlanRecord | undefined {
  const stmt = db.prepare("SELECT * FROM agent_plans WHERE run_id = ? AND status = 'ACTIVE' ORDER BY plan_version DESC LIMIT 1");
  const r = stmt.get(runId) as any;
  if (!r) return undefined;
  return {
    ...r,
    steps: JSON.parse(r.steps || '[]'),
    validity_assumptions: JSON.parse(r.validity_assumptions || '[]'),
    candidate_actions: JSON.parse(r.candidate_actions || '[]'),
  };
}

// 6. Agent Hypotheses
export function insertAgentHypothesis(hyp: AgentHypothesisRecord): void {
  ensureAgentRun(hyp.run_id);
  const stmt = db.prepare(`
    INSERT INTO agent_hypotheses (
      id, run_id, failure_category, root_cause_hypothesis,
      confidence, supporting_evidence, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
  `);
  stmt.run(
    hyp.id,
    hyp.run_id,
    hyp.failure_category,
    hyp.root_cause_hypothesis,
    hyp.confidence,
    JSON.stringify(hyp.supporting_evidence),
    hyp.created_at || new Date().toISOString()
  );
}

export function getAgentHypothesesByRunId(runId: string): AgentHypothesisRecord[] {
  const stmt = db.prepare('SELECT * FROM agent_hypotheses WHERE run_id = ? ORDER BY created_at ASC');
  const rows = stmt.all(runId) as any[];
  return rows.map((r) => ({
    ...r,
    supporting_evidence: JSON.parse(r.supporting_evidence || '[]'),
  }));
}

// 7. Agent Proposals
export function insertAgentProposal(prop: AgentProposalRecord): void {
  ensureAgentRun(prop.run_id, prop.opportunity_id);
  const stmt = db.prepare(`
    INSERT INTO agent_proposals (
      id, run_id, opportunity_id, proposal_type,
      payload, status, review_notes, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  stmt.run(
    prop.id,
    prop.run_id,
    prop.opportunity_id,
    prop.proposal_type,
    JSON.stringify(prop.payload),
    prop.status,
    prop.review_notes || null,
    prop.created_at || new Date().toISOString()
  );
}

export function updateAgentProposalStatus(id: string, status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'SUPERSEDED', notes?: string): void {
  const stmt = db.prepare('UPDATE agent_proposals SET status = ?, review_notes = ? WHERE id = ?');
  stmt.run(status, notes || null, id);
}

export function getAgentProposalsByOpportunityId(oppId: string): AgentProposalRecord[] {
  const stmt = db.prepare('SELECT * FROM agent_proposals WHERE opportunity_id = ? ORDER BY created_at DESC');
  const rows = stmt.all(oppId) as any[];
  return rows.map((r) => ({
    ...r,
    payload: JSON.parse(r.payload || '{}'),
  }));
}

export function getAllAgentProposals(): AgentProposalRecord[] {
  const stmt = db.prepare('SELECT * FROM agent_proposals ORDER BY created_at DESC');
  const rows = stmt.all() as any[];
  return rows.map((r) => ({
    ...r,
    payload: JSON.parse(r.payload || '{}'),
  }));
}

// 8. Agent Memories
export function insertAgentMemory(mem: AgentMemoryItem): void {
  const stmt = db.prepare(`
    INSERT INTO agent_memories (
      id, memory_type, run_id, opportunity_id, failure_type,
      context_summary, action_taken, predicted_outcome, actual_outcome,
      prediction_error, semantic_key, semantic_value, confidence, provenance, created_at
    ) VALUES (
      ?, ?, ?, ?, ?,
      ?, ?, ?, ?,
      ?, ?, ?, ?, ?, ?
    )
  `);
  stmt.run(
    mem.id,
    mem.memory_type,
    mem.run_id || null,
    mem.opportunity_id || null,
    mem.failure_type || null,
    mem.context_summary,
    mem.action_taken || null,
    mem.predicted_outcome || null,
    mem.actual_outcome || null,
    mem.prediction_error !== undefined ? mem.prediction_error : null,
    mem.semantic_key || null,
    mem.semantic_value || null,
    mem.confidence,
    mem.provenance,
    mem.created_at || new Date().toISOString()
  );
}

export function getMemories(type?: 'working' | 'episodic' | 'semantic', maxTimestamp?: string): AgentMemoryItem[] {
  let query = 'SELECT * FROM agent_memories WHERE 1=1';
  const params: any[] = [];
  if (type) {
    query += ' AND memory_type = ?';
    params.push(type);
  }
  if (maxTimestamp) {
    query += ' AND created_at <= ?';
    params.push(maxTimestamp);
  }
  query += ' ORDER BY created_at DESC';
  const stmt = db.prepare(query);
  return stmt.all(...params) as unknown as AgentMemoryItem[];
}

export function getEpisodicMemories(failureType?: string, maxTimestamp?: string): AgentMemoryItem[] {
  let query = "SELECT * FROM agent_memories WHERE memory_type = 'episodic'";
  const params: any[] = [];
  if (failureType) {
    query += ' AND failure_type = ?';
    params.push(failureType);
  }
  if (maxTimestamp) {
    query += ' AND created_at <= ?';
    params.push(maxTimestamp);
  }
  query += ' ORDER BY created_at DESC LIMIT 50';
  const stmt = db.prepare(query);
  return stmt.all(...params) as unknown as AgentMemoryItem[];
}

export function getSemanticMemories(keyPrefix?: string, maxTimestamp?: string): AgentMemoryItem[] {
  let query = "SELECT * FROM agent_memories WHERE memory_type = 'semantic'";
  const params: any[] = [];
  if (keyPrefix) {
    query += ' AND semantic_key LIKE ?';
    params.push(`${keyPrefix}%`);
  }
  if (maxTimestamp) {
    query += ' AND created_at <= ?';
    params.push(maxTimestamp);
  }
  query += ' ORDER BY created_at DESC';
  const stmt = db.prepare(query);
  return stmt.all(...params) as unknown as AgentMemoryItem[];
}

export function getWorkingMemoryForRun(runId: string): AgentMemoryItem[] {
  const stmt = db.prepare("SELECT * FROM agent_memories WHERE memory_type = 'working' AND run_id = ? ORDER BY created_at ASC");
  return stmt.all(runId) as unknown as AgentMemoryItem[];
}

// 9. Agent Outcomes
export function insertAgentOutcome(outcome: AgentOutcomeRecord): void {
  ensureAgentRun(outcome.run_id, outcome.opportunity_id);
  const stmt = db.prepare(`
    INSERT INTO agent_outcomes (
      id, run_id, opportunity_id, predicted_recovery_prob, actual_recovered,
      prediction_error, actual_revenue_paise, operational_cost_paise,
      net_gain_paise, customer_response, evaluated_at
    ) VALUES (
      ?, ?, ?, ?, ?,
      ?, ?, ?,
      ?, ?, ?
    )
  `);
  stmt.run(
    outcome.id,
    outcome.run_id,
    outcome.opportunity_id,
    outcome.predicted_recovery_prob,
    outcome.actual_recovered ? 1 : 0,
    outcome.prediction_error,
    outcome.actual_revenue_paise,
    outcome.operational_cost_paise,
    outcome.net_gain_paise,
    outcome.customer_response || null,
    outcome.evaluated_at || new Date().toISOString()
  );
}

export function getAgentOutcomeByOpportunityId(oppId: string): AgentOutcomeRecord | undefined {
  const stmt = db.prepare('SELECT * FROM agent_outcomes WHERE opportunity_id = ?');
  const r = stmt.get(oppId) as any;
  if (!r) return undefined;
  return {
    ...r,
    actual_recovered: Boolean(r.actual_recovered),
  };
}

export function getAllAgentOutcomes(): AgentOutcomeRecord[] {
  const stmt = db.prepare('SELECT * FROM agent_outcomes ORDER BY evaluated_at DESC');
  const rows = stmt.all() as any[];
  return rows.map((r) => ({
    ...r,
    actual_recovered: Boolean(r.actual_recovered),
  }));
}

// 10. Agent Authority Checks
export function insertAgentAuthorityCheck(check: AgentAuthorityCheckRecord): void {
  ensureAgentRun(check.run_id);
  const stmt = db.prepare(`
    INSERT INTO agent_authority_checks (
      run_id, tool_name, agent_name, check_name, passed, reason, timestamp
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
  `);
  stmt.run(
    check.run_id,
    check.tool_name,
    check.agent_name,
    check.check_name,
    check.passed ? 1 : 0,
    check.reason,
    check.timestamp || new Date().toISOString()
  );
}

export function getAgentAuthorityChecksByRunId(runId: string): AgentAuthorityCheckRecord[] {
  const stmt = db.prepare('SELECT * FROM agent_authority_checks WHERE run_id = ? ORDER BY id ASC');
  const rows = stmt.all(runId) as any[];
  return rows.map((r) => ({
    ...r,
    passed: Boolean(r.passed),
  }));
}

// 11. LLM Invocations
export function insertLLMInvocation(inv: LLMInvocationRecord): void {
  ensureAgentRun(inv.run_id);
  const stmt = db.prepare(`
    INSERT INTO llm_invocations (
      id, run_id, model, provider, prompt_hash,
      prompt_preview, completion_hash, completion_preview, reasoning_preview,
      latency_ms, prompt_tokens, completion_tokens, total_tokens, error, created_at
    ) VALUES (
      ?, ?, ?, ?, ?,
      ?, ?, ?, ?,
      ?, ?, ?, ?, ?, ?
    )
  `);
  stmt.run(
    inv.id,
    inv.run_id,
    inv.model,
    inv.provider,
    inv.prompt_hash,
    inv.prompt_preview,
    inv.completion_hash,
    inv.completion_preview,
    inv.reasoning_preview || null,
    inv.latency_ms,
    inv.prompt_tokens,
    inv.completion_tokens,
    inv.total_tokens,
    inv.error || null,
    inv.created_at || new Date().toISOString()
  );
}

export function getLLMInvocationsByRunId(runId: string): LLMInvocationRecord[] {
  const stmt = db.prepare('SELECT * FROM llm_invocations WHERE run_id = ? ORDER BY created_at ASC');
  return stmt.all(runId) as unknown as LLMInvocationRecord[];
}

export function getAllLLMInvocations(): LLMInvocationRecord[] {
  const stmt = db.prepare('SELECT * FROM llm_invocations ORDER BY created_at DESC LIMIT 100');
  return stmt.all() as unknown as LLMInvocationRecord[];
}

// 12. Outreach Drafts
export function insertOutreachDraft(draft: OutreachDraftRecord): void {
  ensureAgentRun(draft.run_id, draft.opportunity_id);
  const stmt = db.prepare(`
    INSERT INTO outreach_drafts (
      id, run_id, opportunity_id, channel, recipient,
      subject, body, compliance_footer, status, review_feedback, created_at
    ) VALUES (
      ?, ?, ?, ?, ?,
      ?, ?, ?, ?, ?, ?
    )
  `);
  stmt.run(
    draft.id,
    draft.run_id,
    draft.opportunity_id,
    draft.channel,
    draft.recipient,
    draft.subject || null,
    draft.body,
    draft.compliance_footer,
    draft.status || 'PENDING_REVIEW',
    draft.review_feedback || null,
    draft.created_at || new Date().toISOString()
  );
}

export function updateOutreachDraftStatus(id: string, status: 'PENDING_REVIEW' | 'APPROVED' | 'REJECTED', feedback?: string): void {
  const stmt = db.prepare('UPDATE outreach_drafts SET status = ?, review_feedback = ? WHERE id = ?');
  stmt.run(status, feedback || null, id);
}

export function getOutreachDraftsByOpportunityId(oppId: string): OutreachDraftRecord[] {
  const stmt = db.prepare('SELECT * FROM outreach_drafts WHERE opportunity_id = ? ORDER BY created_at DESC');
  return stmt.all(oppId) as unknown as OutreachDraftRecord[];
}

export function getAllOutreachDrafts(): OutreachDraftRecord[] {
  const stmt = db.prepare('SELECT * FROM outreach_drafts ORDER BY created_at DESC');
  return stmt.all() as unknown as OutreachDraftRecord[];
}

// 13. Perception Annotations
export function insertPerceptionAnnotation(ann: PerceptionAnnotationRecord): void {
  ensureOpportunity(ann.opportunity_id);
  const stmt = db.prepare(`
    INSERT INTO perception_annotations (
      id, opportunity_id, failure_intent, customer_urgency_score,
      merchant_risk_score, semantic_notes, confidence, created_at
    ) VALUES (
      ?, ?, ?, ?,
      ?, ?, ?, ?
    )
    ON CONFLICT(id) DO UPDATE SET
      failure_intent = excluded.failure_intent,
      customer_urgency_score = excluded.customer_urgency_score,
      merchant_risk_score = excluded.merchant_risk_score,
      semantic_notes = excluded.semantic_notes,
      confidence = excluded.confidence
  `);
  stmt.run(
    ann.id,
    ann.opportunity_id,
    ann.failure_intent,
    ann.customer_urgency_score,
    ann.merchant_risk_score,
    ann.semantic_notes,
    ann.confidence,
    ann.created_at || new Date().toISOString()
  );
}

export function getPerceptionAnnotationByOpportunityId(oppId: string): PerceptionAnnotationRecord | undefined {
  const stmt = db.prepare('SELECT * FROM perception_annotations WHERE opportunity_id = ?');
  return stmt.get(oppId) as unknown as PerceptionAnnotationRecord | undefined;
}

