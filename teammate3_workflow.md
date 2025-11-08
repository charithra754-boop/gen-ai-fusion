# Teammate 3 Workflow: The Frontend Developer (FPO Dashboard)

**Your Mission:** Build the user interface that brings the power of the CMGA and MIA to the farmers. You will create a new **FPO Dashboard**.

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
    └─────────┘          └─────────┘         │  YOU!   │
         │                    │               └─────────┘
    Publishes:           Publishes:               │
    MARKET_DATA_         - PORTFOLIO_         Listens to:
    UPDATED                UPDATED            - MARKET_DATA_UPDATED
                         - INVESTMENT_        - PORTFOLIO_UPDATED
                           UNITS_             - INVESTMENT_UNITS_
                           CALCULATED           CALCULATED
```

**Your Role in the Data Flow:**
1. **MIA (Team 2)** publishes market prices every 30s
2. **CMGA (Team 1)** publishes portfolio updates and investment units
3. **YOU (Frontend)** subscribe to ALL events → Update dashboard in real-time
4. **YOU display:**
   - Market price charts (from MIA)
   - Collective portfolio distribution (from CMGA)
   - Investment units table (from CMGA)

**Message Formats You Must Handle:**
```typescript
// From MIA - Market data updates:
{
  type: 'MARKET_DATA_UPDATED',
  payload: [
    { crop: 'Tomato', price: 2500, unit: 'quintal' },
    { crop: 'Onion', price: 1800, unit: 'quintal' },
    { crop: 'Potato', price: 2000, unit: 'quintal' }
  ]
}

// From CMGA - Portfolio updates:
{
  type: 'PORTFOLIO_UPDATED',
  payload: [
    { crop: 'Tomato', percentage: 40 },
    { crop: 'Onion', percentage: 30 },
    { crop: 'Potato', percentage: 30 }
  ]
}

