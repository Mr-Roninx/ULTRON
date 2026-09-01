import { Router, Request, Response } from 'express';
import { DatabaseAdapter } from '../db/adapter.js';

export const auditRouter = Router();

// GET /audit/records
auditRouter.get('/records', async (req: Request, res: Response) => {
  try {
    const db = DatabaseAdapter.getInstance();
    const tenantId = (req as any).user?.tenantId || (req as any).user?.merchant_id || 'tenant_system_default';
    
    // Fetch audit_records
    const records = await db.query<any>(
      `SELECT * FROM audit_records WHERE tenant_id = ? ORDER BY timestamp DESC LIMIT 50;`,
      [tenantId]
    );

    // Also fetch ledger_entries if available
    const ledger = await db.query<any>(
      `SELECT * FROM ledger_entries ORDER BY timestamp DESC LIMIT 50;`
    ).catch(() => []);

    res.json({
      count: records.length,
      records,
      ledger,
    });
  } catch (error: any) {
    console.error('Failed to fetch audit records:', error);
    res.status(500).json({ error: 'Failed to fetch audit records', details: error.message });
  }
});
