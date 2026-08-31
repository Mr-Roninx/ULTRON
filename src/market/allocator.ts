import {
  getAllOpportunities,
  getScoreByOpportunityId,
  upsertAllocationDecision,
  updateOpportunityStatus,
} from '../db/database.js';
import { scoreOpportunity } from '../economics/scorer.js';
import {
  RecoveryOpportunity,
  Score,
  AllocationDecision,
  DecisionType,
} from '../types/index.js';

export interface OpportunityWithScore {
  opportunity: RecoveryOpportunity;
  score: Score;
}

export interface MarketAllocationItem {
  opportunity_id: string;
  amount_paise: number;
  currency: string;
  reason_code: string;
  decline_type: string;
  attempt_count: number;
  incremental_prob: number;
  expected_incremental_value_paise: number;
  confidence: string;
  decision: DecisionType;
  rank_in_batch: number;
  shadow_price_paise_at_decision: number;
  reason: string;
}

export interface MarketRunResult {
  capacity: number;
  total_opportunities: number;
  eligible_count: number;
  abstained_count: number;
  accepted_count: number;
  deferred_count: number;
  shadow_price_paise: number;
  shadow_price_display: string;
  items: MarketAllocationItem[];
}

export function runMarketAllocation(options: { capacity?: number } = {}): MarketRunResult {
  const capacity =
    options.capacity !== undefined
      ? options.capacity
      : Number(process.env.MAX_LINKS_PER_RUN) || 5;

  const allOpps = getAllOpportunities();

  // 1. Fetch or compute economic scores for all opportunities
  const scoredItems: OpportunityWithScore[] = allOpps.map((opp) => {
    let score = getScoreByOpportunityId(opp.id);
    if (!score) {
      score = scoreOpportunity(opp);
    }
    return { opportunity: opp, score };
  });

  const abstainedList: { item: OpportunityWithScore; reason: string }[] = [];
  const eligibleList: OpportunityWithScore[] = [];

  // 2. Filter: Route confidence=low or IVEN <= 0 straight to ABSTAIN (never enters ranking)
  for (const entry of scoredItems) {
    const { opportunity, score } = entry;
    if (score.confidence === 'low') {
      abstainedList.push({
        item: entry,
        reason: `abstained — low confidence score (${opportunity.decline_type}, attempt ${opportunity.attempt_count})`,
      });
    } else if (score.expected_incremental_value_paise <= 0) {
      abstainedList.push({
        item: entry,
        reason: `abstained — non-positive expected incremental value (₹${(score.expected_incremental_value_paise / 100).toFixed(2)})`,
      });
    } else {
      eligibleList.push(entry);
    }
  }

  // 3. Rank remaining eligible opportunities by IVEN descending
  eligibleList.sort((a, b) => {
    return b.score.expected_incremental_value_paise - a.score.expected_incremental_value_paise;
  });

  // 4. Calculate Shadow Price = IVEN of the last allocated (marginal) opportunity
  const acceptedCount = Math.min(capacity, eligibleList.length);
  let shadowPricePaise = 0;
  if (acceptedCount > 0) {
    shadowPricePaise = eligibleList[acceptedCount - 1].score.expected_incremental_value_paise;
  }
  const shadowPriceDisplay = `₹${(shadowPricePaise / 100).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const finalItems: MarketAllocationItem[] = [];

  // 5. Assign ACT and WAIT decisions to ranked items
  for (let i = 0; i < eligibleList.length; i++) {
    const rank = i + 1;
    const { opportunity, score } = eligibleList[i];
    let decision: DecisionType;
    let reason: string;

    if (rank <= capacity) {
      decision = 'ACT';
      reason = `accepted — rank #${rank} within capacity limit of ${capacity} (marginal cutoff: ${shadowPriceDisplay})`;
      updateOpportunityStatus(opportunity.id, 'allocated');
    } else {
      decision = 'WAIT';
      reason = `deferred — below this run's marginal value of ${shadowPriceDisplay} (rank #${rank} vs cap ${capacity})`;
      updateOpportunityStatus(opportunity.id, 'deferred');
    }

    const decisionRecord: AllocationDecision = {
      opportunity_id: opportunity.id,
      decision,
      rank_in_batch: rank,
      shadow_price_paise_at_decision: shadowPricePaise,
      reason,
    };

    upsertAllocationDecision(decisionRecord);

    finalItems.push({
      opportunity_id: opportunity.id,
      amount_paise: opportunity.amount_paise,
      currency: opportunity.currency,
      reason_code: opportunity.reason_code,
      decline_type: opportunity.decline_type,
      attempt_count: opportunity.attempt_count,
      incremental_prob: score.incremental_prob,
      expected_incremental_value_paise: score.expected_incremental_value_paise,
      confidence: score.confidence,
      decision,
      rank_in_batch: rank,
      shadow_price_paise_at_decision: shadowPricePaise,
      reason,
    });
  }

  // 6. Record ABSTAIN decisions (rank_in_batch = 0)
  for (const { item, reason } of abstainedList) {
    const { opportunity, score } = item;
    const decision: DecisionType = 'ABSTAIN';
    updateOpportunityStatus(opportunity.id, 'abstained');

    const decisionRecord: AllocationDecision = {
      opportunity_id: opportunity.id,
      decision,
      rank_in_batch: 0,
      shadow_price_paise_at_decision: shadowPricePaise,
      reason,
    };

    upsertAllocationDecision(decisionRecord);

    finalItems.push({
      opportunity_id: opportunity.id,
      amount_paise: opportunity.amount_paise,
      currency: opportunity.currency,
      reason_code: opportunity.reason_code,
      decline_type: opportunity.decline_type,
      attempt_count: opportunity.attempt_count,
      incremental_prob: score.incremental_prob,
      expected_incremental_value_paise: score.expected_incremental_value_paise,
      confidence: score.confidence,
      decision,
      rank_in_batch: 0,
      shadow_price_paise_at_decision: shadowPricePaise,
      reason,
    });
  }

  return {
    capacity,
    total_opportunities: allOpps.length,
    eligible_count: eligibleList.length,
    abstained_count: abstainedList.length,
    accepted_count: Math.min(capacity, eligibleList.length),
    deferred_count: Math.max(0, eligibleList.length - capacity),
    shadow_price_paise: shadowPricePaise,
    shadow_price_display: shadowPriceDisplay,
    items: finalItems,
  };
}
