# Teammate 2 Workflow: The Data & AI Specialist (MIA & Database)

**Your Mission:** Connect the KisaanMitra platform to the real world by implementing the **Market Intelligence Agent (MIA)** and setting up the database to support it.

---

## SYSTEM ARCHITECTURE OVERVIEW - How All Agents Work Together

```
┌─────────────────────────────────────────────────────────────┐
│                    MESSAGE BUS (RabbitMQ)                   │
│                  Central Communication Hub                   │
└─────────────────────────────────────────────────────────────┘
         ↑                    ↑                    ↓
         │                    │                    │
    ┌────┴────┐          ┌────┴────┐         ┌────┴────┐
    │   MIA   │          │  CMGA   │         │Frontend │
    │(Team 2) │          │(Team 1) │         │(Team 3) │
    │  YOU!   │          └─────────┘         └─────────┘
    └─────────┘               │                    │
         │               Listens to:           Listens to:
    Publishes:           - MARKET_DATA_        - MARKET_DATA_UPDATED
    MARKET_DATA_           UPDATED             - PORTFOLIO_UPDATED
    UPDATED                                    - INVESTMENT_UNITS_CALCULATED
```

**Your Role in the Data Flow:**
1. **YOU (MIA)** fetch market prices every 30s → Publish `MARKET_DATA_UPDATED`
2. **CMGA** listens to YOUR data → Calculates optimal portfolio → Publishes `PORTFOLIO_UPDATED`
3. **Frontend** listens to YOUR data → Updates market price charts in real-time
4. **PostgreSQL** stores all market data → Provides historical analysis capability

**Message Format You Must Publish:**
```typescript
// Publish this from MIA every 30 seconds:
{
  type: 'MARKET_DATA_UPDATED',
  payload: [
    { crop: 'Tomato', price: 2500, unit: 'quintal', marketName: 'Delhi Mandi', date: '2025-11-08' },
    { crop: 'Onion', price: 1800, unit: 'quintal', marketName: 'Delhi Mandi', date: '2025-11-08' },
    { crop: 'Potato', price: 2000, unit: 'quintal', marketName: 'Delhi Mandi', date: '2025-11-08' }
  ]
}
```

**CRITICAL:** Crop names MUST be consistent! Coordinate with Teammate 1 to ensure:
- Same spelling: "Tomato" not "tomato" or "Tomatoes"
- Same format: Use title case for all crop names
- Same crop list: All three teams use the same crops (Tomato, Onion, Potato for MVP)

---

## 1. Understand the Data Layer

- **Read:** `README.md` and `ASSESSMENT.md` to understand the vision for the MIA and the required database schema.
- **Examine:** `backend/schema/extended_schema.sql`. This file contains the full database schema for the project. You will need to ensure the tables you need are included and correct.
- **Review:** `docker-compose.yml` to see how the PostgreSQL database is configured and started.

## 2. Create the Market Intelligence Agent (MIA)

- **Location:** `backend/agents/mia/`
- **Task:**
    1.  Create a new file: `backend/agents/mia/mia.agent.ts`.
    2.  Implement a basic agent structure, similar to the `BaseAgent` in `backend/agents/base/agent.base.ts`.
    3.  The main purpose of this agent is to fetch and broadcast market data.

## 3. Implement a Mock Market Data API

- **Task:** For the MVP, you will simulate a real-world market data feed.
    1.  Create a new file: `backend/agents/mia/mock-market-data.ts`.
    2.  In this file, create a function that returns a static array of crop prices. For example:
        ```typescript
        export const getMockMarketPrices = () => {
          return [
            { crop: 'Tomato', price: 2500, unit: 'quintal' },
            { crop: 'Onion', price: 1800, unit: 'quintal' },
            { crop: 'Potato', price: 2000, unit: 'quintal' },
          ];
        };
        ```
    3.  Your `mia.agent.ts` will call this function to get its data.

## 4. Update and Verify the Database Schema

- **Location:** `backend/schema/extended_schema.sql`
- **Task:**
    1.  Open the `extended_schema.sql` file and ensure the following tables are defined and not commented out:
        - `fpos`
        - `fpo_members`
        - `investment_units`
        - `collective_portfolios`
        - `mandi_prices`
    2.  The `mandi_prices` table is your highest priority. It should have columns like `crop_name`, `price`, `market_name`, and `date`.

## 5. Ensure the Schema is Deployed

- **Task:** You need to make sure that when the project starts, the database is created with your new tables.
    1.  Check the `docker-compose.yml` file. Look for the `postgres` service definition.
    2.  Verify that the `extended_schema.sql` file is being copied into the `docker-entrypoint-initdb.d` directory of the container. This is what makes Docker run the script on startup.

## 6. Publish Market Data via the Message Bus (MCP)

