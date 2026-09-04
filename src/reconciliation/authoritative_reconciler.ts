import { db, getOpportunityById, getExecutionRecordByOpportunityId, getScoreByOpportunityId } from '../db/database.js';
import { rzpClient } from '../execution/executor.js';
import { RazorpayClientPool } from '../providers/razorpay/client_pool.js';
import { ProviderTruthEvaluator, ProviderTruthEvaluation } from '../truth/provider_truth.js';
import { CanonicalStateMachine, CanonicalPaymentState } from '../truth/canonical_state_machine.js';
import { DoubleEntryLedger } from '../truth/double_entry_ledger.js';
import { RecoveryOpportunity, ExecutionRecord, OpportunityStatus } from '../types/index.js';
import { BayesianProbabilityCalibrator } from '../economics/bayesian_calibration.js';
import { ThompsonSamplingBandit } from '../economics/bandit_policy.js';

export interface ReconciliationResult {
  opportunity_id: string;
  payment_link_id?: string;
  previous_opportunity_status: string;
  new_opportunity_status: string;
  canonical_state: CanonicalPaymentState;
  is_recovered: boolean;
  amount_paid_paise: number;
  payment_id: string | null;
  ledger_entry_hash?: string;
  is_idempotent_no_op: boolean;
  status: 'MATCHED' | 'TRANSITION' | 'PENDING' | 'MISMATCH' | 'UNKNOWN' | 'ESCALATE';
  rationale: string;
  timestamp: string;
  error?: string;
}

