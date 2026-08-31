import Razorpay from 'razorpay';
import dotenv from 'dotenv';
import path from 'node:path';
import {
  getOpportunityById,
  getScoreByOpportunityId,
  getAllocationDecisionByOpportunityId,
  getExecutionRecordByOpportunityId,
  upsertExecutionRecord,
  updateOpportunityStatus,
  insertLedgerEntry,
} from '../db/database.js';
import { scoreOpportunity } from '../economics/scorer.js';
import { evaluateOpportunity, runAuthorityPipeline } from '../authority/gate.js';
import { ExecutionRecord, RecoveryOpportunity } from '../types/index.js';

dotenv.config({ path: path.resolve(process.cwd(), '.env') });

const key_id = process.env.RAZORPAY_KEY_ID || '';
const key_secret = process.env.RAZORPAY_KEY_SECRET || '';

export const rzpClient = new Razorpay({
  key_id,
  key_secret,
});

export interface SingleExecutionResult {
  opportunity_id: string;
  success: boolean;
  created_new: boolean;
  record?: ExecutionRecord;
  error?: string;
}

export interface BatchExecutionResult {
  max_links_cap: number;
  total_authorized: number;
  executed_count: number;
  skipped_count: number;
  failed_count: number;
  results: SingleExecutionResult[];
}

/**
 * Creates a real Razorpay payment link for an AUTHORIZED opportunity with strict compliance checks and idempotency.
 */
export async function executeOpportunity(opportunityId: string): Promise<SingleExecutionResult> {
  const opp = getOpportunityById(opportunityId);
  if (!opp) {
    throw new Error(`Opportunity not found: ${opportunityId}`);
  }

  // 1. Zero-Bypass Authority Check: Explicit assertion of AUTHORIZED status
  let score = getScoreByOpportunityId(opp.id);
  if (!score) score = scoreOpportunity(opp);

  let decision = getAllocationDecisionByOpportunityId(opp.id);
  if (!decision) {
    decision = {
      opportunity_id: opp.id,
      decision: 'WAIT',
      rank_in_batch: 999,
      shadow_price_paise_at_decision: 0,
      reason: 'Unallocated execution attempt',
    };
  }

  const evalResult = evaluateOpportunity(opp, decision, score);
  if (evalResult.verdict !== 'AUTHORIZED') {
    throw new Error(
      `Compliance Violation: Opportunity ${opp.id} is not AUTHORIZED (verdict: ${evalResult.verdict}, reason: "${evalResult.summary_reason}"). Real payment link creation strictly rejected.`
    );
  }

  // 2. Idempotency Check: reference_id = opportunity_id
  const existingRecord = getExecutionRecordByOpportunityId(opp.id);
  if (existingRecord) {
    if (opp.status !== 'recovered') {
      updateOpportunityStatus(opp.id, 'executing');
    }
    return {
      opportunity_id: opp.id,
      success: true,
      created_new: false,
      record: existingRecord,
    };
  }

  // 3. Call Razorpay API (Test Mode)
  try {
    const rzpResponse = await rzpClient.paymentLink.create({
      amount: opp.amount_paise,
      currency: opp.currency || 'INR',
      accept_partial: false,
      reference_id: opp.id,
      description: `ULTRON automated recovery for opportunity ${opp.id}`,
      customer: {
        name: opp.customer_id,
        email: opp.customer_id.includes('@') ? opp.customer_id : undefined,
        contact: opp.customer_id.startsWith('+') ? opp.customer_id : undefined,
      },
      notify: {
        sms: false,
        email: false,
      },
      reminder_enable: false,
      notes: {
        opportunity_id: opp.id,
        source: opp.source,
        reason_code: opp.reason_code,
        system: 'ULTRON Economic Recovery Control Plane',
      },
    });

    const now = new Date().toISOString();
    const linkUrl = rzpResponse.short_url || `https://rzp.io/i/${rzpResponse.id}`;

    const executionRecord: ExecutionRecord = {
      opportunity_id: opp.id,
      razorpay_payment_link_id: rzpResponse.id,
      link_url: linkUrl,
      status: rzpResponse.status || 'created',
      idempotency_key: `ref_${opp.id}`,
      created_at: now,
    };

    // Store in SQLite execution_records
    upsertExecutionRecord(executionRecord);

    // Update opportunity status to executing
    updateOpportunityStatus(opp.id, 'executing');

    // Audit trail in ledger
    insertLedgerEntry({
      id: `led_exec_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      opportunity_id: opp.id,
      event_type: 'reconciled',
      amount_paise: opp.amount_paise,
      timestamp: now,
      raw_payload_ref: JSON.stringify({
        razorpay_payment_link_id: rzpResponse.id,
        short_url: linkUrl,
        amount_paise: opp.amount_paise,
      }),
    });

    return {
      opportunity_id: opp.id,
      success: true,
      created_new: true,
      record: executionRecord,
    };
  } catch (error: any) {
    console.error(`Razorpay API execution error for ${opp.id}:`, error);
    return {
      opportunity_id: opp.id,
      success: false,
      created_new: false,
      error: error?.message || error?.description || 'Razorpay API execution failed',
    };
  }
}

/**
 * Executes payment link creation for all currently AUTHORIZED opportunities up to capacity cap (default 5).
 */
export async function executeAuthorizedBatch(
  options: { maxLinks?: number; capacity?: number } = {}
): Promise<BatchExecutionResult> {
  const maxLinks = options.maxLinks || Number(process.env.MAX_LINKS_PER_RUN) || 5;

  // 1. Run Authority Pipeline to get up-to-date compliance verdicts
  const authorityRun = runAuthorityPipeline({ capacity: options.capacity || maxLinks });
  const authorizedOpps = authorityRun.results.filter((r) => r.verdict === 'AUTHORIZED');

  const executionResults: SingleExecutionResult[] = [];
  let executed_count = 0;
  let skipped_count = 0;
  let failed_count = 0;

  // 2. Process up to maxLinks cap
  const targetBatch = authorizedOpps.slice(0, maxLinks);

  for (const item of targetBatch) {
    try {
      const res = await executeOpportunity(item.opportunity_id);
      executionResults.push(res);
      if (res.success) {
        executed_count++;
      } else {
        failed_count++;
      }
    } catch (err: any) {
      failed_count++;
      executionResults.push({
        opportunity_id: item.opportunity_id,
        success: false,
        created_new: false,
        error: err?.message || 'Execution error',
      });
    }
  }

  skipped_count = Math.max(0, authorizedOpps.length - targetBatch.length);

  return {
    max_links_cap: maxLinks,
    total_authorized: authorizedOpps.length,
    executed_count,
    skipped_count,
    failed_count,
    results: executionResults,
  };
}
