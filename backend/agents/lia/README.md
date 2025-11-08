# Logistics Infrastructure Agent (LIA) - Google ADK Implementation

## Overview

The Logistics Infrastructure Agent (LIA) optimizes post-harvest logistics, reduces losses, and provides end-to-end supply chain visibility for agricultural produce using Google's Agent Development Kit (ADK).

## Features

- **Cold Storage Management**: Find and recommend optimal cold storage facilities
- **Route Optimization**: Calculate optimal transportation routes with cost analysis
- **Loss Tracking**: Track and analyze post-harvest losses with prevention recommendations
- **Supply Chain Monitoring**: Real-time monitoring of produce conditions and location
- **Cost Optimization**: Calculate and optimize total logistics costs
- **Logistics Planning**: Comprehensive planning for FPO operations
- **Multilingual Support**: English, Hindi, and Kannada language support
- **Conversational Interface**: Natural language interaction through Google ADK

## Tools Available

### 1. cold_storage_finder
Find and recommend cold storage facilities based on requirements.

**Parameters:**
- `produce_type`: Type of produce to store
- `location`: Location or region to search
- `capacity_needed`: Required storage capacity in metric tons
- `duration`: Storage duration in days (default: 30)
- `language`: Response language (en, hi, kn)

### 2. route_optimizer
Optimize transportation routes for produce delivery.

**Parameters:**
- `origin`: Starting location for transportation
- `destinations`: List of delivery destinations
- `produce_type`: Type of produce being transported
- `vehicle_type`: Type of vehicle (default: truck)
- `language`: Response language (en, hi, kn)

### 3. loss_tracker
Track and analyze post-harvest losses with prevention recommendations.

**Parameters:**
- `produce_type`: Type of produce that experienced loss
- `loss_stage`: Stage where loss occurred (harvest, storage, transport, market)
- `quantity_lost`: Quantity lost in kg or quintals
- `loss_cause`: Cause of loss (spoilage, damage, theft, etc.)
- `language`: Response language (en, hi, kn)

### 4. supply_chain_monitor
Monitor supply chain conditions and provide alerts.

**Parameters:**
- `batch_id`: Unique identifier for produce batch
- `current_stage`: Current stage in supply chain
- `check_conditions`: Whether to check environmental conditions (default: true)
- `language`: Response language (en, hi, kn)

### 5. cost_calculator
Calculate and optimize logistics costs.

**Parameters:**
- `produce_type`: Type of produce
- `quantity`: Quantity in metric tons
- `origin`: Origin location
- `destination`: Destination location
- `include_storage`: Include storage costs (default: false)
- `language`: Response language (en, hi, kn)

### 6. logistics_planner
Create comprehensive logistics plans and schedules.

**Parameters:**
- `fpo_id`: FPO identifier for collective planning
- `produce_types`: Types of produce to plan logistics for
- `season`: Agricultural season (kharif, rabi, zaid)
- `planning_horizon`: Planning horizon in days (default: 90)
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

### Finding Cold Storage
```python
from main import cold_storage_finder
result = cold_storage_finder("tomato", "Bangalore", 50, 30, "en")
```

### Route Optimization
```python
from main import route_optimizer
result = route_optimizer("Bangalore", ["Kolar", "Hassan"], "tomato", "truck", "en")
```

### Loss Tracking
```python
from main import loss_tracker
result = loss_tracker("tomato", "storage", 100, "spoilage", "en")
```

### Supply Chain Monitoring
```python
from main import supply_chain_monitor
result = supply_chain_monitor("BATCH001", "transport", True, "en")
```

### Cost Calculation
```python
from main import cost_calculator
result = cost_calculator("tomato", 10, "Bangalore", "Kolar", True, "en")
```

### Logistics Planning
```python
from main import logistics_planner
result = logistics_planner("FPO001", ["tomato", "onion"], "kharif", 90, "en")
```

## Conversation Examples

### English
- "Find cold storage for 50 tons of tomatoes near Bangalore"
- "What's the best route from Bangalore to Kolar for transporting tomatoes?"
- "I lost 100 kg of tomatoes due to spoilage during storage"
- "Track batch BATCH001 currently in transport"
- "Calculate logistics cost for 10 tons of tomatoes from Bangalore to Kolar"

