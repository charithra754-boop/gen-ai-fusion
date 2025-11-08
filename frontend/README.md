# KisaanMitra Frontend

React + TypeScript frontend for the KisaanMitra Multi-Agent Agricultural Empowerment Platform.

## Tech Stack

- **Framework**: React 18.3.1
- **Language**: TypeScript
- **Build Tool**: Vite 5.4.1
- **Styling**: Tailwind CSS 3.4.11
- **UI Components**: Shadcn/UI
- **Routing**: React Router DOM 6.26.2
- **State Management**: TanStack Query 5.56.2
- **Backend**: Supabase (PostgreSQL, Auth, Edge Functions)

## Project Structure

```
frontend/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── ui/            # Shadcn/UI components
│   │   ├── fpo/           # FPO-specific components
│   │   ├── SmartAIAssistant.tsx
│   │   ├── DatabaseWeatherWidget.tsx
│   │   └── ...
│   ├── pages/             # Page components
│   │   ├── Index.tsx      # Home page
│   │   ├── SoilAnalysis.tsx
│   │   ├── FPODashboard.tsx
│   │   └── NotFound.tsx
│   ├── hooks/             # Custom React hooks
│   │   ├── useLanguage.tsx
│   │   ├── useAgriculturalData.ts
│   │   └── useFPOData.ts
│   ├── integrations/      # Third-party integrations
│   ├── lib/              # Utility functions
│   └── App.tsx           # Main app component
├── public/               # Static assets
│   └── favicon.svg
├── index.html           # Entry HTML
└── vite.config.ts       # Vite configuration
```

## Features

### Multilingual Support
- **Languages**: English, Kannada, Hindi
- **Voice Interface**: Speech recognition and synthesis
- **SMS/IVR**: Planned integration

### Core Components

1. **SmartAIAssistant** - Voice-enabled AI assistant referencing 7 specialized agents
2. **SoilAnalysisForm** - AI-powered crop recommendations (GAA agent)
3. **FPODashboard** - Collective farming management (CMGA agent)
4. **DatabaseWeatherWidget** - Real-time weather data (CRA agent)
5. **DatabaseCropRecommendations** - Market intelligence (MIA agent)

## Multi-Agent Integration

The frontend interfaces with 7 AI agents:

1. **CMGA** - Collective Market Governance Agent
2. **MIA** - Market Intelligence Agent
3. **GAA** - Geo-Agronomy Agent
4. **CRA** - Climate & Resource Agent
5. **FIA** - Financial Inclusion Agent
6. **LIA** - Logistics Infrastructure Agent
7. **HIA** - Human Interface Agent

## Development

### Install Dependencies
```bash
npm install
```

### Run Development Server
```bash
npm run dev
```
Access at http://localhost:8080

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## UI Components

Built with Shadcn/UI (40+ components):
- Buttons, Cards, Forms
- Dialogs, Dropdowns, Tabs
- Tables, Charts (Recharts)
- Toast notifications (Sonner)
- And more...

## Routing

- `/` - Home dashboard
- `/soil-analysis` - Soil testing and crop recommendations
- `/fpo/:fpoId` - FPO dashboard (planned)
- `*` - 404 Not Found

## State Management

- **TanStack Query** for server state (caching, refetching)
- **React Context** for language preferences
- **Local Storage** for persistent settings

## Styling

- **Tailwind CSS** for utility-first styling
- **CSS Variables** for theming
- **Dark Mode** support (via next-themes)
- **Responsive Design** (mobile-first)

## Testing

```bash
npm run test        # Run tests (planned)
npm run lint        # ESLint
```

## Contributing

1. Follow existing code structure
2. Use TypeScript for type safety
3. Test multilingual features
4. Maintain responsive design
5. Document complex components

## License

MIT License - See LICENSE file for details

---

Built with ❤️ for Indian farmers by the KisaanMitra team
