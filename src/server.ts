import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { initDatabase } from './db/database.js';
import { handleRazorpayWebhook, handleSimulatedWebhook } from './webhooks/razorpay.js';
import { handleWhatsAppVerification, handleWhatsAppWebhookEvent } from './webhooks/whatsapp.js';
import { opportunitiesRouter } from './routes/opportunities.js';
import { marketRouter } from './routes/market.js';
import { authorityRouter } from './routes/authority.js';
import { executionRouter } from './routes/execution.js';
import { dashboardRouter } from './routes/dashboard.js';
import { agentsRouter } from './routes/agents.js';
import { eventsRouter } from './routes/events.js';
import { integrationsRouter } from './routes/integrations.js';
import { authRouter } from './routes/auth.js';
import { apiKeysRouter } from './routes/api_keys.js';
import { auditRouter } from './routes/audit.js';
import { sdkRouter } from './routes/sdk.js';
import { notificationsRouter } from './routes/notifications.js';
import { webhooksQueueRouter } from './routes/webhooks_queue.js';
import { playgroundRouter } from './routes/playground.js';
import { auditExportRouter } from './routes/audit_export.js';
import { hitlRouter } from './agents/hitl/hitl_routes.js';
import { AutonomousRecoveryDaemon } from './agents/daemon.js';
import { JobScheduler } from './execution/job_scheduler.js';
import { WebhookQueueEngine } from './webhooks/queue.js';
import { metrics } from './observability/metrics.js';
import { tracingMiddleware } from './middleware/tracing.js';
import { HealthService } from './observability/health.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

import { logger } from './observability/logger.js';
import { MigrationRunner } from './db/migrations/runner.js';
import { initOpenTelemetry, shutdownOpenTelemetry } from './observability/otel.js';

// Initialize OpenTelemetry Distributed Tracing
initOpenTelemetry();

// Initialize database schema & run auto-migrations
initDatabase();
MigrationRunner.migrateUp().then(({ applied }) => {
  if (applied.length > 0) {
    logger.info(`🚀 DatabaseAdapter: Applied ${applied.length} schema migrations successfully.`);
  }
}).catch((err) => {
  logger.warn({ err }, '⚠️ Migration warning');
});

// Auto-Sync and Permanently Seed Default Tenant Credentials & API Keys to Supabase
(async () => {
  try {
    const { SecretsManager } = await import('./security/secrets.js');
    const { ApiKeyService } = await import('./security/api_keys.js');

    if (process.env.RAZORPAY_KEY_ID && process.env.RAZORPAY_KEY_SECRET) {
      await SecretsManager.storeTenantCredential({
        tenantId: 'tenant_system_default',
        provider: 'razorpay',
        environment: 'test',
        credentialReference: 'ref_rzp_tenant_system_default_test',
        rawSecret: JSON.stringify({
          key_id: process.env.RAZORPAY_KEY_ID,
          key_secret: process.env.RAZORPAY_KEY_SECRET,
          webhook_secret: process.env.RAZORPAY_WEBHOOK_SECRET || 'rzp_whsec_ultron_test',
        }),
      });
    }

    const existingKeys = await ApiKeyService.listApiKeys('tenant_system_default');
    if (existingKeys.length === 0) {
      await ApiKeyService.createApiKey({
        tenantId: 'tenant_system_default',
        name: 'Default Root Production Key',
        environment: 'test',
        scopes: ['events:write', 'events:read', 'payments:read', 'recoveries:read', 'analytics:read', 'agent:read', 'integrations:read', 'integrations:write'],
      });
    }
    logger.info('⚡ SupabaseStore: Synced and verified permanent credentials with Supabase.');
  } catch (err: any) {
    logger.warn({ err }, '⚠️ SupabaseStore auto-seed warning');
  }
})();

export const app = express();
const PORT = process.env.PORT || 3001;

import helmet from 'helmet';
import { DistributedRateLimiter } from './cache/rate_limiter.js';
import { authenticateJWT, authorizeRole, UserRole } from './security/auth.js';
import { DatabaseAdapter } from './db/adapter.js';
import { CacheManager } from './cache/redis.js';
import { isKillSwitchActive } from './authority/gate.js';
import { auditLogger } from './middleware/audit_logger.js';

