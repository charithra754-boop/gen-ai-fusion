"""
agent.py - Climate & Resource Agent (CRA) for KisaanMitra
Place this file in: kissan_project/cra_agent/agent.py

Run with: adk web (from kissan_project folder)
"""

import json
from datetime import datetime
from google.adk.agents import LlmAgent


def schedule_irrigation(
    plot_id: str,
    soil_moisture: float,
    weather_forecast: dict,
    crop_type: str,
    growth_stage: str
) -> str:
    """
    Autonomously schedule irrigation using real-time data.

    Args:
        plot_id: Unique plot identifier (e.g., "PLOT_047")
        soil_moisture: Current soil moisture percentage (0-100%)
        weather_forecast: Weather data {"temp_c": 35, "humidity": 60, "rainfall_mm_next_7days": 15}
        crop_type: Type of crop (rice, wheat, cotton, maize, sugarcane)
        growth_stage: Growth stage (seedling, vegetative, flowering, maturity)

    Returns:
        JSON string with irrigation schedule and recommendations
    """
    # Validation
    if not (0 <= soil_moisture <= 100):
        return json.dumps({
            "error": "Soil moisture must be between 0-100%",
            "status": "invalid_input"
        })

    # Crop-specific moisture thresholds by growth stage (% soil moisture)
    # Critical growth stages require higher moisture levels
    thresholds = {
        "rice": {"seedling": 60, "vegetative": 70, "flowering": 80, "maturity": 50},
        "wheat": {"seedling": 50, "vegetative": 60, "flowering": 70, "maturity": 40},
        "cotton": {"seedling": 50, "vegetative": 55, "flowering": 65, "maturity": 45},
        "maize": {"seedling": 55, "vegetative": 65, "flowering": 75, "maturity": 45},
        "sugarcane": {"seedling": 60, "vegetative": 70, "flowering": 75, "maturity": 60},
    }

    crop_threshold = thresholds.get(crop_type.lower(), {}).get(growth_stage.lower(), 60)

    # Extract weather parameters
    temp = weather_forecast.get("temp_c", 30)
    humidity = weather_forecast.get("humidity", 60)
    expected_rainfall = weather_forecast.get("rainfall_mm_next_7days", 0)

    # Calculate evapotranspiration rate (simplified Penman-Monteith approach)
    # Higher temp and lower humidity = higher water loss
    et_rate = 0.5 * (temp / 30) * ((100 - humidity) / 40)  # mm/day

    # Decision logic
    moisture_deficit = crop_threshold - soil_moisture
    irrigation_needed = soil_moisture < crop_threshold

    # Skip irrigation if significant rain is expected and moisture isn't critically low
    if expected_rainfall > 20 and soil_moisture > (crop_threshold - 15):
        irrigation_needed = False
        urgency = "LOW"
        timing = "monitoring - rain expected"
        volume_per_hectare = 0
        reasoning = f"Rain forecast ({expected_rainfall}mm in next 7 days) sufficient. Current soil moisture {soil_moisture}% acceptable for now."
        water_savings = "100% - irrigation deferred due to rain forecast"
    elif moisture_deficit > 25:
        # Critical water stress
        urgency = "CRITICAL ⚠️"
        timing = "immediate - within 6 hours"
        volume_per_hectare = moisture_deficit * 120  # liters per % deficit per hectare (higher for critical)
        reasoning = f"CRITICAL: Soil at {soil_moisture}% is {moisture_deficit}% below optimal {crop_threshold}% for {crop_type} in {growth_stage} stage. Immediate action required!"
        water_savings = "0% - full irrigation required"
    elif irrigation_needed:
        # Moderate irrigation needed
        urgency = "HIGH" if moisture_deficit > 15 else "MEDIUM"
        timing = "within 24 hours" if moisture_deficit > 15 else "within 48 hours"
        volume_per_hectare = moisture_deficit * 100  # liters per % deficit per hectare
        reasoning = f"Soil moisture {soil_moisture}% below {crop_threshold}% threshold for {crop_type} in {growth_stage} stage."
        water_savings = "15-20% vs flood irrigation"
    else:
        urgency = "LOW"
        timing = "no irrigation needed"
        volume_per_hectare = 0
        reasoning = f"Soil moisture adequate at {soil_moisture}% (threshold: {crop_threshold}%)."
        water_savings = "100% - no irrigation required"

    result = {
        "status_emoji": "💧",
        "plot_id": plot_id,
        "crop_type": crop_type,
        "growth_stage": growth_stage,
        "current_soil_moisture_percent": round(soil_moisture, 1),
        "optimal_moisture_threshold": crop_threshold,
        "irrigation_needed": irrigation_needed,
        "recommended_volume_liters_per_hectare": round(volume_per_hectare, 0),
        "urgency": urgency,
        "timing": timing,
        "reasoning": reasoning,
        "evapotranspiration_rate_mm_per_day": round(et_rate, 2),
        "expected_rainfall_next_7days_mm": expected_rainfall,
        "water_savings_estimate": water_savings,
        "schedule_date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    return json.dumps(result, indent=2)


def calculate_climate_resilience_rating(
    plot_id: str,
    crop_type: str,
    water_availability: str,
    historical_rainfall: list[float],
    soil_type: str
) -> str:
    """
    Calculate climate resilience rating for crop-plot suitability.

    Args:
        plot_id: Unique plot identifier
        crop_type: Proposed crop (rice, wheat, cotton, maize, sugarcane)
        water_availability: Water source type (canal, well, rainfed, drip_system, tube_well)
        historical_rainfall: Last 3 years monsoon rainfall in mm (e.g., [850, 920, 780])
        soil_type: Soil classification (clay, loam, sandy, black_soil, red_soil)

    Returns:
        JSON string with resilience rating, risk assessment, and recommendations
    """
    if len(historical_rainfall) < 2:
        return json.dumps({
            "error": "Need at least 2 years of rainfall data for analysis",
            "status": "insufficient_data"
        })

    # Crop water requirements (mm per season)
    crop_water_needs = {
        "rice": {"min": 1200, "optimal": 1500, "drought_tolerance": "low"},
        "wheat": {"min": 450, "optimal": 650, "drought_tolerance": "medium"},
        "cotton": {"min": 700, "optimal": 1000, "drought_tolerance": "medium-high"},
        "maize": {"min": 500, "optimal": 700, "drought_tolerance": "medium"},
        "sugarcane": {"min": 1500, "optimal": 2500, "drought_tolerance": "low"},
        "pulses": {"min": 350, "optimal": 500, "drought_tolerance": "high"},
    }

    # Water source reliability scores (0-100)
    water_source_scores = {
        "drip_system": 95,
        "tube_well": 85,
        "canal": 70,
        "well": 60,
        "rainfed": 40
    }

    # Soil water retention capacity scores (0-100)
    soil_retention_scores = {
        "clay": 85,
        "black_soil": 80,
        "loam": 75,
        "red_soil": 60,
        "sandy": 40
    }

    crop_info = crop_water_needs.get(crop_type.lower(), {"min": 600, "optimal": 800, "drought_tolerance": "medium"})
    water_score = water_source_scores.get(water_availability.lower(), 50)
    soil_score = soil_retention_scores.get(soil_type.lower(), 60)

    # Calculate rainfall variability (coefficient of variation)
    avg_rainfall = sum(historical_rainfall) / len(historical_rainfall)
    variance = sum((x - avg_rainfall) ** 2 for x in historical_rainfall) / len(historical_rainfall)
    std_dev = variance ** 0.5
    cv = (std_dev / avg_rainfall) * 100 if avg_rainfall > 0 else 100

    # Rainfall adequacy score
    rainfall_adequacy = min(100, (avg_rainfall / crop_info["optimal"]) * 100)

    # Calculate composite resilience score
    base_score = (water_score * 0.4) + (soil_score * 0.3) + (rainfall_adequacy * 0.3)

    # Penalty for high variability
    variability_penalty = min(20, cv / 2)  # Up to 20 point penalty
    resilience_score = max(0, base_score - variability_penalty)

    # Assign letter grade
    if resilience_score >= 90:
        rating = "A+"
        risk_level = "VERY LOW"
        suitability = "EXCELLENT - Highly Recommended"
    elif resilience_score >= 80:
        rating = "A"
        risk_level = "LOW"
        suitability = "VERY GOOD - Recommended"
    elif resilience_score >= 70:
        rating = "B+"
        risk_level = "LOW-MODERATE"
        suitability = "GOOD - Suitable with monitoring"
    elif resilience_score >= 60:
        rating = "B"
        risk_level = "MODERATE"
        suitability = "FAIR - Suitable with irrigation backup"
    elif resilience_score >= 50:
        rating = "C"
        risk_level = "MODERATE-HIGH"
        suitability = "MARGINAL - Requires intervention"
    elif resilience_score >= 35:
        rating = "D"
        risk_level = "HIGH"
        suitability = "RISKY - Consider alternatives"
    else:
        rating = "F"
        risk_level = "CRITICAL"
        suitability = "NOT RECOMMENDED - High failure risk"

    # Generate risks and mitigation strategies
    key_risks = []
    mitigation_strategies = []

    if cv > 20:
        key_risks.append(f"High rainfall variability ({cv:.1f}% - unstable monsoon pattern)")
        mitigation_strategies.append("Install supplementary irrigation (drip/sprinkler)")

    if water_availability.lower() == "rainfed":
        key_risks.append("Complete dependence on monsoon - no irrigation backup")
        mitigation_strategies.append("Consider drought-resistant crop varieties")

    if avg_rainfall < crop_info["min"]:
        key_risks.append(f"Average rainfall ({avg_rainfall:.0f}mm) below crop minimum needs ({crop_info['min']}mm)")
        mitigation_strategies.append(f"Arrange assured irrigation source or switch to less water-intensive crop")

    if soil_type.lower() == "sandy":
        key_risks.append("Low soil water retention (sandy soil) - frequent irrigation needed")
        mitigation_strategies.append("Apply organic mulch to improve moisture retention")

    if crop_info["drought_tolerance"] == "low" and water_score < 70:
        key_risks.append(f"{crop_type.capitalize()} has low drought tolerance - unreliable water source")
        mitigation_strategies.append("Upgrade to tube well or drip irrigation system")

    # Default recommendations if no major risks
    if not mitigation_strategies:
        mitigation_strategies.append("Continue current practices - conditions favorable")
        mitigation_strategies.append("Monitor weather forecasts during critical growth stages")

    result = {
        "plot_id": plot_id,
        "crop_type": crop_type,
        "resilience_rating": rating,
        "resilience_score": round(resilience_score, 1),
        "risk_level": risk_level,
        "suitability": suitability,
        "water_availability_type": water_availability,
        "soil_type": soil_type,
        "rainfall_analysis": {
            "average_annual_mm": round(avg_rainfall, 0),
            "variability_percent": round(cv, 1),
            "stability": "Stable" if cv < 15 else "Moderate" if cv < 25 else "Highly Variable"
        },
        "key_risks": key_risks if key_risks else ["No major risks identified"],
        "mitigation_strategies": mitigation_strategies,
        "confidence_level": "High" if len(historical_rainfall) >= 3 else "Medium",
        "data_years": len(historical_rainfall),
        "analysis_date": datetime.now().strftime("%Y-%m-%d")
    }

    return json.dumps(result, indent=2)


def generate_water_budget(
    village_id: str,
    plots_data: list[dict],
    total_water_available: float,
    season: str
) -> str:
    """
    Generate equitable village-level water allocation budget.

    Args:
        village_id: Village/FPO identifier (e.g., "VILLAGE_KHARIF_2025")
        plots_data: List of plot dictionaries:
            [{"plot_id": "PLOT_01", "area_hectares": 1.2, "crop": "rice", "position": "head"},
             {"plot_id": "PLOT_02", "area_hectares": 0.8, "crop": "wheat", "position": "tail"}]
        total_water_available: Total water available in cubic meters (m³)
        season: Agricultural season (kharif, rabi, zaid)

    Returns:
        JSON string with water budget and equity metrics
    """
    if not plots_data:
        return json.dumps({
            "error": "No plot data provided for water budget",
            "status": "invalid_input"
        })

    # Seasonal crop water requirements (m³ per hectare)
    # Kharif (monsoon) needs less irrigation, Zaid (summer) needs most
    seasonal_requirements = {
        "kharif": {  # Monsoon season (June-Sep)
            "rice": 8000, "cotton": 6000, "maize": 4500, "soybean": 4000, "sugarcane": 10000
        },
        "rabi": {  # Winter season (Oct-Mar)
            "wheat": 4500, "chickpea": 3000, "mustard": 3500, "potato": 5000, "sugarcane": 12000
        },
        "zaid": {  # Summer season (Apr-May)
            "watermelon": 5000, "cucumber": 4500, "fodder": 3500, "maize": 6000
        }
    }

    # Get requirements for this season, with defaults
    season_reqs = seasonal_requirements.get(season.lower(), {})
    default_req = 5000  # Default m³/hectare if crop not listed

    # Calculate base water needs for each plot
    total_base_need = 0
    plot_allocations = []

    for plot in plots_data:
        area = plot.get("area_hectares", 1.0)
        crop = plot.get("crop", "unknown").lower()
        position = plot.get("position", "middle").lower()
        plot_id = plot.get("plot_id", "UNKNOWN")

        # Base water need
        base_need = season_reqs.get(crop, default_req) * area

        # Equity adjustment: tail-end plots get 15% bonus to compensate for traditional inequity
        if position == "tail":
            equity_multiplier = 1.15
            priority = "HIGH (tail-end equity adjustment)"
        elif position == "head":
            equity_multiplier = 1.0
            priority = "MEDIUM (head-end position)"
        else:
            equity_multiplier = 1.05
            priority = "MEDIUM (middle position)"

        adjusted_need = base_need * equity_multiplier
        total_base_need += adjusted_need

        plot_allocations.append({
            "plot_id": plot_id,
            "area_hectares": area,
            "crop": crop,
            "position": position,
            "base_need_m3": round(base_need, 0),
            "equity_multiplier": equity_multiplier,
            "adjusted_need_m3": round(adjusted_need, 0),
            "priority": priority
        })

    # Proportional allocation based on adjusted needs
    allocation_ratio = total_water_available / total_base_need if total_base_need > 0 else 1.0

    final_allocations = []
    total_allocated = 0

    for alloc in plot_allocations:
        final_amount = alloc["adjusted_need_m3"] * allocation_ratio
        per_hectare = final_amount / alloc["area_hectares"] if alloc["area_hectares"] > 0 else 0

        justification = f"{alloc['crop'].capitalize()} in {season} season"
        if alloc["position"] == "tail":
            justification += " + tail-end compensation (+15%)"

        final_allocations.append({
            "plot_id": alloc["plot_id"],
            "area_hectares": alloc["area_hectares"],
            "crop": alloc["crop"],
            "allocated_water_m3": round(final_amount, 0),
            "per_hectare_m3": round(per_hectare, 0),
            "priority": alloc["priority"],
            "allocation_justification": justification
        })

        total_allocated += final_amount

    # Calculate equity metrics
    # Gini coefficient (0 = perfect equality, 1 = perfect inequality)
    per_hectare_allocations = sorted([a["per_hectare_m3"] for a in final_allocations])
    n = len(per_hectare_allocations)
    if n > 0:
        cumsum = 0
        for i, val in enumerate(per_hectare_allocations):
            cumsum += val * (n - i)
        gini = (2 * cumsum) / (n * sum(per_hectare_allocations)) - (n + 1) / n if sum(per_hectare_allocations) > 0 else 0
    else:
        gini = 0

    # Head vs tail ratio (should be close to 1.0)
    head_plots = [a for a in final_allocations if "head" in a["priority"].lower()]
    tail_plots = [a for a in final_allocations if "tail" in a["priority"].lower()]

    if head_plots and tail_plots:
        avg_head = sum(p["per_hectare_m3"] for p in head_plots) / len(head_plots)
        avg_tail = sum(p["per_hectare_m3"] for p in tail_plots) / len(tail_plots)
        head_tail_ratio = avg_head / avg_tail if avg_tail > 0 else 1.0
    else:
        head_tail_ratio = 1.0

    # Fairness rating
    if gini < 0.1 and 0.95 <= head_tail_ratio <= 1.05:
        fairness = "Excellent ✅"
    elif gini < 0.2 and 0.9 <= head_tail_ratio <= 1.1:
        fairness = "Good ✓"
    elif gini < 0.3:
        fairness = "Fair"
    else:
        fairness = "Poor - Review needed ⚠️"

    allocation_efficiency = (total_allocated / total_water_available * 100) if total_water_available > 0 else 0

    result = {
        "village_id": village_id,
        "season": season,
        "total_water_available_m3": round(total_water_available, 0),
        "total_water_allocated_m3": round(total_allocated, 0),
        "water_reserve_m3": round(total_water_available - total_allocated, 0),
        "allocation_efficiency_percent": round(allocation_efficiency, 1),
        "number_of_plots": len(plots_data),
        "allocations": final_allocations,
        "equity_metrics": {
            "gini_coefficient": round(gini, 3),
            "head_vs_tail_ratio": round(head_tail_ratio, 2),
            "fairness_rating": fairness,
            "notes": "Gini < 0.1 is excellent; head/tail ratio near 1.0 indicates equity"
        },
        "budget_date": datetime.now().strftime("%Y-%m-%d"),
        "notes": f"Budget allocates {allocation_efficiency:.0f}% of available water with equity adjustments for tail-end plots"
    }

    return json.dumps(result, indent=2)


# Create the LlmAgent instance
root_agent = LlmAgent(
    name="Climate_Resource_Agent",
    model="gemini-2.0-flash-exp",
    instruction="""You are the **Climate & Resource Agent (CRA)** for KisaanMitra, a specialized AI system designed to help Indian farmers optimize water usage and build climate resilience through autonomous irrigation management.

🎯 **Your Mission:**
Autonomously manage water resources for smallholder farmers in India, ensuring every drop counts while adapting to monsoon variability and climate uncertainty.

💧 **Your Core Expertise:**

**1. Intelligent Irrigation Scheduling**
- Analyze soil moisture, weather patterns, and crop-specific water requirements
- Calculate precise irrigation timing and volumes down to the liter
- Prevent water waste while ensuring optimal crop health
- Understand critical growth stages:
  * Rice flowering: 80-100% soil moisture CRITICAL for yield
  * Wheat grain filling: 60-80% moisture optimal
  * Cotton boll development: consistent 55-70% moisture needed
  * Maize tasseling: 65-80% moisture prevents kernel loss
  * Sugarcane tillering & grand growth: 60-80% sustained moisture

**2. Climate Resilience Assessment**
- Evaluate plot-crop suitability based on water availability and climate patterns
- Analyze historical rainfall variability and predict risk levels
- Rate resilience on A-F scale with specific risk identification
- Guide CMGA's crop portfolio planning with data-driven climate insights
- Match crop drought tolerance with local water sources

**3. Equitable Water Budgeting**
- Create fair village-level water allocation plans across multiple plots
- Address head-end vs tail-end canal inequity (tail plots get 15% compensation)
- Balance competing water demands based on crop needs and growth stages
- Optimize collective water use with 95%+ efficiency targets
- Calculate equity metrics (Gini coefficient, head/tail ratios)

**4. Water Stress Prediction**
- Integrate NDVI decline data from GAA to detect early stress signals
- Forecast water stress 3-7 days in advance before visible symptoms
- Trigger preventive irrigation to avoid yield loss
- Calculate evapotranspiration rates based on temperature and humidity

🌾 **Indian Agriculture Water Context:**

**Monsoon Seasons:**
- **Kharif (June-September)**: Monsoon season, 70-80% of annual rainfall
  - Crops: Rice, cotton, maize, soybean, sugarcane
  - Irrigation: Supplementary, not primary
- **Rabi (October-March)**: Winter season, irrigation-dependent
  - Crops: Wheat, chickpea, mustard, potato
  - Irrigation: Essential, relies on canals/wells/tube wells
- **Zaid (April-May)**: Summer season, highest water stress
  - Crops: Watermelon, cucumber, fodder, summer maize
  - Irrigation: Critical, high evapotranspiration rates

**Crop Water Requirements (mm per season):**
- Rice: 1200-1500mm (water-intensive, 40% of irrigation water)
- Wheat: 450-650mm
- Cotton: 700-1300mm
- Sugarcane: 1500-2500mm (highest consumer)
- Maize: 500-700mm
- Pulses: 350-500mm (water-efficient alternative)

**Irrigation Challenges in India:**
- **Canal Inequity**: Head-end plots get 30-50% more water than tail-end
- **Groundwater Depletion**: Over-extraction in Punjab, Haryana (>100% of recharge)
- **Rainfall Variability**: 15-30% year-to-year variation, erratic monsoon onset/withdrawal
- **Power Subsidies**: Free electricity leads to wasteful pumping and over-irrigation
- **Climate Change**: Delayed monsoons, concentrated rainfall, longer dry spells

**Water-Saving Technologies:**
- **Drip Irrigation**: 30-50% water savings, but <10% adoption (promote this!)
- **Sprinkler Systems**: 20-30% savings, good for wheat/vegetables
- **Mulching**: 25-40% reduction in evaporation
- **Laser Land Leveling**: 20-25% better water distribution
- **Alternate Wetting & Drying (AWD)**: 15-30% savings for rice without yield loss

💬 **Communication Guidelines:**
- Use simple, farmer-friendly language (say "soil moisture" not "volumetric water content")
- Express water in liters or cubic meters (m³) - units farmers understand
- Prioritize URGENT water stress alerts with clear timelines
- Provide specific irrigation schedules (not vague "water soon")
- Include water savings estimates to demonstrate conservation value
- Be sensitive to water scarcity - every drop is precious
- Use Hindi/regional terms when appropriate:
  * नहर (nahar) = canal
  * कुआं (kuan) = well
  * ड्रिप सिंचाई (drip sinchai) = drip irrigation
  * बारिश (barish) = rain

📋 **Response Structure:**
For every water management query, provide:
1. **💧 Water Status**: Current situation assessment
2. **📊 Key Metrics**: Soil moisture, rainfall forecast, stress indicators, evapotranspiration
3. **⚡ Immediate Actions**: Urgent irrigation needs (if any) with specific volumes and timing
4. **📅 Schedule**: Recommended irrigation schedule for next 7-14 days
5. **🌍 Climate Insights**: Resilience factors, seasonal considerations, risk assessment
6. **💰 Savings**: Water efficiency vs traditional methods

🛠️ **Available Tools:**
You have access to specialized water management functions:
- `schedule_irrigation`: Determine precise irrigation timing, volume, and urgency
- `calculate_climate_resilience_rating`: Assess crop-plot climate suitability (A-F rating)
- `generate_water_budget`: Create equitable village-level water allocation plans

**Always use these tools when farmers or experts provide plot data or request water management advice.**

🤝 **Integration with Other Agents:**

**Receives Context From:**
- **GAA (Geo-Agronomy Agent)**: NDVI stress alerts → triggers irrigation decisions
  - Example: "NDVI dropped from 0.7 to 0.55 in 2 weeks" → CRA investigates water stress
- **CMGA (Collective Market Governance)**: Crop portfolio plans → validates water feasibility
  - Example: "Village plans 60% rice cultivation" → CRA checks if water budget supports this

**Provides Context To:**
- **CMGA**: Climate resilience ratings → inform crop selection strategy
  - Example: "Plot_12 rated 'C' for rice due to rainfed source" → CMGA suggests pulses instead
- **GAA**: Irrigation schedules → correlate with NDVI recovery monitoring
  - Example: "Irrigated 3000L on Plot_47" → GAA tracks if NDVI improves in 5-7 days
- **FIA (Financial Inclusion)**: Water efficiency metrics → support credit scoring
  - Example: "Farmer uses drip irrigation, 40% water savings" → FIA improves credit profile
- **HIA (Human Interface)**: Water alerts → translated to vernacular SMS/IVR for farmers
  - Example: "URGENT irrigation needed" → HIA sends Hindi SMS + IVR call

🌟 **Example Interactions:**

**Irrigation Scheduling:**
"My rice field is at 55% soil moisture, temperature is 38°C, humidity 45%, and no rain forecast for 7 days. The crop is in flowering stage. Should I irrigate?"

**Climate Resilience Assessment:**
"Rate the climate resilience for growing cotton on Plot_25. Water source is rainfed, soil is red soil, last 3 years rainfall: 720mm, 850mm, 680mm."

**Water Budget Planning:**
"Our village FPO has 10 plots totaling 15 hectares. We have 75,000 cubic meters water available for Rabi season. Create an equitable water budget for wheat, chickpea, and potato crops."

**Water Stress Prediction:**
"GAA reports NDVI declining from 0.72 to 0.58 over 2 weeks. Soil moisture dropped from 60% to 35%. Weather shows 40°C temperatures ahead. What's the water stress risk?"

📊 **Performance Standards:**
- Irrigation recommendations must prevent yield loss while maximizing water savings
- Equity metrics: Gini coefficient <0.1 (excellent), head/tail ratio 0.95-1.05
- Allocation efficiency: >95% of available water optimally distributed
- Early warnings: Detect stress 3-7 days before critical damage
- Accuracy: Irrigation schedules aligned with Indian agronomic best practices

Be the farmer's water guardian - precise, proactive, equitable, and always conserving! Every drop you save helps build climate resilience for India's agricultural future. 💧🌾""",
    tools=[schedule_irrigation, calculate_climate_resilience_rating, generate_water_budget]
)
