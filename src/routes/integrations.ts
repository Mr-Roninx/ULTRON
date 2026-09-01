import { Router, Response } from 'express';
import { TenancyEnforcer, TenantScopedRequest } from '../security/tenancy.js';
import { RazorpayConnectionService } from '../providers/razorpay/connection_service.js';

export const integrationsRouter = Router();

// 1. POST /v1/integrations - Configure Provider Credentials (Requires integrations:write scope)
integrationsRouter.post(
  '/',
  TenancyEnforcer.authenticateTenant('integrations:write'),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const tenantContext = req.tenantContext!;
      const { provider, environment, key_id, key_secret, webhook_secret } = req.body;

      if (provider !== 'razorpay') {
        res.status(400).json({ error: 'Unsupported provider', message: 'Only razorpay is currently supported.' });
        return;
      }

      if (!key_id || !key_secret) {
        res.status(400).json({ error: 'Validation Error', message: 'key_id and key_secret are required.' });
        return;
      }

      const env = environment === 'live' ? 'live' : 'test';

      const result = await RazorpayConnectionService.registerConnection({
        tenantId: tenantContext.tenantId,
        environment: env,
        keyId: key_id,
        keySecret: key_secret,
        webhookSecret: webhook_secret,
      });

      res.status(201).json({
        success: true,
        message: 'Provider credentials encrypted and saved successfully.',
        tenant_id: tenantContext.tenantId,
        provider: 'razorpay',
        environment: env,
        connection_id: result.connectionId,
      });
    } catch (err: any) {
      res.status(500).json({ error: 'Internal Server Error', details: err.message });
    }
  }
);

// 2. POST /v1/integrations/verify - Verify Connection & Discover Capabilities
integrationsRouter.post(
  '/verify',
  TenancyEnforcer.authenticateTenant('integrations:write'),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const tenantContext = req.tenantContext!;
      const env = req.body.environment === 'live' ? 'live' : 'test';
      const credRef = `ref_rzp_${tenantContext.tenantId}_${env}`;

      const verification = await RazorpayConnectionService.verifyConnection(
        tenantContext.tenantId,
        env,
        credRef
      );

      res.json({
        tenant_id: tenantContext.tenantId,
        provider: 'razorpay',
        environment: env,
        ...verification,
      });
    } catch (err: any) {
      res.status(500).json({ error: 'Internal Server Error', details: err.message });
    }
  }
);

// 3. GET /v1/integrations/capabilities - Retrieve Gated Capabilities
integrationsRouter.get(
  '/capabilities',
  TenancyEnforcer.authenticateTenant('integrations:read'),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const tenantContext = req.tenantContext!;
      const env = req.query.environment === 'live' ? 'live' : 'test';
      const credRef = `ref_rzp_${tenantContext.tenantId}_${env}`;

      const verification = await RazorpayConnectionService.verifyConnection(
        tenantContext.tenantId,
        env,
        credRef
      );

      res.json({
        tenant_id: tenantContext.tenantId,
        provider: 'razorpay',
        environment: env,
        capabilities: verification.capabilities,
      });
    } catch (err: any) {
      res.status(500).json({ error: 'Internal Server Error', details: err.message });
    }
  }
);

// 4. GET /v1/integrations/connections - List All Connections
integrationsRouter.get(
  '/connections',
  TenancyEnforcer.authenticateTenant('integrations:read'),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const tenantContext = req.tenantContext!;
      const connections = await RazorpayConnectionService.listConnections(tenantContext.tenantId);
      
      // Attempt verification to discover capabilities
      const verifiedConnections = await Promise.all(
        connections.map(async (conn) => {
          const credRef = `ref_rzp_${tenantContext.tenantId}_${conn.environment}`;
          const verification = await RazorpayConnectionService.verifyConnection(
            tenantContext.tenantId,
            conn.environment as any,
            credRef
          );
          
          return {
            ...conn,
            status: verification.status,
            capabilities: verification.capabilities,
          };
        })
      );
      
      res.json({
        connections: verifiedConnections,
      });
    } catch (err: any) {
      res.status(500).json({ error: 'Internal Server Error', details: err.message });
    }
  }
);

// 5. POST /v1/integrations/razorpay/connect - Razorpay Connect Helper
integrationsRouter.post(
  '/razorpay/connect',
  TenancyEnforcer.authenticateTenant('integrations:write'),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const tenantContext = req.tenantContext!;
      const { environment, key_id, key_secret, webhook_secret } = req.body;

      if (!key_id || !key_secret) {
        res.status(400).json({ error: 'Validation Error', message: 'key_id and key_secret are required.' });
        return;
      }

      const env = environment === 'live' ? 'live' : 'test';

      const result = await RazorpayConnectionService.registerConnection({
        tenantId: tenantContext.tenantId,
        environment: env,
        keyId: key_id,
        keySecret: key_secret,
        webhookSecret: webhook_secret,
      });

      res.status(201).json({
        success: true,
        message: 'Razorpay credentials verified and saved successfully.',
        tenant_id: tenantContext.tenantId,
        environment: env,
        connection_id: result.connectionId,
      });
    } catch (err: any) {
      res.status(500).json({
        error: 'Failed to connect Razorpay account',
        message: err.message || 'Unknown database or encryption error',
        details: err.message,
      });
    }
  }
);