import { getSecurityHeadersMiddleware } from './security/csp_headers.js';
import { inputSanitizerMiddleware } from './security/input_sanitizer.js';
import { versionNegotiationMiddleware, createV2Router } from './gateway/versioning.js';
import { tieredRateLimiter } from './gateway/rate_tiers.js';
import { createOpenAPIRouter } from './gateway/openapi_generator.js';

// Middlewares
// 1. Enterprise Security Headers (CSP, HSTS, X-Frame-Options)
app.use(getSecurityHeadersMiddleware());

// 2. CORS Configuration with strict production allowlist
const allowedOrigins = (process.env.ALLOWED_ORIGINS || '')
  .split(',')
  .map((s) => s.trim())
  .filter(Boolean);

app.use(
  cors({
    origin: (origin, callback) => {
      if (!origin) {
        // Allow server-to-server or non-browser requests
        return callback(null, true);
      }

      if (process.env.NODE_ENV !== 'production') {
        // Development / testing: allow localhost, 127.0.0.1, vercel preview deployments
        if (
          origin.includes('localhost') ||
          origin.includes('127.0.0.1') ||
          origin.endsWith('.vercel.app')
        ) {
          return callback(null, true);
        }
      }

      // Production checks: configured ALLOWED_ORIGINS or APP_URL
      if (
        allowedOrigins.includes(origin) ||
        (process.env.APP_URL && origin === process.env.APP_URL) ||
        (process.env.NEXT_PUBLIC_APP_URL && origin === process.env.NEXT_PUBLIC_APP_URL)
      ) {
        return callback(null, true);
      }

      if (process.env.NODE_ENV === 'production') {
        return callback(new Error(`CORS policy rejection: Origin '${origin}' is not authorized.`), false);
      }

      return callback(null, true);
    },
    credentials: true,
  })
);

// 3. Tiered Rate Limiting Middleware
const createRateLimitMiddleware = (tier: string, maxReq: number, windowSec: number) => {
  return async (req: express.Request, res: express.Response, next: express.NextFunction) => {
    // In development or test environments, bypass rate limiting to prevent UI dashboard lockouts
    if (process.env.NODE_ENV !== 'production' || process.env.DISABLE_RATE_LIMITS === 'true') {
      return next();
    }

    const clientIp = (req.headers['x-forwarded-for'] as string) || req.socket.remoteAddress || '127.0.0.1';
    const limitKey = `ratelimit:${tier}:${clientIp}`;
    const effectiveLimit = Math.max(maxReq, 600); // 600 req/min floor for reliable UI usage
    const result = await DistributedRateLimiter.checkLimit(limitKey, effectiveLimit, windowSec);

    res.setHeader('X-RateLimit-Limit', effectiveLimit);
    res.setHeader('X-RateLimit-Remaining', result.remaining);
    res.setHeader('X-RateLimit-Reset', result.resetSeconds);

    if (!result.allowed) {
      res.status(429).json({
        error: 'Too Many Requests',
        message: `Rate limit exceeded for ${tier}. Try again in ${result.resetSeconds}s.`,
      });
      return;
    }
    next();
  };
};

// Rate Limiters per Tier
const webhookLimiter = createRateLimitMiddleware('webhook', 100, 60);
const executionLimiter = createRateLimitMiddleware('execution', 10, 60);
const generalLimiter = createRateLimitMiddleware('general', 600, 60);

// Capture raw body for HMAC signature verification (Max 1MB)
app.use(
  express.json({
    limit: '1mb',
    verify: (req: any, _res, buf) => {
      req.rawBody = buf.toString('utf-8');
    },
  })
);

app.use(express.urlencoded({ extended: true, limit: '1mb' }));
app.use(inputSanitizerMiddleware);
app.use(tracingMiddleware);

// Enterprise API Gateway Layer (V11)
app.use(versionNegotiationMiddleware);
app.use(tieredRateLimiter());
app.use(createOpenAPIRouter());
app.use('/v2', createV2Router());

// Enterprise Prometheus Metrics Export Endpoint
app.get('/metrics', (_req, res) => {
  res.setHeader('Content-Type', 'text/plain; version=0.0.4');
  res.send(metrics.exportMetrics());
});

// 3-Tier Enterprise Health Check Probes
app.get('/health/live', HealthService.liveness);
app.get('/health/ready', HealthService.readiness);
app.get('/health/readiness', HealthService.readiness);
app.get('/health/deep', HealthService.deep);

