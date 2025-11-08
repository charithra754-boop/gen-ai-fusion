# Teammate 1 Workflow: The Backend Architect (CMGA & MCP)

**Your Mission:** Bring the **Collective Market Governance Agent (CMGA)** to life. You will build the engine that allows farmers to act as a collective.

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
    └─────────┘          └─────────┘         └─────────┘
         │                    │                    │
    Publishes:           Publishes:           Listens to:
    MARKET_DATA_         PORTFOLIO_           - MARKET_DATA_UPDATED
    UPDATED              UPDATED              - PORTFOLIO_UPDATED
                                              - INVESTMENT_UNITS_CALCULATED
```

**Data Flow Sequence:**
1. **MIA** fetches market prices every 30s → Publishes `MARKET_DATA_UPDATED`
2. **CMGA** (YOUR AGENT) listens to market data → Calculates optimal portfolio → Publishes `PORTFOLIO_UPDATED`
3. **CMGA** calculates investment units for members → Publishes `INVESTMENT_UNITS_CALCULATED`
4. **Frontend** listens to all events → Updates dashboard in real-time

**Message Formats You Must Use:**
```typescript
// Listen for this from MIA:
{
  type: 'MARKET_DATA_UPDATED',
  payload: { crop: string; price: number; unit: string }[]
}

// Publish this from CMGA:
{
  type: 'PORTFOLIO_UPDATED',
  payload: { crop: string; percentage: number }[]
}

// Publish this from CMGA:
{
  type: 'INVESTMENT_UNITS_CALCULATED',
  payload: { farmerId: string; name: string; units: number }[]
}
```

---

## 1. Understand the Core Logic

- **Read:** `README.md` and `ASSESSMENT.md` to understand the vision for CMGA.
- **Familiarize yourself with the MCP:** Look at `backend/mcp-bus/src/bus/message-bus.ts` to see how agents are intended to communicate.

## 2. Implement the CMGA Agent

- **Location:** `backend/agents/cmga/cmga.agent.ts`
- **Task:** This file already has a basic structure. You need to:
    1.  Implement the `handleEvent` method. This will be the core of your agent. It should process incoming messages. For now, you can log the messages to the console.
    2.  Implement the `start` method. This should register the agent with the message bus and start any internal processes (like a timer to periodically check for new data).
    3.  Use the `BaseAgent` class from `backend/agents/base/agent.base.ts` as a reference.

## 3. Build the Investment Unit Calculator

- **Location:** `backend/agents/cmga/investment-calculator.ts`
- **Task:**
    1.  Implement the `calculateInvestmentUnits` function.
    2.  The formula is in the `README.md`: `Units = 0.4 * land + 0.2 * inputs + 0.15 * labor + 0.1 * water + 0.1 * soil + 0.05 * equipment`.
    3.  You can create a mock function to provide input data (e.g., a farmer's land size, labor hours).
    4.  The function should take a farmer's data and return the calculated investment units.

## 4. Create a Basic Portfolio Optimizer

- **Location:** `backend/agents/cmga/portfolio-optimizer.ts`
- **Task:**
    1.  Implement a function called `optimizePortfolio`.
    2.  For the MVP, this will be a simple, rule-based function. It does not need to involve complex AI.
    3.  Hardcode a recommended crop portfolio, for example: `{ "Tomato": 0.4, "Onion": 0.3, "Potato": 0.3 }`.
    4.  The function should return this portfolio object.

## 5. Integrate with the Message Bus (MCP)

- **Task:** Your final step is to make the CMGA communicate with other agents.
    1.  In `cmga.agent.ts`, import the `messageBus` from `backend/mcp-bus/src/bus/message-bus.ts`.
    2.  **Subscribe to MIA's market data:**
        ```typescript
        this.messageBus.subscribe('MARKET_DATA_UPDATED', (message) => {
          // Store the market data
          this.latestMarketData = message.payload;
          // Trigger portfolio optimization
          this.optimizeAndPublish();
        });
        ```
    3.  **Publish portfolio updates:**
        ```typescript
        const portfolio = this.optimizePortfolio(this.latestMarketData);
        this.messageBus.publish({
          type: 'PORTFOLIO_UPDATED',
          payload: portfolio
        });
        ```
    4.  **Publish investment units:**
        ```typescript
        const units = this.calculateInvestmentUnits(farmerData);
        this.messageBus.publish({
          type: 'INVESTMENT_UNITS_CALCULATED',
          payload: units
        });
        ```

## 6. Dependencies on Other Teammates

**What you need from Teammate 2 (MIA):**
- The MIA must be publishing `MARKET_DATA_UPDATED` events for your CMGA to work
- The database schema (especially `fpos`, `fpo_members`, `investment_units` tables) must be set up
- **Coordination Point:** Agree on the exact market data format (crop names must match!)

**What Teammate 3 (Frontend) needs from you:**
- Your CMGA must publish `PORTFOLIO_UPDATED` and `INVESTMENT_UNITS_CALCULATED` events
- Event formats must match the interface definitions in `src/hooks/useFPOData.ts`
- **Coordination Point:** Test message formats together before final integration

## How to Test Your Work

### Stage 1: Isolated Testing (No Dependencies)
1.  **Run just the message bus:** Use `docker-compose up -d rabbitmq`.
2.  **Run your agent:** Start your CMGA agent separately.
3.  **Mock the MIA:** Publish test messages to the bus to simulate MIA:
    ```bash
    # In RabbitMQ console or using a test script
    Publish: { type: 'MARKET_DATA_UPDATED', payload: [...] }
    ```
4.  **Verify:** Check that your CMGA receives the message and publishes `PORTFOLIO_UPDATED`.

### Stage 2: Integration Testing (With Other Teammates)
1.  **Run the full system:** Use `docker-compose up -d`.
2.  **Check the logs:**
    - `docker-compose logs -f mcp-bus` - See all agent registrations and messages
    - `docker-compose logs -f cmga` - See your specific agent output
3.  **Use the RabbitMQ console:** Go to `http://localhost:15672` (user: `guest`, pass: `guest`)
    - Check the `kisaanmitra.events` exchange
    - Verify messages are being routed correctly
4.  **Verify the complete flow:**
    - ✓ MIA publishes market data every 30s
    - ✓ Your CMGA receives it and publishes portfolio updates
    - ✓ Frontend dashboard shows the portfolio (coordinate with Teammate 3)

### Stage 3: End-to-End Testing
1.  **Test with Teammates 2 & 3:**
    - Teammate 2's MIA should be running and publishing real data
    - Your CMGA should be processing it
    - Teammate 3's dashboard should be updating in real-time
2.  **Verify data consistency:** The crop names in MIA's data, your portfolio, and the frontend should all match!

## Success Criteria

- [ ] CMGA agent starts and registers with the message bus
- [ ] CMGA listens to `MARKET_DATA_UPDATED` events
- [ ] Investment units are calculated correctly using the formula
- [ ] Portfolio optimization function returns reasonable crop allocations
- [ ] CMGA publishes `PORTFOLIO_UPDATED` events with correct format
- [ ] CMGA publishes `INVESTMENT_UNITS_CALCULATED` events
- [ ] All events are visible in RabbitMQ console
- [ ] Frontend (Teammate 3) can consume your events successfully
