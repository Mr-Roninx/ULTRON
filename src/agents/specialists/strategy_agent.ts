import { AgentLearningEngine } from '../learning.js';
import { AgentToolRegistry } from '../tool_registry.js';
import { AgentProposalRecord } from '../types.js';

export class StrategyAgent {
  public static async evaluateStrategyCalibration(params: {
    runId: string;
    opportunityId?: string;
  }): Promise<{
    eligible: boolean;
    statistics: any;
    proposal?: AgentProposalRecord;
    message: string;
  }> {
    const stats = AgentLearningEngine.getCalibrationStatistics();
    const oppId = params.opportunityId || 'global_calibration';

    if (stats.total_outcomes < AgentLearningEngine.EVIDENCE_THRESHOLD) {
      return {
        eligible: false,
        statistics: stats,
        message: `Insufficient empirical evidence (${stats.total_outcomes}/${AgentLearningEngine.EVIDENCE_THRESHOLD} outcomes). Policy updates blocked.`,
      };
    }

    // If empirical recovery rate deviates from predicted baseline, propose calibration
    const proposedDelta = Number((stats.empirical_recovery_rate - 0.45).toFixed(4));

    const toolRes = await AgentToolRegistry.executeTool({
      toolId: 'create_strategy_proposal',
      runId: params.runId,
      agentName: 'StrategyAgent',
      inputPayload: {
        run_id: params.runId,
        opportunity_id: oppId,
        proposed_intervention_prob_delta: proposedDelta,
        empirical_sample_size: stats.total_outcomes,
        justification: `Empirical recovery rate (${stats.empirical_recovery_rate}) over ${stats.total_outcomes} outcomes indicates model calibration shift.`,
      },
    });

    return {
      eligible: true,
      statistics: stats,
      proposal: toolRes.data,
      message: `Strategy proposal created for operator review based on ${stats.total_outcomes} validated outcomes.`,
    };
  }
}
