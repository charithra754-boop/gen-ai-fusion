import express from 'express';
import dotenv from 'dotenv';
import { MCPMessageBus } from './bus/message-bus';
import { ContextManager } from './context/context-manager';

dotenv.config();

const app = express();
const PORT = process.env.MCP_PORT || 3001;

// Initialize MCP infrastructure
const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';
const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://admin:admin@localhost:5672';

let messageBus: MCPMessageBus;
let contextManager: ContextManager;

async function initialize() {
  console.log('🚀 Initializing KisaanMitra MCP Bus...');

  try {
    // Initialize infrastructure
    messageBus = new MCPMessageBus(REDIS_URL, RABBITMQ_URL);
    contextManager = new ContextManager(REDIS_URL);

    // Health check endpoint
    app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        service: 'mcp-bus',
        timestamp: new Date().toISOString()
      });
    });

    // Metrics endpoint (for monitoring)
    app.get('/metrics', async (req, res) => {
      const activeFarmers = await contextManager.getActiveFarmers();
      res.json({
        activeFarmers: activeFarmers.length,
        timestamp: new Date().toISOString()
      });
    });

    app.listen(PORT, () => {
      console.log(`✅ MCP Bus server running on port ${PORT}`);
      console.log(`📡 Redis: ${REDIS_URL}`);
      console.log(`🐰 RabbitMQ: ${RABBITMQ_URL}`);
    });

  } catch (error) {
    console.error('❌ Failed to initialize MCP Bus:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Shutting down MCP Bus...');
  if (messageBus) await messageBus.close();
  if (contextManager) await contextManager.close();
  process.exit(0);
});

initialize();

export { messageBus, contextManager };
