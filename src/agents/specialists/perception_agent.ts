import { RecoveryOpportunity } from '../../types/index.js';
import { AgentToolRegistry } from '../tool_registry.js';
import { PerceptionAnnotationRecord } from '../types.js';
import { getPerceptionAnnotationByOpportunityId } from '../../db/database.js';

export class PerceptionAgent {
  public static async analyzeOpportunity(params: {
    runId: string;
    opportunity: RecoveryOpportunity;
  }): Promise<PerceptionAnnotationRecord> {
    const existing = getPerceptionAnnotationByOpportunityId(params.opportunity.id);
    if (existing) return existing;

    const reason = (params.opportunity.reason_code || '').toLowerCase();
    const isHard = params.opportunity.decline_type === 'hard';

    // Call bounded tools to inspect context
    await AgentToolRegistry.executeTool({
      toolId: 'get_payment_attempts',
      runId: params.runId,
      agentName: 'PerceptionAgent',
      inputPayload: { opportunity_id: params.opportunity.id },
    });

    let failureIntent = 'Temporary lack of liquid funds';
    let urgencyScore = 0.6;
    let riskScore = 0.2;
    let confidence = 0.85;

    if (isHard) {
      failureIntent = 'Reported card stolen or issuer security stop';
      urgencyScore = 0.1;
      riskScore = 0.95;
      confidence = 0.95;
    } else if (reason.includes('timeout') || reason.includes('gateway')) {
      failureIntent = 'Bank gateway switch latency / network congestion';
      urgencyScore = 0.8;
      riskScore = 0.1;
      confidence = 0.90;
    } else if (params.opportunity.attempt_count >= 3) {
      failureIntent = 'Persistent payment decline, customer contact fatigue elevated';
      urgencyScore = 0.3;
      riskScore = 0.7;
      confidence = 0.80;
    }

    const toolRes = await AgentToolRegistry.executeTool({
      toolId: 'create_perception_annotation',
      runId: params.runId,
      agentName: 'PerceptionAgent',
      inputPayload: {
        opportunity_id: params.opportunity.id,
        failure_intent: failureIntent,
        customer_urgency_score: urgencyScore,
        merchant_risk_score: riskScore,
        semantic_notes: `Perception Agent evaluated reason '${params.opportunity.reason_code}' at attempt ${params.opportunity.attempt_count}.`,
        confidence,
      },
    });

    return {
      id: toolRes.data?.id || `annot_${params.opportunity.id}`,
      opportunity_id: params.opportunity.id,
      failure_intent: failureIntent,
      customer_urgency_score: urgencyScore,
      merchant_risk_score: riskScore,
      semantic_notes: `Perception Agent evaluated reason '${params.opportunity.reason_code}' at attempt ${params.opportunity.attempt_count}.`,
      confidence,
      created_at: new Date().toISOString(),
    };
  }
}