export class AuthoritativeReconciler {
  /**
   * Authoritatively reconciles an opportunity against external provider truth.
   * Runs atomically across SQLite tables.
   */
  public static async reconcileOpportunity(
    opportunityId: string,
    options: {
      providerPayloadOverride?: any;
      actor?: string;
    } = {}
  ): Promise<ReconciliationResult> {
    const opp = getOpportunityById(opportunityId);
    if (!opp) {
      return {
        opportunity_id: opportunityId,
        previous_opportunity_status: 'UNKNOWN',
        new_opportunity_status: 'UNKNOWN',
        canonical_state: 'UNKNOWN',
        is_recovered: false,
        amount_paid_paise: 0,
        payment_id: null,
        is_idempotent_no_op: false,
        status: 'UNKNOWN',
        rationale: `Opportunity not found in database: ${opportunityId}`,
        timestamp: new Date().toISOString(),
        error: 'OPPORTUNITY_NOT_FOUND',
      };
    }

    const execRecord = getExecutionRecordByOpportunityId(opp.id);
    const now = new Date().toISOString();

    // 1. Fetch provider truth payload
    let providerPayload = options.providerPayloadOverride;
    if (!providerPayload && execRecord && execRecord.razorpay_payment_link_id) {
      try {
        const tenantId = (opp as any).tenant_id || 'tenant_system_default';
        const env: 'test' | 'live' = (opp as any).environment === 'live' ? 'live' : 'test';
        const client = await RazorpayClientPool.getClient(tenantId, env).catch(() => rzpClient);
        providerPayload = await client.paymentLink.fetch(execRecord.razorpay_payment_link_id);
      } catch (err: any) {
        // Provider network/API error -> quarantine as UNKNOWN
        return {
          opportunity_id: opp.id,
          payment_link_id: execRecord.razorpay_payment_link_id,
          previous_opportunity_status: opp.status,
          new_opportunity_status: opp.status,
          canonical_state: 'UNKNOWN',
          is_recovered: false,
          amount_paid_paise: 0,
          payment_id: null,
          is_idempotent_no_op: true,
          status: 'UNKNOWN',
          rationale: `Failed to query Razorpay API (${err.message}). Opportunity quarantined in '${opp.status}' state.`,
          timestamp: now,
          error: err.message,
        };
      }
    }

    if (!providerPayload) {
      return {
        opportunity_id: opp.id,
        previous_opportunity_status: opp.status,
        new_opportunity_status: opp.status,
        canonical_state: 'PENDING',
        is_recovered: false,
        amount_paid_paise: 0,
        payment_id: null,
        is_idempotent_no_op: true,
        status: 'PENDING',
        rationale: 'No provider payment link exists for this opportunity; remaining in current state.',
        timestamp: now,
      };
    }

    // 2. Evaluate Provider Truth
    const truthEval = ProviderTruthEvaluator.evaluate(providerPayload);
    const canonicalMapping = CanonicalStateMachine.mapRazorpayStatusToCanonicalState({
      status: truthEval.provider_status,
      amount_paise: opp.amount_paise,
      amount_paid_paise: truthEval.amount_paid_paise,
    });

    // 3. Idempotency Check & Out-of-Order Protection: If already recovered, terminal state is immutable
    if (opp.status === 'recovered') {
      return {
        opportunity_id: opp.id,
        payment_link_id: truthEval.payment_link_id,
        previous_opportunity_status: opp.status,
        new_opportunity_status: 'recovered',
        canonical_state: 'RECOVERED',
        is_recovered: true,
        amount_paid_paise: truthEval.amount_paid_paise || opp.amount_paise,
        payment_id: truthEval.payment_id,
        is_idempotent_no_op: true,
        status: 'MATCHED',
        rationale: 'Opportunity is already settled in terminal RECOVERED state. Out-of-order events ignored.',
        timestamp: now,
      };
    }

    // 4. Determine Target Status
    let targetOpportunityStatus: OpportunityStatus = opp.status;
    let targetExecStatus = execRecord?.status || 'created';
    let reconciliationOutcome: 'MATCHED' | 'TRANSITION' | 'PENDING' | 'MISMATCH' | 'UNKNOWN' | 'ESCALATE' = 'MATCHED';

    if (canonicalMapping.canonical_state === 'PAYMENT_CONFIRMED' || truthEval.is_recovered) {
      targetOpportunityStatus = 'recovered';
      targetExecStatus = 'completed';
      reconciliationOutcome = 'TRANSITION';
    } else if (canonicalMapping.canonical_state === 'EXPIRED' || canonicalMapping.canonical_state === 'CANCELLED' || canonicalMapping.canonical_state === 'FAILED') {
      targetOpportunityStatus = 'not_recovered';
      targetExecStatus = 'failed';
      reconciliationOutcome = 'TRANSITION';
    } else if (canonicalMapping.canonical_state === 'MISMATCH') {
      targetOpportunityStatus = 'executing';
      targetExecStatus = 'created';
      reconciliationOutcome = 'MISMATCH';
    } else {
      // Pending / Created
      targetOpportunityStatus = opp.status === 'pending' || opp.status === 'deferred' || opp.status === 'allocated' ? 'executing' : opp.status;
      targetExecStatus = 'created';
      reconciliationOutcome = 'PENDING';
    }

    // 5. Execute Atomic Database Transaction
    let recordedLedgerHash: string | undefined;

    try {
      db.exec('BEGIN TRANSACTION;');

      // 5a. Update recovery_opportunities
      db.prepare(`
        UPDATE recovery_opportunities
        SET status = ?
        WHERE id = ?;
      `).run(targetOpportunityStatus, opp.id);

      // 5b. Update execution_records if exists
      if (execRecord) {
        db.prepare(`
          UPDATE execution_records
          SET status = ?
          WHERE opportunity_id = ?;
        `).run(targetExecStatus, opp.id);
      }

      // 5c. If recovered, record DoubleEntryLedger and Learning Outcome
      if (targetOpportunityStatus === 'recovered') {
        const doubleEntryId = `del_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
        
        // Fetch latest entry_hash for hash chain
        const latestEntry = db.prepare(
          'SELECT entry_hash FROM double_entry_ledger ORDER BY rowid DESC LIMIT 1;'
        ).get() as { entry_hash: string } | undefined;
        
        const prevHash = latestEntry?.entry_hash || DoubleEntryLedger.GENESIS_HASH;
        
        const entryHash = DoubleEntryLedger.computeHash({
          prev_hash: prevHash,
          id: doubleEntryId,
          opportunity_id: opp.id,
          event_type: 'PAYMENT_RECOVERED',
          debit_account: 'bank_settlement',
          credit_account: 'recovered_revenue',
          amount_paise: truthEval.amount_paid_paise,
          timestamp: now,
        });

        db.prepare(`
          INSERT INTO double_entry_ledger (id, opportunity_id, event_type, debit_account, credit_account, amount_paise, timestamp, prev_hash, entry_hash)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        `).run(
          doubleEntryId,
          opp.id,
          'PAYMENT_RECOVERED',
          'bank_settlement',
          'recovered_revenue',
          truthEval.amount_paid_paise,
          now,
          prevHash,
          entryHash
        );

        recordedLedgerHash = entryHash;

        // Record general ledger audit entry
        const ledgerAuditId = `led_rec_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
        db.prepare(`
          INSERT INTO ledger_entries (id, opportunity_id, event_type, amount_paise, timestamp, raw_payload_ref)
          VALUES (?, ?, ?, ?, ?, ?);
        `).run(
          ledgerAuditId,
          opp.id,
          'recovered',
          truthEval.amount_paid_paise,
          now,
          JSON.stringify({
            payment_link_id: truthEval.payment_link_id,
            payment_id: truthEval.payment_id,
            amount_paid: truthEval.amount_paid_paise,
            reconciled_by: options.actor || 'authoritative_reconciler',
          })
        );

        // Ensure parent agent_run exists for foreign key constraint
        const reconRunId = `run_rec_${opp.id}`;
        db.prepare(`
          INSERT OR IGNORE INTO agent_runs (
            id, mission_id, opportunity_id, goal_type, status, start_time, end_time,
            total_steps, llm_calls, tool_calls, replan_count, total_tokens, latency_ms,
            termination_reason, created_at
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        `).run(
          reconRunId,
          `miss_${reconRunId}`,
          opp.id,
          'RECOVER_PAYMENT',
          'completed',
          now,
          now,
          1,
          0,
          1,
          0,
          0,
          50,
          'Mission completed normally via Authoritative Reconciliation',
          now
        );

        // Record agent outcome
        const score = getScoreByOpportunityId(opp.id);
        const predictedProb = score ? score.intervention_recovery_prob : 0.65;
        const brierError = Number(Math.pow(1 - predictedProb, 2).toFixed(4));
        const netGain = truthEval.amount_paid_paise - (score?.operational_cost_paise || 400);

        const outcomeId = `out_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
        db.prepare(`
          INSERT OR REPLACE INTO agent_outcomes (
            id, run_id, opportunity_id, predicted_recovery_prob, actual_recovered,
            prediction_error, actual_revenue_paise, operational_cost_paise, net_gain_paise, customer_response, evaluated_at
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        `).run(
          outcomeId,
          reconRunId,
          opp.id,
          predictedProb,
          1,
          brierError,
          truthEval.amount_paid_paise,
          score?.operational_cost_paise || 400,
          netGain,
          'PAYMENT_CONFIRMED',
          now
        );

        // Record episodic memory
        const memoryId = `mem_e_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
        db.prepare(`
          INSERT INTO agent_memories (
            id, memory_type, run_id, opportunity_id, failure_type, context_summary,
            action_taken, predicted_outcome, actual_outcome, prediction_error,
            semantic_key, semantic_value, confidence, provenance, created_at
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        `).run(
          memoryId,
          'episodic',
          reconRunId,
          opp.id,
          opp.reason_code,
          `Reconciled confirmed provider payment of ₹${(truthEval.amount_paid_paise / 100).toFixed(2)} on ${truthEval.payment_link_id}.`,
          'SEND_PAYMENT_LINK',
          `P(int)=${predictedProb}`,
          'RECOVERED',
          brierError,
          `opp:${opp.id}:recovery`,
          JSON.stringify({ payment_id: truthEval.payment_id, amount_paid: truthEval.amount_paid_paise }),
          1.0,
          'AUTHORITATIVE_RECONCILER',
          now
        );
      }

      // If mismatch, record divergence
      if (reconciliationOutcome === 'MISMATCH') {
        const divId = `div_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
        db.prepare(`
          INSERT INTO reconciliation_divergences (id, tenant_id, opportunity_id, type, severity, description, status, created_at)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        `).run(
          divId,
          (opp as any).tenant_id || 'tenant_system_default',
          opp.id,
          'AMOUNT_OR_STATE_MISMATCH',
          'HIGH',
          `Reconciliation mismatch: provider status is ${truthEval.provider_status} with paid amount ${truthEval.amount_paid_paise}`,
          'OPEN',
          now
        );
      }

      db.exec('COMMIT;');
    } catch (err: any) {
      try {
        db.exec('ROLLBACK;');
      } catch {}
      return {
        opportunity_id: opp.id,
        payment_link_id: truthEval.payment_link_id,
        previous_opportunity_status: opp.status,
        new_opportunity_status: opp.status,
        canonical_state: 'UNKNOWN',
        is_recovered: false,
        amount_paid_paise: 0,
        payment_id: null,
        is_idempotent_no_op: false,
        status: 'UNKNOWN',
        rationale: `Database transaction rolled back due to error: ${err.message}`,
        timestamp: now,
        error: err.message,
      };
    }

    // Real-Time Bayesian Continuous Learning Feedback (executed safely post-commit)
    if (targetOpportunityStatus === 'recovered' || targetOpportunityStatus === 'not_recovered') {
      const isRecovered = targetOpportunityStatus === 'recovered';
      const wasIntervention = Boolean(execRecord?.razorpay_payment_link_id);
      BayesianProbabilityCalibrator.recordRealtimeObservation(
        opp.reason_code,
        isRecovered,
        wasIntervention
      ).catch(() => {});

      try {
        const bandit = ThompsonSamplingBandit.getInstance();
        const contextKey = bandit.getContextKey(opp);
        bandit.updateReward({
          tenantId: (opp as any).tenant_id || 'tenant_system_default',
          contextKey,
          isRecovered,
          isIntervention: wasIntervention,
        });
      } catch {}
    }

    return {
      opportunity_id: opp.id,
      payment_link_id: truthEval.payment_link_id,
      previous_opportunity_status: opp.status,
      new_opportunity_status: targetOpportunityStatus,
      canonical_state: canonicalMapping.canonical_state,
      is_recovered: targetOpportunityStatus === 'recovered',
      amount_paid_paise: truthEval.amount_paid_paise,
      payment_id: truthEval.payment_id,
      ledger_entry_hash: recordedLedgerHash,
      is_idempotent_no_op: false,
      status: reconciliationOutcome,
      rationale: canonicalMapping.rationale,
      timestamp: now,
    };
  }

  /**
   * Scans all active execution records and synchronizes their state against provider truth.
   */
  public static async reconcileAllActive(): Promise<{
    total_scanned: number;
    reconciled_count: number;
    recovered_count: number;
    pending_count: number;
    results: ReconciliationResult[];
  }> {
    const execRecords = db.prepare('SELECT * FROM execution_records;').all() as unknown as ExecutionRecord[];
    const results: ReconciliationResult[] = [];
    let recovered_count = 0;
    let pending_count = 0;

    for (const rec of execRecords) {
      // Small throttle to avoid hitting Razorpay test mode rate limit (429)
      await new Promise((resolve) => setTimeout(resolve, 350));

      const res = await this.reconcileOpportunity(rec.opportunity_id, {
        actor: 'reconcile_all_active_sweep',
      });
      results.push(res);

      if (res.is_recovered) {
        recovered_count++;
      } else {
        pending_count++;
      }
    }

    return {
      total_scanned: execRecords.length,
      reconciled_count: results.filter(r => !r.is_idempotent_no_op).length,
      recovered_count,
      pending_count,
      results,
    };
  }
}