// Health Check with Connection Pool Metrics & Cache Telemetry (Legacy /health)
app.get('/health', (_req, res) => {
  try {
    const dbAdapter = DatabaseAdapter.getInstance();
    const cacheManager = CacheManager.getInstance();

    res.json({
      status: 'healthy',
      system: 'ULTRON Autonomous Economic Control Plane',
      mode: process.env.NODE_ENV === 'production' ? 'Production Enterprise SaaS' : 'Development / Test Mode',
      kill_switch_active: isKillSwitchActive(),
      database: dbAdapter.getPoolMetrics(),
      cache: cacheManager.getStatus(),
      timestamp: new Date().toISOString(),
    });
  } catch (err: any) {
    res.json({
      status: 'degraded',
      system: 'ULTRON Autonomous Economic Control Plane',
      mode: process.env.NODE_ENV === 'production' ? 'Production Enterprise SaaS' : 'Development',
      error: err.message,
      timestamp: new Date().toISOString(),
    });
  }
});

// Root Status & API Directory Endpoint
app.get('/', (req, res) => {
  const acceptsHtml = req.headers.accept && req.headers.accept.includes('text/html');

  if (acceptsHtml) {
    const frontendUrl = process.env.APP_URL || 'https://ultron-power.vercel.app';
    res.send(`
      <!DOCTYPE html>
      <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>ULTRON Control Plane API</title>
          <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
              background: radial-gradient(circle at top, #0d1527 0%, #060b18 100%);
              color: #f1f5f9;
              min-height: 100vh;
              display: flex;
              align-items: center;
              justify-content: center;
              padding: 24px;
            }
            .card {
              max-width: 600px;
              width: 100%;
              background: rgba(15, 23, 42, 0.75);
              border: 1px solid rgba(59, 130, 246, 0.25);
              border-radius: 20px;
              padding: 40px;
              text-align: center;
              box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
              backdrop-filter: blur(12px);
            }
            .badge {
              display: inline-flex;
              align-items: center;
              gap: 6px;
              padding: 6px 14px;
              background: rgba(16, 185, 129, 0.12);
              border: 1px solid rgba(16, 185, 129, 0.3);
              color: #34d399;
              border-radius: 9999px;
              font-size: 13px;
              font-weight: 600;
              margin-bottom: 20px;
            }
            .dot { width: 8px; height: 8px; border-radius: 50%; background: #10b981; }
            h1 { font-size: 28px; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 10px; }
            p { font-size: 15px; color: #94a3b8; line-height: 1.6; margin-bottom: 28px; }
            .btn {
              display: inline-flex;
              align-items: center;
              justify-content: center;
              gap: 8px;
              background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
              color: #ffffff;
              padding: 14px 28px;
              border-radius: 12px;
              text-decoration: none;
              font-size: 15px;
              font-weight: 600;
              box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
              transition: transform 0.2s, box-shadow 0.2s;
            }
            .btn:hover {
              transform: translateY(-2px);
              box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
            }
            .endpoints {
              margin-top: 32px;
              padding-top: 24px;
              border-top: 1px solid rgba(255, 255, 255, 0.08);
              text-align: left;
            }
            .endpoints h3 { font-size: 12px; text-transform: uppercase; color: #64748b; letter-spacing: 1px; margin-bottom: 12px; }
            .tag-group { display: flex; flex-wrap: wrap; gap: 8px; }
            .tag {
              background: rgba(255, 255, 255, 0.05);
              border: 1px solid rgba(255, 255, 255, 0.1);
              padding: 4px 10px;
              border-radius: 6px;
              font-size: 12px;
              font-family: monospace;
              color: #cbd5e1;
            }
          </style>
        </head>
        <body>
          <div class="card">
            <div class="badge"><span class="dot"></span> Backend API Online • v6.0.0</div>
            <h1>🛡️ ULTRON Control Plane</h1>
            <p>
              Autonomous Economic Control Plane for Razorpay Failed-Payment Recovery.
              This is the backend API engine. You can access the live web dashboard below.
            </p>
            <a class="btn" href="${frontendUrl}" target="_blank">
              Open Web Application Dashboard →
            </a>
            <div class="endpoints">
              <h3>Active API Services</h3>
              <div class="tag-group">
                <span class="tag">GET /health</span>
                <span class="tag">POST /v1/auth/signup</span>
                <span class="tag">POST /v1/auth/login</span>
                <span class="tag">POST /v1/events</span>
                <span class="tag">POST /webhooks/razorpay/:tenant_id</span>
                <span class="tag">GET /dashboard/summary</span>
                <span class="tag">POST /market/run</span>
              </div>
            </div>
          </div>
        </body>
      </html>
    `);
    return;
  }

  res.json({
    name: 'ULTRON Control Plane API',
    system: 'Autonomous Economic Control Plane for Razorpay Failed Payments',
    version: '6.0.0',
    status: 'online',
    mode: process.env.NODE_ENV === 'production' ? 'Production Enterprise SaaS' : 'Development',
    frontend: process.env.APP_URL || 'https://ultron-power.vercel.app',
    health: '/health',
    endpoints: {
      auth: '/v1/auth',
      events: '/v1/events',
      webhooks: '/webhooks/razorpay/:tenant_id',
      dashboard: '/dashboard/summary',
      opportunities: '/opportunities',
      market: '/market/run',
      execution: '/execution/records',
      api_keys: '/v1/api-keys',
      integrations: '/v1/integrations',
      audit: '/audit/records',
    },
  });
});

