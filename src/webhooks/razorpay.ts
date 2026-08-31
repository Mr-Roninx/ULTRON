import crypto from 'node:crypto';
import { Request, Response } from 'express';
import {
  getOpportunityById,
  getOpportunityByRazorpayEventId,
  insertOpportunity,
  insertLedgerEntry,
} from '../db/database.js';
import { DeclineType, RecoveryOpportunity } from '../types/index.js';

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

export function classifyDeclineType(errorCode?: string, errorReason?: string): DeclineType {
  const code = (errorCode || '').toLowerCase();
  const reason = (errorReason || '').toLowerCase();

  // Hard declines: irreversible account / card issues
  if (
    code.includes('stolen') ||
    code.includes('lost') ||
    code.includes('expired') ||
    code.includes('card_invalid') ||
    code.includes('fraud') ||
    reason.includes('stolen') ||
    reason.includes('lost') ||
    reason.includes('expired') ||
    reason.includes('fraud')
  ) {
    return 'hard';
  }

  // Soft declines: transient or fund-related issues
  if (
    code.includes('insufficient_funds') ||
    code.includes('gateway_error') ||
    code.includes('timeout') ||
    code.includes('network') ||
    code.includes('authentication_failed') ||
    code.includes('otp') ||
    code.includes('limit_exceeded') ||
    reason.includes('insufficient') ||
    reason.includes('timeout') ||
    reason.includes('network') ||
    reason.includes('authentication') ||
    reason.includes('otp')
  ) {
    return 'soft';
  }

  return 'unknown';
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
    const amountPaise: number = Number(paymentEntity.amount) || 0;
    const currency: string = paymentEntity.currency || 'INR';

    // Error details
    const errorCode: string = paymentEntity.error_code || paymentEntity.error?.code || 'UNKNOWN_ERROR';
    const errorReason: string = paymentEntity.error_reason || paymentEntity.error?.reason || paymentEntity.error_description || 'Payment failed';
    const errorSource: string = paymentEntity.error_source || paymentEntity.error?.source || 'gateway';
    const errorStep: string = paymentEntity.error_step || paymentEntity.error?.step || 'payment_authorization';

    const declineType = classifyDeclineType(errorCode, errorReason);

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

    const customerId: string =
      paymentEntity.customer_id ||
      paymentEntity.email ||
      paymentEntity.contact ||
      `cust_${paymentId.slice(-8)}`;

    const oppId = paymentId;
    const now = new Date().toISOString();

    const opportunity: RecoveryOpportunity = {
      id: oppId,
      source: 'real',
      amount_paise: amountPaise,
      currency,
      reason_code: errorCode,
      decline_type: declineType,
      attempt_count: paymentEntity.attempts || 1,
      customer_id: customerId,
      customer_trust_score: 0.5,
      created_at: now,
      status: 'pending',
      razorpay_event_id: eventId || null,
      raw_payload_ref: JSON.stringify({
        error_source: errorSource,
        error_step: errorStep,
        error_reason: errorReason,
        error_code: errorCode,
        notes: paymentEntity.notes,
      }),
    };

    insertOpportunity(opportunity);

    // Audit trail in ledger
    insertLedgerEntry({
      id: `led_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
      opportunity_id: oppId,
      event_type: 'webhook_received',
      amount_paise: amountPaise,
      timestamp: now,
      raw_payload_ref: JSON.stringify({
        event: eventName,
        event_id: eventId,
        payment_id: paymentId,
        error_code: errorCode,
        error_reason: errorReason,
      }),
    });

    res.status(200).json({
      received: true,
      opportunity_id: oppId,
      status: 'pending',
    });
  } catch (error) {
    console.error('Error handling webhook:', error);
    res.status(500).json({ error: 'Internal server error processing webhook' });
  }
}
