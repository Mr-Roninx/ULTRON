import {
  RecoveryOpportunity,
  Score,
  AllocationDecision,
  AuthorityCheck,
  AuthorityVerdict,
} from '../types/index.js';
import {
  db,
  insertAuthorityCheck,
  clearAuthorityChecksForOpportunity,
  updateOpportunityStatus,
  getAllOpportunities,
  getScoreByOpportunityId,
  getAllocationDecisionByOpportunityId,
} from '../db/database.js';
import { runMarketAllocation } from '../market/allocator.js';
import { scoreOpportunity } from '../economics/scorer.js';

// Multi-Level Kill Switch State
let isGlobalKillSwitchActive = false;
const tenantKillSwitches = new Map<string, boolean>();
const providerKillSwitches = new Map<string, boolean>();

export function isKillSwitchActive(tenantId?: string, provider?: string): boolean {
  if (isGlobalKillSwitchActive) return true;
  if (tenantId && tenantKillSwitches.get(tenantId) === true) return true;
  if (provider && providerKillSwitches.get(provider) === true) return true;
  return false;
}

export function setKillSwitch(enabled: boolean): boolean {
  isGlobalKillSwitchActive = Boolean(enabled);
  return isGlobalKillSwitchActive;
}

export function setTenantKillSwitch(tenantId: string, enabled: boolean): boolean {
  tenantKillSwitches.set(tenantId, Boolean(enabled));
  return Boolean(enabled);
}

export function setProviderKillSwitch(provider: string, enabled: boolean): boolean {
  providerKillSwitches.set(provider, Boolean(enabled));
  return Boolean(enabled);
}

export function resetAllKillSwitches(): void {
  isGlobalKillSwitchActive = false;
  tenantKillSwitches.clear();
  providerKillSwitches.clear();
}

export interface AuthorityEvaluationResult {
  opportunity_id: string;
  verdict: AuthorityVerdict;
  checks: AuthorityCheck[];
  summary_reason: string;
}

/**
 * Runs 5 independent deterministic compliance checks on an opportunity
 */
export function evaluateOpportunity(
  opp: RecoveryOpportunity,
  decision?: AllocationDecision,
  score?: Score
): AuthorityEvaluationResult {
  const effectiveScore = score || getScoreByOpportunityId(opp.id) || scoreOpportunity(opp);
  const effectiveDecision = decision || getAllocationDecisionByOpportunityId(opp.id) || {
    opportunity_id: opp.id,
    decision: 'ACT',
    rank_in_batch: 1,
    shadow_price_paise_at_decision: 0,
    reason: 'Default evaluation',
  };

  const checks: AuthorityCheck[] = [];

  // Check 1: Hard Decline Check
  if (opp.decline_type === 'hard') {
    checks.push({
      opportunity_id: opp.id,
      check_name: 'hard_decline_check',
      passed: false,
      reason: 'no auto-contact after a hard/fraud-coded decline',
    });
  } else {
    checks.push({
      opportunity_id: opp.id,
      check_name: 'hard_decline_check',
      passed: true,
      reason: `decline type is recoverable (${opp.decline_type})`,
    });
  }

  // Check 2: Retry Cap Check
  if (opp.attempt_count >= 3) {
    checks.push({
      opportunity_id: opp.id,
      check_name: 'retry_cap_check',
      passed: false,
      reason: 'retry cap reached — route to manual fallback, not further auto-contact',
    });
  } else {
    checks.push({
      opportunity_id: opp.id,
      check_name: 'retry_cap_check',
      passed: true,
      reason: `attempt count (${opp.attempt_count}) within retry cap limit of 3`,
    });
  }

  // Check 3: Kill Switch Check
  if (isKillSwitchActive(opp.tenant_id)) {
    checks.push({
      opportunity_id: opp.id,
      check_name: 'kill_switch_check',
      passed: false,
      reason: 'manual kill switch engaged',
    });
  } else {
    checks.push({
      opportunity_id: opp.id,
      check_name: 'kill_switch_check',
      passed: true,
      reason: 'system operating normally (kill switch disengaged)',
    });
  }

  // Check 4: Confidence Recheck
  if (effectiveScore.confidence === 'low') {
    checks.push({
      opportunity_id: opp.id,
      check_name: 'confidence_recheck',
      passed: false,
      reason: 'low confidence score — requires human or observational review',
    });
  } else {
    checks.push({
      opportunity_id: opp.id,
      check_name: 'confidence_recheck',
      passed: true,
      reason: `confidence level is sufficient (${effectiveScore.confidence})`,
    });
  }

  // Check 5: Capacity Recheck
  if (effectiveDecision.decision !== 'ACT') {
    checks.push({
      opportunity_id: opp.id,
      check_name: 'capacity_recheck',
      passed: false,
      reason: `not within active market allocation batch (market status: ${effectiveDecision.decision})`,
    });
  } else {
    checks.push({
      opportunity_id: opp.id,
      check_name: 'capacity_recheck',
      passed: true,
      reason: `allocated in current active batch (rank #${effectiveDecision.rank_in_batch})`,
    });
  }

  // Persist all check records to SQLite
  clearAuthorityChecksForOpportunity(opp.id);
  for (const check of checks) {
    insertAuthorityCheck(check);
  }

  // Determine Final Authority Verdict
  const hardFail = checks.find((c) => c.check_name === 'hard_decline_check' && !c.passed);
  const retryCapFail = checks.find((c) => c.check_name === 'retry_cap_check' && !c.passed);
  const killSwitchFail = checks.find((c) => c.check_name === 'kill_switch_check' && !c.passed);
  const confidenceFail = checks.find((c) => c.check_name === 'confidence_recheck' && !c.passed);
  const capacityFail = checks.find((c) => c.check_name === 'capacity_recheck' && !c.passed);

  let verdict: AuthorityVerdict;
  let summary_reason: string;

  if (hardFail) {
    verdict = 'BLOCKED';
    summary_reason = hardFail.reason;
    updateOpportunityStatus(opp.id, 'blocked');
  } else if (retryCapFail) {
    verdict = 'BLOCKED';
    summary_reason = retryCapFail.reason;
    updateOpportunityStatus(opp.id, 'blocked');
  } else if (killSwitchFail) {
    verdict = 'BLOCKED';
    summary_reason = killSwitchFail.reason;
    updateOpportunityStatus(opp.id, 'blocked');
  } else if (confidenceFail) {
    verdict = 'ABSTAIN';
    summary_reason = confidenceFail.reason;
    updateOpportunityStatus(opp.id, 'abstained');
  } else if (capacityFail) {
    verdict = 'WAIT';
    summary_reason = capacityFail.reason;
    updateOpportunityStatus(opp.id, 'deferred');
  } else {
    verdict = 'AUTHORIZED';
    summary_reason = 'all deterministic authority and compliance checks passed';
    updateOpportunityStatus(opp.id, 'authorized');
  }

  return {
    opportunity_id: opp.id,
    verdict,
    checks,
    summary_reason,
  };
}

