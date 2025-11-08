# KisaanMitra: Getting Started Guide

Welcome to the KisaanMitra Multi-Agent System! This guide will help you get the development environment up and running.

---

## 📚 Documentation Overview

Before you start, please review these key documents:

1. **[ASSESSMENT.md](./ASSESSMENT.md)** - Current state vs. vision analysis (READ THIS FIRST!)
2. **[IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)** - Detailed implementation plan
3. **[PROGRESS_SUMMARY.md](./PROGRESS_SUMMARY.md)** - What's built, what's pending
4. This guide - Setup instructions

---

## 🎯 Current Status

**Overall Vision Alignment:** 8% ✅ (Up from 4.5%!)

**What's Ready:**
- ✅ MCP (Model Context Protocol) infrastructure
- ✅ Agent base architecture
- ✅ Extended database schema
- ✅ Message bus (Redis + RabbitMQ)
- ✅ Context management system
- ✅ Docker development environment

**What's Next:**
- 🔨 CMGA (Collective Market Governance Agent)
- 🔨 MIA (Market Intelligence Agent)
- 🔨 FPO Management UI
- ⏳ Other agents (GAA, CRA, FIA, LIA, enhanced HIA)

---

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose** (required)
- **Node.js 18+** (for local development)
- **Git** (for version control)

### Option 1: Docker Setup (Recommended)

```bash
# 1. Clone the repository (if not already done)
cd /home/cherry/KisaanMitra

# 2. Start all services
docker-compose up -d

# 3. Check service status
docker-compose ps

# 4. View logs
docker-compose logs -f
```

**Services Started:**
- PostgreSQL (port 5432) - Main database
- TimescaleDB (port 5433) - IoT time-series data
- Redis (port 6379) - Context caching
- RabbitMQ (port 5672, management UI: 15672) - Message queue
- MCP Bus (port 3001) - Agent communication server
- Frontend (port 8080) - React app

**Access Points:**
- Frontend: http://localhost:8080
- RabbitMQ Management: http://localhost:15672 (admin/admin)
- MCP Health Check: http://localhost:3001/health

### Option 2: Local Development Setup

```bash
# 1. Install MCP Bus dependencies
cd backend/mcp-bus
npm install

# 2. Start infrastructure services only
docker-compose up -d redis rabbitmq postgres timescaledb

# 3. Run MCP Bus locally
npm run dev

# 4. In a new terminal, start frontend
cd ../..
npm run dev
```

---

## 📊 Database Setup

### Initialize Extended Schema

```bash
# Connect to PostgreSQL
docker exec -it kisaanmitra-postgres psql -U postgres -d kisaanmitra

# Run the extended schema
\i /docker-entrypoint-initdb.d/extended_schema.sql

# Verify tables
\dt

# You should see 30+ tables including:
# - fpos, fpo_members, investment_units
# - collective_portfolios, profit_distributions
# - mandi_prices, price_forecasts
# - iot_sensors, irrigation_schedules
# - satellite_imagery, ndvi_analysis
# - credit_scores, loan_applications
# - insurance_policies, insurance_claims
# - cold_storage_facilities, post_harvest_losses
# - message_templates, sent_messages
```

### Sample Data (Optional)

```sql
-- Insert a sample FPO
INSERT INTO fpos (name, village, district, state, total_members, total_land_area, status)
VALUES
  ('Raitha Sangha', 'Kanakapura', 'Bangalore Rural', 'Karnataka', 50, 125.5, 'active');

-- Insert sample members (replace user_id with actual IDs from users table)
INSERT INTO fpo_members (fpo_id, user_id, join_date, land_area, role, status)
SELECT
  (SELECT id FROM fpos WHERE name = 'Raitha Sangha'),
  id,
  CURRENT_DATE,
  2.5,
  'member',
  'active'
FROM users
LIMIT 10;
```

---

## 🧪 Testing the MCP System

### 1. Check MCP Bus Health

```bash
curl http://localhost:3001/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "mcp-bus",
  "timestamp": "2025-11-08T..."
}
```

### 2. Monitor RabbitMQ

