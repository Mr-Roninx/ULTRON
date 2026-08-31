import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { initDatabase } from './db/database.js';
import { handleRazorpayWebhook } from './webhooks/razorpay.js';
import { opportunitiesRouter } from './routes/opportunities.js';
import { marketRouter } from './routes/market.js';
import { authorityRouter } from './routes/authority.js';
import { executionRouter } from './routes/execution.js';
import { dashboardRouter } from './routes/dashboard.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

// Initialize database schema
initDatabase();

export const app = express();
const PORT = process.env.PORT || 3001;

// Middlewares
app.use(cors());

// Capture raw body for HMAC signature verification
app.use(
  express.json({
    verify: (req: any, _res, buf) => {
      req.rawBody = buf.toString('utf-8');
    },
  })
);

app.use(express.urlencoded({ extended: true }));

// Health Check
app.get('/health', (_req, res) => {
  res.json({
    status: 'healthy',
    system: 'ULTRON Autonomous Economic Control Plane',
    mode: 'Razorpay Test Mode',
    timestamp: new Date().toISOString(),
  });
});

// Webhook endpoint
app.post('/webhooks/razorpay', handleRazorpayWebhook);

// Opportunities endpoints
app.use('/opportunities', opportunitiesRouter);

// Recovery Market endpoints (Feature 4)
app.use('/market', marketRouter);

// Action Authority endpoints (Feature 5)
app.use('/authority', authorityRouter);

// Execution endpoints (Feature 6)
app.use('/execution', executionRouter);

// Dashboard endpoints (Feature 7)
app.use('/dashboard', dashboardRouter);

// Start server if run directly
if (process.env.NODE_ENV !== 'test' && !process.env.TEST_MODE) {
  app.listen(PORT, () => {
    console.log(`🚀 ULTRON Event Fabric running on http://localhost:${PORT}`);
    console.log(`📡 Webhook endpoint: POST http://localhost:${PORT}/webhooks/razorpay`);
    console.log(`📊 Opportunities endpoint: GET http://localhost:${PORT}/opportunities`);
    console.log(`🏛️ Recovery Market endpoint: GET/POST http://localhost:${PORT}/market/run`);
    console.log(`🛡️ Action Authority endpoint: GET/POST http://localhost:${PORT}/authority/run`);
    console.log(`⚡ Execution endpoint: POST http://localhost:${PORT}/execution/run`);
    console.log(`📈 Dashboard summary: GET http://localhost:${PORT}/dashboard/summary`);
  });
}
