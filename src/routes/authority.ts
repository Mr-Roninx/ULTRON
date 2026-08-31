import { Router, Request, Response } from 'express';
import {
  isKillSwitchActive,
  setKillSwitch,
  runAuthorityPipeline,
} from '../authority/gate.js';

export const authorityRouter = Router();

// GET /authority/kill-switch
authorityRouter.get('/kill-switch', (_req: Request, res: Response) => {
  res.json({
    kill_switch_active: isKillSwitchActive(),
    status: isKillSwitchActive() ? 'ENGAGED (ALL ACTIONS BLOCKED)' : 'DISENGAGED (NORMAL OPERATION)',
  });
});

// POST /authority/kill-switch
authorityRouter.post('/kill-switch', (req: Request, res: Response) => {
  try {
    const { enabled } = req.body;
    if (typeof enabled !== 'boolean') {
      res.status(400).json({ error: 'Missing or invalid boolean "enabled" in request body' });
      return;
    }

    const state = setKillSwitch(enabled);
    res.json({
      success: true,
      kill_switch_active: state,
      status: state ? 'ENGAGED (ALL ACTIONS BLOCKED)' : 'DISENGAGED (NORMAL OPERATION)',
    });
  } catch (error) {
    console.error('Failed to toggle kill switch:', error);
    res.status(500).json({ error: 'Failed to toggle kill switch' });
  }
});

// GET /authority/run?capacity=5
authorityRouter.get('/run', (req: Request, res: Response) => {
  try {
    const capacityParam = req.query.capacity as string | undefined;
    const capacity = capacityParam ? parseInt(capacityParam, 10) : undefined;

    const result = runAuthorityPipeline({ capacity });
    res.json(result);
  } catch (error) {
    console.error('Failed to run authority pipeline:', error);
    res.status(500).json({ error: 'Failed to run authority pipeline' });
  }
});

// POST /authority/run
authorityRouter.post('/run', (req: Request, res: Response) => {
  try {
    const capacity = req.body.capacity !== undefined ? Number(req.body.capacity) : undefined;
    const result = runAuthorityPipeline({ capacity });
    res.json(result);
  } catch (error) {
    console.error('Failed to execute authority pipeline:', error);
    res.status(500).json({ error: 'Failed to execute authority pipeline' });
  }
});
