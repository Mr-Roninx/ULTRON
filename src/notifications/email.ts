import { Resend } from 'resend';

const resendApiKey = process.env.RESEND_API_KEY;
const fromEmail = process.env.RESEND_FROM_EMAIL || 'ULTRON Recovery <onboarding@resend.dev>';

let resendClient: Resend | null = null;

if (resendApiKey) {
  resendClient = new Resend(resendApiKey);
}

export interface SendEmailOptions {
  to: string | string[];
  subject: string;
  html: string;
}

/**
 * Dispatches an email via Resend with graceful console fallback in development.
 */
export async function sendEmail(options: SendEmailOptions): Promise<{ success: boolean; id?: string; error?: string }> {
  try {
    if (!resendClient) {
      console.log(`📧 [EMAIL SIMULATION] To: ${options.to} | Subject: ${options.subject}`);
      return { success: true, id: `sim_${Date.now()}` };
    }

    const { data, error } = await resendClient.emails.send({
      from: fromEmail,
      to: options.to,
      subject: options.subject,
      html: options.html,
    });

    if (error) {
      console.error('Failed to send email via Resend:', error);
      return { success: false, error: error.message };
    }

    return { success: true, id: data?.id };
  } catch (err: any) {
    console.error('Error sending email:', err);
    return { success: false, error: err.message };
  }
}

/**
 * Sends a Team Invitation email.
 */
export async function sendTeamInviteEmail(recipientEmail: string, role: string, inviterName: string, inviteUrl: string) {
  const html = `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 560px; margin: 0 auto; padding: 32px 20px; color: #1e293b;">
      <h2 style="color: #0f172a; margin-bottom: 16px;">You've been invited to join ULTRON</h2>
      <p style="font-size: 15px; line-height: 1.6; color: #475569;">
        <strong>${inviterName}</strong> has invited you to join their autonomous payment recovery workspace as a <strong>${role}</strong>.
      </p>
      <div style="margin: 28px 0;">
        <a href="${inviteUrl}" style="background: #3b82f6; color: #ffffff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px; display: inline-block;">
          Accept Invitation
        </a>
      </div>
      <p style="font-size: 13px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 16px;">
        ULTRON — Autonomous Economic Control Plane for Failed Payments.
      </p>
    </div>
  `;

  return sendEmail({
    to: recipientEmail,
    subject: `Invitation to join ULTRON (${role})`,
    html,
  });
}
