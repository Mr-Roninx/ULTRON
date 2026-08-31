import crypto from 'node:crypto';
import { Request, Response } from 'express';
import {
  getOpportunityById,
  getOpportunityByRazorpayEventId,
  insertOpportunity,
  insertLedgerEntry,
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

    // We only process payment.failed events for recovery opportunities
    if (eventName !== 'payment.failed') {
      res.status(200).json({ received: true, ignored: true, event: eventName });
      return;
    }

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

    // Run Perception Normalization
    const opportunity = normalizeOpportunity(paymentEntity, eventId);

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
  } catch (error) {
    console.error('Error handling webhook:', error);
    res.status(500).json({ error: 'Internal server error processing webhook' });
  }
}
