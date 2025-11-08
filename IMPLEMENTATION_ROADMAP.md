# KisaanMitra: Complete Implementation Roadmap
## From MVP to Full Multi-Agent System Vision

**Version:** 1.0
**Date:** 2025-11-08
**Target Completion:** 18-24 months
**Current Status:** MVP Phase (4.5% complete)

---

## Table of Contents

1. [Overview & Strategy](#overview--strategy)
2. [Phase 0: Foundation & Architecture](#phase-0-foundation--architecture-weeks-1-4)
3. [Phase 1: Core Agent Infrastructure](#phase-1-core-agent-infrastructure-weeks-5-12)
4. [Phase 2: Collective Market Governance (CMGA)](#phase-2-collective-market-governance-cmga-weeks-13-20)
5. [Phase 3: Market Intelligence (MIA)](#phase-3-market-intelligence-mia-weeks-21-26)
6. [Phase 4: Geo-Agronomy Agent (GAA)](#phase-4-geo-agronomy-agent-gaa-weeks-27-38)
7. [Phase 5: Climate & Resource Agent (CRA)](#phase-5-climate--resource-agent-cra-weeks-39-50)
8. [Phase 6: Financial Inclusion Agent (FIA)](#phase-6-financial-inclusion-agent-fia-weeks-51-62)
9. [Phase 7: Logistics Infrastructure Agent (LIA)](#phase-7-logistics-infrastructure-agent-lia-weeks-63-72)
10. [Phase 8: Enhanced Human Interface (HIA)](#phase-8-enhanced-human-interface-hia-weeks-73-80)
11. [Phase 9: Integration & Testing](#phase-9-integration--testing-weeks-81-92)
12. [Phase 10: Pilot & Production](#phase-10-pilot--production-weeks-93-104)
13. [Technical Specifications](#technical-specifications)
14. [File Structure & New Components](#file-structure--new-components)
15. [Deployment Architecture](#deployment-architecture)
16. [Testing Strategy](#testing-strategy)
17. [Success Metrics](#success-metrics)

---

## Overview & Strategy

### Implementation Philosophy

**Build in Vertical Slices:** Each phase delivers a working, integrated feature rather than horizontal layers.

**Prioritization Criteria:**
1. **Business Impact:** CMGA first (unique differentiator)
2. **Technical Dependencies:** MCP before individual agents
3. **Quick Wins:** MIA (mandi prices) for early user value
4. **Complexity:** Save IoT/hardware for later phases

### Architecture Transition

```
Current: Monolithic React App
         ↓
Target:  Microservices-based Multi-Agent System

┌─────────────────────────────────────────────┐
│           Frontend (React + TS)              │
│  - HIA Interface                            │
│  - FPO Dashboard                            │
│  - Individual Farmer Dashboard              │
└────────────────┬────────────────────────────┘
                 │ REST/GraphQL
┌────────────────┴────────────────────────────┐
│         API Gateway (Kong/Traefik)          │
└────────────────┬────────────────────────────┘
                 │
      ┌──────────┴──────────┐
      │   MCP Message Bus   │
      │   (Redis/RabbitMQ)  │
      └──────────┬──────────┘
                 │
    ┌────────────┴─────────────┐
    │  Agent Services (Docker) │
    ├──────────────────────────┤
    │ CMGA │ CRA │ GAA │ FIA  │
    │ MIA  │ LIA │ HIA         │
    └──────────────────────────┘
                 │
    ┌────────────┴─────────────┐
    │ Data Layer               │
    ├──────────────────────────┤
    │ PostgreSQL (Supabase)    │
    │ TimescaleDB (IoT data)   │
    │ Redis (cache)            │
    │ S3 (images/models)       │
    └──────────────────────────┘
```

---

## Phase 0: Foundation & Architecture (Weeks 1-4)

### Goals
- Set up microservices infrastructure
- Implement MCP (Model Context Protocol)
- Migrate from monolithic to distributed architecture
- Establish CI/CD pipelines

### Deliverables

#### 1. Docker & Kubernetes Setup

**New Files:**
```
/infrastructure/
├── docker/
│   ├── Dockerfile.agent-base
│   ├── Dockerfile.python-ml
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── kubernetes/
│   ├── namespace.yaml
│   ├── deployments/
│   │   ├── agent-deployment.yaml
│   │   ├── mcp-bus-deployment.yaml
│   │   └── api-gateway-deployment.yaml
│   ├── services/
│   │   └── ...
│   └── ingress/
│       └── ingress.yaml
└── terraform/
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

**docker-compose.yml** (for local development):
```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: kisaanmitra
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data

  timescaledb:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_DB: iot_data
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5433:5432"
    volumes:
      - timescale-data:/var/lib/postgresql/data

  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq

  mcp-bus:
    build:
      context: ./backend/mcp-bus
      dockerfile: Dockerfile
    depends_on:
      - redis
      - rabbitmq
    environment:
      REDIS_URL: redis://redis:6379
      RABBITMQ_URL: amqp://admin:admin@rabbitmq:5672
    ports:
      - "3001:3001"

  frontend:
    build:
      context: .
      dockerfile: infrastructure/docker/Dockerfile.frontend
    ports:
      - "8080:8080"
    volumes:
      - ./src:/app/src
    environment:
      VITE_API_GATEWAY_URL: http://localhost:3000

volumes:
  redis-data:
  postgres-data:
  timescale-data:
  rabbitmq-data:
```

#### 2. MCP (Model Context Protocol) Implementation

**New Directory:**
```
/backend/mcp-bus/
├── src/
│   ├── index.ts
│   ├── protocols/
│   │   ├── mcp.protocol.ts
│   │   ├── message.types.ts
│   │   └── context.types.ts
│   ├── bus/
│   │   ├── message-bus.ts
│   │   ├── pub-sub.ts
│   │   └── request-reply.ts
│   ├── context/
│   │   ├── context-manager.ts
│   │   ├── context-store.ts
│   │   └── context-resolver.ts
│   ├── agents/
│   │   ├── agent-registry.ts
│   │   └── agent-discovery.ts
│   └── middleware/
│       ├── logger.ts
│       ├── validator.ts
│       └── rate-limiter.ts
├── package.json
├── tsconfig.json
└── Dockerfile
```

**mcp.protocol.ts:**
```typescript
/**
 * Model Context Protocol (MCP) Implementation
 * Enables efficient, context-aware communication between agents
 */

export enum MessageType {
  REQUEST = 'request',
  RESPONSE = 'response',
  EVENT = 'event',
  CONTEXT_UPDATE = 'context_update',
  BROADCAST = 'broadcast'
}

export enum AgentType {
  CMGA = 'collective-market-governance',
  CRA = 'climate-resource',
  GAA = 'geo-agronomy',
  FIA = 'financial-inclusion',
  MIA = 'market-intelligence',
  LIA = 'logistics-infrastructure',
  HIA = 'human-interface'
}

export interface MCPMessage {
  id: string;
  type: MessageType;
  source: AgentType;
  target?: AgentType | AgentType[];
  timestamp: Date;
  payload: any;
  context?: MessageContext;
  priority: MessagePriority;
  ttl?: number; // Time-to-live in seconds
}

export interface MessageContext {
  farmerId?: string;
  fpoId?: string;
  location?: GeoLocation;
  cropType?: string;
  season?: string;
  previousMessages?: string[]; // IDs of related messages
  metadata?: Record<string, any>;
}

export interface GeoLocation {
  latitude: number;
  longitude: number;
  accuracy?: number;
  village?: string;
  district?: string;
  state?: string;
}

export enum MessagePriority {
  LOW = 0,
  NORMAL = 1,
  HIGH = 2,
  CRITICAL = 3
}

export interface AgentCapability {
  agentType: AgentType;
  version: string;
  capabilities: string[];
  inputSchemas: Record<string, any>;
  outputSchemas: Record<string, any>;
  dependencies: AgentType[];
}

export interface ContextState {
  farmContext?: FarmContext;
  marketContext?: MarketContext;
  weatherContext?: WeatherContext;
  fpoContext?: FPOContext;
}

export interface FarmContext {
  farmerId: string;
  fieldBoundaries?: any;
  soilData?: any;
  cropHistory?: any;
  currentCrops?: any;
}

export interface MarketContext {
  currentPrices?: any;
  demandForecast?: any;
  inventoryLevel?: number;
}

export interface WeatherContext {
  current?: any;
  forecast?: any;
  historicalAnomaly?: boolean;
}

export interface FPOContext {
  fpoId: string;
  members?: string[];
  collectivePortfolio?: any;
  investmentUnits?: Map<string, number>;
}
```

**message-bus.ts:**
```typescript
import { EventEmitter } from 'events';
import Redis from 'ioredis';
import amqp from 'amqplib';
import { MCPMessage, MessageType, AgentType, MessagePriority } from '../protocols/mcp.protocol';
import { v4 as uuidv4 } from 'uuid';

export class MCPMessageBus extends EventEmitter {
  private redis: Redis;
  private rabbitmq: amqp.Connection;
  private channel: amqp.Channel;
  private readonly EXCHANGE_NAME = 'mcp_exchange';

  constructor(redisUrl: string, rabbitmqUrl: string) {
    super();
    this.redis = new Redis(redisUrl);
    this.initRabbitMQ(rabbitmqUrl);
  }

  private async initRabbitMQ(url: string) {
    this.rabbitmq = await amqp.connect(url);
    this.channel = await this.rabbitmq.createChannel();

    // Create fanout exchange for broadcasts
    await this.channel.assertExchange(this.EXCHANGE_NAME, 'topic', { durable: true });

    // Create priority queue for each agent
    for (const agentType of Object.values(AgentType)) {
      await this.channel.assertQueue(agentType, {
        durable: true,
        maxPriority: 3
      });
    }
  }

  /**
   * Publish message to specific agent(s)
   */
  async publish(message: Omit<MCPMessage, 'id' | 'timestamp'>): Promise<string> {
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
          this.channel.ack(msg);
        } catch (error) {
          console.error(`Error processing message for ${agentType}:`, error);
          // Reject and requeue with limit
          this.channel.nack(msg, false, msg.fields.deliveryTag < 3);
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
    const correlationId = uuidv4();
    const replyQueue = await this.channel.assertQueue('', { exclusive: true });

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`Request timeout for ${target}`));
      }, timeout);

      this.channel.consume(
        replyQueue.queue,
        (msg) => {
          if (msg && msg.properties.correlationId === correlationId) {
            clearTimeout(timer);
            resolve(JSON.parse(msg.content.toString()));
            this.channel.ack(msg);
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
    await this.channel.close();
    await this.rabbitmq.close();
    this.redis.disconnect();
  }
}
```

**context-manager.ts:**
```typescript
import Redis from 'ioredis';
import { ContextState, FarmContext, MarketContext } from '../protocols/mcp.protocol';

export class ContextManager {
  private redis: Redis;
  private readonly TTL = 3600; // 1 hour

  constructor(redisUrl: string) {
    this.redis = new Redis(redisUrl);
  }

  /**
   * Get complete context for a farmer
   */
  async getFarmerContext(farmerId: string): Promise<ContextState> {
    const key = `context:farmer:${farmerId}`;
    const data = await this.redis.get(key);
    return data ? JSON.parse(data) : {};
  }

  /**
   * Update specific context slice
   */
  async updateContext(
    farmerId: string,
    contextType: keyof ContextState,
    data: any
  ): Promise<void> {
    const key = `context:farmer:${farmerId}`;
    const existing = await this.getFarmerContext(farmerId);

    existing[contextType] = {
      ...existing[contextType],
      ...data,
      updatedAt: new Date()
    };

    await this.redis.setex(key, this.TTL, JSON.stringify(existing));
  }

  /**
   * Get FPO-level context
   */
  async getFPOContext(fpoId: string): Promise<any> {
    const key = `context:fpo:${fpoId}`;
    const data = await this.redis.get(key);
    return data ? JSON.parse(data) : {};
  }

  /**
   * Update FPO context
   */
  async updateFPOContext(fpoId: string, data: any): Promise<void> {
    const key = `context:fpo:${fpoId}`;
    const existing = await this.getFPOContext(fpoId);

    const updated = {
      ...existing,
      ...data,
      updatedAt: new Date()
    };

    await this.redis.setex(key, this.TTL * 24, JSON.stringify(updated)); // 24 hour TTL for FPO
  }

  /**
   * Resolve context from message chain
   */
  async resolveMessageContext(messageIds: string[]): Promise<ContextState> {
    const contexts = await Promise.all(
      messageIds.map(id => this.redis.get(`mcp:message:${id}`))
    );

    // Merge contexts in chronological order
    return contexts.reduce((merged, ctx) => {
      if (ctx) {
        const parsed = JSON.parse(ctx);
        return { ...merged, ...parsed.context };
      }
      return merged;
    }, {});
  }
}
```

#### 3. Agent Base Class

**New File: `/backend/agents/base/agent.base.ts`**
```typescript
import { MCPMessageBus } from '../../mcp-bus/src/bus/message-bus';
import { ContextManager } from '../../mcp-bus/src/context/context-manager';
import {
  MCPMessage,
  AgentType,
  MessageType,
  MessagePriority,
  AgentCapability
} from '../../mcp-bus/src/protocols/mcp.protocol';

export abstract class BaseAgent {
  protected agentType: AgentType;
  protected messageBus: MCPMessageBus;
  protected contextManager: ContextManager;
  protected capabilities: AgentCapability;

  constructor(
    agentType: AgentType,
    messageBus: MCPMessageBus,
    contextManager: ContextManager
  ) {
    this.agentType = agentType;
    this.messageBus = messageBus;
    this.contextManager = contextManager;
    this.capabilities = this.defineCapabilities();
  }

  /**
   * Each agent must define its capabilities
   */
  protected abstract defineCapabilities(): AgentCapability;

  /**
   * Main message handler - to be implemented by each agent
   */
  protected abstract handleMessage(message: MCPMessage): Promise<any>;

  /**
   * Start the agent
   */
  async start() {
    console.log(`🚀 Starting ${this.agentType} agent...`);

    // Subscribe to messages
    await this.messageBus.subscribe(this.agentType, async (message) => {
      try {
        console.log(`📨 ${this.agentType} received message:`, message.type);
        const result = await this.handleMessage(message);

        // Send response if it was a request
        if (message.type === MessageType.REQUEST) {
          await this.sendResponse(message, result);
        }
      } catch (error) {
        console.error(`❌ ${this.agentType} error:`, error);
        if (message.type === MessageType.REQUEST) {
          await this.sendError(message, error);
        }
      }
    });

    console.log(`✅ ${this.agentType} agent ready`);
  }

  /**
   * Send message to another agent
   */
  protected async sendMessage(
    target: AgentType | AgentType[],
    type: MessageType,
    payload: any,
    context?: any,
    priority: MessagePriority = MessagePriority.NORMAL
  ): Promise<string> {
    return this.messageBus.publish({
      type,
      source: this.agentType,
      target,
      payload,
      context,
      priority
    });
  }

  /**
   * Request-Reply to another agent
   */
  protected async requestFromAgent(
    target: AgentType,
    payload: any,
    context?: any
  ): Promise<any> {
    return this.messageBus.request(target, payload, context);
  }

  /**
   * Broadcast event to all agents
   */
  protected async broadcast(payload: any, context?: any): Promise<string> {
    return this.messageBus.publish({
      type: MessageType.BROADCAST,
      source: this.agentType,
      payload,
      context,
      priority: MessagePriority.NORMAL
    });
  }

  /**
   * Send response to a request
   */
  private async sendResponse(originalMessage: MCPMessage, result: any) {
    await this.sendMessage(
      originalMessage.source,
      MessageType.RESPONSE,
      {
        success: true,
        data: result,
        requestId: originalMessage.id
      },
      originalMessage.context,
      MessagePriority.HIGH
    );
  }

  /**
   * Send error response
   */
  private async sendError(originalMessage: MCPMessage, error: any) {
    await this.sendMessage(
      originalMessage.source,
      MessageType.RESPONSE,
      {
        success: false,
        error: error.message,
        requestId: originalMessage.id
      },
      originalMessage.context,
      MessagePriority.HIGH
    );
  }

  /**
   * Get context for current operation
   */
  protected async getContext(farmerId?: string, fpoId?: string): Promise<any> {
    if (farmerId) {
      return this.contextManager.getFarmerContext(farmerId);
    }
    if (fpoId) {
      return this.contextManager.getFPOContext(fpoId);
    }
    return {};
  }

  /**
   * Update context
   */
  protected async updateContext(
    farmerId: string,
    contextType: string,
    data: any
  ): Promise<void> {
    await this.contextManager.updateContext(farmerId, contextType as any, data);
  }
}
```

### Week-by-Week Tasks

**Week 1:**
- Set up Docker and docker-compose
- Configure PostgreSQL with PostGIS extension
- Set up Redis and RabbitMQ
- Create basic project structure

**Week 2:**
- Implement MCP protocol types and interfaces
- Build MessageBus class
- Create ContextManager
- Set up agent registry

**Week 3:**
- Implement BaseAgent class
- Create agent discovery mechanism
- Build API Gateway (Kong or custom Express)
- Set up logging and monitoring (Prometheus + Grafana)

**Week 4:**
- Write integration tests for MCP
- Document MCP protocol
- Set up CI/CD pipelines (GitHub Actions)
- Prepare for Phase 1

---

## Phase 1: Core Agent Infrastructure (Weeks 5-12)

### Goals
- Create skeleton for all 7 agents
- Establish database schemas
- Build API endpoints
- Test agent-to-agent communication

### Database Schema Extensions

**New SQL File: `/backend/schema/phase1_agents.sql`**
```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- AGENT REGISTRY
-- ============================================
CREATE TABLE agents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_type VARCHAR(50) UNIQUE NOT NULL,
  version VARCHAR(20) NOT NULL,
  status VARCHAR(20) DEFAULT 'active',
  capabilities JSONB,
  health_check_url VARCHAR(255),
  last_heartbeat TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agents_type ON agents(agent_type);
CREATE INDEX idx_agents_status ON agents(status);

-- ============================================
-- FPO (Farmer Producer Organizations)
-- ============================================
CREATE TABLE fpos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  registration_number VARCHAR(100) UNIQUE,
  village VARCHAR(100),
  district VARCHAR(100),
  state VARCHAR(100),
  location GEOGRAPHY(POINT, 4326),
  total_members INTEGER DEFAULT 0,
  total_land_area DECIMAL(10, 2), -- in hectares
  formation_date DATE,
  status VARCHAR(20) DEFAULT 'active',
  contact_person VARCHAR(255),
  contact_phone VARCHAR(20),
  contact_email VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_fpos_location ON fpos USING GIST(location);
CREATE INDEX idx_fpos_district ON fpos(district);
CREATE INDEX idx_fpos_status ON fpos(status);

-- ============================================
-- FPO MEMBERSHIP
-- ============================================
CREATE TABLE fpo_members (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  fpo_id UUID REFERENCES fpos(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  join_date DATE NOT NULL,
  land_area DECIMAL(10, 2), -- in hectares
  role VARCHAR(50) DEFAULT 'member', -- member, secretary, president
  investment_units DECIMAL(15, 2) DEFAULT 0,
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(fpo_id, user_id)
);

CREATE INDEX idx_fpo_members_fpo ON fpo_members(fpo_id);
CREATE INDEX idx_fpo_members_user ON fpo_members(user_id);

-- ============================================
-- INVESTMENT UNITS LEDGER
-- ============================================
CREATE TABLE investment_units (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  fpo_id UUID REFERENCES fpos(id) ON DELETE CASCADE,
  member_id UUID REFERENCES fpo_members(id) ON DELETE CASCADE,
  units DECIMAL(15, 2) NOT NULL,
  calculation_basis JSONB, -- land_area, inputs, labor, etc.
  season VARCHAR(50),
  crop_cycle VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  verified_at TIMESTAMPTZ,
  verified_by UUID REFERENCES users(id)
);

CREATE INDEX idx_investment_units_fpo ON investment_units(fpo_id);
CREATE INDEX idx_investment_units_member ON investment_units(member_id);
CREATE INDEX idx_investment_units_season ON investment_units(season);

-- ============================================
-- COLLECTIVE PORTFOLIOS
-- ============================================
CREATE TABLE collective_portfolios (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  fpo_id UUID REFERENCES fpos(id) ON DELETE CASCADE,
  season VARCHAR(50) NOT NULL,
  year INTEGER NOT NULL,
  planned_crops JSONB, -- [{crop, area, members[]}]
  risk_score DECIMAL(5, 2),
  expected_revenue DECIMAL(15, 2),
  status VARCHAR(20) DEFAULT 'planning', -- planning, approved, active, completed
  created_by UUID REFERENCES users(id),
  approved_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_portfolios_fpo ON collective_portfolios(fpo_id);
CREATE INDEX idx_portfolios_season ON collective_portfolios(season, year);

-- ============================================
-- PROFIT DISTRIBUTIONS
-- ============================================
CREATE TABLE profit_distributions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  fpo_id UUID REFERENCES fpos(id) ON DELETE CASCADE,
  portfolio_id UUID REFERENCES collective_portfolios(id),
  member_id UUID REFERENCES fpo_members(id) ON DELETE CASCADE,
  investment_units DECIMAL(15, 2),
  share_percentage DECIMAL(5, 2),
  gross_profit DECIMAL(15, 2),
  deductions DECIMAL(15, 2) DEFAULT 0,
  net_profit DECIMAL(15, 2),
  payment_status VARCHAR(20) DEFAULT 'pending',
  payment_date DATE,
  payment_reference VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_profit_dist_fpo ON profit_distributions(fpo_id);
CREATE INDEX idx_profit_dist_member ON profit_distributions(member_id);
CREATE INDEX idx_profit_dist_status ON profit_distributions(payment_status);

-- ============================================
-- MANDI PRICES
-- ============================================
CREATE TABLE mandi_prices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  mandi_name VARCHAR(255) NOT NULL,
  state VARCHAR(100),
  district VARCHAR(100),
  commodity VARCHAR(255) NOT NULL,
  variety VARCHAR(255),
  grade VARCHAR(50),
  min_price DECIMAL(10, 2),
  max_price DECIMAL(10, 2),
  modal_price DECIMAL(10, 2),
  arrival_quantity DECIMAL(10, 2), -- in quintals
  unit VARCHAR(20) DEFAULT 'quintal',
  price_date DATE NOT NULL,
  source VARCHAR(100), -- agmarknet, state portal
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_mandi_prices_commodity ON mandi_prices(commodity);
CREATE INDEX idx_mandi_prices_date ON mandi_prices(price_date DESC);
CREATE INDEX idx_mandi_prices_location ON mandi_prices(state, district);

-- ============================================
-- DEMAND FORECASTS
-- ============================================
CREATE TABLE demand_forecasts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  commodity VARCHAR(255) NOT NULL,
  region VARCHAR(255),
  forecast_date DATE NOT NULL,
  predicted_demand DECIMAL(15, 2),
  confidence_score DECIMAL(5, 2),
  model_version VARCHAR(50),
  features_used JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_demand_forecasts_commodity ON demand_forecasts(commodity);
CREATE INDEX idx_demand_forecasts_date ON demand_forecasts(forecast_date);

-- ============================================
-- IOT SENSORS
-- ============================================
CREATE TABLE iot_sensors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  sensor_id VARCHAR(100) UNIQUE NOT NULL,
  sensor_type VARCHAR(50), -- soil_moisture, weather_station, water_flow
  location GEOGRAPHY(POINT, 4326),
  farm_id UUID, -- If linked to specific farm
  fpo_id UUID REFERENCES fpos(id),
  installation_date DATE,
  status VARCHAR(20) DEFAULT 'active',
  calibration_date DATE,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_iot_sensors_type ON iot_sensors(sensor_type);
CREATE INDEX idx_iot_sensors_location ON iot_sensors USING GIST(location);

-- Note: Sensor readings will go to TimescaleDB (time-series database)

-- ============================================
-- IRRIGATION SCHEDULES
-- ============================================
CREATE TABLE irrigation_schedules (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farm_id UUID, -- Link to farm/field
  farmer_id UUID REFERENCES users(id),
  fpo_id UUID REFERENCES fpos(id),
  crop_type VARCHAR(100),
  scheduled_time TIMESTAMPTZ NOT NULL,
  duration_minutes INTEGER,
  water_volume DECIMAL(10, 2), -- in liters
  status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, executed, skipped, failed
  execution_time TIMESTAMPTZ,
  actual_volume DECIMAL(10, 2),
  created_by VARCHAR(50) DEFAULT 'CRA', -- Agent that created it
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_irrigation_schedules_time ON irrigation_schedules(scheduled_time);
CREATE INDEX idx_irrigation_schedules_farmer ON irrigation_schedules(farmer_id);
CREATE INDEX idx_irrigation_schedules_status ON irrigation_schedules(status);

-- ============================================
-- SATELLITE IMAGERY METADATA
-- ============================================
CREATE TABLE satellite_imagery (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  image_id VARCHAR(255) UNIQUE NOT NULL,
  satellite_source VARCHAR(50), -- sentinel-2, landsat-8
  acquisition_date DATE NOT NULL,
  cloud_coverage DECIMAL(5, 2),
  bounds GEOGRAPHY(POLYGON, 4326),
  resolution_meters DECIMAL(5, 2),
  bands JSONB, -- Available spectral bands
  s3_bucket VARCHAR(255),
  s3_key VARCHAR(500),
  processing_status VARCHAR(20) DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_satellite_imagery_date ON satellite_imagery(acquisition_date DESC);
CREATE INDEX idx_satellite_imagery_bounds ON satellite_imagery USING GIST(bounds);

-- ============================================
-- NDVI ANALYSIS
-- ============================================
CREATE TABLE ndvi_analysis (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farm_id UUID,
  farmer_id UUID REFERENCES users(id),
  image_id UUID REFERENCES satellite_imagery(id),
  analysis_date DATE NOT NULL,
  mean_ndvi DECIMAL(5, 4),
  min_ndvi DECIMAL(5, 4),
  max_ndvi DECIMAL(5, 4),
  vegetation_health VARCHAR(20), -- excellent, good, fair, poor, critical
  stress_detected BOOLEAN DEFAULT false,
  stress_areas JSONB, -- GeoJSON of stressed areas
  recommendations TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ndvi_analysis_farmer ON ndvi_analysis(farmer_id);
CREATE INDEX idx_ndvi_analysis_date ON ndvi_analysis(analysis_date DESC);

-- ============================================
-- YIELD FORECASTS
-- ============================================
CREATE TABLE yield_forecasts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farm_id UUID,
  farmer_id UUID REFERENCES users(id),
  fpo_id UUID REFERENCES fpos(id),
  crop_type VARCHAR(100) NOT NULL,
  season VARCHAR(50),
  forecast_date DATE NOT NULL,
  harvest_date DATE,
  predicted_yield DECIMAL(10, 2), -- in quintals
  confidence_score DECIMAL(5, 2),
  model_version VARCHAR(50),
  input_features JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_yield_forecasts_farmer ON yield_forecasts(farmer_id);
CREATE INDEX idx_yield_forecasts_crop ON yield_forecasts(crop_type);
CREATE INDEX idx_yield_forecasts_date ON yield_forecasts(forecast_date DESC);

-- ============================================
-- DISEASE & PEST DETECTIONS
-- ============================================
CREATE TABLE disease_detections (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farm_id UUID,
  farmer_id UUID REFERENCES users(id),
  detection_date TIMESTAMPTZ NOT NULL,
  crop_type VARCHAR(100),
  disease_type VARCHAR(255),
  pest_type VARCHAR(255),
  severity VARCHAR(20), -- low, medium, high, critical
  confidence_score DECIMAL(5, 2),
  image_url VARCHAR(500),
  location GEOGRAPHY(POINT, 4326),
  recommendations TEXT,
  status VARCHAR(20) DEFAULT 'active', -- active, treated, resolved
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_disease_detections_farmer ON disease_detections(farmer_id);
CREATE INDEX idx_disease_detections_date ON disease_detections(detection_date DESC);
CREATE INDEX idx_disease_detections_status ON disease_detections(status);

-- ============================================
-- CREDIT SCORES
-- ============================================
CREATE TABLE credit_scores (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farmer_id UUID REFERENCES users(id) ON DELETE CASCADE,
  score DECIMAL(5, 2) NOT NULL CHECK (score >= 0 AND score <= 1000),
  rating VARCHAR(10), -- AAA, AA, A, BBB, BB, B, C
  calculation_date DATE NOT NULL,
  factors JSONB, -- {yield_history: 0.3, soil_quality: 0.2, ...}
  model_version VARCHAR(50),
  expires_at DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_credit_scores_farmer ON credit_scores(farmer_id);
CREATE INDEX idx_credit_scores_date ON credit_scores(calculation_date DESC);

-- ============================================
-- LOAN APPLICATIONS
-- ============================================
CREATE TABLE loan_applications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farmer_id UUID REFERENCES users(id) ON DELETE CASCADE,
  credit_score_id UUID REFERENCES credit_scores(id),
  amount DECIMAL(15, 2) NOT NULL,
  purpose TEXT,
  tenure_months INTEGER,
  interest_rate DECIMAL(5, 2),
  status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, disbursed
  application_date DATE NOT NULL,
  decision_date DATE,
  disbursement_date DATE,
  lender_name VARCHAR(255),
  lender_reference VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_loan_applications_farmer ON loan_applications(farmer_id);
CREATE INDEX idx_loan_applications_status ON loan_applications(status);

-- ============================================
-- INSURANCE POLICIES
-- ============================================
CREATE TABLE insurance_policies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farmer_id UUID REFERENCES users(id) ON DELETE CASCADE,
  policy_number VARCHAR(100) UNIQUE NOT NULL,
  insurance_type VARCHAR(50), -- crop, weather, livestock
  crop_type VARCHAR(100),
  insured_area DECIMAL(10, 2),
  sum_insured DECIMAL(15, 2),
  premium_amount DECIMAL(15, 2),
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  status VARCHAR(20) DEFAULT 'active',
  provider_name VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_insurance_policies_farmer ON insurance_policies(farmer_id);
CREATE INDEX idx_insurance_policies_status ON insurance_policies(status);

-- ============================================
-- INSURANCE CLAIMS
-- ============================================
CREATE TABLE insurance_claims (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  policy_id UUID REFERENCES insurance_policies(id) ON DELETE CASCADE,
  farmer_id UUID REFERENCES users(id),
  claim_number VARCHAR(100) UNIQUE NOT NULL,
  loss_type VARCHAR(100), -- drought, flood, pest, disease
  loss_date DATE NOT NULL,
  reported_date DATE NOT NULL,
  estimated_loss DECIMAL(15, 2),
  assessed_loss DECIMAL(15, 2),
  claim_amount DECIMAL(15, 2),
  status VARCHAR(20) DEFAULT 'submitted', -- submitted, under_review, approved, rejected, paid
  satellite_evidence UUID REFERENCES satellite_imagery(id),
  adjuster_notes TEXT,
  settlement_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_insurance_claims_policy ON insurance_claims(policy_id);
CREATE INDEX idx_insurance_claims_farmer ON insurance_claims(farmer_id);
CREATE INDEX idx_insurance_claims_status ON insurance_claims(status);

-- ============================================
-- COLD STORAGE FACILITIES
-- ============================================
CREATE TABLE cold_storage_facilities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  location GEOGRAPHY(POINT, 4326),
  address TEXT,
  district VARCHAR(100),
  state VARCHAR(100),
  total_capacity DECIMAL(10, 2), -- in metric tons
  available_capacity DECIMAL(10, 2),
  temperature_range VARCHAR(50), -- e.g., "0-4°C"
  commodities_supported JSONB, -- ["potato", "onion", "tomato"]
  power_source VARCHAR(50), -- grid, solar, hybrid
  rental_rate_per_quintal DECIMAL(10, 2),
  contact_person VARCHAR(255),
  contact_phone VARCHAR(20),
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_cold_storage_location ON cold_storage_facilities USING GIST(location);
CREATE INDEX idx_cold_storage_district ON cold_storage_facilities(district);

-- ============================================
-- LOGISTICS ROUTES
-- ============================================
CREATE TABLE logistics_routes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  route_name VARCHAR(255),
  origin_location GEOGRAPHY(POINT, 4326),
  destination_location GEOGRAPHY(POINT, 4326),
  distance_km DECIMAL(10, 2),
  estimated_duration_hours DECIMAL(5, 2),
  waypoints JSONB, -- Array of intermediate points
  road_quality VARCHAR(50),
  preferred_vehicle_type VARCHAR(50),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- POST HARVEST LOSSES
-- ============================================
CREATE TABLE post_harvest_losses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  fpo_id UUID REFERENCES fpos(id),
  farmer_id UUID REFERENCES users(id),
  commodity VARCHAR(255) NOT NULL,
  total_harvest DECIMAL(10, 2), -- in quintals
  loss_quantity DECIMAL(10, 2),
  loss_percentage DECIMAL(5, 2),
  loss_stage VARCHAR(50), -- harvesting, transport, storage
  loss_reason VARCHAR(100), -- temperature, moisture, pest, damage
  loss_date DATE,
  estimated_value_loss DECIMAL(15, 2),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_losses_commodity ON post_harvest_losses(commodity);
CREATE INDEX idx_losses_date ON post_harvest_losses(loss_date DESC);

-- ============================================
-- MESSAGE TEMPLATES (for SMS/IVR)
-- ============================================
CREATE TABLE message_templates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  template_key VARCHAR(100) UNIQUE NOT NULL,
  category VARCHAR(50), -- alert, advisory, notification
  channel VARCHAR(20), -- sms, ivr, whatsapp
  language VARCHAR(10),
  template_text TEXT NOT NULL,
  variables JSONB, -- Placeholder variables
  priority VARCHAR(20) DEFAULT 'normal',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_message_templates_key ON message_templates(template_key);
CREATE INDEX idx_message_templates_category ON message_templates(category);

-- ============================================
-- SENT MESSAGES LOG
-- ============================================
CREATE TABLE sent_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  recipient_id UUID REFERENCES users(id),
  channel VARCHAR(20), -- sms, ivr, whatsapp, push
  template_id UUID REFERENCES message_templates(id),
  message_content TEXT,
  phone_number VARCHAR(20),
  status VARCHAR(20) DEFAULT 'sent', -- sent, delivered, failed, read
  sent_at TIMESTAMPTZ DEFAULT NOW(),
  delivered_at TIMESTAMPTZ,
  cost DECIMAL(10, 4),
  provider_reference VARCHAR(255),
  error_message TEXT
);

CREATE INDEX idx_sent_messages_recipient ON sent_messages(recipient_id);
CREATE INDEX idx_sent_messages_status ON sent_messages(status);
CREATE INDEX idx_sent_messages_sent_at ON sent_messages(sent_at DESC);

-- ============================================
-- AGENT TASK QUEUE
-- ============================================
CREATE TABLE agent_tasks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_type VARCHAR(50) NOT NULL,
  task_type VARCHAR(100) NOT NULL,
  priority INTEGER DEFAULT 1,
  payload JSONB,
  status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
  scheduled_at TIMESTAMPTZ,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  error_message TEXT,
  retry_count INTEGER DEFAULT 0,
  max_retries INTEGER DEFAULT 3,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_tasks_agent ON agent_tasks(agent_type);
CREATE INDEX idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX idx_agent_tasks_scheduled ON agent_tasks(scheduled_at);
```

### Agent Skeletons

I'll create skeleton implementations for each agent to be built out in subsequent phases.

**Example: CMGA Skeleton**

**New File: `/backend/agents/cmga/cmga.agent.ts`**
```typescript
import { BaseAgent } from '../base/agent.base';
import {
  MCPMessage,
  AgentType,
  MessageType,
  AgentCapability
} from '../../mcp-bus/src/protocols/mcp.protocol';

export class CMGAAgent extends BaseAgent {
  constructor(messageBus: any, contextManager: any) {
    super(AgentType.CMGA, messageBus, contextManager);
  }

  protected defineCapabilities(): AgentCapability {
    return {
      agentType: AgentType.CMGA,
      version: '1.0.0',
      capabilities: [
        'collective-portfolio-planning',
        'investment-unit-calculation',
        'profit-distribution',
        'risk-assessment'
      ],
      inputSchemas: {
        planPortfolio: {
          fpoId: 'string',
          season: 'string',
          year: 'number'
        },
        calculateInvestmentUnits: {
          fpoId: 'string',
          memberId: 'string',
          landArea: 'number',
          inputs: 'object'
        },
        distributeProfits: {
          fpoId: 'string',
          portfolioId: 'string',
          totalRevenue: 'number'
        }
      },
      outputSchemas: {},
      dependencies: [AgentType.MIA, AgentType.GAA, AgentType.CRA]
    };
  }

  protected async handleMessage(message: MCPMessage): Promise<any> {
    const { type, payload } = message;

    switch (payload.action) {
      case 'planPortfolio':
        return this.planCollectivePortfolio(payload.data);

      case 'calculateInvestmentUnits':
        return this.calculateInvestmentUnits(payload.data);

      case 'distributeProfits':
        return this.distributeProfit(payload.data);

      default:
        throw new Error(`Unknown action: ${payload.action}`);
    }
  }

  private async planCollectivePortfolio(data: any): Promise<any> {
    // TODO: Implement in Phase 2
    console.log('📊 CMGA: Planning collective portfolio', data);

    // Request market intelligence from MIA
    const marketData = await this.requestFromAgent(
      AgentType.MIA,
      { action: 'getPriceForecast', crops: data.crops }
    );

    // Request climate resilience from CRA
    const climateData = await this.requestFromAgent(
      AgentType.CRA,
      { action: 'getClimateResilience', location: data.location }
    );

    // Request yield forecast from GAA
    const yieldData = await this.requestFromAgent(
      AgentType.GAA,
      { action: 'forecastYield', crops: data.crops }
    );

    // Portfolio optimization algorithm (placeholder)
    return {
      portfolioId: 'port-123',
      recommendedCrops: [],
      riskScore: 0.5,
      expectedRevenue: 0
    };
  }

  private async calculateInvestmentUnits(data: any): Promise<any> {
    // TODO: Implement in Phase 2
    console.log('💰 CMGA: Calculating investment units', data);
    return { units: 0 };
  }

  private async distributeProfit(data: any): Promise<any> {
    // TODO: Implement in Phase 2
    console.log('💸 CMGA: Distributing profits', data);
    return { distributions: [] };
  }
}
```

### Week-by-Week Tasks

**Week 5-6:**
- Create database schema (run phase1_agents.sql)
- Build all 7 agent skeletons
- Set up agent deployment structure

**Week 7-8:**
- Create REST API endpoints for each agent
- Build admin dashboard (basic)
- Implement agent health checks

**Week 9-10:**
- Write unit tests for each agent skeleton
- Create integration tests for MCP communication
- Document APIs (Swagger/OpenAPI)

**Week 11-12:**
- End-to-end testing
- Performance testing
- Security audit (basic)
- Prepare for Phase 2

---

## Phase 2: Collective Market Governance (CMGA) (Weeks 13-20)

This is your **key differentiator** - prioritized for maximum impact.

### Goals
- Build complete CMGA functionality
- Create FPO management UI
- Implement Investment Unit system
- Build profit distribution engine

### Key Features to Implement

#### 1. FPO Management System

**New Component: `/src/pages/FPODashboard.tsx`**
```typescript
import React from 'react';
import { useFPOData } from '@/hooks/useFPOData';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { InvestmentUnitsTable } from '@/components/fpo/InvestmentUnitsTable';
import { CollectivePortfolio } from '@/components/fpo/CollectivePortfolio';
import { ProfitDistribution } from '@/components/fpo/ProfitDistribution';
import { MemberManagement } from '@/components/fpo/MemberManagement';

export default function FPODashboard() {
  const { fpo, members, portfolio, loading } = useFPOData();

  if (loading) return <div>Loading FPO data...</div>;

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">{fpo.name}</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card className="p-4">
          <h3 className="text-sm text-gray-500">Total Members</h3>
          <p className="text-3xl font-bold">{fpo.total_members}</p>
        </Card>

        <Card className="p-4">
          <h3 className="text-sm text-gray-500">Total Land Area</h3>
          <p className="text-3xl font-bold">{fpo.total_land_area} ha</p>
        </Card>

        <Card className="p-4">
          <h3 className="text-sm text-gray-500">Current Season Revenue</h3>
          <p className="text-3xl font-bold">₹{portfolio.expected_revenue}</p>
        </Card>
      </div>

      <Tabs defaultValue="portfolio">
        <TabsList>
          <TabsTrigger value="portfolio">Collective Portfolio</TabsTrigger>
          <TabsTrigger value="members">Members</TabsTrigger>
          <TabsTrigger value="units">Investment Units</TabsTrigger>
          <TabsTrigger value="profits">Profit Distribution</TabsTrigger>
        </TabsList>

        <TabsContent value="portfolio">
          <CollectivePortfolio portfolio={portfolio} />
        </TabsContent>

        <TabsContent value="members">
          <MemberManagement members={members} fpoId={fpo.id} />
        </TabsContent>

        <TabsContent value="units">
          <InvestmentUnitsTable fpoId={fpo.id} />
        </TabsContent>

        <TabsContent value="profits">
          <ProfitDistribution fpoId={fpo.id} portfolioId={portfolio.id} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

#### 2. Portfolio Optimization Algorithm

**New File: `/backend/agents/cmga/portfolio-optimizer.ts`**
```typescript
import { PortfolioConstraints, CropOption, OptimizedPortfolio } from './types';

export class PortfolioOptimizer {
  /**
   * Optimize collective crop portfolio using Modern Portfolio Theory
   * adapted for agriculture
   */
  async optimize(
    constraints: PortfolioConstraints,
    cropOptions: CropOption[],
    marketData: any,
    climateData: any,
    yieldForecasts: any
  ): Promise<OptimizedPortfolio> {

    // Calculate expected returns for each crop
    const returns = cropOptions.map(crop =>
      this.calculateExpectedReturn(crop, marketData, yieldForecasts)
    );

    // Calculate risk (variance) for each crop
    const risks = cropOptions.map(crop =>
      this.calculateRisk(crop, climateData, marketData)
    );

    // Calculate correlation matrix
    const correlationMatrix = this.calculateCorrelations(cropOptions, marketData);

    // Optimize using quadratic programming
    // Maximize: expected return
    // Minimize: portfolio variance
    // Subject to: land constraints, water availability, labor
    const allocation = await this.solveQuadraticProgram(
      returns,
      risks,
      correlationMatrix,
      constraints
    );

    return {
      crops: allocation,
      expectedReturn: this.calculatePortfolioReturn(allocation, returns),
      portfolioRisk: this.calculatePortfolioRisk(allocation, risks, correlationMatrix),
      sharpeRatio: this.calculateSharpeRatio(allocation, returns, risks),
      diversificationIndex: this.calculateDiversification(allocation)
    };
  }

  private calculateExpectedReturn(crop: CropOption, market: any, yield: any): number {
    const predictedYield = yield[crop.name] || crop.avgYield;
    const predictedPrice = market.priceForecast[crop.name] || crop.avgPrice;
    const costPerHa = crop.cultivationCost;

    return (predictedYield * predictedPrice - costPerHa) / costPerHa;
  }

  private calculateRisk(crop: CropOption, climate: any, market: any): number {
    // Risk factors: price volatility, yield variability, climate vulnerability
    const priceVolatility = market.volatility[crop.name] || 0.2;
    const yieldVariability = crop.yieldStdDev / crop.avgYield;
    const climateRisk = climate.riskScore[crop.name] || 0.5;

    // Weighted combination
    return 0.4 * priceVolatility + 0.4 * yieldVariability + 0.2 * climateRisk;
  }

  private calculateCorrelations(crops: CropOption[], market: any): number[][] {
    // Simplified correlation calculation
    // In production, use historical price/yield data
    const n = crops.length;
    const matrix: number[][] = Array(n).fill(null).map(() => Array(n).fill(0));

    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (i === j) {
          matrix[i][j] = 1.0;
        } else {
          // Crops of same family have higher correlation
          const correlation = this.estimateCorrelation(crops[i], crops[j], market);
          matrix[i][j] = correlation;
        }
      }
    }

    return matrix;
  }

  private estimateCorrelation(crop1: CropOption, crop2: CropOption, market: any): number {
    // Simplified estimation
    if (crop1.family === crop2.family) return 0.7;
    if (crop1.season === crop2.season) return 0.5;
    return 0.2;
  }

  private async solveQuadraticProgram(
    returns: number[],
    risks: number[],
    correlations: number[][],
    constraints: PortfolioConstraints
  ): Promise<any[]> {
    // Simplified solver - in production use optimization library
    // like google-or-tools, cvxpy (Python), or quadprog

    // For now, use greedy heuristic:
    // 1. Sort crops by Sharpe ratio (return/risk)
    // 2. Allocate proportionally within constraints

    const sharpeRatios = returns.map((r, i) => ({
      index: i,
      sharpe: r / risks[i],
      return: r,
      risk: risks[i]
    })).sort((a, b) => b.sharpe - a.sharpe);

    const allocation: any[] = [];
    let remainingLand = constraints.totalLand;
    let remainingWater = constraints.totalWater;

    for (const crop of sharpeRatios) {
      const maxLandByCrop = remainingLand * 0.4; // Max 40% in single crop
      const maxLandByWater = remainingWater / crop.waterRequirement;
      const allocatedLand = Math.min(maxLandByCrop, maxLandByWater, remainingLand);

      if (allocatedLand > 0) {
        allocation.push({
          cropIndex: crop.index,
          landArea: allocatedLand,
          expectedReturn: crop.return,
          risk: crop.risk
        });

        remainingLand -= allocatedLand;
        remainingWater -= allocatedLand * crop.waterRequirement;
      }
    }

    return allocation;
  }

  private calculatePortfolioReturn(allocation: any[], returns: number[]): number {
    const totalLand = allocation.reduce((sum, a) => sum + a.landArea, 0);
    return allocation.reduce((sum, a) => {
      const weight = a.landArea / totalLand;
      return sum + weight * returns[a.cropIndex];
    }, 0);
  }

  private calculatePortfolioRisk(
    allocation: any[],
    risks: number[],
    correlations: number[][]
  ): number {
    // Portfolio variance formula
    const totalLand = allocation.reduce((sum, a) => sum + a.landArea, 0);
    let variance = 0;

    for (let i = 0; i < allocation.length; i++) {
      for (let j = 0; j < allocation.length; j++) {
        const wi = allocation[i].landArea / totalLand;
        const wj = allocation[j].landArea / totalLand;
        const corr = correlations[allocation[i].cropIndex][allocation[j].cropIndex];
        variance += wi * wj * risks[allocation[i].cropIndex] *
                    risks[allocation[j].cropIndex] * corr;
      }
    }

    return Math.sqrt(variance);
  }

  private calculateSharpeRatio(allocation: any[], returns: number[], risks: number[]): number {
    const portfolioReturn = this.calculatePortfolioReturn(allocation, returns);
    const portfolioRisk = this.calculatePortfolioRisk(allocation, risks, [[1]]);
    const riskFreeRate = 0.05; // 5% assumption

    return (portfolioReturn - riskFreeRate) / portfolioRisk;
  }

  private calculateDiversification(allocation: any[]): number {
    // Herfindahl index: 1 - sum(weight^2)
    const totalLand = allocation.reduce((sum, a) => sum + a.landArea, 0);
    const sumSquares = allocation.reduce((sum, a) => {
      const weight = a.landArea / totalLand;
      return sum + weight * weight;
    }, 0);

    return 1 - sumSquares;
  }
}
```

#### 3. Investment Unit Calculator

**New File: `/backend/agents/cmga/investment-unit-calculator.ts`**
```typescript
export interface InvestmentFactors {
  landArea: number; // hectares
  soilQuality: number; // 0-1 score
  inputsValue: number; // ₹ value of seeds, fertilizers
  laborDays: number;
  waterAccess: number; // 0-1 score
  equipmentContribution: number; // ₹ value
}

export class InvestmentUnitCalculator {
  /**
   * Calculate investment units based on multiple factors
   * Ensures fair profit distribution
   */
  calculateUnits(factors: InvestmentFactors, weights?: any): number {
    // Default weights - can be customized per FPO
    const w = weights || {
      land: 0.40,
      soil: 0.10,
      inputs: 0.20,
      labor: 0.15,
      water: 0.10,
      equipment: 0.05
    };

    // Normalize each factor (0-1 scale)
    const normalized = {
      land: this.normalizeLand(factors.landArea),
      soil: factors.soilQuality,
      inputs: this.normalizeInputs(factors.inputsValue),
      labor: this.normalizeLabor(factors.laborDays),
      water: factors.waterAccess,
      equipment: this.normalizeEquipment(factors.equipmentContribution)
    };

    // Weighted sum
    const score =
      w.land * normalized.land +
      w.soil * normalized.soil +
      w.inputs * normalized.inputs +
      w.labor * normalized.labor +
      w.water * normalized.water +
      w.equipment * normalized.equipment;

    // Scale to units (e.g., 1 unit per 0.01 score)
    return score * 100;
  }

  private normalizeLand(area: number): number {
    // Normalize using sigmoid to prevent extreme values
    // Assuming average holding is 2 hectares
    const avgHolding = 2;
    return 1 / (1 + Math.exp(-(area - avgHolding) / avgHolding));
  }

  private normalizeInputs(value: number): number {
    // Normalize input value (assuming max ₹50,000 per ha)
    const maxValue = 50000;
    return Math.min(value / maxValue, 1);
  }

  private normalizeLabor(days: number): number {
    // Normalize labor contribution (assuming max 100 days)
    const maxDays = 100;
    return Math.min(days / maxDays, 1);
  }

  private normalizeEquipment(value: number): number {
    // Normalize equipment value (assuming max ₹100,000)
    const maxValue = 100000;
    return Math.min(value / maxValue, 1);
  }

  /**
   * Calculate profit distribution based on investment units
   */
  distributeProfit(
    totalProfit: number,
    memberUnits: Map<string, number>
  ): Map<string, number> {
    const totalUnits = Array.from(memberUnits.values())
      .reduce((sum, units) => sum + units, 0);

    const distribution = new Map<string, number>();

    for (const [memberId, units] of memberUnits.entries()) {
      const share = (units / totalUnits) * totalProfit;
      distribution.set(memberId, share);
    }

    return distribution;
  }
}
```

### Deliverables

- ✅ Complete CMGA agent with portfolio optimization
- ✅ FPO management dashboard
- ✅ Investment Unit calculation system
- ✅ Profit distribution engine
- ✅ Member management interface
- ✅ Portfolio visualization

### Week-by-Week Tasks

**Week 13-14:** Build portfolio optimization algorithm
**Week 15-16:** Implement Investment Unit calculator
**Week 17-18:** Build FPO dashboard UI
**Week 19:** Integrate with MIA/GAA/CRA
**Week 20:** Testing and documentation

---

## Phase 3: Market Intelligence (MIA) (Weeks 21-26)

### Goals
- Integrate mandi price APIs
- Build price forecasting models
- Implement demand forecasting
- Create market analytics dashboard

### Key Integrations

#### 1. Agmarknet API Integration

**New File: `/backend/agents/mia/integrations/agmarknet.ts`**
```typescript
import axios from 'axios';

export class AgmarknetIntegration {
  private readonly BASE_URL = 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070';
  private readonly API_KEY = process.env.AGMARKNET_API_KEY;

  async fetchMandiPrices(params: {
    state?: string;
    district?: string;
    commodity?: string;
    fromDate?: string;
    toDate?: string;
  }): Promise<any[]> {
    try {
      const response = await axios.get(this.BASE_URL, {
        params: {
          'api-key': this.API_KEY,
          format: 'json',
          limit: 1000,
          ...params
        }
      });

      return this.parseResponse(response.data);
    } catch (error) {
      console.error('Error fetching mandi prices:', error);
      throw error;
    }
  }

  private parseResponse(data: any): any[] {
    // Parse Agmarknet response format
    if (!data.records) return [];

    return data.records.map((record: any) => ({
      mandName: record.market,
      state: record.state,
      district: record.district,
      commodity: record.commodity,
      variety: record.variety,
      grade: record.grade,
      minPrice: parseFloat(record.min_price),
      maxPrice: parseFloat(record.max_price),
      modalPrice: parseFloat(record.modal_price),
      arrivalQuantity: parseFloat(record.arrival_tonnes || 0),
      priceDate: new Date(record.arrival_date)
    }));
  }

  /**
   * Store prices in database
   */
  async storePrices(prices: any[]): Promise<void> {
    // Bulk insert into mandi_prices table
    const { supabase } = await import('@/integrations/supabase/client');

    const { error } = await supabase
      .from('mandi_prices')
      .upsert(prices, {
        onConflict: 'mandi_name,commodity,variety,price_date'
      });

    if (error) {
      console.error('Error storing mandi prices:', error);
      throw error;
    }
  }
}
```

#### 2. Price Forecasting Model

**New File: `/backend/agents/mia/models/price-forecaster.py`**
```python
import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_percentage_error
import psycopg2
from datetime import datetime, timedelta

class PriceForecaster:
    """
    Time-series forecasting for agricultural commodity prices
    using Facebook Prophet
    """

    def __init__(self, db_connection_string):
        self.conn = psycopg2.connect(db_connection_string)
        self.models = {}

    def fetch_historical_prices(self, commodity, mandi=None, lookback_days=730):
        """Fetch historical price data from database"""
        query = """
            SELECT price_date as ds, modal_price as y
            FROM mandi_prices
            WHERE commodity = %s
              AND price_date >= %s
        """

        params = [commodity, datetime.now() - timedelta(days=lookback_days)]

        if mandi:
            query += " AND mandi_name = %s"
            params.append(mandi)

        query += " ORDER BY price_date"

        df = pd.read_sql(query, self.conn, params=params)
        return df

    def train_model(self, commodity, mandi=None):
        """Train Prophet model for commodity"""
        df = self.fetch_historical_prices(commodity, mandi)

        if len(df) < 60:  # Need at least 2 months of data
            raise ValueError(f"Insufficient data for {commodity}")

        # Initialize Prophet with Indian holidays
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,  # Less flexible for stability
            seasonality_prior_scale=10.0
        )

        # Add custom seasonality for agricultural cycles
        model.add_seasonality(name='monthly', period=30.5, fourier_order=5)

        # Add regressor for arrival quantity if available
        # model.add_regressor('arrival_quantity')

        model.fit(df)

        model_key = f"{commodity}_{mandi if mandi else 'all'}"
        self.models[model_key] = model

        return model

    def forecast(self, commodity, mandi=None, horizon_days=90):
        """Generate price forecast"""
        model_key = f"{commodity}_{mandi if mandi else 'all'}"

        if model_key not in self.models:
            self.train_model(commodity, mandi)

        model = self.models[model_key]

        # Create future dataframe
        future = model.make_future_dataframe(periods=horizon_days)

        # Generate forecast
        forecast = model.predict(future)

        # Extract relevant columns
        result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(horizon_days)

        return {
            'commodity': commodity,
            'mandi': mandi,
            'forecast_date': datetime.now().isoformat(),
            'predictions': result.to_dict('records'),
            'model_performance': self.evaluate_model(model, commodity, mandi)
        }

    def evaluate_model(self, model, commodity, mandi):
        """Calculate model accuracy metrics"""
        df = self.fetch_historical_prices(commodity, mandi)

        if len(df) < 90:
            return {'mape': None, 'note': 'Insufficient data for evaluation'}

        # Use last 30 days for validation
        train = df[:-30]
        test = df[-30:]

        model_temp = Prophet()
        model_temp.fit(train)

        future = model_temp.make_future_dataframe(periods=30)
        forecast = model_temp.predict(future)

        predicted = forecast['yhat'].tail(30).values
        actual = test['y'].values

        mape = mean_absolute_percentage_error(actual, predicted)

        return {
            'mape': round(mape * 100, 2),  # Percentage
            'validation_period': '30 days'
        }

    def store_forecast(self, forecast_result):
        """Store forecast in database"""
        cursor = self.conn.cursor()

        for pred in forecast_result['predictions']:
            cursor.execute("""
                INSERT INTO price_forecasts (
                    commodity, mandi_name, forecast_date,
                    predicted_price, lower_bound, upper_bound,
                    model_version, confidence_score
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (commodity, mandi_name, forecast_date)
                DO UPDATE SET
                    predicted_price = EXCLUDED.predicted_price,
                    lower_bound = EXCLUDED.lower_bound,
                    upper_bound = EXCLUDED.upper_bound,
                    updated_at = NOW()
            """, (
                forecast_result['commodity'],
                forecast_result['mandi'],
                pred['ds'],
                pred['yhat'],
                pred['yhat_lower'],
                pred['yhat_upper'],
                'prophet-v1',
                100 - forecast_result['model_performance']['mape']
            ))

        self.conn.commit()
        cursor.close()

# Scheduled job to update forecasts daily
if __name__ == '__main__':
    forecaster = PriceForecaster(os.environ['DATABASE_URL'])

    commodities = ['Tomato', 'Onion', 'Potato', 'Rice', 'Wheat']

    for commodity in commodities:
        try:
            result = forecaster.forecast(commodity, horizon_days=90)
            forecaster.store_forecast(result)
            print(f"✅ Forecast updated for {commodity}")
        except Exception as e:
            print(f"❌ Error forecasting {commodity}: {e}")
```

### Deliverables

- ✅ Agmarknet API integration
- ✅ Historical price database (2+ years)
- ✅ Price forecasting models (Prophet)
- ✅ Demand forecasting
- ✅ Market analytics dashboard
- ✅ Price alerts system

### Week-by-Week Tasks

**Week 21-22:** Integrate Agmarknet + historical data ingestion
**Week 23-24:** Build price forecasting models (Python)
**Week 25:** Create market analytics dashboard
**Week 26:** Testing + MIA-CMGA integration

---

## Phase 4: Geo-Agronomy Agent (GAA) (Weeks 27-38)

### Goals
- Integrate satellite imagery (Sentinel-2)
- Build NDVI analysis pipeline
- Implement crop disease detection (CNN)
- Deploy yield forecasting models

### Key Components

#### 1. Satellite Imagery Integration

**New File: `/backend/agents/gaa/integrations/sentinel-hub.ts`**
```typescript
import axios from 'axios';
import { createClient } from '@supabase/supabase-js';

export class SentinelHubIntegration {
  private readonly CLIENT_ID = process.env.SENTINEL_HUB_CLIENT_ID;
  private readonly CLIENT_SECRET = process.env.SENTINEL_HUB_CLIENT_SECRET;
  private accessToken: string;

  async authenticate() {
    const response = await axios.post(
      'https://services.sentinel-hub.com/oauth/token',
      new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: this.CLIENT_ID!,
        client_secret: this.CLIENT_SECRET!
      })
    );

    this.accessToken = response.data.access_token;
  }

  async fetchNDVIImage(bounds: any, date: string): Promise<Buffer> {
    const evalscript = `
      //VERSION=3
      function setup() {
        return {
          input: ["B04", "B08", "dataMask"],
          output: { bands: 4 }
        };
      }

      function evaluatePixel(sample) {
        let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);

        // Color mapping for NDVI
        if (ndvi < -0.2) return [0.0, 0.0, 0.5, sample.dataMask]; // Water (blue)
        if (ndvi < 0) return [0.5, 0.5, 0.5, sample.dataMask]; // Barren (gray)
        if (ndvi < 0.2) return [1.0, 1.0, 0.7, sample.dataMask]; // Sparse veg (tan)
        if (ndvi < 0.4) return [1.0, 1.0, 0.0, sample.dataMask]; // Moderate (yellow)
        if (ndvi < 0.6) return [0.5, 1.0, 0.0, sample.dataMask]; // Healthy (yellow-green)
        return [0.0, 0.8, 0.0, sample.dataMask]; // Very healthy (green)
      }
    `;

    const response = await axios.post(
      'https://services.sentinel-hub.com/api/v1/process',
      {
        input: {
          bounds: {
            bbox: bounds,  // [minX, minY, maxX, maxY]
            properties: { crs: 'http://www.opengis.net/def/crs/EPSG/0/4326' }
          },
          data: [{
            type: 'sentinel-2-l2a',
            dataFilter: {
              timeRange: {
                from: `${date}T00:00:00Z`,
                to: `${date}T23:59:59Z`
              },
              maxCloudCoverage: 30
            }
          }]
        },
        output: {
          width: 512,
          height: 512,
          responses: [{
            identifier: 'default',
            format: { type: 'image/png' }
          }]
        },
        evalscript
      },
      {
        headers: { Authorization: `Bearer ${this.accessToken}` },
        responseType: 'arraybuffer'
      }
    );

    return Buffer.from(response.data);
  }

  async calculateNDVI(bounds: any, date: string): Promise<any> {
    const evalscript = `
      //VERSION=3
      function setup() {
        return {
          input: ["B04", "B08"],
          output: { bands: 1, sampleType: "FLOAT32" }
        };
      }

      function evaluatePixel(sample) {
        return [(sample.B08 - sample.B04) / (sample.B08 + sample.B04)];
      }
    `;

    const response = await axios.post(
      'https://services.sentinel-hub.com/api/v1/process',
      {
        input: {
          bounds: {
            bbox: bounds,
            properties: { crs: 'http://www.opengis.net/def/crs/EPSG/0/4326' }
          },
          data: [{
            type: 'sentinel-2-l2a',
            dataFilter: {
              timeRange: {
                from: `${date}T00:00:00Z`,
                to: `${date}T23:59:59Z`
              },
              maxCloudCoverage: 30
            }
          }]
        },
        output: {
          responses: [{
            identifier: 'default',
            format: { type: 'application/json' }
          }]
        },
        evalscript
      },
      {
        headers: { Authorization: `Bearer ${this.accessToken}` }
      }
    );

    // Calculate statistics
    const ndviValues = response.data;
    const stats = this.calculateStatistics(ndviValues);

    return stats;
  }

  private calculateStatistics(values: number[]): any {
    const validValues = values.filter(v => !isNaN(v) && v >= -1 && v <= 1);

    const mean = validValues.reduce((sum, v) => sum + v, 0) / validValues.length;
    const sorted = validValues.sort((a, b) => a - b);
    const min = sorted[0];
    const max = sorted[sorted.length - 1];

    return {
      mean: mean.toFixed(4),
      min: min.toFixed(4),
      max: max.toFixed(4),
      vegetationHealth: this.classifyHealth(mean)
    };
  }

  private classifyHealth(ndvi: number): string {
    if (ndvi < 0.2) return 'critical';
    if (ndvi < 0.4) return 'poor';
    if (ndvi < 0.6) return 'fair';
    if (ndvi < 0.7) return 'good';
    return 'excellent';
  }
}
```

#### 2. Disease Detection CNN

**New File: `/backend/agents/gaa/models/disease-detector.py`**
```python
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
from PIL import Image
import io

class CropDiseaseDetector:
    """
    CNN-based crop disease detection using EfficientNet
    """

    def __init__(self, model_path=None):
        if model_path:
            self.model = keras.models.load_model(model_path)
        else:
            self.model = self.build_model()

        self.class_names = [
            'Healthy',
            'Bacterial Blight',
            'Brown Spot',
            'Leaf Blast',
            'Tungro',
            'Bacterial Leaf Streak',
            'Sheath Blight'
        ]

    def build_model(self, num_classes=7):
        """Build EfficientNet-based model"""
        base_model = EfficientNetB0(
            include_top=False,
            weights='imagenet',
            input_shape=(224, 224, 3)
        )

        # Freeze base model initially
        base_model.trainable = False

        # Add custom head
        model = keras.Sequential([
            base_model,
            keras.layers.GlobalAveragePooling2D(),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(256, activation='relu'),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(num_classes, activation='softmax')
        ])

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'top_k_categorical_accuracy']
        )

        return model

    def preprocess_image(self, image_bytes):
        """Preprocess image for inference"""
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert('RGB')
        image = image.resize((224, 224))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)

        return image_array

    def predict(self, image_bytes):
        """Detect disease in crop image"""
        processed_image = self.preprocess_image(image_bytes)

        predictions = self.model.predict(processed_image)[0]

        # Get top 3 predictions
        top_indices = np.argsort(predictions)[-3:][::-1]

        results = []
        for idx in top_indices:
            results.append({
                'disease': self.class_names[idx],
                'confidence': float(predictions[idx]),
                'severity': self.estimate_severity(predictions[idx])
            })

        return {
            'primary_detection': results[0],
            'alternative_detections': results[1:],
            'is_healthy': results[0]['disease'] == 'Healthy',
            'recommendation': self.get_recommendation(results[0])
        }

    def estimate_severity(self, confidence):
        """Estimate severity based on confidence"""
        if confidence > 0.8:
            return 'high'
        elif confidence > 0.5:
            return 'medium'
        else:
            return 'low'

    def get_recommendation(self, detection):
        """Get treatment recommendation"""
        recommendations = {
            'Bacterial Blight': 'Apply copper-based bactericide. Remove infected plants.',
            'Brown Spot': 'Apply fungicide. Improve drainage and reduce humidity.',
            'Leaf Blast': 'Apply tricyclazole or carbendazim. Increase spacing.',
            'Tungro': 'Control green leafhopper vector. Remove infected plants.',
            'Bacterial Leaf Streak': 'Apply copper oxychloride. Avoid overhead irrigation.',
            'Sheath Blight': 'Apply validamycin or hexaconazole. Improve air circulation.'
        }

        return recommendations.get(
            detection['disease'],
            'Monitor closely and consult agricultural extension officer.'
        )

    def train(self, train_data_dir, validation_data_dir, epochs=30):
        """Train the model on labeled dataset"""
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=40,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )

        val_datagen = ImageDataGenerator(rescale=1./255)

        train_generator = train_datagen.flow_from_directory(
            train_data_dir,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical'
        )

        validation_generator = val_datagen.flow_from_directory(
            validation_data_dir,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical'
        )

        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                patience=5,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                factor=0.2,
                patience=3
            ),
            keras.callbacks.ModelCheckpoint(
                'best_model.h5',
                save_best_only=True
            )
        ]

        # Train
        history = self.model.fit(
            train_generator,
            validation_data=validation_generator,
            epochs=epochs,
            callbacks=callbacks
        )

        # Fine-tune
        base_model = self.model.layers[0]
        base_model.trainable = True

        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        history_fine = self.model.fit(
            train_generator,
            validation_data=validation_generator,
            epochs=10,
            callbacks=callbacks
        )

        return history, history_fine

# API endpoint integration
from fastapi import FastAPI, File, UploadFile
import uvicorn

app = FastAPI()
detector = CropDiseaseDetector(model_path='./models/disease_detector.h5')

@app.post("/detect")
async def detect_disease(file: UploadFile = File(...)):
    contents = await file.read()
    result = detector.predict(contents)
    return result

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8001)
```

### Deliverables

- ✅ Sentinel-2 satellite imagery integration
- ✅ NDVI analysis pipeline
- ✅ Disease detection CNN (75%+ accuracy)
- ✅ Yield forecasting models
- ✅ Field boundary detection
- ✅ Image upload API for farmers

### Week-by-Week Tasks

**Week 27-29:** Sentinel Hub integration + NDVI pipeline
**Week 30-33:** Train disease detection CNN (collect/label data)
**Week 34-36:** Build yield forecasting models
**Week 37-38:** Testing + GAA-CMGA integration

---

Due to length constraints, I'll continue the roadmap in the next section. This covers:
- Phase 5: Climate & Resource Agent (CRA)
- Phase 6: Financial Inclusion Agent (FIA)
- Phase 7: Logistics Infrastructure Agent (LIA)
- Phase 8: Enhanced Human Interface (HIA)
- Phase 9-10: Integration, Testing, Pilot

Should I continue with the remaining phases in the same file or create a separate continuation document?
