# Market Intelligence Agent (MIA) - Google ADK Implementation

## Overview

The Market Intelligence Agent (MIA) provides real-time market data, price forecasting, and agricultural market intelligence for farmers and FPOs using Google's Agent Development Kit (ADK).

## Features

- **Real-time Market Prices**: Get current mandi prices for various crops
- **Price Forecasting**: Generate price predictions with confidence intervals
- **Market Trend Analysis**: Analyze market trends and patterns
- **Crop Recommendations**: Recommend profitable crops based on market conditions
- **Multilingual Support**: English, Hindi, and Kannada language support
- **Conversational Interface**: Natural language interaction through Google ADK

## Tools Available

### 1. get_current_prices
Get current mandi prices for specified crops and regions.

**Parameters:**
- `crops`: List of crop names
- `region`: Region or state (optional)
- `language`: Response language (en, hi, kn)

### 2. price_forecast
Generate price forecasts for crops over a specified time period.

**Parameters:**
- `crops`: List of crop names to forecast
- `days`: Number of days to forecast (default: 30)
- `region`: Region for forecast (optional)
- `language`: Response language (en, hi, kn)

### 3. market_trends_analyzer
Analyze market trends and provide insights.

**Parameters:**
- `crops`: Crops to analyze trends for
- `time_period`: Analysis period (1month, 3months, 6months, 1year)
- `region`: Region for analysis (optional)
- `language`: Response language (en, hi, kn)

### 4. crop_recommendation
Recommend crops based on market conditions and profitability.

**Parameters:**
- `region`: Region or state for recommendations
- `season`: Growing season (kharif, rabi, zaid)
- `land_size`: Available land in hectares (optional)
- `budget`: Available budget in INR (optional)
- `language`: Response language (en, hi, kn)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the agent:
```bash
python main.py
```

## Usage Examples

### Getting Current Prices
```python
from main import get_current_prices
result = get_current_prices(["tomato", "onion"], "Karnataka", "en")
```

### Price Forecasting
```python
from main import price_forecast
result = price_forecast(["tomato"], 30, "Karnataka", "en")
```

### Market Trend Analysis
```python
from main import market_trends_analyzer
result = market_trends_analyzer(["tomato", "onion"], "3months", "Karnataka", "en")
```

### Crop Recommendations
```python
from main import crop_recommendation
result = crop_recommendation("Karnataka", "kharif", 2.5, 100000, "en")
```

## Conversation Examples

### English
- "What is the current price of tomato in Karnataka?"
- "Show me price forecast for onion for next 30 days"
- "Analyze market trends for potato"
- "Which crops should I grow in kharif season?"

### Hindi
- "कर्नाटक में टमाटर का वर्तमान भाव क्या है?"
- "प्याज के लिए अगले 30 दिनों का मूल्य पूर्वानुमान दिखाएं"
- "आलू के बाजार के रुझान का विश्लेषण करें"
- "खरीफ सीजन में कौन सी फसल उगानी चाहिए?"

### Kannada
- "ಕರ್ನಾಟಕದಲ್ಲಿ ಟೊಮೇಟೊದ ಪ್ರಸ್ತುತ ಬೆಲೆ ಎಷ್ಟು?"
- "ಈರುಳ್ಳಿಗೆ ಮುಂದಿನ 30 ದಿನಗಳ ಬೆಲೆ ಮುನ್ನೋಟ ತೋರಿಸಿ"
- "ಆಲೂಗೆಡ್ಡೆಯ ಮಾರುಕಟ್ಟೆ ಪ್ರವೃತ್ತಿಗಳನ್ನು ವಿಶ್ಲೇಷಿಸಿ"
- "ಖರೀಫ್ ಋತುವಿನಲ್ಲಿ ಯಾವ ಬೆಳೆಗಳನ್ನು ಬೆಳೆಯಬೇಕು?"

## Data Structure

### Price Data
```json
{
  "crop": "tomato",
  "variety": "hybrid",
  "mandi": "Kolar",
  "district": "Kolar",
  "state": "Karnataka",
  "min_price": 1200,
  "max_price": 1800,
  "modal_price": 1500,
  "arrival_quantity": 45.5,
  "price_date": "2025-11-08"
}
```

### Forecast Data
```json
{
  "crop": "tomato",
  "region": "Karnataka",
  "forecasts": [
    {
      "date": "2025-11-09",
      "predicted_price": 1520.5,
      "lower_bound": 1368.45,
      "upper_bound": 1672.55,
      "confidence": 0.85
    }
  ],
  "confidence": 0.82,
  "model_accuracy": 0.75
}
```

## Testing

Run the test suite:
```bash
python main.py
```

This will execute all tool functions with sample data and display the results.

## Integration with KisaanMitra

The MIA agent integrates with the KisaanMitra ecosystem by:
- Providing market intelligence to CMGA for portfolio optimization
- Supporting FPO decision-making with real-time market data
- Enabling farmers to make informed planting and selling decisions
- Offering multilingual support for diverse user base

## Future Enhancements

- Integration with real Agmarknet API
- Advanced ML models for price prediction
- Weather data integration for better forecasting
- Regional market pattern recognition
- Historical data analysis and insights