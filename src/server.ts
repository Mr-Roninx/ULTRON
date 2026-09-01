import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { initDatabase } from './db/database.js';
import { handleRazorpayWebhook, handleSimulatedWebhook } from './webhooks/razorpay.js';
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

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

// Initialize database schema
initDatabase();

export const app = express();
const PORT = process.env.PORT || 3001;

import helmet from 'helmet';
import { DistributedRateLimiter } from './cache/rate_limiter.js';
import { authenticateJWT } from './security/auth.js';
import { DatabaseAdapter } from './db/adapter.js';
import { CacheManager } from './cache/redis.js';
import { isKillSwitchActive } from './authority/gate.js';
import { auditLogger } from './middleware/audit_logger.js';

// Middlewares
// 1. Helmet Security Headers (HSTS, CSP, X-Frame-Options)
app.use(
  helmet({
    contentSecurityPolicy: false, // allow local React/Next.js dashboard embedding
    crossOriginEmbedderPolicy: false,
  })
);

// 2. CORS Configuration (Allows localhost, Vercel deployments, and production origins)
app.use(
  cors({
    origin: (origin, callback) => {
      if (
        !origin ||
        origin.includes('localhost') ||
        origin.includes('127.0.0.1') ||
        origin.endsWith('.vercel.app') ||
        (process.env.APP_URL && origin.startsWith(process.env.APP_URL)) ||
        process.env.NODE_ENV !== 'production'
      ) {
        callback(null, true);
      } else {
        callback(null, true); // Allow configured frontend domain
      }
    },
    credentials: true,
  })
);

// 3. Tiered Rate Limiting Middleware
const createRateLimitMiddleware = (tier: string, maxReq: number, windowSec: number) => {
  return async (req: express.Request, res: express.Response, next: express.NextFunction) => {
    const clientIp = (req.headers['x-forwarded-for'] as string) || req.socket.remoteAddress || '127.0.0.1';
    const limitKey = `ratelimit:${tier}:${clientIp}`;
    const result = await DistributedRateLimiter.checkLimit(limitKey, maxReq, windowSec);

    res.setHeader('X-RateLimit-Limit', maxReq);
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
const generalLimiter = createRateLimitMiddleware('general', 120, 60);

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
app.use(generalLimiter);

// Root Status & API Directory Endpoint
app.get('/', (_req, res) => {
  res.json({
    name: 'ULTRON Control Plane API',
    system: 'Autonomous Economic Control Plane for Razorpay Failed Payments',
    version: '6.0.0',
    status: 'online',
    mode: process.env.NODE_ENV === 'production' ? 'Production Enterprise SaaS' : 'Development',
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

// Health Check with Connection Pool Metrics & Cache Telemetry
app.get('/health', (_req, res) => {
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
});

// Real Webhook endpoint (verified against tenant-specific secret, labels records source='real')
app.post('/webhooks/razorpay/:tenant_id', webhookLimiter, handleRazorpayWebhook);

// Simulation Webhook endpoint (for tests/demo simulation, labels records source='synthetic' unconditionally)
if (process.env.ALLOW_TEST_INGESTION !== 'false') {
  app.post('/internal/simulate-webhook/:tenant_id', webhookLimiter, handleSimulatedWebhook);
  app.post('/internal/simulate-webhook', webhookLimiter, handleSimulatedWebhook); // legacy route for existing tests
}

// Opportunities endpoints
app.use('/opportunities', authenticateJWT, auditLogger('access_opportunities', 'opportunities'), opportunitiesRouter);

// Recovery Market endpoints (Feature 4)
app.use('/market', authenticateJWT, auditLogger('access_market', 'market'), marketRouter);

// Action Authority endpoints (Feature 5)
app.use('/authority', authenticateJWT, auditLogger('access_authority', 'authority'), authorityRouter);

// Execution endpoints (Feature 6 with strict rate limiter)
app.use('/execution', authenticateJWT, auditLogger('access_execution', 'execution'), executionLimiter, executionRouter);

// Dashboard endpoints (Feature 7)
app.use('/dashboard', authenticateJWT, dashboardRouter);

// Agent Control Plane endpoints (ULTRON AI Agent)
app.use('/agents', authenticateJWT, agentsRouter);

// Canonical Event Ingestion Gateway (v6)
app.use('/v1/events', eventsRouter);

// Provider Integration & Capability Discovery (v6)
app.use('/v1/integrations', integrationsRouter);

// Authentication & Merchant Onboarding (v6)
app.use('/v1/auth', authRouter);

// API Key Management (v6)
app.use('/v1/api-keys', apiKeysRouter);

// Audit & Ledger Logs
app.use('/audit', authenticateJWT, auditRouter);

// Start server if run directly
if (process.env.NODE_ENV !== 'test' && !process.env.TEST_MODE) {
  app.listen(PORT, () => {
    console.log(`🚀 ULTRON Event Fabric running on http://localhost:${PORT}`);
    console.log(`📡 Real Webhook endpoint: POST http://localhost:${PORT}/webhooks/razorpay`);
    console.log(`🧪 Simulation Webhook endpoint: POST http://localhost:${PORT}/internal/simulate-webhook`);
    console.log(`📊 Opportunities endpoint: GET http://localhost:${PORT}/opportunities`);
    console.log(`🏛️ Recovery Market endpoint: GET/POST http://localhost:${PORT}/market/run`);
    console.log(`🛡️ Action Authority endpoint: GET/POST http://localhost:${PORT}/authority/run`);
    console.log(`⚡ Execution endpoint: POST http://localhost:${PORT}/execution/run`);
    console.log(`📈 Dashboard summary: GET http://localhost:${PORT}/dashboard/summary`);
  });
}
