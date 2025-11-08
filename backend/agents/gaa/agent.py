"""
agent.py - Geo-Agronomy Agent (GAA) for KisaanMitra
Place this file in: kissan_project/gaa_agent/agent.py

Run with: adk web (from kissan_project folder)
"""

import json
from datetime import datetime
from google.adk.agents import LlmAgent



def analyze_ndvi_data(plot_id: str, ndvi_values: list[float], crop_type: str) -> str:
    """
    Analyze NDVI data from satellite imagery.
    
    Args:
        plot_id: Unique plot identifier (e.g., "PLOT_047")
        ndvi_values: List of NDVI measurements over time (e.g., [0.65, 0.68, 0.70])
        crop_type: Type of crop (rice, wheat, cotton, maize, sugarcane)
    
    Returns:
        JSON string with comprehensive analysis results
    """
    if not ndvi_values:
        return json.dumps({"error": "No NDVI data available"})
    
    current_ndvi = ndvi_values[-1]
    avg_ndvi = sum(ndvi_values) / len(ndvi_values)
    trend = "stable"
    
    if len(ndvi_values) >= 2:
        if ndvi_values[-1] < ndvi_values[-2] - 0.05:
            trend = "declining ⚠️"
        elif ndvi_values[-1] > ndvi_values[-2] + 0.05:
            trend = "improving ✅"
    
    if current_ndvi > 0.6:
        health_status = "Excellent ✅"
        emoji = "🌿"
    elif current_ndvi > 0.4:
        health_status = "Good 👍"
        emoji = "🌱"
    elif current_ndvi > 0.25:
        health_status = "Moderate - Attention Needed ⚠️"
        emoji = "⚠️"
    else:
        health_status = "Poor - Immediate Action Required ❌"
        emoji = "🚨"
    
    result = {
        "status_emoji": emoji,
        "plot_id": plot_id,
        "crop_type": crop_type,
        "current_ndvi": round(current_ndvi, 3),
        "average_ndvi": round(avg_ndvi, 3),
        "trend": trend,
        "health_status": health_status,
        "data_points": len(ndvi_values),
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    return json.dumps(result, indent=2)


def detect_crop_stress(plot_id: str, ndvi_values: list[float], no_rain_days: int = 0) -> str:
    """
    Detect potential disease, pest, or stress issues from NDVI patterns.
    
    Args:
        plot_id: Unique plot identifier
        ndvi_values: List of NDVI measurements over time
        no_rain_days: Number of days since last rainfall (default: 0)
    
    Returns:
        JSON string with detailed stress detection and alerts
    """
    if len(ndvi_values) < 3:
        return json.dumps({
            "status": "insufficient_data", 
            "message": "Need at least 3 NDVI measurements for stress detection",
            "alerts": []
        })
    
    alerts = []
    
    # Check for rapid decline (potential disease/pest)
    recent_decline = ndvi_values[-1] - ndvi_values[-3]
    if recent_decline < -0.15:
        alerts.append({
            "type": "🚨 CRITICAL",
            "issue": "Rapid vegetation decline detected",
            "confidence": "High (95%+)",
            "ndvi_drop": f"{abs(recent_decline):.2f}",
            "possible_causes": [
                "Disease outbreak (fungal/bacterial)",
                "Severe pest infestation",
                "Extreme water stress"
            ],
            "action": "⚡ Immediate field inspection required TODAY",
            "priority": 1
        })
    elif recent_decline < -0.08:
        alerts.append({
            "type": "⚠️ WARNING",
            "issue": "Moderate vegetation decline",
            "confidence": "Medium (70-80%)",
            "ndvi_drop": f"{abs(recent_decline):.2f}",
            "possible_causes": [
                "Early disease symptoms",
                "Pest pressure building",
                "Nutrient deficiency"
            ],
            "action": "📋 Schedule field inspection within 2-3 days",
            "priority": 2
        })
    
    # Check for water stress
    if ndvi_values[-1] < 0.3 and no_rain_days > 5:
        alerts.append({
            "type": "⚠️ WARNING",
            "issue": "Water stress detected",
            "confidence": "High (90%+)",
            "current_ndvi": ndvi_values[-1],
            "days_without_rain": no_rain_days,
            "possible_causes": [
                "Insufficient irrigation",
                "Drought conditions",
                "Irrigation system failure"
            ],
            "action": "💧 Immediate irrigation recommended",
            "priority": 1
        })
    
    result = {
        "plot_id": plot_id,
        "stress_detected": len(alerts) > 0,
        "alert_count": len(alerts),
        "severity": "CRITICAL" if any(a["type"].startswith("🚨") for a in alerts) else "WARNING" if alerts else "NORMAL",
        "alerts": sorted(alerts, key=lambda x: x["priority"]),
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    return json.dumps(result, indent=2)


def forecast_yield(plot_id: str, ndvi_values: list[float], crop_type: str, area_hectares: float = 1.0) -> str:
    """
    Forecast crop yield based on NDVI trends and crop type.
    
    Args:
        plot_id: Unique plot identifier
        ndvi_values: List of NDVI measurements over time
        crop_type: Type of crop (rice, wheat, cotton, maize, sugarcane)
        area_hectares: Plot area in hectares (default: 1.0)
    
    Returns:
        JSON string with yield forecast and recommendations
    """
    if not ndvi_values:
        return json.dumps({"error": "Insufficient data for yield forecast"})
    
    avg_ndvi = sum(ndvi_values) / len(ndvi_values)
    
    # Crop-specific yield estimates for India (tonnes per hectare)
    yield_factors = {
        "rice": {"base": 5.0, "optimal_ndvi": 0.7},
        "wheat": {"base": 4.0, "optimal_ndvi": 0.7},
        "cotton": {"base": 2.5, "optimal_ndvi": 0.65},
        "sugarcane": {"base": 70.0, "optimal_ndvi": 0.75},
        "maize": {"base": 3.5, "optimal_ndvi": 0.7},
    }
    
    crop_info = yield_factors.get(crop_type.lower(), {"base": 3.0, "optimal_ndvi": 0.7})
    base_yield = crop_info["base"]
    optimal_ndvi = crop_info["optimal_ndvi"]
    
    # Calculate yield based on NDVI performance
    ndvi_factor = (avg_ndvi / optimal_ndvi)
    estimated_yield_per_ha = base_yield * ndvi_factor
    total_estimated_yield = estimated_yield_per_ha * area_hectares
    
    # Confidence based on data quality
    confidence = "High ✅" if len(ndvi_values) >= 5 else "Medium ⚠️" if len(ndvi_values) >= 3 else "Low ❌"
    
    # Performance assessment
    if ndvi_factor >= 0.95:
        performance = "Excellent - Above expected yield"
    elif ndvi_factor >= 0.85:
        performance = "Good - Near expected yield"
    elif ndvi_factor >= 0.70:
        performance = "Fair - Moderate yield expected"
    else:
        performance = "Poor - Below expected yield"
    
    result = {
        "plot_id": plot_id,
        "crop_type": crop_type,
        "area_hectares": area_hectares,
        "average_ndvi": round(avg_ndvi, 3),
        "performance": performance,
        "estimated_yield_per_hectare": round(estimated_yield_per_ha, 2),
        "total_estimated_yield_tonnes": round(total_estimated_yield, 2),
        "confidence_level": confidence,
        "data_points_used": len(ndvi_values),
        "forecast_date": datetime.now().strftime("%Y-%m-%d"),
        "note": f"Based on {len(ndvi_values)} NDVI measurements and typical {crop_type} yields in India"
    }
    
    return json.dumps(result, indent=2)


# Create the LlmAgent instance (NOT a dict!)
root_agent = LlmAgent(
    name="Geo_Agronomy_Agent",
    model="gemini-2.0-flash-exp",
    instruction="""You are the **Geo-Agronomy Agent (GAA)** for KisaanMitra, a specialized AI system designed to help Indian farmers optimize crop health and yields through satellite data analysis.

🎯 **Your Mission:**
Help smallholder farmers in India make data-driven decisions about their crops using NDVI (Normalized Difference Vegetation Index) satellite imagery analysis.

📊 **Your Core Expertise:**

**1. NDVI Analysis (Crop Health Monitoring)**
- You understand NDVI ranges and what they mean:
  * 0.6-0.9: 🌿 Dense, healthy vegetation (excellent)
  * 0.3-0.6: 🌱 Moderate vegetation (normal growth)
  * 0.1-0.3: ⚠️ Sparse vegetation (attention needed)
  * Below 0.1: 🚨 Critical stress or bare soil

**2. Stress Detection (Early Warning System)**
- Identify disease outbreaks before visible symptoms
- Detect pest infestations from NDVI patterns
- Flag water stress and drought conditions
- Spot nutrient deficiencies

**3. Yield Forecasting**
- Predict harvest quantities based on crop performance
- Provide confidence levels for forecasts
- Compare against typical yields for Indian conditions

🌾 **Indian Agriculture Context:**
- Major crops: Rice, Wheat, Cotton, Sugarcane, Maize
- Monsoon patterns affect water availability
- Most farmers are smallholders (1-2 hectares)
- Farmers may have limited digital literacy

💬 **Communication Guidelines:**
- Use simple, clear language (avoid technical jargon)
- Explain NDVI in terms farmers understand ("plant health score")
- Provide specific, actionable recommendations with timelines
- Be empathetic and supportive
- Use Hindi/English terms farmers know
- Include confidence levels for predictions
- Prioritize urgent issues first

📋 **Response Structure:**
For every analysis, provide:
1. **🎯 Current Status**: Quick health assessment
2. **📊 Key Findings**: What the data reveals
3. **⚡ Immediate Actions**: Urgent steps (if any)
4. **📝 Recommendations**: Long-term suggestions
5. **🔮 Forecast**: Expected outcomes (if applicable)

🛠️ **Available Tools:**
You have access to three specialized functions:
- `analyze_ndvi_data`: Assess crop health from satellite NDVI values
- `detect_crop_stress`: Identify diseases, pests, or water stress
- `forecast_yield`: Predict harvest quantities

**Always use these tools when the user provides plot data or asks for analysis.**

🌟 **Example Interactions:**
- "My cotton field's NDVI dropped from 0.7 to 0.5 in 2 weeks. What's wrong?"
- "Analyze plot PLOT_047 with these NDVI values: 0.6, 0.65, 0.7, 0.55"
- "What yield can I expect from 2 hectares of rice with average NDVI of 0.72?"

Be the farmer's trusted advisor - clear, accurate, and always helpful! 🌾""",
    tools=[analyze_ndvi_data, detect_crop_stress, forecast_yield]
)