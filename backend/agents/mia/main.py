#!/usr/bin/env python3
"""
Market Intelligence Agent (MIA) - Google ADK Implementation
Provides real-time market data, price forecasting, and agricultural market intelligence
"""

import json
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PriceData:
    """Market price data structure"""
    crop: str
    variety: str
    mandi: str
    district: str
    state: str
    min_price: float
    max_price: float
    modal_price: float
    arrival_quantity: float
    price_date: str
    source: str = "mock_data"

@dataclass
class ForecastData:
    """Price forecast data structure"""
    crop: str
    region: str
    forecasts: List[Dict[str, Any]]
    confidence: float
    model_accuracy: float
    generated_at: str

@dataclass
class MarketTrend:
    """Market trend analysis structure"""
    crop: str
    region: str
    trend_direction: str  # bullish, bearish, stable
    price_change_percent: float
    volatility: float
    seasonal_pattern: str
    analysis_period: str
    key_insights: List[str]

class MIAAgent:
    """Market Intelligence Agent implementation"""
    
    def __init__(self):
        self.name = "Market Intelligence Agent"
        self.version = "1.0.0"
        self.supported_languages = ["en", "hi", "kn"]
        self.mock_data = self._initialize_mock_data()
        logger.info(f"Initialized {self.name} v{self.version}")
    
    def _initialize_mock_data(self) -> Dict[str, Any]:
        """Initialize mock market data for demonstration"""
        return {
            "current_prices": {
                "tomato": PriceData(
                    crop="tomato", variety="hybrid", mandi="Kolar", district="Kolar", 
                    state="Karnataka", min_price=1200, max_price=1800, modal_price=1500,
                    arrival_quantity=45.5, price_date=datetime.now().strftime("%Y-%m-%d")
                ),
                "onion": PriceData(
                    crop="onion", variety="red", mandi="Bangalore", district="Bangalore Urban",
                    state="Karnataka", min_price=2000, max_price=2800, modal_price=2400,
                    arrival_quantity=78.2, price_date=datetime.now().strftime("%Y-%m-%d")
                ),
                "potato": PriceData(
                    crop="potato", variety="local", mandi="Hassan", district="Hassan",
                    state="Karnataka", min_price=800, max_price=1200, modal_price=1000,
                    arrival_quantity=120.3, price_date=datetime.now().strftime("%Y-%m-%d")
                ),
                "rice": PriceData(
                    crop="rice", variety="basmati", mandi="Mandya", district="Mandya",
                    state="Karnataka", min_price=3500, max_price=4200, modal_price=3850,
                    arrival_quantity=95.7, price_date=datetime.now().strftime("%Y-%m-%d")
                )
            },
            "seasonal_patterns": {
                "tomato": {"peak_months": ["Dec", "Jan", "Feb"], "low_months": ["Jun", "Jul", "Aug"]},
                "onion": {"peak_months": ["Mar", "Apr", "May"], "low_months": ["Oct", "Nov", "Dec"]},
                "potato": {"peak_months": ["Jan", "Feb", "Mar"], "low_months": ["Jul", "Aug", "Sep"]},
                "rice": {"peak_months": ["Oct", "Nov", "Dec"], "low_months": ["Apr", "May", "Jun"]}
            }
        }
    
    def get_current_prices(self, crops: List[str], region: Optional[str] = None, 
                          language: str = "en") -> Dict[str, Any]:
        """Get current mandi prices for specified crops"""
        logger.info(f"Getting current prices for crops: {crops}, region: {region}, language: {language}")
        
        try:
            results = []
            for crop in crops:
                crop_lower = crop.lower()
                if crop_lower in self.mock_data["current_prices"]:
                    price_data = self.mock_data["current_prices"][crop_lower]
                    # Add some realistic variation
                    variation = random.uniform(-0.1, 0.1)
                    price_data.modal_price = int(price_data.modal_price * (1 + variation))
                    price_data.min_price = int(price_data.modal_price * 0.8)
                    price_data.max_price = int(price_data.modal_price * 1.2)
                    results.append(asdict(price_data))
                else:
                    # Generate mock data for unknown crops
                    base_price = random.randint(500, 3000)
                    results.append(asdict(PriceData(
                        crop=crop, variety="local", mandi="Local Market", 
                        district="Unknown", state=region or "Karnataka",
                        min_price=int(base_price * 0.8), max_price=int(base_price * 1.2),
                        modal_price=base_price, arrival_quantity=random.uniform(20, 100),
                        price_date=datetime.now().strftime("%Y-%m-%d")
                    )))
            
            response = {
                "success": True,
                "data": results,
                "timestamp": datetime.now().isoformat(),
                "message": self._translate_message("Current market prices retrieved successfully", language)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting current prices: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": self._translate_message("Failed to retrieve current prices", language)
            }
    
    def price_forecast(self, crops: List[str], days: int = 30, region: Optional[str] = None,
                      language: str = "en") -> Dict[str, Any]:
        """Generate price forecasts for crops"""
        logger.info(f"Generating price forecast for crops: {crops}, days: {days}, region: {region}")
        
        try:
            forecasts = []
            for crop in crops:
                crop_lower = crop.lower()
                base_price = 1500  # Default base price
                
                if crop_lower in self.mock_data["current_prices"]:
                    base_price = self.mock_data["current_prices"][crop_lower].modal_price
                
                # Generate forecast data points
                forecast_points = []
                current_price = base_price
                
                for i in range(days):
                    # Add realistic price movement with trend and seasonality
                    trend = random.uniform(-0.02, 0.03)  # Slight upward bias
                    seasonal = self._get_seasonal_factor(crop_lower, i)
                    noise = random.uniform(-0.05, 0.05)
                    
                    price_change = trend + seasonal + noise
                    current_price = max(current_price * (1 + price_change), base_price * 0.5)
                    
                    forecast_date = (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d")
                    forecast_points.append({
                        "date": forecast_date,
                        "predicted_price": round(current_price, 2),
                        "lower_bound": round(current_price * 0.9, 2),
                        "upper_bound": round(current_price * 1.1, 2),
                        "confidence": round(random.uniform(0.7, 0.9), 2)
                    })
                
                forecast_data = ForecastData(
                    crop=crop,
                    region=region or "Karnataka",
                    forecasts=forecast_points,
                    confidence=round(random.uniform(0.75, 0.85), 2),
                    model_accuracy=round(random.uniform(0.70, 0.80), 2),
                    generated_at=datetime.now().isoformat()
                )
                
                forecasts.append(asdict(forecast_data))
            
            response = {
                "success": True,
                "data": forecasts,
                "timestamp": datetime.now().isoformat(),
                "message": self._translate_message(f"Price forecast generated for {days} days", language)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating price forecast: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": self._translate_message("Failed to generate price forecast", language)
            }
    
    def market_trends_analyzer(self, crops: List[str], time_period: str = "3months",
                              region: Optional[str] = None, language: str = "en") -> Dict[str, Any]:
        """Analyze market trends for specified crops"""
        logger.info(f"Analyzing market trends for crops: {crops}, period: {time_period}, region: {region}")
        
        try:
            trends = []
            for crop in crops:
                # Generate realistic trend analysis
                trend_directions = ["bullish", "bearish", "stable"]
                trend_direction = random.choice(trend_directions)
                
                price_change = random.uniform(-25, 35)  # Percentage change
                volatility = random.uniform(0.1, 0.4)
                
                # Generate insights based on trend
                insights = self._generate_market_insights(crop, trend_direction, price_change)
                
                trend_data = MarketTrend(
                    crop=crop,
                    region=region or "Karnataka",
                    trend_direction=trend_direction,
                    price_change_percent=round(price_change, 2),
                    volatility=round(volatility, 2),
                    seasonal_pattern=self._get_seasonal_pattern(crop.lower()),
                    analysis_period=time_period,
                    key_insights=insights
                )
                
                trends.append(asdict(trend_data))
            
            response = {
                "success": True,
                "data": trends,
                "timestamp": datetime.now().isoformat(),
                "message": self._translate_message("Market trend analysis completed", language)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": self._translate_message("Failed to analyze market trends", language)
            }
    
    def crop_recommendation(self, region: str, season: str, land_size: Optional[float] = None,
                           budget: Optional[float] = None, language: str = "en") -> Dict[str, Any]:
        """Recommend crops based on market conditions and profitability"""
        logger.info(f"Generating crop recommendations for region: {region}, season: {season}")
        
        try:
            # Define crop recommendations by season
            seasonal_crops = {
                "kharif": ["rice", "cotton", "sugarcane", "maize", "soybean"],
                "rabi": ["wheat", "barley", "peas", "mustard", "gram"],
                "zaid": ["watermelon", "cucumber", "fodder", "green_gram"]
            }
            
            season_lower = season.lower()
            available_crops = seasonal_crops.get(season_lower, ["tomato", "onion", "potato"])
            
            recommendations = []
            for crop in available_crops[:3]:  # Top 3 recommendations
                # Calculate profitability score
                base_price = random.randint(1000, 4000)
                cultivation_cost = random.randint(20000, 80000)  # per hectare
                expected_yield = random.uniform(15, 45)  # quintals per hectare
                
                gross_income = base_price * expected_yield
                net_profit = gross_income - cultivation_cost
                profit_margin = (net_profit / gross_income) * 100 if gross_income > 0 else 0
                
                recommendation = {
                    "crop": crop,
                    "season": season,
                    "region": region,
                    "expected_price": base_price,
                    "cultivation_cost_per_hectare": cultivation_cost,
                    "expected_yield_quintals": round(expected_yield, 1),
                    "gross_income_per_hectare": int(gross_income),
                    "net_profit_per_hectare": int(net_profit),
                    "profit_margin_percent": round(profit_margin, 1),
                    "market_demand": random.choice(["High", "Medium", "Low"]),
                    "risk_level": random.choice(["Low", "Medium", "High"]),
                    "water_requirement": random.choice(["Low", "Medium", "High"]),
                    "growing_duration_days": random.randint(60, 150),
                    "reasons": self._generate_recommendation_reasons(crop, profit_margin)
                }
                
                recommendations.append(recommendation)
            
            # Sort by profitability
            recommendations.sort(key=lambda x: x["profit_margin_percent"], reverse=True)
            
            response = {
                "success": True,
                "data": {
                    "region": region,
                    "season": season,
                    "land_size_hectares": land_size,
                    "budget_inr": budget,
                    "recommendations": recommendations,
                    "generated_at": datetime.now().isoformat()
                },
                "message": self._translate_message("Crop recommendations generated successfully", language)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating crop recommendations: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": self._translate_message("Failed to generate crop recommendations", language)
            }
    
    def _get_seasonal_factor(self, crop: str, day_offset: int) -> float:
        """Get seasonal price factor for a crop"""
        if crop not in self.mock_data["seasonal_patterns"]:
            return 0
        
        # Simple seasonal modeling
        current_month = (datetime.now() + timedelta(days=day_offset)).month
        pattern = self.mock_data["seasonal_patterns"][crop]
        
        peak_months = [datetime.strptime(m, "%b").month for m in pattern["peak_months"]]
        low_months = [datetime.strptime(m, "%b").month for m in pattern["low_months"]]
        
        if current_month in peak_months:
            return random.uniform(0.02, 0.05)  # Price increase during peak
        elif current_month in low_months:
            return random.uniform(-0.05, -0.02)  # Price decrease during low season
        else:
            return random.uniform(-0.01, 0.01)  # Neutral
    
    def _get_seasonal_pattern(self, crop: str) -> str:
        """Get seasonal pattern description for a crop"""
        if crop in self.mock_data["seasonal_patterns"]:
            pattern = self.mock_data["seasonal_patterns"][crop]
            return f"Peak: {', '.join(pattern['peak_months'])}, Low: {', '.join(pattern['low_months'])}"
        return "Pattern not available"
    
    def _generate_market_insights(self, crop: str, trend: str, price_change: float) -> List[str]:
        """Generate market insights based on trend analysis"""
        insights = []
        
        if trend == "bullish":
            insights.append(f"{crop.title()} prices showing upward momentum with {abs(price_change):.1f}% increase")
            insights.append("Strong demand and limited supply driving price growth")
            insights.append("Good time for farmers to sell existing stock")
        elif trend == "bearish":
            insights.append(f"{crop.title()} prices declining by {abs(price_change):.1f}% due to oversupply")
            insights.append("Consider holding stock if storage facilities available")
            insights.append("Focus on quality to get better prices")
        else:
            insights.append(f"{crop.title()} prices stable with minimal volatility")
            insights.append("Balanced supply-demand situation")
            insights.append("Predictable market conditions for planning")
        
        return insights
    
    def _generate_recommendation_reasons(self, crop: str, profit_margin: float) -> List[str]:
        """Generate reasons for crop recommendation"""
        reasons = []
        
        if profit_margin > 30:
            reasons.append("High profit margin expected")
            reasons.append("Strong market demand")
        elif profit_margin > 15:
            reasons.append("Moderate profitability with stable returns")
            reasons.append("Balanced risk-reward ratio")
        else:
            reasons.append("Lower risk option")
            reasons.append("Suitable for risk-averse farmers")
        
        reasons.append(f"Well-suited for current season ({crop} is a good seasonal choice)")
        reasons.append("Local market acceptance and demand")
        
        return reasons
    
    def _translate_message(self, message: str, language: str) -> str:
        """Translate messages to specified language"""
        if language == "hi":
            translations = {
                "Current market prices retrieved successfully": "वर्तमान बाजार मूल्य सफलतापूर्वक प्राप्त किए गए",
                "Failed to retrieve current prices": "वर्तमान मूल्य प्राप्त करने में विफल",
                "Market trend analysis completed": "बाजार प्रवृत्ति विश्लेषण पूर्ण",
                "Failed to analyze market trends": "बाजार प्रवृत्ति विश्लेषण में विफल",
                "Crop recommendations generated successfully": "फसल सिफारिशें सफलतापूर्वक तैयार की गईं",
                "Failed to generate crop recommendations": "फसल सिफारिशें तैयार करने में विफल"
            }
            return translations.get(message, message)
        elif language == "kn":
            translations = {
                "Current market prices retrieved successfully": "ಪ್ರಸ್ತುತ ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಪಡೆಯಲಾಗಿದೆ",
                "Failed to retrieve current prices": "ಪ್ರಸ್ತುತ ಬೆಲೆಗಳನ್ನು ಪಡೆಯುವಲ್ಲಿ ವಿಫಲವಾಗಿದೆ",
                "Market trend analysis completed": "ಮಾರುಕಟ್ಟೆ ಪ್ರವೃತ್ತಿ ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ",
                "Failed to analyze market trends": "ಮಾರುಕಟ್ಟೆ ಪ್ರವೃತ್ತಿ ವಿಶ್ಲೇಷಣೆಯಲ್ಲಿ ವಿಫಲವಾಗಿದೆ",
                "Crop recommendations generated successfully": "ಬೆಳೆ ಶಿಫಾರಸುಗಳನ್ನು ಯಶಸ್ವಿಯಾಗಿ ರಚಿಸಲಾಗಿದೆ",
                "Failed to generate crop recommendations": "ಬೆಳೆ ಶಿಫಾರಸುಗಳನ್ನು ರಚಿಸುವಲ್ಲಿ ವಿಫಲವಾಗಿದೆ"
            }
            return translations.get(message, message)
        return message

# Google ADK tool functions
def get_current_prices(crops: List[str], region: str = None, language: str = "en") -> str:
    """Tool function for getting current market prices"""
    agent = MIAAgent()
    result = agent.get_current_prices(crops, region, language)
    return json.dumps(result, indent=2)

def price_forecast(crops: List[str], days: int = 30, region: str = None, language: str = "en") -> str:
    """Tool function for price forecasting"""
    agent = MIAAgent()
    result = agent.price_forecast(crops, days, region, language)
    return json.dumps(result, indent=2)

def market_trends_analyzer(crops: List[str], time_period: str = "3months", 
                          region: str = None, language: str = "en") -> str:
    """Tool function for market trend analysis"""
    agent = MIAAgent()
    result = agent.market_trends_analyzer(crops, time_period, region, language)
    return json.dumps(result, indent=2)

def crop_recommendation(region: str, season: str, land_size: float = None, 
                       budget: float = None, language: str = "en") -> str:
    """Tool function for crop recommendations"""
    agent = MIAAgent()
    result = agent.crop_recommendation(region, season, land_size, budget, language)
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    # Test the agent
    agent = MIAAgent()
    
    print("=== Testing MIA Agent ===")
    
    # Test current prices
    print("\n1. Current Prices:")
    prices = agent.get_current_prices(["tomato", "onion"], "Karnataka", "en")
    print(json.dumps(prices, indent=2))
    
    # Test price forecast
    print("\n2. Price Forecast:")
    forecast = agent.price_forecast(["tomato"], 7, "Karnataka", "en")
    print(json.dumps(forecast, indent=2))
    
    # Test market trends
    print("\n3. Market Trends:")
    trends = agent.market_trends_analyzer(["tomato", "onion"], "1month", "Karnataka", "en")
    print(json.dumps(trends, indent=2))
    
    # Test crop recommendations
    print("\n4. Crop Recommendations:")
    recommendations = agent.crop_recommendation("Karnataka", "kharif", 2.5, 100000, "en")
    print(json.dumps(recommendations, indent=2))