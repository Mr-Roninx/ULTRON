import { DatabaseSync } from 'node:sqlite';
import path from 'node:path';
import {
  RecoveryOpportunity,
  Score,
  AllocationDecision,
  AuthorityCheck,
  ExecutionRecord,
  LedgerEntry,
} from '../types/index.js';

const DB_PATH = process.env.DATABASE_PATH || path.resolve(process.cwd(), 'ultron.db');

export const db = new DatabaseSync(DB_PATH);

// Enable WAL mode & foreign keys
db.exec(`
  PRAGMA journal_mode = WAL;
  PRAGMA foreign_keys = ON;

  CREATE TABLE IF NOT EXISTS recovery_opportunities (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL CHECK(source IN ('real', 'synthetic')),
    amount_paise INTEGER NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',
    reason_code TEXT NOT NULL,
    decline_type TEXT NOT NULL CHECK(decline_type IN ('hard', 'soft', 'unknown')),
    attempt_count INTEGER NOT NULL DEFAULT 1,
    customer_id TEXT NOT NULL,
    customer_trust_score REAL NOT NULL DEFAULT 0.5,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN (
      'pending', 'scored', 'allocated', 'deferred', 'blocked', 'abstained', 'executing', 'recovered', 'not_recovered'
    )),
    razorpay_event_id TEXT UNIQUE,
    raw_payload_ref TEXT
  );

  CREATE INDEX IF NOT EXISTS idx_opportunities_source ON recovery_opportunities(source);
  CREATE INDEX IF NOT EXISTS idx_opportunities_status ON recovery_opportunities(status);
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

export function initDatabase(): void {
  // DB schema is verified and tables created above
}

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
    opp.customer_trust_score ?? 0.5,
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
    opp.customer_trust_score ?? 0.5,
    opp.created_at || new Date().toISOString(),
    opp.status || 'pending',
    opp.razorpay_event_id || null,
    opp.raw_payload_ref || null
  );
}

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
