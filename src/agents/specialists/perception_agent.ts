import { RecoveryOpportunity } from '../../types/index.js';
import { AgentToolRegistry } from '../tool_registry.js';
import { PerceptionAnnotationRecord } from '../types.js';
import { getPerceptionAnnotationByOpportunityId } from '../../db/database.js';

export class PerceptionAgent {
  /**
   * Translates bank-specific decline codes into standardized semantic failure modes.
   */
  public static translateBankDeclineCode(rawCode: string): {
    normalized_reason: string;
    is_hard: boolean;
    category: 'INSUFFICIENT_FUNDS' | 'NETWORK_LATENCY' | 'SECURITY_STOP' | 'USER_ABORT' | 'UNKNOWN';
  } {
    const code = (rawCode || '').toUpperCase().trim();

    // HDFC bank decline maps
    if (code === 'DECLINE_05' || code === 'DECLINE_51' || code === 'ERR_BAL_51' || code === 'INSUFFICIENT_FUNDS') {
      return { normalized_reason: 'INSUFFICIENT_FUNDS', is_hard: false, category: 'INSUFFICIENT_FUNDS' };
    }
    if (code === 'DECLINE_91' || code === 'ERR_AUTH_99' || code === 'GATEWAY_TIMEOUT' || code === 'NETWORK_ERROR') {
      return { normalized_reason: 'GATEWAY_ERROR', is_hard: false, category: 'NETWORK_LATENCY' };
    }
    if (code === 'ERR_CARD_43' || code === 'STOLEN_CARD' || code === 'LOST_CARD' || code === 'CARD_EXPIRED') {
      return { normalized_reason: 'STOLEN_CARD', is_hard: true, category: 'SECURITY_STOP' };
    }
    if (code === 'USER_CANCELLED' || code === 'OTP_EXPIRED') {
      return { normalized_reason: 'USER_DROPPED', is_hard: false, category: 'USER_ABORT' };
    }

    return { normalized_reason: code || 'UNKNOWN_ERROR', is_hard: false, category: 'UNKNOWN' };
  }

  /**
   * Extracts temporal features: salary window, banking maintenance hours.
   */
  public static extractTemporalSignals(timestamp?: string): {
    is_salary_window: boolean;
    is_maintenance_window: boolean;
    liquidity_multiplier: number;
  } {
    const date = timestamp ? new Date(timestamp) : new Date();
    // Indian Standard Time (UTC+5.5)
    const istTime = new Date(date.getTime() + 5.5 * 3600 * 1000);
    const day = istTime.getUTCDate();
    const hour = istTime.getUTCHours();
    const minute = istTime.getUTCMinutes();

    // Indian salary cycle: 28th to 5th of month
    const isSalaryWindow = day >= 28 || day <= 5;

    // Banking settlement & NPCI maintenance hours: 11:30 PM to 2:30 AM IST
    const isMaintenance = (hour === 23 && minute >= 30) || hour === 0 || hour === 1 || (hour === 2 && minute <= 30);

    return {
      is_salary_window: isSalaryWindow,
      is_maintenance_window: isMaintenance,
      liquidity_multiplier: isSalaryWindow ? 1.25 : 0.90,
    };
  }

  public static async analyzeOpportunity(params: {
    runId: string;
    opportunity: RecoveryOpportunity;
  }): Promise<PerceptionAnnotationRecord> {
    const existing = getPerceptionAnnotationByOpportunityId(params.opportunity.id);
    if (existing) return existing;

    const bankTranslation = this.translateBankDeclineCode(params.opportunity.reason_code);
    const temporal = this.extractTemporalSignals(params.opportunity.created_at);
    const isHard = params.opportunity.decline_type === 'hard' || bankTranslation.is_hard;

    // Call bounded tools to inspect context
    await AgentToolRegistry.executeTool({
      toolId: 'get_payment_attempts',
      runId: params.runId,
      agentName: 'PerceptionAgent',
      inputPayload: { opportunity_id: params.opportunity.id },
    });

    let failureIntent = 'Temporary liquidity deficit';
    let urgencyScore = 0.6;
    let riskScore = 0.2;
    let confidence = 0.85;

    if (isHard) {
      failureIntent = 'Reported stolen card, issuer security block, or account freeze';
      urgencyScore = 0.05;
      riskScore = 0.98;
      confidence = 0.98;
    } else if (bankTranslation.category === 'NETWORK_LATENCY' || temporal.is_maintenance_window) {
      failureIntent = temporal.is_maintenance_window
        ? 'NPCI/Banking maintenance window congestion — high spontaneous recovery'
        : 'Bank gateway switch latency / network congestion';
      urgencyScore = 0.85;
      riskScore = 0.10;
      confidence = 0.92;
    } else if (params.opportunity.attempt_count >= 3) {
      failureIntent = 'Persistent payment decline, customer contact fatigue elevated';
      urgencyScore = 0.30;
      riskScore = 0.70;
      confidence = 0.80;
    } else if (temporal.is_salary_window) {
      failureIntent = 'Payday window liquidity active — elevated conversion propensity';
      urgencyScore = 0.75;
      riskScore = 0.15;
      confidence = 0.88;
    }

    const notes = `Perception Agent: [Normalized: ${bankTranslation.normalized_reason}] [Category: ${bankTranslation.category}] [SalaryWindow: ${temporal.is_salary_window}] [Maintenance: ${temporal.is_maintenance_window}]. Attempt: ${params.opportunity.attempt_count}.`;

    const toolRes = await AgentToolRegistry.executeTool({
      toolId: 'create_perception_annotation',
      runId: params.runId,
      agentName: 'PerceptionAgent',
      inputPayload: {
        opportunity_id: params.opportunity.id,
        failure_intent: failureIntent,
        customer_urgency_score: urgencyScore,
        merchant_risk_score: riskScore,
        semantic_notes: notes,
        confidence,
      },
    });

    return {
      id: toolRes.data?.id || `annot_${params.opportunity.id}`,
      opportunity_id: params.opportunity.id,
      failure_intent: failureIntent,
      customer_urgency_score: urgencyScore,
      merchant_risk_score: riskScore,
      semantic_notes: notes,
      confidence,
      created_at: new Date().toISOString(),
    };
  }
}
