import { DatabaseAdapter } from '../db/adapter.js';

export interface ExecutionFailureRecord {
  id?: number;
  opportunity_id: string;
  failure_count: number;
  last_error: string;
  next_retry_at: string | null;
  status: 'PENDING_RETRY' | 'PERMANENTLY_FAILED';
  created_at: string;
}

export class ExecutionDLQ {
  private static retryIntervalsMin = [5, 15, 60, 240]; // 5m, 15m, 1h, 4h

  public static async initTable(db?: DatabaseAdapter): Promise<void> {
    const adapter = db || DatabaseAdapter.getInstance();
    await adapter.execute(`
      CREATE TABLE IF NOT EXISTS execution_failures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        opportunity_id TEXT NOT NULL,
        failure_count INTEGER NOT NULL DEFAULT 1,
        last_error TEXT NOT NULL,
        next_retry_at TEXT,
        status TEXT NOT NULL CHECK(status IN ('PENDING_RETRY', 'PERMANENTLY_FAILED')),
        created_at TEXT NOT NULL,
        FOREIGN KEY (opportunity_id) REFERENCES recovery_opportunities(id) ON DELETE CASCADE
      );
    `);
  }

  public static async recordExecutionFailure(opportunityId: string, error: string): Promise<ExecutionFailureRecord> {
    const adapter = DatabaseAdapter.getInstance();
    await this.initTable(adapter);

    const existing = await adapter.query<ExecutionFailureRecord>(
      'SELECT * FROM execution_failures WHERE opportunity_id = ? ORDER BY id DESC LIMIT 1;',
      [opportunityId]
    );

    const prevCount = existing[0]?.failure_count ?? 0;
    const newCount = prevCount + 1;

    let nextRetryAt: string | null = null;
    let status: 'PENDING_RETRY' | 'PERMANENTLY_FAILED' = 'PENDING_RETRY';

    if (newCount <= this.retryIntervalsMin.length) {
      const delayMin = this.retryIntervalsMin[newCount - 1] ?? 1;
      nextRetryAt = new Date(Date.now() + delayMin * 60 * 1000).toISOString();
      console.warn(`📥 ExecutionDLQ: Opportunity ${opportunityId} scheduled for retry #${newCount} in ${delayMin}m (${nextRetryAt})`);
    } else {
      status = 'PERMANENTLY_FAILED';
      console.error(`🚨 ExecutionDLQ: Opportunity ${opportunityId} permanently failed after ${newCount} attempts! Operator alert generated.`);
    }

    await adapter.execute(
      `INSERT INTO execution_failures (opportunity_id, failure_count, last_error, next_retry_at, status, created_at)
       VALUES (?, ?, ?, ?, ?, ?);`,
      [opportunityId, newCount, error, nextRetryAt, status, new Date().toISOString()]
    );

    return {
      opportunity_id: opportunityId,
      failure_count: newCount,
      last_error: error,
      next_retry_at: nextRetryAt,
      status,
      created_at: new Date().toISOString(),
    };
  }

  public static async getPendingRetries(): Promise<ExecutionFailureRecord[]> {
    const adapter = DatabaseAdapter.getInstance();
    await this.initTable(adapter);

    const now = new Date().toISOString();
    return adapter.query<ExecutionFailureRecord>(
      `SELECT * FROM execution_failures WHERE status = 'PENDING_RETRY' AND next_retry_at <= ? ORDER BY next_retry_at ASC;`,
      [now]
    );
  }
}
