import { RecoveryOpportunity, Score, ConfidenceLevel } from '../types/index.js';
import { upsertScore, updateOpportunityStatus } from '../db/database.js';

export interface ProbabilityEstimate {
  natural_recovery_prob: number;
  intervention_recovery_prob: number;
  incremental_prob: number;
}

export interface CostBreakdown {
  operational_cost_paise: number;
  fatigue_cost_paise: number;
  total_cost_paise: number;
}

/**
 * Starter hand-coded probability tables
 * Note: All probabilities are model-estimated counterfactuals.
 */
export function estimateProbabilities(opp: RecoveryOpportunity): ProbabilityEstimate {
  const reason = (opp.reason_code || '').toLowerCase();
  const declineType = opp.decline_type;

  let natural = 0.10;
  let intervention = 0.10;

  if (declineType === 'hard') {
    // Hard declines have near-zero natural or intervention recovery
    natural = 0.02;
    intervention = 0.02;
  } else if (reason.includes('insufficient_funds')) {
    // Insufficient funds: customers often fund account after notification
    natural = 0.35;
    intervention = 0.55;
  } else if (reason.includes('expired_card') || reason.includes('card_expired')) {
    // Expired card: low natural auto-recovery, very high with direct payment link
    natural = 0.05;
    intervention = 0.60;
  } else if (
    reason.includes('generic_decline') ||
    reason.includes('do_not_honor') ||
    reason.includes('transaction_not_permitted') ||
    reason.includes('declined_by_bank')
  ) {
    // Generic bank blocks / do not honor
    natural = 0.25;
    intervention = 0.45;
  } else if (
    reason.includes('timeout') ||
    reason.includes('network') ||
    reason.includes('gateway') ||
    reason.includes('bank_gateway_timeout')
  ) {
    // Bank timeouts: high natural recovery (system comes back up)
    natural = 0.60;
    intervention = 0.70;
  } else if (declineType === 'unknown') {
    // Unknown unmapped decline
    natural = 0.10;
    intervention = 0.10;
  } else {
    // Default soft decline fallback
    natural = 0.25;
    intervention = 0.45;
  }

  const incremental = Math.max(0, Number((intervention - natural).toFixed(4)));

  return {
    natural_recovery_prob: natural,
    intervention_recovery_prob: intervention,
    incremental_prob: incremental,
  };
}

/**
 * Calculates operational delivery cost and customer fatigue penalties
 * 
 * Fatigue cost curve:
 * - Attempt 1: 0 paise (₹0.00)
 * - Attempt 2: 250 paise (₹2.50)
 * - Attempt 3: 750 paise (₹7.50)
 * - Attempt 4+: 1500 paise (₹15.00) + 500 paise per subsequent attempt
 */
export function calculateCosts(attemptCount: number): CostBreakdown {
  const operational_cost_paise = 400; // Fixed ₹4.00 per payment link

  let fatigue_cost_paise = 0;
  if (attemptCount <= 1) {
    fatigue_cost_paise = 0;
  } else if (attemptCount === 2) {
    fatigue_cost_paise = 250;
  } else if (attemptCount === 3) {
    fatigue_cost_paise = 750;
  } else {
    fatigue_cost_paise = 1500 + (attemptCount - 4) * 500;
  }

  return {
    operational_cost_paise,
    fatigue_cost_paise,
    total_cost_paise: operational_cost_paise + fatigue_cost_paise,
  };
}

/**
 * Computes confidence level based on decline determinism and attempt history
 * - low: unknown decline OR attempt_count >= 3
 * - high: hard decline OR bank timeout (clear-cut outcomes)
 * - medium: standard soft declines at attempts 1-2
 */
export function determineConfidence(opp: RecoveryOpportunity): ConfidenceLevel {
  const reason = (opp.reason_code || '').toLowerCase();
  const isBankTimeout =
    reason.includes('timeout') ||
    reason.includes('network') ||
    reason.includes('bank_gateway_timeout');

  if (opp.decline_type === 'unknown' || opp.attempt_count >= 3) {
    return 'low';
  }

  if (opp.decline_type === 'hard' || isBankTimeout) {
    return 'high';
  }

  return 'medium';
}

/**
 * Full scoring calculation for an opportunity
 * Computes IVEN (Expected Incremental Value) = incremental_prob * amount - costs
 */
export function calculateScore(opp: RecoveryOpportunity): Score {
  const probs = estimateProbabilities(opp);
  const costs = calculateCosts(opp.attempt_count || 1);
  const confidence = determineConfidence(opp);

  // IVEN = (incremental_prob * amount_paise) - operational_cost - fatigue_cost
  const expectedIncrementalGross = probs.incremental_prob * opp.amount_paise;
  const expected_incremental_value_paise = Math.round(
    expectedIncrementalGross - costs.operational_cost_paise - costs.fatigue_cost_paise
  );

  return {
    opportunity_id: opp.id,
    natural_recovery_prob: probs.natural_recovery_prob,
    intervention_recovery_prob: probs.intervention_recovery_prob,
    incremental_prob: probs.incremental_prob,
    operational_cost_paise: costs.operational_cost_paise,
    fatigue_cost_paise: costs.fatigue_cost_paise,
    expected_incremental_value_paise,
    confidence,
  };
}

/**
 * Scores an opportunity, saves to SQLite scores table, and updates opportunity status
 */
export function scoreOpportunity(opp: RecoveryOpportunity): Score {
  const score = calculateScore(opp);
  upsertScore(score);

  if (opp.status === 'pending') {
    updateOpportunityStatus(opp.id, 'scored');
  }

  return score;
}