1. Open http://localhost:15672
2. Login: admin/admin
3. Go to "Queues" tab
4. You should see 7 queues (one for each agent):
   - `collective-market-governance`
   - `climate-resource`
   - `geo-agronomy`
   - `financial-inclusion`
   - `market-intelligence`
   - `logistics-infrastructure`
   - `human-interface`

### 3. Test Redis Context Storage

```bash
# Connect to Redis
docker exec -it kisaanmitra-redis redis-cli

# Test context storage
SET context:farmer:test-123 '{"farmContext":{"farmerId":"test-123"}}'
GET context:farmer:test-123

# Should return the JSON you just set
```

---

## 🏗️ Project Structure

```
KisaanMitra/
├── ASSESSMENT.md                 # Gap analysis
├── IMPLEMENTATION_ROADMAP.md     # Build plan
├── PROGRESS_SUMMARY.md           # Current status
├── GETTING_STARTED.md            # This file
├── docker-compose.yml            # Docker orchestration
│
├── infrastructure/
│   └── docker/
│       ├── Dockerfile.mcp-bus    # MCP server container
│       └── Dockerfile.frontend   # React app container
│
├── backend/
│   ├── mcp-bus/                  # Message bus service
│   │   ├── src/
│   │   │   ├── protocols/
│   │   │   │   └── mcp.protocol.ts
│   │   │   ├── bus/
│   │   │   │   └── message-bus.ts
│   │   │   ├── context/
│   │   │   │   └── context-manager.ts
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── agents/
│   │   ├── base/
│   │   │   └── agent.base.ts     # Base class for all agents
│   │   ├── cmga/                 # 🔨 To implement
│   │   ├── cra/                  # ⏳ Pending
│   │   ├── gaa/                  # ⏳ Pending
│   │   ├── fia/                  # ⏳ Pending
│   │   ├── mia/                  # ⏳ Pending
│   │   ├── lia/                  # ⏳ Pending
│   │   └── hia/                  # ⏳ Pending
│   │
│   └── schema/
│       ├── schema.sql            # Original schema
│       └── extended_schema.sql   # Multi-agent schema
│
├── src/                          # Frontend (existing React app)
│   ├── pages/
│   ├── components/
│   ├── hooks/
│   └── ...
│
└── package.json                  # Root package.json
```

---

## 🔧 Development Workflow

### Working on Agents

Each agent follows this pattern:

```typescript
// backend/agents/[agent-name]/[agent-name].agent.ts

import { BaseAgent } from '../base/agent.base';
import { MCPMessage, AgentType, AgentCapability } from '../../mcp-bus/src/protocols/mcp.protocol';

export class [AgentName]Agent extends BaseAgent {
  constructor(messageBus: any, contextManager: any) {
    super(AgentType.[AGENT_TYPE], messageBus, contextManager);
  }

  protected defineCapabilities(): AgentCapability {
    return {
      agentType: AgentType.[AGENT_TYPE],
      version: '1.0.0',
      capabilities: ['capability1', 'capability2'],
      inputSchemas: { /* ... */ },
      outputSchemas: { /* ... */ },
      dependencies: [/* other agents */]
    };
  }

  protected async handleMessage(message: MCPMessage): Promise<any> {
    // Agent logic here
  }
}
```

### Adding New Endpoints

1. Create agent implementation in `backend/agents/[agent-name]/`
2. Update database schema if needed in `backend/schema/extended_schema.sql`
3. Add frontend components in `src/components/[feature]/`
4. Create API hooks in `src/hooks/use[Feature].ts`

---

## 📝 Next Implementation Steps

### Priority 1: CMGA (Collective Market Governance)

**Files to Create:**
1. `backend/agents/cmga/cmga.agent.ts` - Main agent
2. `backend/agents/cmga/portfolio-optimizer.ts` - Optimization algorithm
3. `backend/agents/cmga/investment-calculator.ts` - Unit calculation
4. `src/pages/FPODashboard.tsx` - FPO management UI
5. `src/components/fpo/CollectivePortfolio.tsx` - Portfolio display
6. `src/components/fpo/InvestmentUnitsTable.tsx` - Units tracker
7. `src/hooks/useFPOData.ts` - Data fetching

**See IMPLEMENTATION_ROADMAP.md Phase 2 for detailed code examples.**

### Priority 2: MIA (Market Intelligence)

