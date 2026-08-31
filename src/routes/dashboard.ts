import { Router, Request, Response } from 'express';
import {
  getAllOpportunities,
  getAllExecutionRecords,
  getAllAllocationDecisions,
} from '../db/database.js';
import { isKillSwitchActive } from '../authority/gate.js';
import { pollAndReconcile } from '../reconciliation/poller.js';

export const dashboardRouter = Router();

// GET /dashboard/summary
dashboardRouter.get('/summary', (_req: Request, res: Response) => {
  try {
    const allOpps = getAllOpportunities();
    const decisions = getAllAllocationDecisions();
    const executionRecords = getAllExecutionRecords();

    // 1. Total Opportunities
    const total_opportunities = allOpps.length;

    // 2. Total Amount at Risk
    const total_at_risk_paise = allOpps.reduce((sum, o) => sum + o.amount_paise, 0);

    // 3. Total Recovered (CRITICAL CONTRACT RULE: Real, reconciled payments ONLY)
    const realRecoveredOpps = allOpps.filter(
      (o) => o.source === 'real' && o.status === 'recovered'
    );
    const total_recovered_paise = realRecoveredOpps.reduce((sum, o) => sum + o.amount_paise, 0);

    const syntheticRecoveredOpps = allOpps.filter(
      (o) => o.source === 'synthetic' && o.status === 'recovered'
    );
    const synthetic_recovered_paise = syntheticRecoveredOpps.reduce((sum, o) => sum + o.amount_paise, 0);

    // 4. Shadow Price (from latest allocation decision)
    const shadowPriceDecision = decisions.find((d) => d.shadow_price_paise_at_decision > 0);
    const shadow_price_paise = shadowPriceDecision ? shadowPriceDecision.shadow_price_paise_at_decision : 0;

    // 5. Capacity
    const capacity_limit = Number(process.env.MAX_LINKS_PER_RUN) || 5;
    const capacity_used = allOpps.filter(
      (o) => o.status === 'executing' || o.status === 'recovered' || o.status === 'allocated' || o.status === 'authorized'
    ).length;

    // 6. Status distribution
    const status_counts: Record<string, number> = {};
    for (const opp of allOpps) {
      status_counts[opp.status] = (status_counts[opp.status] || 0) + 1;
    }

    res.json({
      total_opportunities,
      total_at_risk_paise,
      total_at_risk_display: `₹${(total_at_risk_paise / 100).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      total_recovered_paise,
      total_recovered_display: `₹${(total_recovered_paise / 100).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      real_recovered_count: realRecoveredOpps.length,
      synthetic_recovered_count: syntheticRecoveredOpps.length,
      synthetic_recovered_paise,
      shadow_price_paise,
      shadow_price_display: `₹${(shadow_price_paise / 100).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      capacity_limit,
      capacity_used,
      capacity_available: Math.max(0, capacity_limit - capacity_used),
      kill_switch_active: isKillSwitchActive(),
      status_counts,
      total_execution_records: executionRecords.length,
      _note: 'total_recovered_display contains STRICTLY real reconciled payments as required by contract.',
    });
  } catch (error) {
    console.error('Failed to compute dashboard summary:', error);
    res.status(500).json({ error: 'Failed to compute dashboard summary' });
  }
});

// POST /dashboard/reconcile-poll
dashboardRouter.post('/reconcile-poll', async (_req: Request, res: Response) => {
  try {
    const result = await pollAndReconcile();
    res.json(result);
  } catch (error: any) {
    console.error('Failed to run reconciliation poller:', error);
    res.status(500).json({ error: error?.message || 'Reconciliation poll failed' });
  }
});