export interface AuthorityPipelineResult {
  kill_switch_active: boolean;
  total_evaluated: number;
  authorized_count: number;
  blocked_count: number;
  abstained_count: number;
  deferred_count: number;
  results: AuthorityEvaluationResult[];
}

/**
 * Runs full two-stage pipeline: Recovery Market Allocation followed by Action Authority Gate
 */
export function runAuthorityPipeline(options: { capacity?: number; tenantId?: string; environment?: 'test' | 'live' } = {}): AuthorityPipelineResult {
  // 1. Run Market Allocation scoped to tenant & environment
  runMarketAllocation(options);

  let env = options.environment;
  if (!env && options.tenantId) {
    try {
      const stmt = db.prepare('SELECT environment FROM tenants WHERE id = ? LIMIT 1;');
      const row = stmt.get(options.tenantId) as { environment?: 'test' | 'live' } | undefined;
      if (row?.environment) env = row.environment;
    } catch { /* fallthrough */ }
  }

  const rawOpps = getAllOpportunities(options.tenantId, env);
  const allOpps = rawOpps.filter(
    (opp) => opp.status !== 'recovered' && opp.status !== 'not_recovered' && opp.status !== 'executing'
  );
  const results: AuthorityEvaluationResult[] = [];

  let authorized_count = 0;
  let blocked_count = 0;
  let abstained_count = 0;
  let deferred_count = 0;

  for (const opp of allOpps) {
    let score = getScoreByOpportunityId(opp.id);
    if (!score) score = scoreOpportunity(opp);

    let decision = getAllocationDecisionByOpportunityId(opp.id);
    if (!decision) {
      decision = {
        opportunity_id: opp.id,
        decision: 'WAIT',
        rank_in_batch: 999,
        shadow_price_paise_at_decision: 0,
        reason: 'Unallocated evaluation',
      };
    }

    const evalResult = evaluateOpportunity(opp, decision, score);
    results.push(evalResult);

    if (evalResult.verdict === 'AUTHORIZED') authorized_count++;
    else if (evalResult.verdict === 'BLOCKED') blocked_count++;
    else if (evalResult.verdict === 'ABSTAIN') abstained_count++;
    else if (evalResult.verdict === 'WAIT') deferred_count++;
  }

  return {
    kill_switch_active: isKillSwitchActive(options.tenantId),
    total_evaluated: allOpps.length,
    authorized_count,
    blocked_count,
    abstained_count,
    deferred_count,
    results,
  };
}
