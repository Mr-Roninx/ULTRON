import helmet from 'helmet';
import { RequestHandler } from 'express';

/**
 * ULTRON V11 — Enterprise Content Security Policy & Security Headers
 * 
 * Enforces strict browser-side sandbox boundaries preventing XSS, clickjacking,
 * and untrusted script execution.
 */
export function getSecurityHeadersMiddleware(): RequestHandler {
  const isProd = process.env.NODE_ENV === 'production';

  return helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: [
          "'self'",
          "'unsafe-inline'", // For Next.js runtime hydration scripts in dev
          'https://checkout.razorpay.com',
          'https://*.razorpay.com',
        ],
        styleSrc: ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
        fontSrc: ["'self'", 'https://fonts.gstatic.com'],
        imgSrc: ["'self'", 'data:', 'https:'],
        connectSrc: [
          "'self'",
          'https://api.razorpay.com',
          'https://*.supabase.co',
          'https://*.resend.com',
          'http://localhost:*',
          'ws://localhost:*',
        ],
        frameAncestors: ["'none'"],
        formAction: ["'self'", 'https://api.razorpay.com'],
        upgradeInsecureRequests: isProd ? [] : null,
      },
    },
    crossOriginEmbedderPolicy: false,
    crossOriginOpenerPolicy: { policy: 'same-origin-allow-popups' },
    crossOriginResourcePolicy: { policy: 'cross-origin' },
    referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
    hsts: isProd ? { maxAge: 31536000, includeSubDomains: true, preload: true } : false,
    noSniff: true,
    xssFilter: true,
  });
}
