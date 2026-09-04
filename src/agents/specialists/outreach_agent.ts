import { RecoveryOpportunity } from '../../types/index.js';
import { AgentToolRegistry } from '../tool_registry.js';
import { OutreachDraftRecord } from '../types.js';

export type OutreachTone = 'POLITE_REMINDER' | 'URGENT_ACTION' | 'ASSISTED_SUPPORT';

export class OutreachAgent {
  /**
   * Determine the most effective outreach tone.
   */
  public static determineTone(opp: RecoveryOpportunity): OutreachTone {
    if (opp.attempt_count >= 2) {
      return 'URGENT_ACTION';
    }
    if (opp.reason_code?.includes('NETWORK') || opp.reason_code?.includes('TIMEOUT')) {
      return 'POLITE_REMINDER';
    }
    return 'ASSISTED_SUPPORT';
  }

  public static async draftCustomerCommunication(params: {
    runId: string;
    opportunity: RecoveryOpportunity;
    channel: 'SMS' | 'WHATSAPP' | 'EMAIL';
    paymentLinkUrl?: string;
    tone?: OutreachTone;
  }): Promise<OutreachDraftRecord> {
    const amountInr = `₹${(params.opportunity.amount_paise / 100).toFixed(2)}`;
    const link = params.paymentLinkUrl || `https://rzp.io/i/${params.opportunity.id}`;
    const tone = params.tone || this.determineTone(params.opportunity);

    let subject: string | undefined = undefined;
    let body = '';

    if (params.channel === 'EMAIL') {
      if (tone === 'URGENT_ACTION') {
        subject = `Action Required: Final attempt to complete your payment of ${amountInr}`;
        body = `Dear Customer,\n\nYour transaction of ${amountInr} for order ${params.opportunity.id} could not be processed. This is your active retry link to avoid order cancellation:\n\n${link}\n\nOur team is available if you need further assistance.`;
      } else {
        subject = `Complete your payment of ${amountInr} for order ${params.opportunity.id}`;
        body = `Hello,\n\nWe noticed your recent payment of ${amountInr} was interrupted. You can safely complete it using our verified secure link:\n\n${link}\n\nIf you have already paid or have questions, please feel free to reply.`;
      }
    } else if (params.channel === 'WHATSAPP') {
      if (tone === 'URGENT_ACTION') {
        body = `⚠️ *Payment Pending*: Your transaction of ${amountInr} is on hold. Complete it now to secure your order: ${link}`;
      } else {
        body = `👋 Hi! Your payment of ${amountInr} was interrupted. Tap here to retry safely via Razorpay: ${link}`;
      }
    } else {
      // SMS
      if (tone === 'URGENT_ACTION') {
        body = `URGENT: Order ${params.opportunity.id.slice(0, 8)} pending payment of ${amountInr}. Pay securely: ${link}`;
      } else {
        body = `Payment of ${amountInr} for ref ${params.opportunity.id.slice(0, 8)} interrupted. Complete securely: ${link}`;
      }
    }

    const complianceFooter = 'ULTRON Autonomous Recovery • RBI Compliant • Reply STOP to opt out • Merchant Support';

    const toolRes = await AgentToolRegistry.executeTool({
      toolId: 'create_outreach_draft',
      runId: params.runId,
      agentName: 'OutreachAgent',
      inputPayload: {
        run_id: params.runId,
        opportunity_id: params.opportunity.id,
        channel: params.channel,
        recipient: params.opportunity.customer_id,
        subject,
        body,
        compliance_footer: complianceFooter,
      },
    });

    return {
      id: (toolRes as any).proposal_id || (toolRes.data as any)?.proposal_id || `draft_${Date.now()}`,
      run_id: params.runId,
      opportunity_id: params.opportunity.id,
      channel: params.channel,
      recipient: params.opportunity.customer_id,
      subject: subject || null,
      body,
      compliance_footer: complianceFooter,
      status: 'PENDING_REVIEW',
      review_feedback: null,
      created_at: new Date().toISOString(),
    };
  }
}
