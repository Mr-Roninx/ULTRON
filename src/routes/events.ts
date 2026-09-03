import { Router, Response } from 'express';
import { TenancyEnforcer, TenantScopedRequest } from '../security/tenancy.js';
import { CanonicalPaymentEventSchema, WebAppPingSchema } from '../security/schemas.js';
import { DatabaseAdapter } from '../db/adapter.js';
import { normalizeOpportunity } from '../perception/normalizer.js';
import {
  getOpportunityById,
  getOpportunityByRazorpayEventId,
  insertOpportunity,
  insertLedgerEntry,
  upsertWebAppConnection,
  getWebAppConnections,
  getAllExecutionRecords,
  insertEventIngestionLog,
  getEventIngestionLogs,
} from '../db/database.js';
import { AuthoritativeReconciler } from '../reconciliation/authoritative_reconciler.js';
import { RealtimeBroadcaster } from '../realtime/broadcaster.js';

export const eventsRouter = Router();

// 1. POST /v1/events/ping (or /sdk/ping) - Web App Connection Handshake & Heartbeat
eventsRouter.post(
  '/ping',
  TenancyEnforcer.authenticateTenant(),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const tenantContext = req.tenantContext!;
      const parseResult = WebAppPingSchema.safeParse({
        ...req.body,
        app_origin: req.body.app_origin || req.headers.origin || req.headers.referer || 'unknown_origin',
        app_url: req.body.app_url || req.headers.referer || req.headers.origin || 'unknown_url',
        user_agent: req.body.user_agent || req.headers['user-agent'] || 'Unknown Browser',
      });

      const pingData = parseResult.success
        ? parseResult.data
        : {
            app_origin: req.body.app_origin || req.headers.origin || 'unknown_origin',
            app_url: req.body.app_url || req.headers.referer || 'unknown_url',
            app_name: req.body.app_name || 'Web App Client',
            sdk_version: req.body.sdk_version || '6.1.0',
            user_agent: req.headers['user-agent'] || 'Unknown Browser',
            timestamp: new Date().toISOString(),
            metadata: req.body.metadata || {},
          };

      const cleanOrigin = pingData.app_origin.replace(/\/+$/, '');

      const connection = upsertWebAppConnection({
        tenant_id: tenantContext.tenantId,
        app_origin: cleanOrigin,
        app_url: pingData.app_url,
        app_name: pingData.app_name || (cleanOrigin.includes('localhost') ? 'Local Development App' : cleanOrigin.replace(/^https?:\/\//, '')),
        sdk_version: pingData.sdk_version || '6.1.0',
        last_ping_at: new Date().toISOString(),
        metadata: JSON.stringify({
          user_agent: pingData.user_agent,
          ip: req.ip,
          headers: {
            referer: req.headers.referer,
            origin: req.headers.origin,
          },
          ...(pingData.metadata || {}),
        }),
      });

      res.status(200).json({
        success: true,
        connected: true,
        tenant_id: tenantContext.tenantId,
        app_origin: cleanOrigin,
        status: 'ONLINE',
        last_ping_at: connection.last_ping_at,
        message: 'Web application successfully connected to ULTRON Control Plane.',
      });
    } catch (err: any) {
      console.error('❌ Error handling web app ping:', err);
      res.status(500).json({ error: 'Internal Server Error', details: err.message });
    }
  }
);

// 2. GET /v1/events/connected-apps - Query Live Web Application Connections
eventsRouter.get(
  '/connected-apps',
  TenancyEnforcer.authenticateTenant(),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const tenantContext = req.tenantContext!;
      const apps = getWebAppConnections(tenantContext.tenantId);
      const onlineApps = apps.filter((a) => a.status === 'ONLINE');

      res.json({
        connected: onlineApps.length > 0,
        total_apps: apps.length,
        active_count: onlineApps.length,
        apps,
      });
    } catch (err: any) {
      console.error('❌ Error fetching connected apps:', err);
      res.status(500).json({ error: 'Internal Server Error', details: err.message });
    }
  }
);

