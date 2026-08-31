import crypto from 'node:crypto';
import { Request, Response } from 'express';
import {
  getOpportunityById,
  getOpportunityByRazorpayEventId,
  insertOpportunity,
  insertLedgerEntry,
  updateOpportunityStatus,
  getAllExecutionRecords,
} from '../db/database.js';
import { normalizeOpportunity } from '../perception/normalizer.js';

export function verifyWebhookSignature(
  rawBody: string | Buffer,
  signature: string | undefined,
  secret: string | undefined
): boolean {
  if (!signature || !secret) {
    return false;
  }

  try {
    const expectedSignature = crypto
      .createHmac('sha256', secret)
      .update(typeof rawBody === 'string' ? rawBody : rawBody.toString('utf-8'))
      .digest('hex');

    const sigBuf = Buffer.from(signature, 'utf-8');
    const expBuf = Buffer.from(expectedSignature, 'utf-8');

    if (sigBuf.length !== expBuf.length) {
      return false;
    }

    return crypto.timingSafeEqual(sigBuf, expBuf);
  } catch {
    return false;
  }
}

/**
 * Real Razorpay Webhook Ingestion Handler.
 * NOTE: This endpoint accepts deliveries verified against RAZORPAY_WEBHOOK_SECRET.
 * Every failed payment ingested here is assigned source='real'.
 */
