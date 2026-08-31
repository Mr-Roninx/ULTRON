import {
  getAllOpportunities,
  getExecutionRecordByOpportunityId,
  updateOpportunityStatus,
  insertLedgerEntry,
} from '../db/database.js';
import { rzpClient } from '../execution/executor.js';

/**
 * RECONCILIATION DESIGN NOTE:
 * Webhooks are not guaranteed to arrive in production or test environments due to potential
 * network drops, intermediate gateway retry timeouts, or server cold starts.
 * The active reconciliation poller provides a deterministic secondary verification loop
 * by querying Razorpay's API directly for any opportunity in 'executing' status, ensuring
 * dual-path eventual truth reconciliation without relying solely on asynchronous webhooks.
 */

export interface PolledItemResult {
  opportunity_id: string;
  payment_link_id: string;
  previous_status: string;
  new_status: string;
  reconciled: boolean;
  error?: string;
}

export interface PollerRunResult {
  total_checked: number;
  reconciled_count: number;
  still_executing_count: number;
  failed_count: number;
  items: PolledItemResult[];
}

export async function pollAndReconcile(): Promise<PollerRunResult> {
  const allOpps = getAllOpportunities();
  // Opportunities currently in flight
  const executingOpps = allOpps.filter(
    (opp) => opp.status === 'executing' || opp.status === 'authorized' || opp.status === 'allocated'
  );

  const items: PolledItemResult[] = [];
  let reconciled_count = 0;
  let still_executing_count = 0;
  let failed_count = 0;

  for (const opp of executingOpps) {
    const record = getExecutionRecordByOpportunityId(opp.id);
    if (!record || !record.razorpay_payment_link_id) {
      continue;
    }

    try {
      // Direct API query to Razorpay
      const plink: any = await rzpClient.paymentLink.fetch(record.razorpay_payment_link_id);
      const linkStatus = plink?.status; // 'created', 'paid', 'expired', 'cancelled', 'partially_paid'

      if (linkStatus === 'paid') {
        updateOpportunityStatus(opp.id, 'recovered');
        const now = new Date().toISOString();
        insertLedgerEntry({
          id: `led_poll_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
          opportunity_id: opp.id,
          event_type: 'recovered',
          amount_paise: opp.amount_paise,
          timestamp: now,
          raw_payload_ref: JSON.stringify({
            source: 'reconciliation_poller',
            razorpay_payment_link_id: record.razorpay_payment_link_id,
            amount_paid: plink?.amount_paid || opp.amount_paise,
            payment_id: plink?.payments?.[0]?.payment_id,
          }),
        });

        reconciled_count++;
        items.push({
          opportunity_id: opp.id,
          payment_link_id: record.razorpay_payment_link_id,
          previous_status: opp.status,
          new_status: 'recovered',
          reconciled: true,
        });
      } else if (linkStatus === 'expired' || linkStatus === 'cancelled') {
        updateOpportunityStatus(opp.id, 'not_recovered');
        const now = new Date().toISOString();
        insertLedgerEntry({
          id: `led_poll_exp_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
          opportunity_id: opp.id,
          event_type: 'not_recovered',
          amount_paise: opp.amount_paise,
          timestamp: now,
          raw_payload_ref: JSON.stringify({
            source: 'reconciliation_poller',
            razorpay_payment_link_id: record.razorpay_payment_link_id,
            link_status: linkStatus,
          }),
        });

        reconciled_count++;
        items.push({
          opportunity_id: opp.id,
          payment_link_id: record.razorpay_payment_link_id,
          previous_status: opp.status,
          new_status: 'not_recovered',
          reconciled: true,
        });
      } else {
        still_executing_count++;
        items.push({
          opportunity_id: opp.id,
          payment_link_id: record.razorpay_payment_link_id,
          previous_status: opp.status,
          new_status: opp.status,
          reconciled: false,
        });
      }
    } catch (err: any) {
      failed_count++;
      items.push({
        opportunity_id: opp.id,
        payment_link_id: record.razorpay_payment_link_id,
        previous_status: opp.status,
        new_status: opp.status,
        reconciled: false,
        error: err?.message || 'Poller fetch failed',
      });
    }
  }

  return {
    total_checked: items.length,
    reconciled_count,
    still_executing_count,
    failed_count,
    items,
  };
}
