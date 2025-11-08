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
  Farmers friends? Yes we are ^_^

KisaanMitra is a fully implemented, production-ready **Multi-Agent System (MAS)** designed to serve the complete agricultural value chain. This guide provides the quick, necessary steps to deploy the entire system, including the **7 specialized AI agents**, message bus, database, and multilingual frontend, using Docker Compose.

The **entire stack is containerized**, ensuring a quick, consistent, and reliable deployment across different environments.

-----

## 🛠️ Prerequisites

To deploy the KisaanMitra MAS, you need the following tools installed on your system:

1.  **Docker & Docker Compose:** Essential for orchestrating the multi-container environment (Agents, Database, Message Queue, etc.). Docker Compose is typically included with Docker Desktop for Windows and Mac.
2.  **Node.js 18+:** Required for running the local frontend development server if you choose the MVP-Only setup (Option 2).
3.  **Git:** Used for cloning the project repository.

-----

## 🚀 Deployment Option 1: Full Multi-Agent System (Recommended)

This is the fastest path to launching the entire **7-Agent architecture** with all its supporting services (PostgreSQL, Redis, RabbitMQ) and the frontend.

### Step 1: Clone the Repository

```bash
# Clone the KisaanMitra repository
git clone [repository_url] KisaanMitra
cd KisaanMitra
```

### Step 2: Set Up Environment Variables

While the core services are managed via `docker-compose.yml`, the agents often require keys for external APIs (e.g., Satellite data, Agmarknet, Banking APIs).

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your required API keys (Optional, but recommended for full agent functionality)
# nano .env 
```

### Step 3: Launch the System

The `docker-compose up -d` command builds the necessary images (for the agents and frontend) and starts all services in detached mode.

```bash
# 1. Start all services (PostgreSQL, Redis, RabbitMQ, MCP Bus, 7 Agents, Frontend)
docker-compose up -d

# 2. Check the status of all running containers
docker-compose ps
```

### Step 4: Database Finalization

Ensure the extended schema, which supports all 7 agents' data requirements, is applied to the PostgreSQL database.

```bash
# Connect to the PostgreSQL container
docker exec -it kisaanmitra-postgres psql -U postgres -d kisaanmitra

# Run the extended schema script
\i /docker-entrypoint-initdb.d/extended_schema.sql

# Verify all tables (fpos, investment_units, mandi_prices, etc.) are present
\dt

# Exit PostgreSQL
\q
```

### Access Points

| Service | Access URL / Command | Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | **http://localhost:8080** | Access the main dashboard and the HIA Voice Assistant. |
| **RabbitMQ** | **http://localhost:15672** (admin/admin) | Monitor the agent communication queues (MCP). |
| **MCP Health** | `curl http://localhost:3001/health` | Verify the Multi-Agent Bus is operational. |

-----

## 🚀 Deployment Option 2: MVP Only (Local Frontend)

This option is for quickly testing the user interface (UI), including the **multilingual voice assistant**, without running the full agent backend stack locally. You will need to rely on a separate Supabase/PostgreSQL instance.

### Step 1 & 2: Clone and Install

```bash
# 1. Clone the repository and navigate into the directory
git clone [repository_url] KisaanMitra
cd KisaanMitra

# 2. Install Node dependencies for the frontend
npm install
```

### Step 3: Configure and Run

```bash
# 1. Copy the example environment file
cp .env.example .env

# 2. Edit .env with your external Supabase credentials for the database and Auth
# nano .env

# 3. Run the development server
npm run dev
```

### Access Point

  * **Frontend UI:** **http://localhost:8080**

The deployment instructions for a full-stack system like this often require advanced understanding of container orchestration. You may find the video, [Ultimate Docker Compose Tutorial](https://www.youtube.com/watch?v=SXwC9fSwct8), helpful for understanding the underlying commands like `docker-compose up -d`.
http://googleusercontent.com/youtube_content/0

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
