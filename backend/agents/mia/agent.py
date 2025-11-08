"""
Market Intelligence Agent (MIA)
Built using Google Agent Development Kit (ADK)

Capabilities:
- Mandi price tracking and analysis
- Demand forecasting for crops
- Price prediction using historical data
- Market trend analysis
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Import tools
from .tools import (
    get_mandi_prices,
    forecast_demand,
    predict_price,
    analyze_market_trends,
    get_historical_prices,
    compare_regional_prices
)


class MarketIntelligenceAgent:
    """
    Market Intelligence Agent using Google ADK

    Provides market intelligence including:
    - Real-time mandi price tracking
    - Demand forecasting
    - Price predictions
    - Market trend analysis
    """

    def __init__(self, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize the Market Intelligence Agent

        Args:
            model: LLM model to use (default: gemini-2.0-flash-exp)
        """
        self.model = model

        # Define agent instructions
        self.instructions = """
You are the Market Intelligence Agent (MIA) for KisaanMitra, a platform empowering Indian farmers.

Your responsibilities:
1. **Mandi Price Tracking**: Monitor and report current mandi prices for various crops across regions
2. **Demand Forecasting**: Predict crop demand based on historical data, seasonal patterns, and market trends
3. **Price Prediction**: Forecast future prices to help farmers make informed planting and selling decisions
4. **Market Analysis**: Analyze market trends, identify opportunities, and alert about price volatility

Guidelines:
- Always provide prices in Indian Rupees (₹)
- Consider regional variations in pricing
- Factor in seasonal patterns for accurate forecasting
- Highlight market opportunities for collective bargaining
- Alert farmers about significant price changes
- Support FPOs (Farmer Producer Organizations) with market intelligence for collective planning

When responding:
- Be concise and actionable
- Provide data-driven insights
- Include confidence levels for predictions
- Suggest optimal selling windows when possible
"""

        # Create the LLM agent with tools
        self.agent = LlmAgent(
            model=self.model,
            name="market_intelligence_agent",
            description="Agent specialized in market intelligence for agricultural commodities in India",
            instruction=self.instructions,
            tools=[
                get_mandi_prices,
                forecast_demand,
                predict_price,
                analyze_market_trends,
                get_historical_prices,
                compare_regional_prices
            ]
        )

        # Initialize session service and runner
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            session_service=self.session_service
        )

    async def query(self, user_query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Query the Market Intelligence Agent

        Args:
            user_query: User's question or request
            context: Optional context (farmerId, fpoId, location, etc.)

        Returns:
            Agent's response
        """
        # Create session with context
        session_id = f"session_{datetime.now().timestamp()}"

        if context:
            # Add context to the query
            context_str = f"\nContext: {json.dumps(context)}\n"
            full_query = context_str + user_query
        else:
            full_query = user_query

        # Run the agent
        result_stream = self.runner.run(
            session_id=session_id,
            user_message=full_query
        )

        # Collect response
        response = ""
        async for event in result_stream:
            if hasattr(event, 'text'):
                response += event.text

        return response

    def query_sync(self, user_query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Synchronous wrapper for query method

        Args:
            user_query: User's question or request
            context: Optional context

        Returns:
            Agent's response
        """
        return asyncio.run(self.query(user_query, context))

    async def get_market_insights(
        self,
        crop: str,
        location: Optional[str] = None,
        fpo_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive market insights for a specific crop

        Args:
            crop: Crop name (e.g., "tomato", "onion")
            location: Location/region
            fpo_id: FPO ID for context

        Returns:
            Market insights including prices, forecasts, and recommendations
        """
        context = {
            "crop": crop,
            "location": location,
            "fpo_id": fpo_id,
            "timestamp": datetime.now().isoformat()
        }

        query = f"""
Provide comprehensive market intelligence for {crop} in {location if location else 'India'}.

Include:
1. Current mandi prices across major markets
2. Price trend analysis (last 30 days)
3. Demand forecast for next 3 months
4. Price prediction for next 30 days
5. Recommended selling strategy
6. Market opportunities for collective selling
"""

        response = await self.query(query, context)

        return {
            "crop": crop,
            "location": location,
            "timestamp": datetime.now().isoformat(),
            "insights": response
        }

    async def forecast_collective_portfolio(
        self,
        portfolio: Dict[str, float],
        location: str,
        fpo_id: str
    ) -> Dict[str, Any]:
        """
        Forecast market prospects for an FPO's collective crop portfolio

        Args:
            portfolio: Dict of crop -> acreage (e.g., {"tomato": 40, "onion": 30})
            location: FPO location
            fpo_id: FPO identifier

        Returns:
            Portfolio-level market forecast
        """
        context = {
            "portfolio": portfolio,
            "location": location,
            "fpo_id": fpo_id,
            "timestamp": datetime.now().isoformat()
        }

        crops = ", ".join(portfolio.keys())
        query = f"""
Analyze the market prospects for an FPO's collective portfolio:
{json.dumps(portfolio, indent=2)}

Location: {location}

Provide:
1. Expected revenue per crop
2. Market risk assessment
3. Diversification strategy recommendations
4. Optimal harvest and selling timeline
5. Collective bargaining opportunities
6. Total expected revenue range
"""

        response = await self.query(query, context)

        return {
            "fpo_id": fpo_id,
            "portfolio": portfolio,
            "location": location,
            "forecast": response,
            "timestamp": datetime.now().isoformat()
        }


# Convenience function to create and use the agent
def create_market_intelligence_agent(model: str = "gemini-2.0-flash-exp") -> MarketIntelligenceAgent:
    """
    Factory function to create Market Intelligence Agent

    Args:
        model: LLM model to use

    Returns:
        MarketIntelligenceAgent instance
    """
    return MarketIntelligenceAgent(model=model)