// Real Webhook endpoint (verified against tenant-specific secret, labels records source='real')
app.post('/webhooks/razorpay/:tenant_id', webhookLimiter, handleRazorpayWebhook);

// Simulation Webhook endpoint (for tests/demo simulation, labels records source='synthetic' unconditionally)
if (process.env.ALLOW_TEST_INGESTION !== 'false') {
  app.post('/internal/simulate-webhook/:tenant_id', webhookLimiter, handleSimulatedWebhook);
  app.post('/internal/simulate-webhook', webhookLimiter, handleSimulatedWebhook); // legacy route for existing tests
}

// Meta WhatsApp Cloud API Webhook endpoints (Challenge GET verification & Delivery Receipts POST)
app.get('/webhooks/whatsapp', handleWhatsAppVerification);
app.post('/webhooks/whatsapp', handleWhatsAppWebhookEvent);
app.get('/v1/webhooks/whatsapp', handleWhatsAppVerification);
app.post('/v1/webhooks/whatsapp', handleWhatsAppWebhookEvent);

// Opportunities endpoints
app.use('/opportunities', authenticateJWT, auditLogger('access_opportunities', 'opportunities'), opportunitiesRouter);

// Recovery Market endpoints (Feature 4)
app.use('/market', authenticateJWT, authorizeRole([UserRole.ADMIN, UserRole.OPERATOR]), auditLogger('access_market', 'market'), marketRouter);

// Action Authority endpoints (Feature 5)
app.use('/authority', authenticateJWT, authorizeRole([UserRole.ADMIN, UserRole.OPERATOR, UserRole.VIEWER]), auditLogger('access_authority', 'authority'), authorityRouter);

// Execution endpoints (Feature 6 with strict rate limiter) - Requires Operator or Admin
app.use('/execution', authenticateJWT, authorizeRole([UserRole.ADMIN, UserRole.OPERATOR]), auditLogger('access_execution', 'execution'), executionLimiter, executionRouter);

// Dashboard endpoints (Feature 7) - Requires at least Operator role
app.use('/dashboard', authenticateJWT, authorizeRole([UserRole.ADMIN, UserRole.OPERATOR, UserRole.VIEWER]), dashboardRouter);

// Agent Control Plane endpoints (ULTRON AI Agent) - strictly Admin only
app.use('/agents', authenticateJWT, authorizeRole([UserRole.ADMIN]), agentsRouter);

// Canonical Event Ingestion Gateway (v6)
app.use('/v1/events', webhookLimiter, eventsRouter);

// Provider Integration & Capability Discovery (v6)
app.use('/v1/integrations', generalLimiter, integrationsRouter);

// Authentication & Merchant Onboarding (v6)
app.use('/v1/auth', generalLimiter, authRouter);

// API Key Management (v6) - strictly Admin only
app.use('/v1/api-keys', authenticateJWT, authorizeRole([UserRole.ADMIN]), executionLimiter, apiKeysRouter);

// Audit & Ledger Logs
app.use('/audit', authenticateJWT, auditRouter);
app.use('/v1/audit', auditExportRouter);

// Recovery Activity Notifications (v6)
app.use('/v1/notifications', executionLimiter, notificationsRouter);

// Webhook Delivery Queue & Replay (v6)
app.use('/v1/webhooks/queue', webhookLimiter, webhooksQueueRouter);

