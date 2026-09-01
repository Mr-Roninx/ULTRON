import { Router, Request, Response } from 'express';
import { executeAuthorizedBatch, executeOpportunity } from '../execution/executor.js';
import { getAllExecutionRecords, getExecutionRecordByOpportunityId } from '../db/database.js';

export const executionRouter = Router();

// POST /execution/run
executionRouter.post('/run', async (req: Request, res: Response) => {
  try {
    const maxLinks = req.body.maxLinks !== undefined ? Number(req.body.maxLinks) : undefined;
    const capacity = req.body.capacity !== undefined ? Number(req.body.capacity) : undefined;

    const result = await executeAuthorizedBatch({ maxLinks, capacity });
    res.json(result);
  } catch (error: any) {
    console.error('Failed to execute authorized batch:', error);
    res.status(500).json({ error: error?.message || 'Failed to execute authorized batch' });
  }
});

// POST /execution/opportunity/:id
executionRouter.post('/opportunity/:id', async (req: Request, res: Response) => {
  try {
    const oppId = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;
    if (!oppId) {
      res.status(400).json({ error: 'Missing opportunity ID' });
      return;
    }

    const result = await executeOpportunity(oppId);
    res.json(result);
  } catch (error: any) {
    console.error(`Failed to execute opportunity ${req.params.id}:`, error);
    res.status(403).json({ error: error?.message || 'Execution prohibited by authority or failed' });
  }
});

// GET /execution/records
executionRouter.get('/records', (req: Request, res: Response) => {
  try {
    const tenantId = (req as any).user?.tenantId || (req as any).user?.merchant_id;
    const records = getAllExecutionRecords(tenantId);
    res.json({
      count: records.length,
      records,
    });
  } catch (error) {
    console.error('Failed to fetch execution records:', error);
    res.status(500).json({ error: 'Failed to fetch execution records' });
  }
});

// GET /execution/records/:id
executionRouter.get('/records/:id', (req: Request, res: Response) => {
  try {
    const oppId = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;
    if (!oppId) {
      res.status(400).json({ error: 'Missing opportunity ID' });
      return;
    }

    const record = getExecutionRecordByOpportunityId(oppId);
    if (!record) {
      res.status(404).json({ error: 'Execution record not found' });
      return;
    }

    res.json(record);
  } catch (error) {
    console.error('Failed to fetch execution record:', error);
    res.status(500).json({ error: 'Failed to fetch execution record' });
  }
});