**Files to Create:**
1. `backend/agents/mia/mia.agent.ts` - Main agent
2. `backend/agents/mia/integrations/agmarknet.ts` - API integration
3. `backend/agents/mia/models/price-forecaster.py` - ML model
4. `src/components/market/PriceChart.tsx` - Price visualization
5. `src/hooks/useMandiPrices.ts` - Price data hook

**See IMPLEMENTATION_ROADMAP.md Phase 3 for detailed code examples.**

---

## 🐛 Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs -f

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database connection issues

```bash
# Check if PostgreSQL is ready
docker exec kisaanmitra-postgres pg_isready -U postgres

# Restart database
docker-compose restart postgres
```

### RabbitMQ not connecting

```bash
# Check RabbitMQ status
docker exec kisaanmitra-rabbitmq rabbitmq-diagnostics ping

# Restart RabbitMQ
docker-compose restart rabbitmq
```

### Port conflicts

```bash
# If ports are already in use, modify docker-compose.yml:
# Change "5432:5432" to "5433:5432" for PostgreSQL
# Change "6379:6379" to "6380:6379" for Redis
# etc.
```

---

## 📚 Learning Resources

### Understanding the Architecture

1. **Multi-Agent Systems:**
   - [Introduction to MAS](https://en.wikipedia.org/wiki/Multi-agent_system)
   - [Agent Communication](https://www.fipa.org/repository/aclspecs.html)

2. **Message Queue Patterns:**
   - [RabbitMQ Tutorials](https://www.rabbitmq.com/getstarted.html)
   - [Pub/Sub Pattern](https://www.enterpriseintegrationpatterns.com/patterns/messaging/PublishSubscribeChannel.html)

3. **Context Management:**
   - [Redis Best Practices](https://redis.io/docs/management/optimization/)

### Agricultural Domain

1. **FPO Operations:**
   - [NABARD Guidelines](https://www.nabard.org/content1.aspx?id=523)
   - [FPO Success Stories](https://sfacindia.com/)

2. **Satellite Imagery for Agriculture:**
   - [Sentinel Hub Docs](https://docs.sentinel-hub.com/)
   - [NDVI Explained](https://gisgeography.com/ndvi-normalized-difference-vegetation-index/)

3. **Market Intelligence:**
   - [Agmarknet Portal](https://agmarknet.gov.in/)
   - [Price Forecasting Methods](https://www.fao.org/3/a0233e/a0233e04.htm)

---

## 🤝 Contributing

### Development Guidelines

1. **Code Style:**
   - Use TypeScript for backend
   - Follow ESLint rules
   - Write meaningful commit messages

2. **Testing:**
   - Write unit tests for agents
   - Test MCP message flows
   - Validate database schemas

3. **Documentation:**
   - Update README for new features
   - Document agent capabilities
   - Comment complex algorithms

---

## 📞 Support & Feedback

### Questions?

1. Check ASSESSMENT.md for vision alignment
2. Review IMPLEMENTATION_ROADMAP.md for build plans
3. See PROGRESS_SUMMARY.md for current status

### Found a Bug?

1. Check if it's a known issue in PROGRESS_SUMMARY.md
2. Test in a clean environment
3. Document reproduction steps

---

## 🎯 Success Criteria

### You're on the right track if:

✅ All Docker containers are running (`docker-compose ps`)
✅ MCP health check returns "healthy" (http://localhost:3001/health)
✅ RabbitMQ shows 7 agent queues (http://localhost:15672)
✅ Frontend loads at http://localhost:8080
✅ Database has 30+ tables from extended schema

### Next milestone achieved when:

✅ CMGA agent can create collective portfolios
✅ FPO dashboard displays Investment Units
✅ Profit distribution calculates correctly
✅ MIA agent fetches real mandi prices
✅ GAA agent processes satellite imagery

---

## 🚀 Ready to Build?

Start with implementing the CMGA (Collective Market Governance Agent) - your key differentiator!

See **IMPLEMENTATION_ROADMAP.md Phase 2** for detailed implementation steps.

**Quick Start Command:**
```bash
cd /home/cherry/KisaanMitra
docker-compose up -d
docker-compose logs -f
```

**Happy Coding! 🌾**
