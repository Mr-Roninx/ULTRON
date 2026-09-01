import { Router, Response } from 'express';
import { TenancyEnforcer, TenantScopedRequest } from '../security/tenancy.js';
import { CanonicalPaymentEventSchema } from '../security/schemas.js';
import { DatabaseAdapter } from '../db/adapter.js';
import { normalizeOpportunity } from '../perception/normalizer.js';
import {
  getOpportunityById,
  getOpportunityByRazorpayEventId,
  insertOpportunity,
  insertLedgerEntry,
} from '../db/database.js';

export const eventsRouter = Router();

// 1. POST /v1/events - Ingest Canonical Merchant Event (Requires events:write scope)
eventsRouter.post(
  '/',
  TenancyEnforcer.authenticateTenant('events:write'),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const tenantContext = req.tenantContext!;

      // 1. Cross-Tenant Invariant: Reject mismatched tenant_id
      if (req.body.tenant_id && req.body.tenant_id !== tenantContext.tenantId) {
        res.status(403).json({
          error: 'Forbidden',
          message: `Cross-tenant event injection rejected. Authenticated as '${tenantContext.tenantId}'.`,
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
            email: event.customer_email,
            contact: event.customer_phone,
            order_id: event.order_id,
            attempts: event.attempt_number || 1,
            notes: event.metadata,
          },
          event.event_id,
          { source: event.environment === 'live' ? 'real' : 'synthetic' }
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

      // 6. Other Events (created, authorized, captured, etc.)
      res.status(200).json({
        received: true,
        processed: true,
        event_id: event.event_id,
        status: event.status,
      });
    } catch (err: any) {
      console.error('❌ Error ingesting canonical event:', err);
      res.status(500).json({ error: 'Internal Server Error', details: err.message });
    }
  }
);

// 2. GET /v1/events/:id - Query Ingested Event Status (Requires events:read scope)
eventsRouter.get(
  '/:id',
  TenancyEnforcer.authenticateTenant('events:read'),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    const eventId = req.params.id;
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
