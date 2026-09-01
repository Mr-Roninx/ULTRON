import { AgentToolRegistry } from '../tool_registry.js';

export interface ForensicAuditClaim {
  table: string;
  record_id: string;
  field: string;
  value: any;
  explanation: string;
}

export interface ComplianceExplanationResult {
  opportunity_id: string;
  audit_verified: boolean;
  claims: ForensicAuditClaim[];
  structured_summary: {
    economic_rationale: string;
    market_capacity_rationale: string;
    authority_compliance_rationale: string;
  };
  generated_at: string;
}

export class ComplianceCopilot {
  /**
   * Explains an opportunity decision strictly by reading durable SQLite records through get_full_audit_trail tool.
   */
  public static async explainOpportunity(params: {
    runId: string;
    opportunityId: string;
  }): Promise<ComplianceExplanationResult> {
    const auditRes = await AgentToolRegistry.executeTool({
      toolId: 'get_full_audit_trail',
      runId: params.runId,
      agentName: 'ComplianceCopilot',
      inputPayload: { opportunity_id: params.opportunityId },
    });

    if (!auditRes.success || !auditRes.data) {
      throw new Error(`Compliance Copilot could not retrieve audit trail for opportunity ${params.opportunityId}: ${auditRes.error}`);
    }

    const trail = auditRes.data;
    const opp = trail.opportunity;
    const score = trail.score;
    const decision = trail.decision;
    const checks = trail.authority_checks || [];

    const amountInr = `₹${(opp.amount_paise / 100).toFixed(2)}`;
    const ivenInr = score ? `₹${(score.expected_incremental_value_paise / 100).toFixed(2)}` : 'N/A';
    const shadowPriceInr = decision ? `₹${(decision.shadow_price_paise_at_decision / 100).toFixed(2)}` : 'N/A';

    const claims: ForensicAuditClaim[] = [
      {
        table: 'recovery_opportunities',
        record_id: opp.id,
        field: 'amount_paise',
        value: opp.amount_paise,
        explanation: `Amount at risk is ${amountInr} (${opp.amount_paise} paise).`,
      },
      {
        table: 'recovery_opportunities',
        record_id: opp.id,
        field: 'decline_type',
        value: opp.decline_type,
        explanation: `Decline classified under perception taxonomy as '${opp.decline_type}'.`,
      },
      {
        table: 'scores',
        record_id: opp.id,
        field: 'expected_incremental_value_paise',
        value: score?.expected_incremental_value_paise ?? null,
        explanation: `Deterministic Expected Incremental Value (IVEN) computed at ${ivenInr}.`,
      },
      {
        table: 'allocation_decisions',
        record_id: opp.id,
        field: 'decision',
        value: decision?.decision || 'PENDING',
        explanation: `Portfolio recovery market assigned action '${decision?.decision || 'PENDING'}' at rank #${decision?.rank_in_batch ?? '-'}.`,
      },
    ];

    for (const check of checks) {
      claims.push({
        table: 'authority_checks',
        record_id: `${opp.id}:${check.check_name}`,
        field: 'passed',
        value: check.passed,
        explanation: `Compliance check '${check.check_name}': ${check.passed ? 'PASSED' : 'FAILED'} (${check.reason}).`,
      });
    }

    const economicRationale = `Opportunity ${opp.id} (${amountInr}, ${opp.decline_type} decline) evaluated with natural recovery probability ${score?.natural_recovery_prob ?? 'N/A'} and intervention recovery probability ${score?.intervention_recovery_prob ?? 'N/A'}, generating incremental probability of ${score?.incremental_prob ?? 'N/A'} and net IVEN of ${ivenInr}.`;

    const marketRationale = decision
      ? `Ranked #${decision.rank_in_batch} in batch with market shadow price ${shadowPriceInr}. Resulting allocation: ${decision.decision} (${decision.reason}).`
      : 'Market allocation pending.';

    const passedCount = checks.filter((c: any) => c.passed).length;
    const authRationale = `Action Authority independently evaluated ${checks.length} compliance checks (${passedCount}/${checks.length} passed). Final status: ${opp.status}.`;

    return {
      opportunity_id: opp.id,
      audit_verified: true,
      claims,
      structured_summary: {
        economic_rationale: economicRationale,
        market_capacity_rationale: marketRationale,
        authority_compliance_rationale: authRationale,
      },
      generated_at: new Date().toISOString(),
    };
  }
}
