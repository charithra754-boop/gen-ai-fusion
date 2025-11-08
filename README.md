✦ KisaanMitra: Multi-Agent System for Collective Agricultural Empowerment

  > Transforming smallholder farmers from isolated risk-takers to shareholders in a digitally managed, collective enterprise.

  KisaanMitra is an advanced Multi-Agent System (MAS) designed to address systemic agricultural challenges in India through collective action, autonomous field management,
   and comprehensive farmer empowerment.

  ---

  🎯 Vision

  Our platform addresses five critical problems:
   1. Unreliable Climate Data → Autonomous irrigation with IoT sensors
   2. Financial Exclusion → AI credit scoring using alternative data
   3. Post-Harvest Losses (16-40%) → Cold chain optimization
   4. Market Volatility → Collective bargaining through FPOs
   5. Smallholder Vulnerability → Investment Units & transparent profit sharing

  🏗️ Architecture

  Multi-Agent System (7 Specialized Agents)

   1. CMGA - Collective Market Governance (Portfolio planning, Investment Units, Profit distribution)
   2. MIA - Market Intelligence (Mandi prices, Demand forecasting, Price predictions)
   3. GAA - Geo-Agronomy (Satellite imagery, NDVI, Disease detection, Yield forecasting)
   4. CRA - Climate & Resource (IoT sensors, Autonomous irrigation, Water budgets)
   5. FIA - Financial Inclusion (Credit scoring, Insurance automation, Anti-fraud)
   6. LIA - Logistics Infrastructure (Cold chain, Route optimization, Loss tracking)
   7. HIA - Human Interface (Multilingual, Voice, SMS/IVR, Agent synthesis)

  Tech Stack

  Current MVP:
   - Frontend: React 18, TypeScript, Vite, Shadcn/UI, Tailwind CSS
   - Backend: Supabase (PostgreSQL, Auth, Edge Functions)
   - Languages: English, Kannada, Hindi (voice + text)

  Multi-Agent Infrastructure:
   - MCP: Model Context Protocol for agent communication
   - Message Queue: RabbitMQ for reliable message delivery
   - Context Cache: Redis for shared state management
   - Time-Series: TimescaleDB for IoT sensor data
   - Geospatial: PostGIS for location-based queries
   - ML/AI: TensorFlow (CNNs), Prophet (forecasting)

  ---

  📊 Current Status

  Implementation: 8% of full vision ✅

  What's Built:
   - ✅ Multilingual voice interface (English, Kannada, Hindi)
   - ✅ Soil analysis with crop recommendations
   - ✅ Weather display and farming tips
   - ✅ MCP infrastructure (Redis + RabbitMQ)
   - ✅ Agent base architecture
   - ✅ Extended database schema (30+ tables)
   - ✅ Docker development environment

  What's Next:
   - 🔨 CMGA (Collective Market Governance) - Priority #1
   - 🔨 MIA (Market Intelligence with mandi prices)
   - 🔨 FPO Dashboard UI
   - ⏳ Remaining agents (GAA, CRA, FIA, LIA)

  ---

  🚀 Quick Start

  Prerequisites

   - Docker & Docker Compose (required for MAS)
   - Node.js 18+ (for local development)
   - Git

  Option 1: Full Multi-Agent System (Docker)

   1 # Start all services (PostgreSQL, Redis, RabbitMQ, MCP Bus, Frontend)
   2 docker-compose up -d
   3 
   4 # Check status
   5 docker-compose ps
   6 
   7 # View logs
   8 docker-compose logs -f

  Access:
   - Frontend: http://localhost:8080
   - RabbitMQ Management: http://localhost:15672 (admin/admin)
   - MCP Health: http://localhost:3001/health

  Option 2: MVP Only (Existing Features)

   1 # Install dependencies
   2 npm install
   3 
   4 # Set up environment
   5 cp .env.example .env
   6 # Edit .env with your Supabase credentials
   7 
   8 # Run development server
   9 npm run dev

  Access at http://localhost:8080

  ---

  📚 Documentation

  Must-Read Documents (in order)

   1. [GETTING_STARTED.md](./GETTING_STARTED.md) - Setup guide
   2. [ASSESSMENT.md](./ASSESSMENT.md) - Current vs. vision analysis
   3. [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) - Build plan (18-24 months)
   4. [PROGRESS_SUMMARY.md](./PROGRESS_SUMMARY.md) - What's done, what's next

  Database Setup

   1 # Connect to PostgreSQL
   2 docker exec -it kisaanmitra-postgres psql -U postgres -d kisaanmitra
   3 
   4 # Run extended schema (30+ tables for all agents)
   5 \i /docker-entrypoint-initdb.d/extended_schema.sql
   6 
   7 # Verify
   8 \dt  # Should show fpos, investment_units, mandi_prices, etc.

  ---

  🏛️ Project Structure

    1 KisaanMitra/
    2 ├── 📄 Documentation
    3 │   ├── ASSESSMENT.md              # Gap analysis (96% to build)
    4 │   ├── IMPLEMENTATION_ROADMAP.md  # Detailed plan with code examples
    5 │   ├── PROGRESS_SUMMARY.md        # Current status
    6 │   └── GETTING_STARTED.md         # Setup guide
    7 │
    8 ├── 🏗️ Multi-Agent Infrastructure
    9 │   ├── docker-compose.yml         # Orchestration
   10 │   ├── infrastructure/docker/     # Dockerfiles
   11 │   └── backend/
   12 │       ├── mcp-bus/              # Message bus (MCP protocol)
   13 │       ├── agents/               # 7 agent implementations
   14 │       │   ├── base/            # BaseAgent class
   15 │       │   ├── cmga/ 🔨         # Collective governance
   16 │       │   ├── mia/ ⏳          # Market intelligence
   17 │       │   ├── gaa/ ⏳          # Geo-agronomy
   18 │       │   ├── cra/ ⏳          # Climate & resource
   19 │       │   ├── fia/ ⏳          # Financial inclusion
   20 │       │   ├── lia/ ⏳          # Logistics
   21 │       │   └── hia/ ⏳          # Human interface
   22 │       └── schema/
   23 │           ├── schema.sql        # Original
   24 │           └── extended_schema.sql # Multi-agent (NEW)
   25 │
   26 └── 🎨 Frontend (MVP - Working)
   27     └── src/
   28         ├── pages/
   29         │   ├── Index.tsx         # Home dashboard
   30         │   └── SoilAnalysis.tsx  # Soil testing
   31         ├── components/
   32         │   ├── SmartAIAssistant.tsx  # Voice interface
   33         │   ├── DatabaseWeatherWidget.tsx
   34         │   └── ui/               # 40+ Shadcn components
   35         └── hooks/
   36             ├── useAgriculturalData.ts
   37             └── useLanguage.tsx   # Multilingual

  ---

  🎓 Key Concepts

  1. Collective Market Governance (CMGA)

  Problem: Individual farmers have no bargaining power.

  Solution: FPOs plan crop portfolios collectively, track Investment Units transparently, and distribute profits fairly.

  Example:

   1 Raitha Sangha FPO (50 farmers, 125 ha)
   2 ├── Collective Portfolio: 40% Tomato, 30% Onion, 30% Potato
   3 ├── Investment Units: Land (40%) + Inputs (20%) + Labor (15%) + ...
   4 ├── Expected Revenue: ₹75 lakhs
   5 └── Profit Distribution: Transparent, automated, proportional

  2. Model Context Protocol (MCP)

  Problem: Agents need to share context efficiently.

  Solution: Standardized protocol for message passing and context propagation.

  Example:

   1 // GAA detects crop stress → CRA adjusts irrigation → CMGA updates risk
   2 await messageBus.publish({
   3   type: MessageType.EVENT,
   4   source: AgentType.GAA,
   5   target: [AgentType.CRA, AgentType.CMGA],
   6   payload: { stressDetected: true, ndvi: 0.35 },
   7   context: { farmerId: 'farmer-123', cropType: 'tomato' },
   8   priority: MessagePriority.HIGH
   9 });

  3. Investment Units

  Problem: How to fairly distribute profits in collective farming?

  Solution: Transparent calculation based on land, inputs, labor, equipment.

  Formula:

   1 Units = 0.4 × land + 0.2 × inputs + 0.15 × labor + 0.1 × water + 0.1 × soil + 0.05 × equipment
   2 Profit Share = (Member Units / Total Units) × Total Profit

  ---

  🔮 Roadmap

  Phase 1: CMGA Foundation (Months 1-2)
   - ✅ Portfolio optimization algorithm
   - ✅ Investment Unit calculator
   - ✅ FPO dashboard UI
   - ✅ Profit distribution engine

  Phase 2: Market Intelligence (Months 3-4)
   - ⏳ Agmarknet API integration
   - ⏳ Price forecasting (Prophet/ARIMA)
   - ⏳ Demand prediction
   - ⏳ Market analytics dashboard

  Phase 3: Geo-Agronomy (Months 5-8)
   - ⏳ Sentinel-2 satellite imagery
   - ⏳ NDVI analysis pipeline
   - ⏳ Disease detection CNN (75%+ accuracy)
   - ⏳ Yield forecasting

  Phase 4: Climate & Resource (Months 9-11)
   - ⏳ IoT sensor integration
   - ⏳ Autonomous irrigation control
   - ⏳ Water budget optimization
   - ⏳ Climate resilience rating

  Phase 5: Financial Inclusion (Months 12-15)
   - ⏳ AI credit scoring
   - ⏳ Banking API integration
   - ⏳ Insurance automation (FNOL)
   - ⏳ Anti-fraud detection

  Phase 6: Logistics (Months 16-18)
   - ⏳ Cold storage capacity planning
   - ⏳ Route optimization
   - ⏳ IoT tracking for transport
   - ⏳ Loss prevention (target: 15-20% reduction)

  Phase 7: Integration & Testing (Months 19-22)
   - ⏳ End-to-end agent testing
   - ⏳ Performance optimization
   - ⏳ Security audit
   - ⏳ SMS/IVR channels

  Phase 8: Pilot & Production (Months 23-24)
   - ⏳ Pilot with 1-2 FPOs
   - ⏳ User feedback & iteration
   - ⏳ Production deployment
   - ⏳ Monitoring & analytics

  ---

  🧪 Testing

  MCP System

    1 # Check MCP health
    2 curl http://localhost:3001/health
    3 
    4 # Monitor RabbitMQ queues
    5 # Visit http://localhost:15672 → Queues tab
    6 # Should see: collective-market-governance, geo-agronomy, etc.
    7 
    8 # Test Redis context
    9 docker exec -it kisaanmitra-redis redis-cli
   10 > GET context:farmer:test-123

  Database

   1 # Verify tables
   2 docker exec -it kisaanmitra-postgres psql -U postgres -d kisaanmitra -c "\dt"
   3 
   4 # Check FPO data
   5 docker exec -it kisaanmitra-postgres psql -U postgres -d kisaanmitra -c "SELECT * FROM fpos;"

  ---

  🤝 Contributing

  Development Guidelines

   1. Read IMPLEMENTATION_ROADMAP.md for detailed code examples
   2. Follow the agent pattern in backend/agents/base/agent.base.ts
   3. Test MCP communication before merging
   4. Update schema if adding new tables

  Priority Areas for Contribution

   1. CMGA Implementation (HIGH PRIORITY)
      - Portfolio optimizer
      - Investment Unit calculator
      - FPO dashboard UI

   2. MIA Integration (HIGH PRIORITY)
      - Agmarknet API wrapper
      - Price forecasting models

   3. GAA Models (MEDIUM PRIORITY)
      - Disease detection CNN training
      - Yield forecasting models

  ---

  📞 Support

  Questions?

   1. Check GETTING_STARTED.md (./GETTING_STARTED.md) for setup
   2. Review ASSESSMENT.md (./ASSESSMENT.md) for vision alignment
   3. See PROGRESS_SUMMARY.md (./PROGRESS_SUMMARY.md) for current status

  Issues?

   - Docker issues? Check docker-compose logs -f
   - Database issues? See GETTING_STARTED.md (./GETTING_STARTED.md#-troubleshooting)
   - MCP issues? Test health endpoint at http://localhost:3001/health

  ---

  📜 License

  MIT License - See LICENSE file for details

  ---

  🌾 Mission

  Empowering 86% of Indian farmers (smallholders) by transforming them from isolated risk-takers to shareholders in a digitally managed, collective agricultural 
  enterprise.

  Together, we can deliver the highest possible economic impact through collective market governance, autonomous field management, and comprehensive farmer empowerment.

  ---

  Built with ❤️ for Indian farmers
