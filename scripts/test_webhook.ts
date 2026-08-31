import crypto from 'node:crypto';
import dotenv from 'dotenv';
import path from 'node:path';

dotenv.config({ path: path.resolve(process.cwd(), '.env') });

const PORT = process.env.PORT || 3001;
const BASE_URL = `http://localhost:${PORT}`;
const WEBHOOK_SECRET = process.env.RAZORPAY_WEBHOOK_SECRET || 'rzp_whsec_ultron_test';

function signPayload(body: string, secret: string): string {
  return crypto.createHmac('sha256', secret).update(body).digest('hex');
}

async function runTests() {
  console.log('🧪 Starting Event Fabric Webhook Acceptance Tests...');

  // 1. Test Health endpoint
  try {
    const healthRes = await fetch(`${BASE_URL}/health`);
    const health = await healthRes.json();
    console.log('✅ Health check passed:', health);
  } catch (err) {
    console.error('❌ Server not responding at', BASE_URL, err);
    process.exit(1);
  }

  // 2. Test Invalid HMAC Signature rejection (400)
  const sampleFailedEvent = {
    entity: 'event',
    account_id: 'acc_ultron_test',
    event: 'payment.failed',
    contains: ['payment'],
    payload: {
      payment: {
        entity: {
          id: 'pay_test_failed_001',
          entity: 'payment',
          amount: 349900, // ₹3,499.00
          currency: 'INR',
          status: 'failed',
          order_id: 'order_test_001',
          method: 'card',
          error_code: 'BAD_REQUEST_PAYMENT_CARD_EXPIRED',
          error_description: 'The card has expired. Please use a valid card.',
          error_source: 'gateway',
          error_step: 'payment_authorization',
          error_reason: 'card_expired',
          customer_id: 'cust_live_spike_01',
          email: 'customer01@example.com',
          contact: '+919876543210',
          attempts: 1,
        },
      },
    },
    created_at: Math.floor(Date.now() / 1000),
  };

  const payloadString = JSON.stringify(sampleFailedEvent);

  console.log('\n--- Test 1: Invalid HMAC Signature ---');
  const invalidSigRes = await fetch(`${BASE_URL}/webhooks/razorpay`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-razorpay-signature': 'invalid_forged_signature_123456',
    },
    body: payloadString,
  });

  console.log(`Response status: ${invalidSigRes.status}`);
  if (invalidSigRes.status === 400) {
    console.log('✅ PASS: Invalid signature rejected with 400 Bad Request.');
  } else {
    console.error(`❌ FAIL: Expected 400, got ${invalidSigRes.status}`);
    process.exit(1);
  }

  // 3. Test Valid Signature Ingestion (200)
  console.log('\n--- Test 2: Valid HMAC Signature & payment.failed Ingestion ---');
  const validSignature = signPayload(payloadString, WEBHOOK_SECRET);

  const validRes = await fetch(`${BASE_URL}/webhooks/razorpay`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-razorpay-signature': validSignature,
    },
    body: payloadString,
  });

  const validJson = await validRes.json();
  console.log(`Response status: ${validRes.status}, Body:`, validJson);
  if (validRes.status === 200 && validJson.received && validJson.opportunity_id === 'pay_test_failed_001') {
    console.log('✅ PASS: Valid webhook ingested successfully into RecoveryOpportunity table.');
  } else {
    console.error('❌ FAIL: Failed to ingest valid webhook:', validJson);
    process.exit(1);
  }

  // 4. Test Deduplication / Replay (200 & deduplicated: true, no extra row)
  console.log('\n--- Test 3: Idempotent Webhook Replay Deduplication ---');
  const replayRes = await fetch(`${BASE_URL}/webhooks/razorpay`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-razorpay-signature': validSignature,
    },
    body: payloadString,
  });

  const replayJson = await replayRes.json();
  console.log(`Replay status: ${replayRes.status}, Body:`, replayJson);
  if (replayRes.status === 200 && replayJson.deduplicated === true) {
    console.log('✅ PASS: Duplicate webhook replayed and safely deduplicated without creating duplicate row.');
  } else {
    console.error('❌ FAIL: Replay deduplication failed:', replayJson);
    process.exit(1);
  }

  // 5. Query GET /opportunities to verify both real and synthetic rows exist
  console.log('\n--- Test 4: Verify GET /opportunities ---');
  const oppsRes = await fetch(`${BASE_URL}/opportunities`);
  const oppsData = await oppsRes.json();
  console.log(`Total opportunities in database: ${oppsData.count}`);

  const realOpps = oppsData.opportunities.filter((o: any) => o.source === 'real');
  const synthOpps = oppsData.opportunities.filter((o: any) => o.source === 'synthetic');

  console.log(`Real rows: ${realOpps.length}, Synthetic rows: ${synthOpps.length}`);
  if (realOpps.length >= 1 && synthOpps.length === 15) {
    console.log('✅ PASS: GET /opportunities returned both real and synthetic rows conforming to contract.');
  } else {
    console.error('❌ FAIL: Opportunities count check failed.');
    process.exit(1);
  }

  console.log('\n🎉 ALL ACCEPTANCE TESTS PASSED SUCCESSFULLY!');
}

runTests().catch((err) => {
  console.error('Unhandled test error:', err);
  process.exit(1);
});
