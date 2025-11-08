import { EventEmitter } from 'events';
import Redis from 'ioredis';
import amqp, { Connection, Channel } from 'amqplib';
import { MCPMessage, MessageType, AgentType, MessagePriority } from '../protocols/mcp.protocol';
import { v4 as uuidv4 } from 'uuid';

export class MCPMessageBus extends EventEmitter {
  private redis: Redis;
  private rabbitmq: Connection | null = null;
  private channel: Channel | null = null;
  private readonly EXCHANGE_NAME = 'mcp_exchange';

  constructor(redisUrl: string, rabbitmqUrl: string) {
    super();
    this.redis = new Redis(redisUrl);
    this.initRabbitMQ(rabbitmqUrl);
  }

  private async initRabbitMQ(url: string) {
    try {
      this.rabbitmq = await amqp.connect(url);
      this.channel = await this.rabbitmq.createChannel();

      // Create topic exchange for routing
      await this.channel.assertExchange(this.EXCHANGE_NAME, 'topic', { durable: true });

      // Create priority queue for each agent
      for (const agentType of Object.values(AgentType)) {
        await this.channel.assertQueue(agentType, {
          durable: true,
          maxPriority: 3
        });
      }

      console.log('✅ MCP Message Bus initialized');
    } catch (error) {
      console.error('❌ Failed to initialize RabbitMQ:', error);
      throw error;
    }
  }

  /**
   * Publish message to specific agent(s)
   */
  async publish(message: Omit<MCPMessage, 'id' | 'timestamp'>): Promise<string> {
    if (!this.channel) {
      throw new Error('Message bus not initialized');
    }

    const fullMessage: MCPMessage = {
      ...message,
      id: uuidv4(),
      timestamp: new Date()
    };

    // Store in Redis for context tracking
    await this.storeMessageContext(fullMessage);

    // Route based on message type
    if (message.type === MessageType.BROADCAST) {
      await this.broadcast(fullMessage);
    } else if (Array.isArray(message.target)) {
      for (const target of message.target) {
        await this.sendToAgent(target, fullMessage);
      }
    } else if (message.target) {
      await this.sendToAgent(message.target, fullMessage);
    }

    this.emit('message:published', fullMessage);
    return fullMessage.id;
  }

  private async sendToAgent(agentType: AgentType, message: MCPMessage) {
    if (!this.channel) return;

    const routingKey = agentType;
    await this.channel.publish(
      this.EXCHANGE_NAME,
      routingKey,
      Buffer.from(JSON.stringify(message)),
      {
        persistent: true,
        priority: message.priority,
        expiration: message.ttl ? message.ttl * 1000 : undefined
      }
    );
  }

  private async broadcast(message: MCPMessage) {
    if (!this.channel) return;

    await this.channel.publish(
      this.EXCHANGE_NAME,
      'broadcast.*',
      Buffer.from(JSON.stringify(message)),
      { persistent: true }
    );
  }

  /**
   * Subscribe to messages for a specific agent
   */
  async subscribe(agentType: AgentType, handler: (message: MCPMessage) => Promise<void>) {
    if (!this.channel) {
      throw new Error('Message bus not initialized');
    }

    const queue = agentType;

    // Bind queue to exchange with routing pattern
    await this.channel.bindQueue(queue, this.EXCHANGE_NAME, agentType);
    await this.channel.bindQueue(queue, this.EXCHANGE_NAME, 'broadcast.*');

    await this.channel.consume(queue, async (msg) => {
      if (msg) {
        try {
          const message: MCPMessage = JSON.parse(msg.content.toString());

          // Load context from Redis
          message.context = await this.loadMessageContext(message.id);

          await handler(message);
          this.channel!.ack(msg);
        } catch (error) {
          console.error(`Error processing message for ${agentType}:`, error);
          // Reject and requeue with limit
          this.channel!.nack(msg, false, msg.fields.deliveryTag < 3);
        }
      }
    });
  }

  /**
   * Request-Reply pattern for synchronous agent communication
   */
  async request(
    target: AgentType,
    payload: any,
    context?: any,
    timeout: number = 30000
  ): Promise<any> {
    if (!this.channel) {
      throw new Error('Message bus not initialized');
    }

    const correlationId = uuidv4();
    const replyQueue = await this.channel.assertQueue('', { exclusive: true });

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`Request timeout for ${target}`));
      }, timeout);

      this.channel!.consume(
        replyQueue.queue,
        (msg) => {
          if (msg && msg.properties.correlationId === correlationId) {
            clearTimeout(timer);
            resolve(JSON.parse(msg.content.toString()));
            this.channel!.ack(msg);
          }
        },
        { noAck: false }
      );

      this.publish({
        type: MessageType.REQUEST,
        source: AgentType.HIA, // Default source
        target,
        payload,
        context,
        priority: MessagePriority.NORMAL
      });
    });
  }

  private async storeMessageContext(message: MCPMessage): Promise<void> {
    const key = `mcp:message:${message.id}`;
    await this.redis.setex(
      key,
      3600, // 1 hour TTL
      JSON.stringify({
        id: message.id,
        type: message.type,
        source: message.source,
        target: message.target,
        context: message.context,
        timestamp: message.timestamp
      })
    );

    // Add to context chain if part of conversation
    if (message.context?.farmerId) {
      const chainKey = `mcp:chain:${message.context.farmerId}`;
      await this.redis.lpush(chainKey, message.id);
      await this.redis.ltrim(chainKey, 0, 99); // Keep last 100 messages
      await this.redis.expire(chainKey, 86400); // 24 hours
    }
  }

  private async loadMessageContext(messageId: string): Promise<any> {
    const key = `mcp:message:${messageId}`;
    const data = await this.redis.get(key);
    return data ? JSON.parse(data).context : null;
  }

  async close() {
    if (this.channel) await this.channel.close();
    if (this.rabbitmq) await this.rabbitmq.close();
    this.redis.disconnect();
  }
}