// From CMGA - Investment units:
{
  type: 'INVESTMENT_UNITS_CALCULATED',
  payload: [
    { farmerId: '1', name: 'Farmer A', units: 120 },
    { farmerId: '2', name: 'Farmer B', units: 80 }
  ]
}
```

**CRITICAL:** Crop names MUST match! Use title case: "Tomato", "Onion", "Potato"

---

## 1. Understand the Frontend Structure

- **Read:** `README.md` and `ASSESSMENT.md` to understand the vision for the FPO Dashboard and the overall project.
- **Familiarize yourself with:**
    - `src/pages/` for existing page structures.
    - `src/components/` for existing components.
    - `src/components/ui/` for the Shadcn/UI components you can leverage.
    - `src/App.tsx` for routing.
    - `src/hooks/` for existing custom hooks.

## 2. Create the FPO Dashboard Page

- **Location:** `src/pages/FPODashboard.tsx`
- **Task:**
    1.  This file already exists. Your job is to populate it with the main layout and structure for the FPO Dashboard.
    2.  Use Shadcn/UI components (e.g., `Card`, `Table`, `Button`) to create a clean and responsive layout.
    3.  The dashboard should eventually display the collective portfolio, investment units, and market prices.

## 3. Build the Collective Portfolio View Component

- **Location:** `src/components/fpo/CollectivePortfolioView.tsx`
- **Task:**
    1.  Create this new component.
    2.  It should receive the collective crop portfolio data as props.
    3.  For the MVP, you can hardcode the display (e.g., "40% Tomato, 30% Onion, 30% Potato").
    4.  **Integrate a Chart:** Use the `chart` component from `src/components/ui/chart.tsx` to visualize the crop distribution (e.g., a pie chart). You'll need to pass the portfolio data to this chart component.

## 4. Build the Investment Units Table Component

- **Location:** `src/components/fpo/InvestmentUnitsTable.tsx`
- **Task:**
    1.  Create this new component.
    2.  It should receive a list of FPO members and their calculated Investment Units as props.
    3.  Use the `Table` component from `src/components/ui/table.tsx` to display this information in a clear, tabular format. Include columns for "Member Name" and "Investment Units".

## 5. Create the `useFPOData` Hook (MVP - Mock Data)

- **Location:** `src/hooks/useFPOData.ts`
- **Task:** For the MVP, start with mock data. Later, you'll connect to the message bus.
    1.  Create this new custom hook with the following structure:
        ```typescript
        import { useState, useEffect } from 'react';

        interface FPOData {
          collectivePortfolio: { crop: string; percentage: number }[];
          fpoMembers: { id: string; name: string; investmentUnits: number }[];
          marketPrices: { crop: string; price: number; unit: string }[];
        }

        export const useFPOData = (): FPOData => {
          const [data, setData] = useState<FPOData>({
            collectivePortfolio: [
              { crop: 'Tomato', percentage: 40 },
              { crop: 'Onion', percentage: 30 },
              { crop: 'Potato', percentage: 30 },
            ],
            fpoMembers: [
              { id: '1', name: 'Farmer A', investmentUnits: 120 },
              { id: '2', name: 'Farmer B', investmentUnits: 80 },
            ],
            marketPrices: [
              { crop: 'Tomato', price: 2500, unit: 'quintal' },
              { crop: 'Onion', price: 1800, unit: 'quintal' },
              { crop: 'Potato', price: 2000, unit: 'quintal' },
            ],
          });

          // TODO: Later, connect to MCP message bus here
          // useEffect(() => {
          //   const ws = connectToMessageBus();
          //   ws.on('MARKET_DATA_UPDATED', (payload) => {
          //     setData(prev => ({ ...prev, marketPrices: payload }));
          //   });
          //   ws.on('PORTFOLIO_UPDATED', (payload) => {
          //     setData(prev => ({ ...prev, collectivePortfolio: payload }));
          //   });
          //   return () => ws.disconnect();
          // }, []);

          return data;
        };
        ```
    2.  **IMPORTANT:** Use the exact crop names: "Tomato", "Onion", "Potato" (title case!)

## 5b. [FUTURE] Upgrade `useFPOData` to Connect to Message Bus

- **Task:** After the MVP works with mock data, connect to real-time events.
- **Implementation Steps:**
    1.  Install WebSocket client: `npm install socket.io-client`
    2.  Create a message bus client in `src/lib/messageBusClient.ts`:
        ```typescript
        import io from 'socket.io-client';

        export const connectToMessageBus = () => {
          const socket = io('http://localhost:3001'); // MCP bus WebSocket endpoint

          return {
            on: (event: string, callback: (data: any) => void) => {
              socket.on(event, callback);
            },
            disconnect: () => socket.disconnect(),
          };
        };
        ```
    3.  Update `useFPOData.ts` to use the client (uncomment the TODO section above)
    4.  **Test integration:** Work with Teammates 1 & 2 to ensure events are being received

## 6. Integrate Components into the Dashboard

- **Location:** `src/pages/FPODashboard.tsx`
- **Task:**
    1.  Import and use your `CollectivePortfolioView` and `InvestmentUnitsTable` components within the `FPODashboard` page.
    2.  Use the `useFPOData` hook to fetch the mock data and pass it down to these components as props.

## 7. Add Navigation to the Dashboard

- **Location:** `src/App.tsx` and `src/components/NavigationGrid.tsx`
- **Task:**
    1.  In `src/App.tsx`, add a new `Route` for `/fpo-dashboard`:
        ```tsx
        import { FPODashboard } from './pages/FPODashboard';

        // Inside your Routes:
        <Route path="/fpo-dashboard" element={<FPODashboard />} />
        ```
    2.  In `src/components/NavigationGrid.tsx`, add a new navigation card:
        ```tsx
        <NavigationCard
          title="FPO Dashboard"
          description="View collective portfolio and investment units"
          icon={<BarChart3 />}
          path="/fpo-dashboard"
        />
        ```

## 8. Dependencies on Other Teammates

**What you need from Teammate 2 (MIA):**
- For **real-time integration** (post-MVP), you need the MIA to publish `MARKET_DATA_UPDATED` events
- Market data format: `{ crop: string; price: number; unit: string }[]`
- **Coordination Point:** Test that you can receive WebSocket events from the message bus

**What you need from Teammate 1 (CMGA):**
- For **real-time integration** (post-MVP), you need CMGA to publish:
  - `PORTFOLIO_UPDATED` events
  - `INVESTMENT_UNITS_CALCULATED` events
- **Coordination Point:** Verify event formats match your TypeScript interfaces

**What you provide:**
- A working dashboard that visualizes the collective portfolio and investment units
- Mock data for initial testing (so other teammates can see what the UI will look like)
- Feedback on data format requirements

## How to Test Your Work

### Stage 1: UI Development (Isolated, No Backend)
1.  **Install dependencies:**
    ```bash
    npm install
    ```
2.  **Run the frontend:**
    ```bash
    npm run dev
    ```
3.  **Navigate to the dashboard:**
    - Open `http://localhost:8080` in your browser
    - Click on "FPO Dashboard" card (or go directly to `http://localhost:8080/fpo-dashboard`)
