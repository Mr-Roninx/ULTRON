import { RecoveryOpportunity } from '../../types/index.js';
import { AgentToolRegistry } from '../tool_registry.js';
import { OutreachDraftRecord } from '../types.js';

export class OutreachAgent {
  public static async draftCustomerCommunication(params: {
    runId: string;
    opportunity: RecoveryOpportunity;
    channel: 'SMS' | 'WHATSAPP' | 'EMAIL';
    paymentLinkUrl?: string;
  }): Promise<OutreachDraftRecord> {
    const amountInr = `₹${(params.opportunity.amount_paise / 100).toFixed(2)}`;
    const link = params.paymentLinkUrl || `https://rzp.io/i/${params.opportunity.id}`;

    let subject: string | undefined = undefined;
    let body = '';

    if (params.channel === 'EMAIL') {
      subject = `Payment update for your order (${params.opportunity.id})`;
      body = `Hello,\n\nWe noticed your recent payment of ${amountInr} could not be completed. You can safely complete the payment using the secure link below:\n\n${link}\n\nIf you have already paid or need assistance, please reply to this email.`;
    } else if (params.channel === 'WHATSAPP') {
      body = `Hi there, your payment of ${amountInr} was interrupted. You can quickly retry and complete it securely here: ${link}`;
    } else {
      // SMS
      body = `Payment of ${amountInr} for ref ${params.opportunity.id.slice(0, 8)} pending. Complete securely: ${link}`;
    }

    const complianceFooter = 'ULTRON Autonomous Recovery • Standard messaging rates may apply • Reply STOP to opt out • Merchant Support';

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
      id: toolRes.proposal_id || `draft_${Date.now()}`,
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
