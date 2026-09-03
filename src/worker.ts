import dotenv from 'dotenv';
import path from 'node:path';
import { initDatabase } from './db/database.js';
import { WebhookQueueEngine } from './webhooks/queue.js';
import { AutonomousRecoveryDaemon } from './agents/daemon.js';

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

// Initialize database connection
initDatabase();

console.log('🚀 ULTRON Background Worker Process Started');

// Start Webhook Queue Retry Worker
WebhookQueueEngine.getInstance().startWorker(10000);
console.log('📦 Webhook Queue Retry Engine started.');

// Auto-start autonomous daemon if enabled
if (process.env.AUTONOMOUS_AGENT_ENABLED === 'true') {
  console.log(`🤖 Starting Autonomous Recovery Agent Daemon (24/7 Background Sweep)`);
  AutonomousRecoveryDaemon.getInstance().start();
} else {
  console.log(`⏸️ Autonomous Recovery Agent Daemon is disabled (AUTONOMOUS_AGENT_ENABLED != 'true')`);
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('Gracefully shutting down worker process...');
    WebhookQueueEngine.getInstance().stopWorker();
    if (process.env.AUTONOMOUS_AGENT_ENABLED === 'true') {
        AutonomousRecoveryDaemon.getInstance().stop();
    }
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('Gracefully shutting down worker process...');
    WebhookQueueEngine.getInstance().stopWorker();
    if (process.env.AUTONOMOUS_AGENT_ENABLED === 'true') {
        AutonomousRecoveryDaemon.getInstance().stop();
    }
    process.exit(0);
});
