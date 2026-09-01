import { Resend } from 'resend';
import nodemailer from 'nodemailer';

const resendApiKey = process.env.RESEND_API_KEY;
const fromEmail = process.env.SMTP_FROM || process.env.RESEND_FROM_EMAIL || 'ULTRON Recovery <onboarding@resend.dev>';

// Initialize Resend Client
let resendClient: Resend | null = null;
if (resendApiKey) {
  resendClient = new Resend(resendApiKey);
}

// Initialize Custom SMTP Transporter
let smtpTransporter: nodemailer.Transporter | null = null;
if (process.env.SMTP_HOST && process.env.SMTP_USER && process.env.SMTP_PASS) {
  const isSecure = process.env.SMTP_SECURE === 'true' || Number(process.env.SMTP_PORT) === 465;
  smtpTransporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT) || (isSecure ? 465 : 587),
    secure: isSecure,
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS,
    },
  });
  console.log(`📧 EmailService: Initialized custom SMTP transporter (${process.env.SMTP_HOST}:${process.env.SMTP_PORT || 587})`);
}

export interface SendEmailOptions {
  to: string | string[];
  subject: string;
  html: string;
}

/**
 * Dispatches an email via SMTP or Resend with graceful console fallback in development.
 */
export async function sendEmail(options: SendEmailOptions): Promise<{ success: boolean; id?: string; error?: string }> {
  try {
    // 1. Prioritize custom SMTP if configured
    if (smtpTransporter) {
      const info = await smtpTransporter.sendMail({
        from: fromEmail,
        to: options.to,
        subject: options.subject,
        html: options.html,
      });
      return { success: true, id: info.messageId };
    }

    // 2. Fallback to Resend API
    if (resendClient) {
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
    }

    // 3. Fallback to Console simulation in dev
    console.log(`📧 [EMAIL SIMULATION] To: ${options.to} | Subject: ${options.subject}`);
    return { success: true, id: `sim_${Date.now()}` };
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

/**
 * Sends a Magic Link sign-in / verification email.
 */
export async function sendMagicLinkEmail(recipientEmail: string, magicLinkUrl: string, businessName: string = 'ULTRON') {
  const html = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sign in to ULTRON</title>
      </head>
      <body style="margin: 0; padding: 0; background-color: #060b18; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f1f5f9;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #060b18; padding: 40px 20px;">
          <tr>
            <td align="center">
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 520px; background: linear-gradient(135deg, #0d1527 0%, #111a33 100%); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 16px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
                <!-- Header / Logo -->
                <tr>
                  <td style="padding: 36px 36px 20px 36px; text-align: center;">
                    <div style="display: inline-block; padding: 12px 16px; background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; margin-bottom: 12px;">
                      <span style="font-size: 20px; font-weight: 800; letter-spacing: 2px; color: #38bdf8;">🛡️ ULTRON</span>
                    </div>
                    <h1 style="margin: 12px 0 6px 0; font-size: 22px; font-weight: 700; color: #ffffff;">Sign in with Magic Link</h1>
                    <p style="margin: 0; font-size: 14px; color: #94a3b8;">Access your autonomous recovery control plane</p>
                  </td>
                </tr>

                <!-- Content -->
                <tr>
                  <td style="padding: 10px 36px 30px 36px; text-align: center;">
                    <p style="font-size: 15px; line-height: 1.6; color: #cbd5e1; margin-bottom: 28px;">
                      Click the button below to securely sign in to your <strong>${businessName}</strong> merchant workspace. This link expires in 15 minutes.
                    </p>

                    <!-- CTA Button -->
                    <table border="0" cellspacing="0" cellpadding="0" style="margin: 0 auto;">
                      <tr>
                        <td align="center" style="border-radius: 10px; background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);">
                          <a href="${magicLinkUrl}" target="_blank" style="display: inline-block; padding: 14px 32px; font-size: 15px; font-weight: 600; color: #ffffff; text-decoration: none; border-radius: 10px; letter-spacing: 0.3px;">
                            Sign in to Control Plane →
                          </a>
                        </td>
                      </tr>
                    </table>

                    <p style="font-size: 12px; line-height: 1.5; color: #64748b; margin-top: 28px; word-break: break-all;">
                      Or copy and paste this link into your browser:<br>
                      <a href="${magicLinkUrl}" style="color: #38bdf8; text-decoration: underline;">${magicLinkUrl}</a>
                    </p>
                  </td>
                </tr>

                <!-- Security Note / Footer -->
                <tr>
                  <td style="padding: 20px 36px; background: rgba(15, 23, 42, 0.6); border-top: 1px solid rgba(255, 255, 255, 0.06); text-align: center;">
                    <p style="margin: 0 0 6px 0; font-size: 12px; color: #64748b;">
                      If you did not request this link, you can safely ignore this email.
                    </p>
                    <p style="margin: 0; font-size: 11px; color: #475569;">
                      ULTRON Control Plane • Razorpay Failed-Payment Autonomous Recovery
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
  `;

  return sendEmail({
    to: recipientEmail,
    subject: `Sign in to ULTRON Control Plane`,
    html,
  });
}
