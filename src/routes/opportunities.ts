import { Router, Request, Response } from 'express';
import {
  getAllOpportunities,
  getOpportunityById,
  getLedgerEntriesByOpportunity,
  getCustomerById,
  getScoreByOpportunityId,
} from '../db/database.js';
import { scoreOpportunity } from '../economics/scorer.js';

export const opportunitiesRouter = Router();

// GET all opportunities
opportunitiesRouter.get('/', (_req: Request, res: Response) => {
  try {
    const opportunities = getAllOpportunities();
    res.json({
      count: opportunities.length,
      opportunities,
    });
  } catch (error) {
    console.error('Failed to fetch opportunities:', error);
    res.status(500).json({ error: 'Failed to fetch recovery opportunities' });
  }
});

// POST score all opportunities
opportunitiesRouter.post('/score-all', (_req: Request, res: Response) => {
  try {
    const opportunities = getAllOpportunities();
    const scoredList = opportunities.map((opp) => scoreOpportunity(opp));
    res.json({
      success: true,
      count: scoredList.length,
      scores: scoredList,
    });
  } catch (error) {
    console.error('Failed to score opportunities:', error);
    res.status(500).json({ error: 'Failed to score opportunities' });
  }
});

// GET single opportunity score breakdown (Feature 3 & 7 "Why?" panel data source)
opportunitiesRouter.get('/:id/score', (req: Request, res: Response) => {
  try {
    const oppId = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;
    if (!oppId) {
      res.status(400).json({ error: 'Missing opportunity ID' });
      return;
    }

    const opp = getOpportunityById(oppId);
    if (!opp) {
      res.status(404).json({ error: 'Opportunity not found' });
      return;
    }

    // Fetch existing or compute on-the-fly
    let score = getScoreByOpportunityId(oppId);
    if (!score) {
      score = scoreOpportunity(opp);
    }

    res.json({
      opportunity_id: score.opportunity_id,
      amount_paise: opp.amount_paise,
      currency: opp.currency,
      decline_type: opp.decline_type,
      reason_code: opp.reason_code,
      attempt_count: opp.attempt_count,
      natural_recovery_prob: score.natural_recovery_prob,
      intervention_recovery_prob: score.intervention_recovery_prob,
      incremental_prob: score.incremental_prob,
      operational_cost_paise: score.operational_cost_paise,
      fatigue_cost_paise: score.fatigue_cost_paise,
      expected_incremental_value_paise: score.expected_incremental_value_paise,
      confidence: score.confidence,
      _labels: {
        natural_recovery_prob: 'model-estimated',
        intervention_recovery_prob: 'model-estimated',
        incremental_prob: 'model-estimated',
        expected_incremental_value_paise: 'model-estimated',
      },
    });
  } catch (error) {
    console.error('Failed to fetch opportunity score:', error);
    res.status(500).json({ error: 'Failed to fetch opportunity score' });
  }
});

// GET single opportunity with full details
opportunitiesRouter.get('/:id', (req: Request, res: Response) => {
  try {
    const oppId = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;
    if (!oppId) {
      res.status(400).json({ error: 'Missing opportunity ID' });
      return;
    }

    const opp = getOpportunityById(oppId);
    if (!opp) {
      res.status(404).json({ error: 'Opportunity not found' });
      return;
    }

    const score = getScoreByOpportunityId(oppId);
    const customer = opp.customer_id ? getCustomerById(opp.customer_id) : undefined;
    const ledger = getLedgerEntriesByOpportunity(oppId);

    res.json({
      opportunity: opp,
      score,
      customer,
      ledger,
    });
  } catch (error) {
    console.error('Failed to fetch opportunity:', error);
    res.status(500).json({ error: 'Failed to fetch opportunity' });
  }
});