// 3. POST /v1/events - Ingest Canonical Merchant Event (Requires events:write scope)
eventsRouter.post(
  '/',
  TenancyEnforcer.authenticateTenant('events:write'),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const tenantContext = req.tenantContext!;

      // Auto-register connected app origin if event originates from web client
      const rawOrigin = req.headers.origin || req.headers.referer || (req.body?.metadata?.url ? new URL(req.body.metadata.url).origin : null);
      if (rawOrigin) {
        try {
          upsertWebAppConnection({
            tenant_id: tenantContext.tenantId,
            app_origin: rawOrigin.replace(/\/+$/, ''),
            app_url: req.body?.metadata?.url || rawOrigin,
            app_name: rawOrigin.includes('localhost') ? 'Local Development Checkout' : rawOrigin.replace(/^https?:\/\//, ''),
            sdk_version: '6.1.0',
            last_ping_at: new Date().toISOString(),
          });
        } catch {}
      }

      // 1. Cross-Tenant Invariant: Reject mismatched tenant_id
      if (req.body.tenant_id && req.body.tenant_id !== tenantContext.tenantId) {
        const rejectionReason = `Cross-tenant event injection rejected. Authenticated as '${tenantContext.tenantId}', received '${req.body.tenant_id}'.`;
        insertEventIngestionLog({
          id: `log_evt_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
          tenant_id: tenantContext.tenantId,
          event_id: req.body.event_id,
          payment_id: req.body.payment_id,
          source: req.body.source || 'CLIENT_SDK',
          status: 'UNAUTHORIZED',
          status_code: 403,
          rejection_reason: rejectionReason,
          raw_payload: JSON.stringify(req.body),
          origin: rawOrigin || req.ip || undefined,
          created_at: new Date().toISOString(),
        });

        res.status(403).json({
          error: 'Forbidden',
          message: rejectionReason,
        });
        return;
      }

      // 2. Schema Validation with Authenticated Tenant Binding
      const parseResult = CanonicalPaymentEventSchema.safeParse({
        ...req.body,
        tenant_id: tenantContext.tenantId,
        environment: tenantContext.environment || req.body.environment || 'test',
        received_at: new Date().toISOString(),
      });

      if (!parseResult.success) {
        const errorDetails = parseResult.error.errors.map((e) => `${e.path.join('.')}: ${e.message}`).join('; ');
        console.warn('⚠️ Canonical event validation failed:', JSON.stringify(parseResult.error.errors));
        
        insertEventIngestionLog({
          id: `log_evt_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
          tenant_id: tenantContext.tenantId,
          event_id: req.body?.event_id,
          payment_id: req.body?.payment_id,
          source: req.body?.source || 'CLIENT_SDK',
          status: 'REJECTED',
          status_code: 400,
          rejection_reason: errorDetails,
          raw_payload: JSON.stringify(req.body),
          origin: rawOrigin || req.ip || undefined,
          created_at: new Date().toISOString(),
        });

        res.status(400).json({
          error: 'Validation Error',
          message: 'Malformed canonical payment event payload.',
          details: parseResult.error.errors.map((e) => ({
            path: e.path.join('.'),
            message: e.message,
          })),
        });
        return;
      }

      const event = parseResult.data;

      // 3. Deduplication Check by event_id
      if (event.event_id) {
        const existingByEvent = getOpportunityByRazorpayEventId(event.event_id);
        if (existingByEvent) {
          insertEventIngestionLog({
            id: `log_evt_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
            tenant_id: tenantContext.tenantId,
            event_id: event.event_id,
            payment_id: event.payment_id,
            source: event.source,
            status: 'DEDUPLICATED',
            status_code: 200,
            opportunity_id: existingByEvent.id,
            rejection_reason: `Event deduplicated by event_id (${event.event_id})`,
            raw_payload: JSON.stringify(req.body),
            origin: rawOrigin || req.ip || undefined,
            created_at: new Date().toISOString(),
          });

          res.status(200).json({
            received: true,
            deduplicated: true,
            event_id: event.event_id,
            opportunity_id: existingByEvent.id,
            status: existingByEvent.status,
          });
          return;
        }
      }

      // 4. Deduplication Check by payment_id
      if (event.payment_id) {
        const existingByPayment = getOpportunityById(event.payment_id);
        if (existingByPayment) {
          // If status is paid/captured, reconcile existing opportunity
          if (event.status === 'paid' || event.status === 'captured') {
            await AuthoritativeReconciler.reconcileOpportunity(existingByPayment.id, {
              actor: 'canonical_event_gateway',
            });
          }

          insertEventIngestionLog({
            id: `log_evt_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
            tenant_id: tenantContext.tenantId,
            event_id: event.event_id,
            payment_id: event.payment_id,
            source: event.source,
            status: 'DEDUPLICATED',
            status_code: 200,
            opportunity_id: existingByPayment.id,
            rejection_reason: `Event deduplicated by payment_id (${event.payment_id})`,
            raw_payload: JSON.stringify(req.body),
            origin: rawOrigin || req.ip || undefined,
            created_at: new Date().toISOString(),
          });

          res.status(200).json({
            received: true,
            deduplicated: true,
            payment_id: event.payment_id,
            opportunity_id: existingByPayment.id,
            status: existingByPayment.status,
          });
          return;
        }
      }

      // 5. Ingestion of Failed Payment Event
      if (event.status === 'failed') {
        const opportunity = normalizeOpportunity(
          {
            id: event.payment_id || `pay_${Date.now()}`,
            amount: event.amount_paise,
            currency: event.currency,
            error_code: event.failure_code || 'UNKNOWN_ERROR',
            error_description: event.failure_description || 'Payment failed',
            customer_id: event.customer_reference,
            email: event.customer_email || undefined,
            contact: event.customer_phone || undefined,
            order_id: event.order_id || undefined,
            attempts: event.attempt_number || 1,
            notes: event.metadata || undefined,
          },
          event.event_id,
          {
            source: event.environment === 'live' ? 'real' : 'synthetic',
            tenantId: tenantContext.tenantId,
          }
        );

        insertOpportunity(opportunity);

        // Record in ledger
        insertLedgerEntry({
          id: `led_evt_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
          opportunity_id: opportunity.id,
          event_type: 'webhook_received',
          amount_paise: opportunity.amount_paise,
          timestamp: opportunity.created_at,
          raw_payload_ref: JSON.stringify({
            event_id: event.event_id,
            source: event.source,
            correlation_id: event.correlation_id,
            tenant_id: tenantContext.tenantId,
          }),
        });

        // Record in event ingestion log
        const logItem = {
          id: `log_evt_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
          tenant_id: tenantContext.tenantId,
          event_id: event.event_id,
          payment_id: event.payment_id,
          source: event.source,
          status: 'ACCEPTED' as const,
          status_code: 201,
          opportunity_id: opportunity.id,
          raw_payload: JSON.stringify(req.body),
          origin: rawOrigin || req.ip || undefined,
          created_at: new Date().toISOString(),
        };
        insertEventIngestionLog(logItem);

        // Realtime Push Broadcast
        RealtimeBroadcaster.getInstance().broadcastToTenant(tenantContext.tenantId, 'EVENT_INGESTED', logItem);
        RealtimeBroadcaster.getInstance().broadcastToTenant(tenantContext.tenantId, 'OPPORTUNITY_UPDATED', opportunity);

        console.log(`📥 [ULTRON Gateway] Ingested failed payment opportunity ${opportunity.id} (₹${(opportunity.amount_paise / 100).toFixed(2)}) for tenant ${tenantContext.tenantId}`);

        res.status(201).json({
          received: true,
          opportunity_id: opportunity.id,
          event_id: event.event_id,
          decline_type: opportunity.decline_type,
          customer_trust_score: opportunity.customer_trust_score,
          status: opportunity.status,
        });
        return;
      }

      // 6. Handle Paid / Captured Event (Reconciliation)
      if (event.status === 'paid' || event.status === 'captured') {
        let matchedOppId: string | null = null;
        if (event.payment_id) {
          const matched = getOpportunityById(event.payment_id);
          if (matched) matchedOppId = matched.id;
        }
        if (!matchedOppId && event.payment_link_id) {
          const records = getAllExecutionRecords(tenantContext.tenantId);
          const found = records.find((r) => r.razorpay_payment_link_id === event.payment_link_id);
          if (found) matchedOppId = found.opportunity_id;
        }

        if (matchedOppId) {
          const reconResult = await AuthoritativeReconciler.reconcileOpportunity(matchedOppId, {
            actor: 'client_sdk_event',
          });

          insertEventIngestionLog({
            id: `log_evt_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
            tenant_id: tenantContext.tenantId,
            event_id: event.event_id,
            payment_id: event.payment_id,
            source: event.source,
            status: 'ACCEPTED',
            status_code: 200,
            opportunity_id: matchedOppId,
            raw_payload: JSON.stringify(req.body),
            origin: rawOrigin || req.ip || undefined,
            created_at: new Date().toISOString(),
          });

          res.status(200).json({
            received: true,
            reconciled: true,
            opportunity_id: matchedOppId,
            status: reconResult.new_opportunity_status,
          });
          return;
        }
      }

      // 7. Other Events (created, authorized, etc.)
      insertEventIngestionLog({
        id: `log_evt_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        tenant_id: tenantContext.tenantId,
        event_id: event.event_id,
        payment_id: event.payment_id,
        source: event.source,
        status: 'ACCEPTED',
        status_code: 200,
        raw_payload: JSON.stringify(req.body),
        origin: rawOrigin || req.ip || undefined,
        created_at: new Date().toISOString(),
      });

      res.status(200).json({
        received: true,
        processed: true,
        event_id: event.event_id,
        status: event.status,
      });
    } catch (err: any) {
      console.error('❌ Error ingesting canonical event:', err);
      insertEventIngestionLog({
        id: `log_evt_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        tenant_id: (req as any).tenantContext?.tenantId || 'unknown',
        event_id: req.body?.event_id,
        payment_id: req.body?.payment_id,
        source: req.body?.source || 'CLIENT_SDK',
        status: 'REJECTED',
        status_code: 500,
        rejection_reason: `Internal server error: ${err.message}`,
        raw_payload: JSON.stringify(req.body || {}),
        origin: (req.headers.origin as string) || (req.headers.referer as string) || req.ip || undefined,
        created_at: new Date().toISOString(),
      });
      res.status(500).json({ error: 'Internal Server Error', details: err.message });
    }
  }
);

// 4. GET /v1/events/stream - Live Ingestion Stream & Debugging Log
eventsRouter.get(
  '/stream',
  TenancyEnforcer.authenticateTenant('events:read'),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const tenantContext = req.tenantContext!;
      const statusParam = typeof req.query.status === 'string' ? req.query.status : undefined;
      const limitParam = typeof req.query.limit === 'string' ? Math.min(100, Math.max(1, parseInt(req.query.limit, 10))) : 50;

      const logs = getEventIngestionLogs({
        tenantId: tenantContext.tenantId,
        status: statusParam,
        limit: limitParam,
      });

      res.json({
        success: true,
        count: logs.length,
        tenant_id: tenantContext.tenantId,
        logs,
      });
    } catch (err: any) {
      console.error('❌ Error querying event stream:', err);
      res.status(500).json({ error: 'Internal Server Error', details: err.message });
    }
  }
);

// 4b. GET /v1/events/live-stream - Server-Sent Events (SSE) Push Stream
eventsRouter.get(
  '/live-stream',
  TenancyEnforcer.authenticateTenant('events:read'),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const tenantContext = req.tenantContext!;
      RealtimeBroadcaster.getInstance().registerClient(tenantContext.tenantId, res);
    } catch (err: any) {
      console.error('❌ Error establishing SSE stream:', err);
      res.status(500).json({ error: 'Failed to establish live SSE stream' });
    }
  }
);

// 5. POST /v1/events/test - Trigger Synthetic Test Event for Integration Setup Verification
eventsRouter.post(
  '/test',
  TenancyEnforcer.authenticateTenant('events:write'),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const tenantContext = req.tenantContext!;
      const amountPaise = typeof req.body.amount_paise === 'number' && req.body.amount_paise > 0 ? req.body.amount_paise : 50000;
      const failureCode = req.body.failure_code || 'INSUFFICIENT_FUNDS';
      const failureDescription = req.body.failure_description || 'Wizard Verification Test: Payment authorization declined by bank';
      const eventId = `evt_test_wiz_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
      const paymentId = `pay_test_wiz_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;

      const opportunity = normalizeOpportunity(
        {
          id: paymentId,
          amount: amountPaise,
          currency: 'INR',
          error_code: failureCode,
          error_description: failureDescription,
          customer_id: req.body.customer_email || 'wizard_test_user@example.com',
          email: req.body.customer_email || 'wizard_test_user@example.com',
          attempts: 1,
          notes: {
            source: 'INTEGRATION_WIZARD_TEST',
            verified_at: new Date().toISOString(),
          },
        },
        eventId,
        {
          source: 'synthetic',
          tenantId: tenantContext.tenantId,
        }
      );

      insertOpportunity(opportunity);

      insertLedgerEntry({
        id: `led_evt_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        opportunity_id: opportunity.id,
        event_type: 'webhook_received',
        amount_paise: opportunity.amount_paise,
        timestamp: opportunity.created_at,
        raw_payload_ref: JSON.stringify({
          event_id: eventId,
          source: 'WIZARD_TEST',
          tenant_id: tenantContext.tenantId,
        }),
      });

      insertEventIngestionLog({
        id: `log_evt_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        tenant_id: tenantContext.tenantId,
        event_id: eventId,
        payment_id: paymentId,
        source: 'WIZARD_TEST',
        status: 'ACCEPTED',
        status_code: 201,
        opportunity_id: opportunity.id,
        raw_payload: JSON.stringify({
          event_id: eventId,
          payment_id: paymentId,
          amount_paise: amountPaise,
          status: 'failed',
          failure_code: failureCode,
          customer_email: req.body.customer_email || 'wizard_test_user@example.com',
        }),
        origin: (req.headers.origin as string) || (req.headers.referer as string) || req.ip || undefined,
        created_at: new Date().toISOString(),
      });

      res.status(201).json({
        success: true,
        message: 'Synthetic test payment failure successfully dispatched and converted into Recovery Opportunity.',
        event_id: eventId,
        payment_id: paymentId,
        opportunity_id: opportunity.id,
        amount_paise: opportunity.amount_paise,
        status: opportunity.status,
        decline_type: opportunity.decline_type,
        created_at: opportunity.created_at,
      });
    } catch (err: any) {
      console.error('❌ Error triggering wizard test event:', err);
      res.status(500).json({ error: 'Internal Server Error', details: err.message });
    }
  }
);

// 6. GET /v1/events/:id - Query Ingested Event Status (Requires events:read scope)
eventsRouter.get(
  '/:id',
  TenancyEnforcer.authenticateTenant('events:read'),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    const rawEventId = req.params.id;
    const eventId = Array.isArray(rawEventId) ? rawEventId[0] : rawEventId;
    const opp = getOpportunityByRazorpayEventId(eventId) || getOpportunityById(eventId);

    if (!opp) {
      res.status(404).json({ error: 'Event or Opportunity not found', event_id: eventId });
      return;
    }

    res.json({
      event_id: eventId,
      opportunity_id: opp.id,
      amount_paise: opp.amount_paise,
      currency: opp.currency,
      decline_type: opp.decline_type,
      status: opp.status,
      created_at: opp.created_at,
    });
  }
);