### Hindi
- "बैंगलोर के पास 50 टन टमाटर के लिए कोल्ड स्टोरेज खोजें"
- "टमाटर परिवहन के लिए बैंगलोर से कोलार तक का बेस्ट रूट क्या है?"
- "स्टोरेज के दौरान खराब होने से 100 किलो टमाटर का नुकसान हुआ"

### Kannada
- "ಬೆಂಗಳೂರಿನ ಬಳಿ 50 ಟನ್ ಟೊಮೇಟೊಗಳಿಗೆ ಕೋಲ್ಡ್ ಸ್ಟೋರೇಜ್ ಹುಡುಕಿ"
- "ಟೊಮೇಟೊ ಸಾರಿಗೆಗಾಗಿ ಬೆಂಗಳೂರಿನಿಂದ ಕೋಲಾರಿಗೆ ಉತ್ತಮ ಮಾರ್ಗ ಯಾವುದು?"
- "ಸಂಗ್ರಹಣೆಯ ಸಮಯದಲ್ಲಿ ಹಾಳಾಗುವಿಕೆಯಿಂದ 100 ಕೆಜಿ ಟೊಮೇಟೊ ನಷ್ಟವಾಯಿತು"

## Data Structures

### Cold Storage Facility
```json
{
  "id": "CS001",
  "name": "Karnataka Cold Storage",
  "location": "Bangalore",
  "total_capacity": 500,
  "available_capacity": 150,
  "temperature_range": "2-8°C",
  "supported_produce": ["tomato", "potato", "onion"],
  "cost_per_ton_per_day": 25,
  "quality_rating": 4.2,
  "distance_km": 65
}
```

### Transport Route
```json
{
  "origin": "Bangalore",
  "destination": "Kolar",
  "distance_km": 65,
  "estimated_time_hours": 1.8,
  "total_cost": 1200,
  "route_quality": "good",
  "traffic_conditions": "moderate"
}
```

### Loss Event
```json
{
  "produce_type": "tomato",
  "loss_stage": "storage",
  "quantity_lost": 100,
  "loss_cause": "spoilage",
  "financial_impact": 15000,
  "prevention_measures": [
    "Maintain temperature",
    "Control humidity",
    "Regular monitoring"
  ]
}
```

## Key Features

### Loss Prevention
- Tracks losses at each stage of supply chain
- Provides specific prevention recommendations
- Calculates financial impact and potential savings
- Benchmarks against industry standards

### Cost Optimization
- Detailed cost breakdown by category
- Optimization suggestions based on analysis
- Comparison with industry averages
- ROI calculations for improvements

### Supply Chain Visibility
- Real-time monitoring of produce conditions
- Environmental condition alerts
- Quality score tracking
- Estimated arrival times

### Regional Adaptation
- State-specific logistics practices
- Local cold storage networks
- Regional transportation hubs
- Cultural and linguistic customization

## Testing

Run the test suite:
```bash
python main.py
```

This will execute all tool functions with sample data and display the results.

## Integration with KisaanMitra

The LIA agent integrates with the KisaanMitra ecosystem by:
- Coordinating with MIA for demand-driven logistics planning
- Supporting CMGA with collective logistics optimization
- Providing cost data to FIA for financial planning
- Enabling FPOs to reduce post-harvest losses significantly

## Performance Metrics

### Target KPIs
- **Loss Reduction**: 15% reduction in post-harvest losses
- **Cost Optimization**: 10% reduction in logistics costs
- **Delivery Time**: 20% improvement in delivery efficiency
- **Storage Utilization**: 85% optimal utilization rate

### Success Factors
- Proper timing of harvest and storage
- Efficient transportation coordination
- Quality maintenance throughout supply chain
- Cost optimization through collective planning

## Future Enhancements

- Integration with real IoT sensor networks
- Advanced ML models for loss prediction
- Blockchain-based supply chain traceability
- Integration with logistics service providers
- Real-time GPS tracking and monitoring
- Automated quality assessment using computer vision