4.  **Verify the UI:**
    - ✓ Collective Portfolio chart displays (pie/bar chart showing Tomato 40%, Onion 30%, Potato 30%)
    - ✓ Investment Units table displays (showing Farmer A: 120 units, Farmer B: 80 units)
    - ✓ Market prices are shown (if you added a market price component)
    - ✓ All components are responsive and styled correctly
5.  **Check for errors:**
    - Open browser DevTools (F12) → Console tab
    - Ensure no React errors, TypeScript errors, or warnings

### Stage 2: Mock Data Testing
1.  **Modify mock data** in `useFPOData.ts`:
    - Change crop percentages (e.g., 50% Tomato, 25% Onion, 25% Potato)
    - Change investment units (e.g., add more farmers)
    - Change market prices
2.  **Refresh the dashboard** and verify:
    - ✓ Charts update correctly with new percentages
    - ✓ Table displays new farmers
    - ✓ Price changes are reflected

### Stage 3: Integration Testing (With Message Bus - Post-MVP)
1.  **Ensure backend is running:**
    ```bash
    docker-compose up -d
    ```
2.  **Update `useFPOData.ts`** to connect to the message bus (use the WebSocket code from section 5b)
3.  **Open the dashboard** and check browser DevTools → Network tab → WS (WebSocket)
4.  **Verify WebSocket connection:**
    - ✓ Connection to `ws://localhost:3001` established
    - ✓ Events are being received every 30 seconds
5.  **Monitor real-time updates:**
    - ✓ When MIA publishes market data, prices update on the dashboard
    - ✓ When CMGA publishes portfolio, the chart updates
    - ✓ When CMGA publishes investment units, the table updates
6.  **Check console logs:**
    ```bash
    docker-compose logs -f mcp-bus
    ```
    - Verify that events are being published by MIA and CMGA

### Stage 4: End-to-End Testing (With All Teammates)
1.  **Coordinate with Teammates 1 & 2:**
    - Ensure MIA is publishing market data every 30s
    - Ensure CMGA is processing and publishing portfolio updates
2.  **Verify the complete data flow on your dashboard:**
    ```
    MIA publishes → Dashboard updates prices
    CMGA publishes → Dashboard updates portfolio chart
    CMGA publishes → Dashboard updates investment units table
    ```
3.  **Test data consistency:**
    - Crop names should match across all displays
    - Numbers should make sense (portfolio percentages = 100%)
    - No missing or null data
4.  **Performance check:**
    - Dashboard should update smoothly without lag
    - No memory leaks (check DevTools → Performance tab)
    - Charts should animate nicely

### Stage 5: User Acceptance Testing
1.  **Simulate farmer workflows:**
    - Navigate from home page to FPO Dashboard
    - Check that all data is easy to understand
    - Verify that the UI is intuitive
2.  **Mobile responsiveness:**
    - Open DevTools → Toggle device toolbar
    - Test on different screen sizes (mobile, tablet, desktop)
    - Ensure charts and tables are readable on small screens

## Success Criteria

**MVP (Mock Data):**
- [ ] FPO Dashboard page is created and accessible via navigation
- [ ] `CollectivePortfolioView` component displays portfolio chart correctly
- [ ] `InvestmentUnitsTable` component displays member data in a table
- [ ] `useFPOData` hook returns properly formatted mock data
- [ ] All components use Shadcn/UI components (Card, Table, Chart)
- [ ] Dashboard is responsive and looks good on mobile/desktop
- [ ] No console errors or TypeScript errors
- [ ] Navigation from home page works correctly

**Post-MVP (Real-time Integration):**
- [ ] WebSocket connection to message bus is established
- [ ] Dashboard receives and displays `MARKET_DATA_UPDATED` events
- [ ] Dashboard receives and displays `PORTFOLIO_UPDATED` events
- [ ] Dashboard receives and displays `INVESTMENT_UNITS_CALCULATED` events
- [ ] Real-time updates work smoothly without page refresh
- [ ] Data from MIA and CMGA matches the dashboard display
- [ ] Crop names are consistent across all components
- [ ] Performance is good (no lag during updates)