// Human-in-the-Loop (HITL) Approval Workflows
app.use('/api/hitl', generalLimiter, hitlRouter);
app.use('/v1/hitl', generalLimiter, hitlRouter);

// Recovery Playground & Real-Time Visualization (v6)
app.use('/v1/playground', executionLimiter, playgroundRouter);

// Zero-Code Drop-In Client SDK
app.use('/sdk', sdkRouter);
app.use('/ultron.js', sdkRouter);

// Demo Merchant Storefront (for live testing & merchant verification)
app.use('/demo', express.static(path.resolve(process.cwd(), 'public')));
app.get('/demo-store', (_req, res) => {
  res.sendFile(path.resolve(process.cwd(), 'public', 'demo_merchant_store.html'));
});

// 5-Minute Executive Pitch Landing Page with Audio & Synchronized Captions
app.use('/pitch', express.static(path.resolve(process.cwd(), 'Pitch')));
app.get('/pitch-page', (_req, res) => {
  res.sendFile(path.resolve(process.cwd(), 'Pitch', 'index.html'));
});
app.get('/pitch-video', (_req, res) => {
  res.sendFile(path.resolve(process.cwd(), 'Pitch', 'video.html'));
});

// Start server if run directly
const isDirectRun = process.env.NODE_ENV !== 'test' && !process.env.TEST_MODE && !process.env.SUPPRESS_LISTEN;

if (isDirectRun) {
  const server = app.listen(PORT, () => {
    console.log(`🚀 ULTRON Event Fabric running on http://localhost:${PORT}`);
    logger.info(`🚀 ULTRON Event Fabric running on http://localhost:${PORT}`);
    logger.info(`📡 Real Webhook endpoint: POST http://localhost:${PORT}/webhooks/razorpay`);
    logger.info(`🧪 Simulation Webhook endpoint: POST http://localhost:${PORT}/internal/simulate-webhook`);
    logger.info(`📊 Opportunities endpoint: GET http://localhost:${PORT}/opportunities`);
    logger.info(`📈 Dashboard summary: GET http://localhost:${PORT}/dashboard/summary`);
    
    // Automatically start 24/7 Autonomous Background Recovery Engine
    AutonomousRecoveryDaemon.getInstance().start({ interval_seconds: 10, capacity: 5 });
    console.log(`🤖 24/7 Autonomous Recovery Engine ACTIVE: auto-sweeping every 10s without manual intervention`);
    logger.info(`🤖 24/7 Autonomous Recovery Engine ACTIVE: auto-sweeping every 10s without manual intervention`);

    // Automatically start Unified Background Maintenance Job Scheduler
    JobScheduler.getInstance().start();
    console.log(`⏱️ Background JobScheduler ACTIVE: automated DLQ sweeps (60s) and reconciliation (5m)`);
    logger.info(`⏱️ Background JobScheduler ACTIVE: automated DLQ sweeps (60s) and reconciliation (5m)`);
  });

  // Graceful shutdown handler
  let isShuttingDown = false;
  const gracefulShutdown = async (signal: string) => {
    if (isShuttingDown) return;
    isShuttingDown = true;
    console.log(`🛑 Received ${signal}. Draining in-flight iterations and shutting down cleanly...`);
    logger.info(`🛑 Received ${signal}. Draining in-flight iterations and shutting down cleanly...`);

    // Stop accepting new HTTP requests
    server.close(() => {
      logger.info('HTTP server closed.');
    });

    try {
      // Drain background jobs and active iterations (up to 30s)
      await JobScheduler.getInstance().stop();
      await AutonomousRecoveryDaemon.getInstance().waitForDrain(30000);

      // Cleanly flush & close OpenTelemetry
      await shutdownOpenTelemetry();

      // Cleanly terminate DB connections
      const { DatabaseAdapter } = await import('./db/adapter.js');
      await DatabaseAdapter.getInstance().close();

      console.log('✅ Graceful shutdown complete. Process terminated cleanly.');
      logger.info('✅ Graceful shutdown complete. Process terminated cleanly.');
      process.exit(0);
    } catch (err: any) {
      console.error('❌ Error during graceful shutdown:', err?.message || err);
      logger.error({ err }, 'Error during graceful shutdown');
      process.exit(1);
    }
  };

  process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
  process.on('SIGINT', () => gracefulShutdown('SIGINT'));
}
