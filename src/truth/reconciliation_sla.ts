import { DatabaseAdapter } from '../db/adapter.js';

export interface SlaMetric {
  path: 'webhook' | 'poller';
  latency_ms: number;
  sla_target_ms: number;
  passed_sla: boolean;
  opportunity_id: string;
  timestamp: string;
}

export interface DivergenceAlert {
  id?: number;
  opportunity_id: string;
  webhook_status: string;
  poller_status: string;
  divergence_type: string;
  detected_at: string;
}

export class ReconciliationSlaTracker {
  // Webhook SLA: < 5,000ms (5s)
  // Poller SLA: < 300,000ms (5 min)
  // Unreconciled Alert: > 1,800,000ms (30 min)
  private static readonly WEBHOOK_SLA_MS = 5000;
  private static readonly POLLER_SLA_MS = 300000;
  private static readonly UNRECONCILED_ALERT_MS = 1800000;

  public static async initTable(db?: DatabaseAdapter): Promise<void> {
    const adapter = db || DatabaseAdapter.getInstance();
    await adapter.execute(`
      CREATE TABLE IF NOT EXISTS reconciliation_divergences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        opportunity_id TEXT NOT NULL,
        webhook_status TEXT NOT NULL,
        poller_status TEXT NOT NULL,
        divergence_type TEXT NOT NULL,
        detected_at TEXT NOT NULL,
        FOREIGN KEY (opportunity_id) REFERENCES recovery_opportunities(id) ON DELETE CASCADE
      );
    `);
  }

  /**
   * Tracks reconciliation SLA latency and verifies compliance.
   */
  public static trackLatency(
    opportunityId: string,
    path: 'webhook' | 'poller',
    latencyMs: number
  ): SlaMetric {
    const targetMs = path === 'webhook' ? this.WEBHOOK_SLA_MS : this.POLLER_SLA_MS;
    const passedSla = latencyMs <= targetMs;

    if (!passedSla) {
      console.warn(
        `⏱️ Reconciliation SLA Breached on ${path} path for ${opportunityId}: took ${latencyMs}ms (target <= ${targetMs}ms)`
      );
    }

    return {
      path,
      latency_ms: latencyMs,
      sla_target_ms: targetMs,
      passed_sla: passedSla,
      opportunity_id: opportunityId,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Checks for executing links that have remained unreconciled for > 30 minutes.
   */
  public static async checkUnreconciledAlerts(): Promise<{ opportunity_id: string; age_minutes: number }[]> {
    const adapter = DatabaseAdapter.getInstance();
    const cutoff = new Date(Date.now() - this.UNRECONCILED_ALERT_MS).toISOString();

    const staleRecords = await adapter.query<{ opportunity_id: string; created_at: string }>(
      `SELECT e.opportunity_id, e.created_at
       FROM execution_records e
       JOIN recovery_opportunities o ON e.opportunity_id = o.id
       WHERE o.status = 'executing' AND e.created_at <= ?;`,
      [cutoff]
    );

    return staleRecords.map((r) => ({
      opportunity_id: r.opportunity_id,
      age_minutes: Math.floor((Date.now() - new Date(r.created_at).getTime()) / 60000),
    }));
  }

  /**
   * Detects divergence between webhook state and poller state.
   */
  public static async detectDivergence(
    opportunityId: string,
    webhookStatus: string,
    pollerStatus: string
  ): Promise<DivergenceAlert | null> {
    if (webhookStatus === pollerStatus) {
      return null;
    }

    const adapter = DatabaseAdapter.getInstance();
    await this.initTable(adapter);

    const alert: DivergenceAlert = {
      opportunity_id: opportunityId,
      webhook_status: webhookStatus,
      poller_status: pollerStatus,
      divergence_type: `MISMATCH (${webhookStatus} vs ${pollerStatus})`,
      detected_at: new Date().toISOString(),
    };

    console.error(`🚨 Divergence Detected for opportunity ${opportunityId}: Webhook=${webhookStatus}, Poller=${pollerStatus}`);

    await adapter.execute(
      `INSERT INTO reconciliation_divergences (opportunity_id, webhook_status, poller_status, divergence_type, detected_at)
       VALUES (?, ?, ?, ?, ?);`,
      [alert.opportunity_id, alert.webhook_status, alert.poller_status, alert.divergence_type, alert.detected_at]
    );

    return alert;
  }
}
