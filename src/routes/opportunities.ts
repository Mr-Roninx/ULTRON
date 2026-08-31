import { Router, Request, Response } from 'express';
import {
  getAllOpportunities,
  getOpportunityById,
  getLedgerEntriesByOpportunity,
  getCustomerById,
} from '../db/database.js';

export const opportunitiesRouter = Router();

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

    const customer = opp.customer_id ? getCustomerById(opp.customer_id) : undefined;
    const ledger = getLedgerEntriesByOpportunity(oppId);

    res.json({
      opportunity: opp,
      customer,
      ledger,
    });
  } catch (error) {
    console.error('Failed to fetch opportunity:', error);
    res.status(500).json({ error: 'Failed to fetch opportunity' });
  }
});
