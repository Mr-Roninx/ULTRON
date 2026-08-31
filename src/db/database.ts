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

const DB_PATH = process.env.DATABASE_PATH || path.resolve(process.cwd(), 'ultron.db');

export const db = new DatabaseSync(DB_PATH);

export function initDatabase(): void {
  // Enable WAL mode & foreign keys
  db.exec(`
    PRAGMA journal_mode = WAL;
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS customers (
      id TEXT PRIMARY KEY,
      trust_score REAL NOT NULL DEFAULT 0.65,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS recovery_opportunities (
      id TEXT PRIMARY KEY,
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

export function getAllOpportunities(): RecoveryOpportunity[] {
  const stmt = db.prepare('SELECT * FROM recovery_opportunities ORDER BY created_at DESC');
  return stmt.all() as unknown as RecoveryOpportunity[];
}

export function insertOpportunity(opp: RecoveryOpportunity): void {
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

export function getAllAllocationDecisions(): AllocationDecision[] {
  const stmt = db.prepare('SELECT * FROM allocation_decisions ORDER BY rank_in_batch ASC');
  return stmt.all() as unknown as AllocationDecision[];
}

// Authority Checks queries
export function insertAuthorityCheck(check: AuthorityCheck): void {
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

export function getAllExecutionRecords(): ExecutionRecord[] {
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