export function handleRazorpayWebhook(req: Request, res: Response): void {
  try {
    const signature = req.headers['x-razorpay-signature'] as string | undefined;
    const webhookSecret = process.env.RAZORPAY_WEBHOOK_SECRET;

    // Verify HMAC signature against raw payload
    const rawBody = (req as any).rawBody || JSON.stringify(req.body);
    const isValid = verifyWebhookSignature(rawBody, signature, webhookSecret);

    if (!isValid) {
      res.status(400).json({ error: 'Invalid webhook signature' });
      return;
    }

    const payload = req.body;
    const eventId: string | undefined = payload?.event_id || payload?.id;
    const eventName: string | undefined = payload?.event;

    // Deduplication check by eventId
    if (eventId) {
      const existingByEvent = getOpportunityByRazorpayEventId(eventId);
      if (existingByEvent) {
        res.status(200).json({
          received: true,
          deduplicated: true,
          opportunity_id: existingByEvent.id,
        });
        return;
      }
    }

    // 1. Handle payment_link.paid event (Truth Engine Reconciliation)
    if (eventName === 'payment_link.paid') {
      const linkEntity = payload?.payload?.payment_link?.entity;
      const refId = linkEntity?.reference_id;
      const linkId = linkEntity?.id;

      // Find opportunity by reference_id or by matching execution record
      let oppId = refId;
      if (!oppId && linkId) {
        const records = getAllExecutionRecords();
        const matched = records.find((r) => r.razorpay_payment_link_id === linkId);
        if (matched) oppId = matched.opportunity_id;
      }

      if (oppId) {
        const opp = getOpportunityById(oppId);
        if (opp) {
          updateOpportunityStatus(oppId, 'recovered');
          const now = new Date().toISOString();
          insertLedgerEntry({
            id: `led_rec_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
            opportunity_id: oppId,
            event_type: 'recovered',
            amount_paise: opp.amount_paise,
            timestamp: now,
            raw_payload_ref: JSON.stringify({
              event: eventName,
              event_id: eventId,
              payment_link_id: linkId,
              amount_paid: linkEntity?.amount_paid || opp.amount_paise,
            }),
          });

          res.status(200).json({
            received: true,
            reconciled: true,
            status: 'recovered',
            opportunity_id: oppId,
          });
          return;
        }
      }

      res.status(200).json({ received: true, processed: false, reason: 'Opportunity not found for payment link' });
      return;
    }

    // 2. Handle payment_link.expired / cancelled event
    if (eventName === 'payment_link.expired' || eventName === 'payment_link.cancelled') {
      const linkEntity = payload?.payload?.payment_link?.entity;
      const refId = linkEntity?.reference_id;
      const linkId = linkEntity?.id;

      let oppId = refId;
      if (!oppId && linkId) {
        const records = getAllExecutionRecords();
        const matched = records.find((r) => r.razorpay_payment_link_id === linkId);
        if (matched) oppId = matched.opportunity_id;
      }

      if (oppId) {
        const opp = getOpportunityById(oppId);
        if (opp) {
          updateOpportunityStatus(oppId, 'not_recovered');
          const now = new Date().toISOString();
          insertLedgerEntry({
            id: `led_unrec_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
            opportunity_id: oppId,
            event_type: 'not_recovered',
            amount_paise: opp.amount_paise,
            timestamp: now,
            raw_payload_ref: JSON.stringify({
              event: eventName,
              event_id: eventId,
              payment_link_id: linkId,
            }),
          });

          res.status(200).json({
            received: true,
            reconciled: true,
            status: 'not_recovered',
            opportunity_id: oppId,
          });
          return;
        }
      }

      res.status(200).json({ received: true, processed: false });
      return;
    }

    // 3. Handle payment.failed event (Event Fabric / Perception Ingestion)
    if (eventName === 'payment.failed') {
      const paymentEntity = payload?.payload?.payment?.entity;
      if (!paymentEntity) {
        res.status(400).json({ error: 'Missing payment entity in payload' });
        return;
      }

      const paymentId: string = paymentEntity.id || `pay_${Date.now()}`;

      // Check if opportunity already exists for this payment_id
      const existingByPaymentId = getOpportunityById(paymentId);
      if (existingByPaymentId) {
        res.status(200).json({
          received: true,
          deduplicated: true,
          opportunity_id: existingByPaymentId.id,
        });
        return;
      }

      // Run Perception Normalization (source='real')
      const opportunity = normalizeOpportunity(paymentEntity, eventId, { source: 'real' });

      // Insert normalized opportunity
      insertOpportunity(opportunity);

      // Audit trail in ledger
      insertLedgerEntry({
        id: `led_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        opportunity_id: opportunity.id,
        event_type: 'webhook_received',
        amount_paise: opportunity.amount_paise,
        timestamp: opportunity.created_at,
        raw_payload_ref: JSON.stringify({
          event: eventName,
          event_id: eventId,
          payment_id: opportunity.id,
          reason_code: opportunity.reason_code,
          decline_type: opportunity.decline_type,
          customer_trust_score: opportunity.customer_trust_score,
        }),
      });

      res.status(200).json({
        received: true,
        opportunity_id: opportunity.id,
        decline_type: opportunity.decline_type,
        customer_trust_score: opportunity.customer_trust_score,
        status: 'pending',
      });
      return;
    }

    // Other Razorpay events ignored safely
    res.status(200).json({ received: true, ignored: true, event: eventName });
  } catch (error) {
    console.error('Error handling webhook:', error);
    res.status(500).json({ error: 'Internal server error processing webhook' });
  }
}

/**
 * Isolated Simulation Webhook Handler (Test Traffic Only).
 * Explicitly marks all ingested opportunities as source='synthetic' unconditionally.
 */
export function handleSimulatedWebhook(req: Request, res: Response): void {
  try {
    const signature = req.headers['x-razorpay-signature'] as string | undefined;
    const webhookSecret = process.env.RAZORPAY_WEBHOOK_SECRET;

    // Verify HMAC signature against raw payload
    const rawBody = (req as any).rawBody || JSON.stringify(req.body);
    const isValid = verifyWebhookSignature(rawBody, signature, webhookSecret);

    if (!isValid) {
      res.status(400).json({ error: 'Invalid simulated webhook signature' });
      return;
    }

    const payload = req.body;
    const eventId: string | undefined = payload?.event_id || payload?.id;
    const eventName: string | undefined = payload?.event;

    // Deduplication check by eventId
    if (eventId) {
      const existingByEvent = getOpportunityByRazorpayEventId(eventId);
      if (existingByEvent) {
        res.status(200).json({
          received: true,
          deduplicated: true,
          simulated: true,
          opportunity_id: existingByEvent.id,
        });
        return;
      }
    }

    // 1. Handle payment_link.paid event (Simulation)
    if (eventName === 'payment_link.paid') {
      const linkEntity = payload?.payload?.payment_link?.entity;
      const refId = linkEntity?.reference_id;
      const linkId = linkEntity?.id;

      let oppId = refId;
      if (!oppId && linkId) {
        const records = getAllExecutionRecords();
        const matched = records.find((r) => r.razorpay_payment_link_id === linkId);
        if (matched) oppId = matched.opportunity_id;
      }

      if (oppId) {
        const opp = getOpportunityById(oppId);
        if (opp) {
          updateOpportunityStatus(oppId, 'recovered');
          const now = new Date().toISOString();
          insertLedgerEntry({
            id: `led_sim_rec_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
            opportunity_id: oppId,
            event_type: 'recovered',
            amount_paise: opp.amount_paise,
            timestamp: now,
            raw_payload_ref: JSON.stringify({
              event: eventName,
              event_id: eventId,
              simulated: true,
              payment_link_id: linkId,
              amount_paid: linkEntity?.amount_paid || opp.amount_paise,
            }),
          });

          res.status(200).json({
            received: true,
            reconciled: true,
            simulated: true,
            status: 'recovered',
            opportunity_id: oppId,
          });
          return;
        }
      }

      res.status(200).json({ received: true, processed: false, simulated: true, reason: 'Opportunity not found' });
      return;
    }

    // 2. Handle payment.failed event (Simulation -> source='synthetic')
    if (eventName === 'payment.failed') {
      const paymentEntity = payload?.payload?.payment?.entity;
      if (!paymentEntity) {
        res.status(400).json({ error: 'Missing payment entity in payload' });
        return;
      }

      const paymentId: string = paymentEntity.id || `pay_sim_${Date.now()}`;

      const existingByPaymentId = getOpportunityById(paymentId);
      if (existingByPaymentId) {
        res.status(200).json({
          received: true,
          deduplicated: true,
          simulated: true,
          opportunity_id: existingByPaymentId.id,
        });
        return;
      }

      // Run Perception Normalization with source='synthetic' unconditionally
      const opportunity = normalizeOpportunity(paymentEntity, eventId, { source: 'synthetic' });

      // Insert synthetic opportunity
      insertOpportunity(opportunity);

      // Audit trail in ledger
      insertLedgerEntry({
        id: `led_sim_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        opportunity_id: opportunity.id,
        event_type: 'webhook_received',
        amount_paise: opportunity.amount_paise,
        timestamp: opportunity.created_at,
        raw_payload_ref: JSON.stringify({
          event: eventName,
          event_id: eventId,
          simulated: true,
          payment_id: opportunity.id,
          reason_code: opportunity.reason_code,
          decline_type: opportunity.decline_type,
          customer_trust_score: opportunity.customer_trust_score,
        }),
      });

      res.status(200).json({
        received: true,
        simulated: true,
        opportunity_id: opportunity.id,
        decline_type: opportunity.decline_type,
        customer_trust_score: opportunity.customer_trust_score,
        status: 'pending',
      });
      return;
    }

    res.status(200).json({ received: true, ignored: true, simulated: true, event: eventName });
  } catch (error) {
    console.error('Error handling simulated webhook:', error);
    res.status(500).json({ error: 'Internal server error processing simulated webhook' });
  }
}