- **Task:** The MIA needs to share its data with the rest of the system.
    1.  In `mia.agent.ts`, import the `messageBus` from `backend/mcp-bus/src/bus/message-bus.ts`.
    2.  Set up a timer using `setInterval` to fetch and publish data every 30 seconds:
        ```typescript
        import { messageBus } from '../../mcp-bus/src/bus/message-bus';
        import { getMockMarketPrices } from './mock-market-data';

        export class MIAAgent extends BaseAgent {
          start() {
            console.log('MIA Agent starting...');

            // Fetch and publish immediately
            this.fetchAndPublish();

            // Then every 30 seconds
            setInterval(() => {
              this.fetchAndPublish();
            }, 30000);
          }

          private fetchAndPublish() {
            const marketData = getMockMarketPrices();

            // Store in database (optional for MVP)
            // await this.storeInDatabase(marketData);

            // Publish to message bus
            messageBus.publish({
              type: 'MARKET_DATA_UPDATED',
              payload: marketData
            });

            console.log('Published market data:', marketData);
          }
        }
        ```
    3.  **IMPORTANT:** Make sure your mock data uses the EXACT crop names agreed upon:
        ```typescript
        export const getMockMarketPrices = () => {
          return [
            { crop: 'Tomato', price: 2500, unit: 'quintal', marketName: 'Delhi Mandi', date: new Date().toISOString() },
            { crop: 'Onion', price: 1800, unit: 'quintal', marketName: 'Delhi Mandi', date: new Date().toISOString() },
            { crop: 'Potato', price: 2000, unit: 'quintal', marketName: 'Delhi Mandi', date: new Date().toISOString() },
          ];
        };
        ```

## 7. Optional: Store Market Data in Database

- **Task:** For historical tracking (can be done after MVP)
    1.  After fetching market data, insert it into the `mandi_prices` table:
        ```typescript
        private async storeInDatabase(marketData) {
          // Use pg client to insert into mandi_prices table
          for (const data of marketData) {
            await db.query(
              'INSERT INTO mandi_prices (crop_name, price, market_name, date) VALUES ($1, $2, $3, $4)',
              [data.crop, data.price, data.marketName, data.date]
            );
          }
        }
        ```

## 8. Dependencies on Other Teammates

**What Teammate 1 (CMGA) needs from you:**
- Your MIA must publish `MARKET_DATA_UPDATED` events every 30 seconds
- Crop names must match exactly (Tomato, Onion, Potato)
- Data format must include: `crop`, `price`, `unit`
- **Coordination Point:** Test together that CMGA receives your messages!

**What Teammate 3 (Frontend) needs from you:**
- Your market data will be displayed in price charts
- The `useFPOData` hook will eventually connect to your MIA events
- **Coordination Point:** Ensure data format matches frontend expectations

**What you need from others:**
- Message bus (RabbitMQ) must be running - this is in `docker-compose.yml`
- Database (PostgreSQL) must be running - also in `docker-compose.yml`

## How to Test Your Work

### Stage 1: Database Setup Testing
1.  **Run the database:** `docker-compose up -d postgres`
2.  **Connect to the database:**
    ```bash
    docker exec -it kisaanmitra-postgres psql -U postgres -d kisaanmitra
    ```
3.  **Verify tables exist:**
    ```sql
    \dt
    -- You should see: fpos, fpo_members, investment_units, collective_portfolios, mandi_prices
    ```
4.  **Check schema:**
    ```sql
    \d mandi_prices
    -- Verify columns: id, crop_name, price, market_name, date, created_at
    ```

### Stage 2: Isolated Agent Testing
1.  **Run the message bus:** `docker-compose up -d rabbitmq`
2.  **Run your MIA agent:** Start it separately to test
3.  **Check console output:** You should see "Published market data" every 30 seconds
4.  **Verify RabbitMQ:** Go to `http://localhost:15672` (user: `guest`, pass: `guest`)
    - Check the `kisaanmitra.events` exchange
    - You should see messages appearing every 30 seconds

### Stage 3: Integration Testing (With Other Teammates)
1.  **Run the full system:** `docker-compose up -d`
2.  **Check all agent logs:**
    ```bash
    docker-compose logs -f mcp-bus
    docker-compose logs -f mia
    ```
3.  **Verify the complete flow:**
    - ✓ Your MIA publishes market data every 30s
    - ✓ Teammate 1's CMGA receives it and logs processing
    - ✓ Teammate 3's frontend dashboard shows market prices
4.  **Test data consistency:**
    - Open RabbitMQ console and check message payloads
    - Verify crop names match across all systems
    - Check timestamps are current

### Stage 4: End-to-End Testing
1.  **Coordinate with both teammates:**
    - Your MIA should be publishing data
    - CMGA should be consuming it and generating portfolios
    - Frontend should be displaying both market prices and portfolios
2.  **Verify message chain:**
    ```
    MIA publishes → CMGA receives → CMGA publishes → Frontend receives
    ```

## Success Criteria

- [ ] PostgreSQL database is running with all required tables
- [ ] `mandi_prices` table has correct schema
- [ ] MIA agent starts and registers with the message bus
- [ ] MIA fetches mock market data successfully
- [ ] MIA publishes `MARKET_DATA_UPDATED` events every 30 seconds
- [ ] Events are visible in RabbitMQ console
- [ ] Crop names are consistent (Tomato, Onion, Potato)
- [ ] CMGA (Teammate 1) successfully receives your messages
- [ ] Frontend (Teammate 3) can consume and display your market data
- [ ] No errors in agent logs
