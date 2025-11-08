#!/usr/bin/env python3
"""
Logistics Infrastructure Agent (LIA) - Google ADK Implementation
Optimizes post-harvest logistics, reduces losses, and provides supply chain visibility
"""

import json
import logging
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ColdStorageFacility:
    """Cold storage facility data structure"""
    id: str
    name: str
    location: str
    district: str
    state: str
    total_capacity: float  # metric tons
    available_capacity: float
    temperature_range: str
    supported_produce: List[str]
    cost_per_ton_per_day: float
    quality_rating: float
    contact_phone: str
    distance_km: float

@dataclass
class TransportRoute:
    """Transportation route data structure"""
    id: str
    origin: str
    destination: str
    distance_km: float
    estimated_time_hours: float
    fuel_cost: float
    toll_cost: float
    driver_cost: float
    total_cost: float
    route_quality: str  # good, average, poor
    traffic_conditions: str

@dataclass
class LossEvent:
    """Post-harvest loss event data structure"""
    id: str
    produce_type: str
    loss_stage: str
    quantity_lost: float
    loss_cause: str
    financial_impact: float
    prevention_measures: List[str]
    timestamp: str
    location: str

@dataclass
class SupplyChainStatus:
    """Supply chain monitoring data structure"""
    batch_id: str
    produce_type: str
    current_stage: str
    location: str
    temperature: float
    humidity: float
    quality_score: float
    alerts: List[str]
    estimated_arrival: str
    last_updated: str

class LIAAgent:
    """Logistics Infrastructure Agent implementation"""
    
    def __init__(self):
        self.name = "Logistics Infrastructure Agent"
        self.version = "1.0.0"
        self.supported_languages = ["en", "hi", "kn"]
        self.mock_data = self._initialize_mock_data()
        logger.info(f"Initialized {self.name} v{self.version}")
    
    def _initialize_mock_data(self) -> Dict[str, Any]:
        """Initialize mock logistics data for demonstration"""
        return {
            "cold_storage_facilities": [
                ColdStorageFacility(
                    id="CS001", name="Karnataka Cold Storage", location="Bangalore",
                    district="Bangalore Urban", state="Karnataka", total_capacity=500,
                    available_capacity=150, temperature_range="2-8°C",
                    supported_produce=["tomato", "potato", "onion", "apple"],
                    cost_per_ton_per_day=25, quality_rating=4.2,
                    contact_phone="+91-9876543210", distance_km=0
                ),
                ColdStorageFacility(
                    id="CS002", name="Kolar Agri Storage", location="Kolar",
                    district="Kolar", state="Karnataka", total_capacity=300,
                    available_capacity=80, temperature_range="0-4°C",
                    supported_produce=["tomato", "grapes", "pomegranate"],
                    cost_per_ton_per_day=30, quality_rating=4.5,
                    contact_phone="+91-9876543211", distance_km=65
                ),
                ColdStorageFacility(
                    id="CS003", name="Hassan Food Hub", location="Hassan",
                    district="Hassan", state="Karnataka", total_capacity=800,
                    available_capacity=200, temperature_range="1-6°C",
                    supported_produce=["potato", "onion", "carrot", "cabbage"],
                    cost_per_ton_per_day=22, quality_rating=4.0,
                    contact_phone="+91-9876543212", distance_km=180
                )
            ],
            "transport_rates": {
                "truck": {"base_rate_per_km": 12, "loading_cost": 500, "fuel_efficiency": 4},
                "tempo": {"base_rate_per_km": 8, "loading_cost": 200, "fuel_efficiency": 6},
                "mini_truck": {"base_rate_per_km": 10, "loading_cost": 300, "fuel_efficiency": 5}
            },
            "produce_requirements": {
                "tomato": {"temp_range": "10-12°C", "humidity": "85-90%", "shelf_life_days": 15},
                "onion": {"temp_range": "0-2°C", "humidity": "65-70%", "shelf_life_days": 90},
                "potato": {"temp_range": "2-4°C", "humidity": "90-95%", "shelf_life_days": 120},
                "apple": {"temp_range": "0-2°C", "humidity": "90-95%", "shelf_life_days": 180}
            },
            "loss_prevention_tips": {
                "harvest": ["Harvest at right maturity", "Use proper tools", "Handle gently"],
                "storage": ["Maintain temperature", "Control humidity", "Regular monitoring"],
                "transport": ["Use refrigerated vehicles", "Minimize handling", "Secure packaging"],
                "market": ["Display properly", "First-in-first-out", "Quick turnover"]
            }
        }
    
    def cold_storage_finder(self, produce_type: str, location: str, capacity_needed: float,
                           duration: int = 30, language: str = "en") -> Dict[str, Any]:
        """Find and recommend cold storage facilities"""
        logger.info(f"Finding cold storage for {produce_type} in {location}, capacity: {capacity_needed}MT")
        
        try:
            suitable_facilities = []
            
            for facility in self.mock_data["cold_storage_facilities"]:
                # Check if facility supports the produce type
                if produce_type.lower() in [p.lower() for p in facility.supported_produce]:
                    # Check if capacity is available
                    if facility.available_capacity >= capacity_needed:
                        # Calculate distance (mock calculation)
                        distance = self._calculate_distance(location, facility.location)
                        facility.distance_km = distance
                        
                        # Calculate total cost
                        total_cost = facility.cost_per_ton_per_day * capacity_needed * duration
                        
                        facility_info = asdict(facility)
                        facility_info.update({
                            "total_cost": total_cost,
                            "cost_per_day": facility.cost_per_ton_per_day * capacity_needed,
                            "suitability_score": self._calculate_suitability_score(
                                facility, produce_type, distance, capacity_needed
                            )
                        })
                        suitable_facilities.append(facility_info)
            
            # Sort by suitability score
            suitable_facilities.sort(key=lambda x: x["suitability_score"], reverse=True)
            
            # Add recommendations
            recommendations = self._generate_storage_recommendations(
                suitable_facilities, produce_type, capacity_needed, duration
            )
            
            response = {
                "success": True,
                "data": {
                    "produce_type": produce_type,
                    "location": location,
                    "capacity_needed": capacity_needed,
                    "duration_days": duration,
                    "facilities_found": len(suitable_facilities),
                    "facilities": suitable_facilities[:3],  # Top 3 recommendations
                    "recommendations": recommendations
                },
                "timestamp": datetime.now().isoformat(),
                "message": self._translate_message("Cold storage facilities found successfully", language)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error finding cold storage: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": self._translate_message("Failed to find cold storage facilities", language)
            }
    
    def route_optimizer(self, origin: str, destinations: List[str], produce_type: str,
                       vehicle_type: str = "truck", language: str = "en") -> Dict[str, Any]:
        """Optimize transportation routes for produce delivery"""
        logger.info(f"Optimizing route from {origin} to {destinations} for {produce_type}")
        
        try:
            # Get vehicle specifications
            vehicle_specs = self.mock_data["transport_rates"].get(vehicle_type, 
                                                                self.mock_data["transport_rates"]["truck"])
            
            routes = []
            total_distance = 0
            total_cost = 0
            total_time = 0
            
            current_location = origin
            
            for i, destination in enumerate(destinations):
                # Calculate route details
                distance = self._calculate_distance(current_location, destination)
                travel_time = self._calculate_travel_time(distance, produce_type)
                route_cost = self._calculate_transport_cost(distance, vehicle_specs, produce_type)
                
                route = TransportRoute(
                    id=f"R{i+1:03d}",
                    origin=current_location,
                    destination=destination,
                    distance_km=distance,
                    estimated_time_hours=travel_time,
                    fuel_cost=distance * vehicle_specs["base_rate_per_km"] * 0.6,
                    toll_cost=distance * 0.5 if distance > 50 else 0,
                    driver_cost=travel_time * 150,  # ₹150 per hour
                    total_cost=route_cost,
                    route_quality=random.choice(["good", "average"]),
                    traffic_conditions=random.choice(["light", "moderate", "heavy"])
                )
                
                routes.append(asdict(route))
                total_distance += distance
                total_cost += route_cost
                total_time += travel_time
                current_location = destination
            
            # Generate optimization recommendations
            optimization_tips = self._generate_route_optimization_tips(
                routes, produce_type, total_distance, total_time
            )
            
            response = {
                "success": True,
                "data": {
                    "origin": origin,
                    "destinations": destinations,
                    "produce_type": produce_type,
                    "vehicle_type": vehicle_type,
                    "routes": routes,
                    "summary": {
                        "total_distance_km": round(total_distance, 1),
                        "total_time_hours": round(total_time, 1),
                        "total_cost_inr": round(total_cost, 2),
                        "cost_per_km": round(total_cost / total_distance, 2) if total_distance > 0 else 0,
                        "average_speed_kmh": round(total_distance / total_time, 1) if total_time > 0 else 0
                    },
                    "optimization_tips": optimization_tips
                },
                "timestamp": datetime.now().isoformat(),
                "message": self._translate_message("Route optimization completed successfully", language)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error optimizing route: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": self._translate_message("Failed to optimize transportation route", language)
            }
    
    def loss_tracker(self, produce_type: str, loss_stage: str, quantity_lost: float,
                    loss_cause: str, language: str = "en") -> Dict[str, Any]:
        """Track and analyze post-harvest losses with prevention recommendations"""
        logger.info(f"Tracking loss: {quantity_lost} units of {produce_type} at {loss_stage} stage")
        
        try:
            # Calculate financial impact
            avg_price_per_unit = self._get_average_price(produce_type)
            financial_impact = quantity_lost * avg_price_per_unit
            
            # Generate prevention measures
            prevention_measures = self._get_prevention_measures(loss_stage, loss_cause, produce_type)
            
            # Create loss event
            loss_event = LossEvent(
                id=f"LOSS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                produce_type=produce_type,
                loss_stage=loss_stage,
                quantity_lost=quantity_lost,
                loss_cause=loss_cause,
                financial_impact=financial_impact,
                prevention_measures=prevention_measures,
                timestamp=datetime.now().isoformat(),
                location="Unknown"  # Would be provided in real implementation
            )
            
            # Generate loss analysis
            loss_analysis = self._analyze_loss_patterns(produce_type, loss_stage, loss_cause)
            
            response = {
                "success": True,
                "data": {
                    "loss_event": asdict(loss_event),
                    "analysis": loss_analysis,
                    "prevention_plan": {
                        "immediate_actions": prevention_measures[:2],
                        "long_term_measures": prevention_measures[2:],
                        "estimated_savings": financial_impact * 0.7  # 70% reduction potential
                    },
                    "benchmarks": {
                        "industry_average_loss_percent": self._get_industry_loss_benchmark(loss_stage),
                        "your_loss_percent": self._calculate_loss_percentage(quantity_lost, produce_type),
                        "improvement_potential": "High" if financial_impact > 10000 else "Medium"
                    }
                },
                "timestamp": datetime.now().isoformat(),
                "message": self._translate_message("Loss tracking and analysis completed", language)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error tracking loss: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": self._translate_message("Failed to track and analyze loss", language)
            }
    
    def supply_chain_monitor(self, batch_id: str, current_stage: str,
                           check_conditions: bool = True, language: str = "en") -> Dict[str, Any]:
        """Monitor supply chain conditions and provide alerts"""
        logger.info(f"Monitoring supply chain for batch {batch_id} at {current_stage} stage")
        
        try:
            # Generate mock sensor data
            temperature = random.uniform(-2, 15)  # °C
            humidity = random.uniform(60, 95)  # %
            quality_score = random.uniform(0.7, 1.0)
            
            # Determine produce type from batch ID (mock logic)
            produce_type = random.choice(["tomato", "onion", "potato", "apple"])
            
            # Check conditions against requirements
            alerts = []
            if check_conditions:
                alerts = self._check_environmental_conditions(
                    produce_type, temperature, humidity, current_stage
                )
            
            # Generate supply chain status
            status = SupplyChainStatus(
                batch_id=batch_id,
                produce_type=produce_type,
                current_stage=current_stage,
                location=self._get_stage_location(current_stage),
                temperature=round(temperature, 1),
                humidity=round(humidity, 1),
                quality_score=round(quality_score, 2),
                alerts=alerts,
                estimated_arrival=self._calculate_estimated_arrival(current_stage),
                last_updated=datetime.now().isoformat()
            )
            
            # Generate recommendations
            recommendations = self._generate_monitoring_recommendations(status, alerts)
            
            response = {
                "success": True,
                "data": {
                    "status": asdict(status),
                    "condition_assessment": {
                        "temperature_status": self._assess_temperature(temperature, produce_type),
                        "humidity_status": self._assess_humidity(humidity, produce_type),
                        "overall_condition": "Good" if quality_score > 0.8 else "Fair" if quality_score > 0.6 else "Poor"
                    },
                    "recommendations": recommendations,
                    "next_checkpoint": self._get_next_checkpoint(current_stage),
                    "tracking_history": self._generate_tracking_history(batch_id)
                },
                "timestamp": datetime.now().isoformat(),
                "message": self._translate_message("Supply chain monitoring completed", language)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error monitoring supply chain: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": self._translate_message("Failed to monitor supply chain", language)
            }
    
    def cost_calculator(self, produce_type: str, quantity: float, origin: str,
                       destination: str, include_storage: bool = False, language: str = "en") -> Dict[str, Any]:
        """Calculate and optimize logistics costs"""
        logger.info(f"Calculating logistics costs for {quantity}MT of {produce_type} from {origin} to {destination}")
        
        try:
            # Calculate transportation costs
            distance = self._calculate_distance(origin, destination)
            vehicle_specs = self.mock_data["transport_rates"]["truck"]
            transport_cost = self._calculate_transport_cost(distance, vehicle_specs, produce_type)
            
            # Calculate storage costs if requested
            storage_cost = 0
            storage_days = 0
            if include_storage:
                storage_days = random.randint(7, 30)
                storage_cost = quantity * 25 * storage_days  # ₹25 per MT per day
            
            # Calculate handling and packaging costs
            handling_cost = quantity * 200  # ₹200 per MT
            packaging_cost = quantity * 150  # ₹150 per MT
            
            # Calculate insurance and miscellaneous costs
            insurance_cost = (transport_cost + storage_cost) * 0.02  # 2% of logistics cost
            misc_cost = quantity * 50  # ₹50 per MT
            
            # Total cost calculation
            total_cost = transport_cost + storage_cost + handling_cost + packaging_cost + insurance_cost + misc_cost
            cost_per_unit = total_cost / quantity if quantity > 0 else 0
            
            # Generate cost optimization suggestions
            optimization_suggestions = self._generate_cost_optimization_suggestions(
                transport_cost, storage_cost, distance, quantity
            )
            
            # Cost breakdown
            cost_breakdown = {
                "transportation": {
                    "amount": round(transport_cost, 2),
                    "percentage": round((transport_cost / total_cost) * 100, 1),
                    "details": {
                        "distance_km": distance,
                        "fuel_cost": round(transport_cost * 0.6, 2),
                        "driver_cost": round(transport_cost * 0.3, 2),
                        "vehicle_maintenance": round(transport_cost * 0.1, 2)
                    }
                },
                "storage": {
                    "amount": round(storage_cost, 2),
                    "percentage": round((storage_cost / total_cost) * 100, 1) if total_cost > 0 else 0,
                    "details": {
                        "days": storage_days,
                        "rate_per_mt_per_day": 25
                    }
                },
                "handling_packaging": {
                    "amount": round(handling_cost + packaging_cost, 2),
                    "percentage": round(((handling_cost + packaging_cost) / total_cost) * 100, 1),
                    "details": {
                        "handling": round(handling_cost, 2),
                        "packaging": round(packaging_cost, 2)
                    }
                },
                "insurance_misc": {
                    "amount": round(insurance_cost + misc_cost, 2),
                    "percentage": round(((insurance_cost + misc_cost) / total_cost) * 100, 1),
                    "details": {
                        "insurance": round(insurance_cost, 2),
                        "miscellaneous": round(misc_cost, 2)
                    }
                }
            }
            
            response = {
                "success": True,
                "data": {
                    "produce_type": produce_type,
                    "quantity_mt": quantity,
                    "route": f"{origin} → {destination}",
                    "distance_km": distance,
                    "include_storage": include_storage,
                    "cost_summary": {
                        "total_cost_inr": round(total_cost, 2),
                        "cost_per_mt": round(cost_per_unit, 2),
                        "cost_per_km": round(total_cost / distance, 2) if distance > 0 else 0
                    },
                    "cost_breakdown": cost_breakdown,
                    "optimization_suggestions": optimization_suggestions,
                    "comparison": {
                        "industry_average_cost_per_mt": round(cost_per_unit * random.uniform(1.1, 1.3), 2),
                        "your_efficiency": "Above Average" if cost_per_unit < 2000 else "Average"
                    }
                },
                "timestamp": datetime.now().isoformat(),
                "message": self._translate_message("Logistics cost calculation completed", language)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error calculating logistics costs: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": self._translate_message("Failed to calculate logistics costs", language)
            }
    
    def logistics_planner(self, fpo_id: str, produce_types: List[str], season: str,
                         planning_horizon: int = 90, language: str = "en") -> Dict[str, Any]:
        """Create comprehensive logistics plans and schedules"""
        logger.info(f"Creating logistics plan for FPO {fpo_id}, season: {season}")
        
        try:
            # Generate logistics timeline
            timeline = self._generate_logistics_timeline(produce_types, season, planning_horizon)
            
            # Calculate resource requirements
            resource_requirements = self._calculate_resource_requirements(produce_types, season)
            
            # Generate storage allocation plan
            storage_plan = self._generate_storage_allocation_plan(produce_types, fpo_id)
            
            # Create transportation schedule
            transport_schedule = self._generate_transport_schedule(produce_types, season)
            
            # Calculate total logistics budget
            total_budget = self._calculate_logistics_budget(produce_types, resource_requirements)
            
            # Generate risk assessment
            risk_assessment = self._generate_logistics_risk_assessment(produce_types, season)
            
            # Create KPI targets
            kpi_targets = {
                "loss_reduction_target": "15%",
                "cost_optimization_target": "10%",
                "delivery_time_improvement": "20%",
                "storage_utilization_target": "85%"
            }
            
            response = {
                "success": True,
                "data": {
                    "fpo_id": fpo_id,
                    "season": season,
                    "planning_horizon_days": planning_horizon,
                    "produce_types": produce_types,
                    "logistics_timeline": timeline,
                    "resource_requirements": resource_requirements,
                    "storage_plan": storage_plan,
                    "transport_schedule": transport_schedule,
                    "budget_estimate": {
                        "total_budget_inr": round(total_budget, 2),
                        "budget_breakdown": {
                            "transportation": round(total_budget * 0.4, 2),
                            "storage": round(total_budget * 0.3, 2),
                            "handling": round(total_budget * 0.2, 2),
                            "contingency": round(total_budget * 0.1, 2)
                        }
                    },
                    "risk_assessment": risk_assessment,
                    "kpi_targets": kpi_targets,
                    "success_factors": [
                        "Proper timing of harvest and storage",
                        "Efficient transportation coordination",
                        "Quality maintenance throughout supply chain",
                        "Cost optimization through collective planning"
                    ]
                },
                "timestamp": datetime.now().isoformat(),
                "message": self._translate_message("Comprehensive logistics plan created successfully", language)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating logistics plan: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": self._translate_message("Failed to create logistics plan", language)
            }
    
    # Helper methods
    
    def _calculate_distance(self, origin: str, destination: str) -> float:
        """Calculate distance between two locations (mock implementation)"""
        # Mock distance calculation based on location names
        distances = {
            ("bangalore", "kolar"): 65,
            ("bangalore", "hassan"): 180,
            ("kolar", "hassan"): 120,
            ("bangalore", "mysore"): 150,
            ("hassan", "mangalore"): 200
        }
        
        key = (origin.lower(), destination.lower())
        reverse_key = (destination.lower(), origin.lower())
        
        if key in distances:
            return distances[key]
        elif reverse_key in distances:
            return distances[reverse_key]
        else:
            # Random distance for unknown routes
            return random.uniform(50, 300)
    
    def _calculate_travel_time(self, distance: float, produce_type: str) -> float:
        """Calculate travel time considering produce requirements"""
        base_speed = 45  # km/h
        
        # Adjust speed based on produce type
        if produce_type.lower() in ["tomato", "grapes"]:
            base_speed *= 0.8  # Slower for delicate produce
        
        return distance / base_speed
    
    def _calculate_transport_cost(self, distance: float, vehicle_specs: Dict, produce_type: str) -> float:
        """Calculate transportation cost"""
        base_cost = distance * vehicle_specs["base_rate_per_km"]
        loading_cost = vehicle_specs["loading_cost"]
        
        # Add premium for temperature-sensitive produce
        if produce_type.lower() in ["tomato", "grapes", "apple"]:
            base_cost *= 1.3  # 30% premium for refrigerated transport
        
        return base_cost + loading_cost
    
    def _calculate_suitability_score(self, facility: ColdStorageFacility, produce_type: str,
                                   distance: float, capacity_needed: float) -> float:
        """Calculate facility suitability score"""
        score = 0
        
        # Quality rating (40% weight)
        score += (facility.quality_rating / 5.0) * 40
        
        # Distance factor (30% weight) - closer is better
        distance_score = max(0, (300 - distance) / 300) * 30
        score += distance_score
        
        # Capacity utilization (20% weight) - not too full, not too empty
        utilization = capacity_needed / facility.available_capacity
        capacity_score = max(0, (1 - abs(utilization - 0.5)) * 2) * 20
        score += capacity_score
        
        # Cost factor (10% weight) - lower cost is better
        cost_score = max(0, (50 - facility.cost_per_ton_per_day) / 50) * 10
        score += cost_score
        
        return round(score, 1)
    
    def _generate_storage_recommendations(self, facilities: List[Dict], produce_type: str,
                                        capacity: float, duration: int) -> List[str]:
        """Generate storage recommendations"""
        recommendations = []
        
        if not facilities:
            recommendations.append("No suitable facilities found. Consider expanding search radius.")
            return recommendations
        
        best_facility = facilities[0]
        recommendations.append(f"Recommended: {best_facility['name']} with {best_facility['suitability_score']}% suitability")
        
        if best_facility['distance_km'] > 100:
            recommendations.append("Consider facilities closer to reduce transportation costs")
        
        if duration > 30:
            recommendations.append("For long-term storage, negotiate better rates with facility")
        
        recommendations.append(f"Monitor temperature regularly for {produce_type}")
        
        return recommendations
    
    def _generate_route_optimization_tips(self, routes: List[Dict], produce_type: str,
                                        total_distance: float, total_time: float) -> List[str]:
        """Generate route optimization tips"""
        tips = []
        
        if total_time > 8:
            tips.append("Consider overnight stops to maintain driver alertness")
        
        if produce_type.lower() in ["tomato", "grapes"]:
            tips.append("Use refrigerated transport to maintain quality")
        
        if total_distance > 200:
            tips.append("Plan fuel stops and vehicle maintenance checks")
        
        tips.append("Load produce during cooler hours (early morning/evening)")
        tips.append("Use GPS tracking for real-time monitoring")
        
        return tips
    
    def _get_average_price(self, produce_type: str) -> float:
        """Get average price for produce type"""
        prices = {
            "tomato": 1500, "onion": 2400, "potato": 1000,
            "apple": 8000, "grapes": 6000, "rice": 3850
        }
        return prices.get(produce_type.lower(), 2000)
    
    def _get_prevention_measures(self, stage: str, cause: str, produce_type: str) -> List[str]:
        """Get loss prevention measures"""
        base_measures = self.mock_data["loss_prevention_tips"].get(stage, [])
        
        specific_measures = []
        if cause.lower() == "spoilage":
            specific_measures = ["Improve temperature control", "Reduce humidity", "Better ventilation"]
        elif cause.lower() == "damage":
            specific_measures = ["Use proper packaging", "Gentle handling", "Avoid overloading"]
        elif cause.lower() == "theft":
            specific_measures = ["Improve security", "Install CCTV", "Better lighting"]
        
        return base_measures + specific_measures
    
    def _analyze_loss_patterns(self, produce_type: str, stage: str, cause: str) -> Dict[str, Any]:
        """Analyze loss patterns and trends"""
        return {
            "common_causes_at_stage": [cause, "temperature_fluctuation", "poor_handling"],
            "seasonal_pattern": f"{produce_type} losses typically higher in summer months",
            "industry_benchmark": f"Average {stage} loss: {random.randint(5, 15)}%",
            "improvement_potential": "High - with proper measures, losses can be reduced by 60-80%"
        }
    
    def _get_industry_loss_benchmark(self, stage: str) -> float:
        """Get industry loss benchmarks by stage"""
        benchmarks = {
            "harvest": 8.5, "storage": 12.3, "transport": 6.7, "market": 4.2
        }
        return benchmarks.get(stage, 10.0)
    
    def _calculate_loss_percentage(self, quantity_lost: float, produce_type: str) -> float:
        """Calculate loss percentage (mock calculation)"""
        # Assume total quantity based on produce type
        total_quantities = {
            "tomato": 1000, "onion": 1500, "potato": 2000, "apple": 500
        }
        total = total_quantities.get(produce_type.lower(), 1000)
        return round((quantity_lost / total) * 100, 1)
    
    def _check_environmental_conditions(self, produce_type: str, temperature: float,
                                      humidity: float, stage: str) -> List[str]:
        """Check environmental conditions and generate alerts"""
        alerts = []
        requirements = self.mock_data["produce_requirements"].get(produce_type, {})
        
        if "temp_range" in requirements:
            temp_range = requirements["temp_range"]
            min_temp, max_temp = map(float, temp_range.replace("°C", "").split("-"))
            
            if temperature < min_temp:
                alerts.append(f"Temperature too low: {temperature}°C (min: {min_temp}°C)")
            elif temperature > max_temp:
                alerts.append(f"Temperature too high: {temperature}°C (max: {max_temp}°C)")
        
        if "humidity" in requirements:
            humidity_range = requirements["humidity"]
            min_hum, max_hum = map(float, humidity_range.replace("%", "").split("-"))
            
            if humidity < min_hum:
                alerts.append(f"Humidity too low: {humidity}% (min: {min_hum}%)")
            elif humidity > max_hum:
                alerts.append(f"Humidity too high: {humidity}% (max: {max_hum}%)")
        
        return alerts
    
    def _get_stage_location(self, stage: str) -> str:
        """Get location based on supply chain stage"""
        locations = {
            "harvest": "Farm", "storage": "Cold Storage Facility",
            "transport": "In Transit", "market": "Market/Distribution Center"
        }
        return locations.get(stage, "Unknown Location")
    
    def _calculate_estimated_arrival(self, current_stage: str) -> str:
        """Calculate estimated arrival time"""
        if current_stage == "transport":
            arrival_time = datetime.now() + timedelta(hours=random.randint(2, 12))
        else:
            arrival_time = datetime.now() + timedelta(days=random.randint(1, 5))
        
        return arrival_time.strftime("%Y-%m-%d %H:%M")
    
    def _assess_temperature(self, temperature: float, produce_type: str) -> str:
        """Assess temperature status"""
        requirements = self.mock_data["produce_requirements"].get(produce_type, {})
        if "temp_range" in requirements:
            temp_range = requirements["temp_range"]
            min_temp, max_temp = map(float, temp_range.replace("°C", "").split("-"))
            
            if min_temp <= temperature <= max_temp:
                return "Optimal"
            elif abs(temperature - (min_temp + max_temp) / 2) <= 2:
                return "Acceptable"
            else:
                return "Critical"
        return "Unknown"
    
    def _assess_humidity(self, humidity: float, produce_type: str) -> str:
        """Assess humidity status"""
        requirements = self.mock_data["produce_requirements"].get(produce_type, {})
        if "humidity" in requirements:
            humidity_range = requirements["humidity"]
            min_hum, max_hum = map(float, humidity_range.replace("%", "").split("-"))
            
            if min_hum <= humidity <= max_hum:
                return "Optimal"
            elif abs(humidity - (min_hum + max_hum) / 2) <= 5:
                return "Acceptable"
            else:
                return "Critical"
        return "Unknown"
    
    def _generate_monitoring_recommendations(self, status: SupplyChainStatus, alerts: List[str]) -> List[str]:
        """Generate monitoring recommendations"""
        recommendations = []
        
        if alerts:
            recommendations.append("Immediate attention required - environmental conditions not optimal")
            recommendations.append("Contact facility manager to adjust temperature/humidity")
        else:
            recommendations.append("Conditions are optimal - continue monitoring")
        
        if status.quality_score < 0.8:
            recommendations.append("Quality degradation detected - consider expedited delivery")
        
        recommendations.append("Schedule next quality check within 4 hours")
        
        return recommendations
    
    def _get_next_checkpoint(self, current_stage: str) -> str:
        """Get next checkpoint in supply chain"""
        checkpoints = {
            "harvest": "Storage Facility",
            "storage": "Loading for Transport",
            "transport": "Destination Market",
            "market": "Final Delivery"
        }
        return checkpoints.get(current_stage, "Unknown")
    
    def _generate_tracking_history(self, batch_id: str) -> List[Dict[str, Any]]:
        """Generate mock tracking history"""
        history = []
        stages = ["harvest", "storage", "transport"]
        
        for i, stage in enumerate(stages):
            timestamp = datetime.now() - timedelta(hours=(len(stages) - i) * 6)
            history.append({
                "stage": stage,
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M"),
                "location": self._get_stage_location(stage),
                "status": "Completed" if i < len(stages) - 1 else "In Progress"
            })
        
        return history
    
    def _generate_cost_optimization_suggestions(self, transport_cost: float, storage_cost: float,
                                              distance: float, quantity: float) -> List[str]:
        """Generate cost optimization suggestions"""
        suggestions = []
        
        if transport_cost > storage_cost * 2:
            suggestions.append("Transportation is major cost driver - consider consolidating shipments")
        
        if distance > 200:
            suggestions.append("Long distance transport - explore rail or multi-modal options")
        
        if quantity < 5:
            suggestions.append("Small quantity - consider grouping with other farmers for better rates")
        
        suggestions.append("Negotiate bulk rates for regular shipments")
        suggestions.append("Consider seasonal pricing for storage facilities")
        
        return suggestions
    
    def _generate_logistics_timeline(self, produce_types: List[str], season: str, horizon: int) -> List[Dict[str, Any]]:
        """Generate logistics timeline"""
        timeline = []
        
        for i, produce in enumerate(produce_types):
            harvest_date = datetime.now() + timedelta(days=i * 15)
            storage_date = harvest_date + timedelta(days=1)
            transport_date = storage_date + timedelta(days=random.randint(7, 30))
            
            timeline.append({
                "produce": produce,
                "harvest_window": harvest_date.strftime("%Y-%m-%d"),
                "storage_start": storage_date.strftime("%Y-%m-%d"),
                "transport_schedule": transport_date.strftime("%Y-%m-%d"),
                "market_arrival": (transport_date + timedelta(days=1)).strftime("%Y-%m-%d")
            })
        
        return timeline
    
    def _calculate_resource_requirements(self, produce_types: List[str], season: str) -> Dict[str, Any]:
        """Calculate resource requirements"""
        return {
            "storage_capacity_mt": len(produce_types) * random.randint(50, 200),
            "transport_vehicles": math.ceil(len(produce_types) / 2),
            "cold_storage_days": random.randint(15, 45),
            "handling_workforce": len(produce_types) * 3,
            "packaging_materials": f"{len(produce_types) * 1000} units"
        }
    
    def _generate_storage_allocation_plan(self, produce_types: List[str], fpo_id: str) -> Dict[str, Any]:
        """Generate storage allocation plan"""
        facilities = self.mock_data["cold_storage_facilities"]
        
        allocation = {}
        for i, produce in enumerate(produce_types):
            facility = facilities[i % len(facilities)]
            allocation[produce] = {
                "facility": facility.name,
                "location": facility.location,
                "allocated_capacity": random.randint(20, 100),
                "cost_per_day": facility.cost_per_ton_per_day
            }
        
        return allocation
    
    def _generate_transport_schedule(self, produce_types: List[str], season: str) -> List[Dict[str, Any]]:
        """Generate transport schedule"""
        schedule = []
        
        for produce in produce_types:
            schedule.append({
                "produce": produce,
                "vehicle_type": "refrigerated_truck",
                "departure_time": "06:00 AM",  # Early morning for freshness
                "estimated_duration": f"{random.randint(4, 12)} hours",
                "route_priority": "high" if produce in ["tomato", "grapes"] else "medium"
            })
        
        return schedule
    
    def _calculate_logistics_budget(self, produce_types: List[str], resources: Dict[str, Any]) -> float:
        """Calculate total logistics budget"""
        base_cost_per_produce = random.randint(50000, 150000)
        return len(produce_types) * base_cost_per_produce
    
    def _generate_logistics_risk_assessment(self, produce_types: List[str], season: str) -> Dict[str, Any]:
        """Generate logistics risk assessment"""
        return {
            "weather_risk": "Medium" if season == "monsoon" else "Low",
            "transport_risk": "Low",
            "storage_risk": "Medium",
            "market_risk": "Medium",
            "mitigation_strategies": [
                "Diversify storage facilities",
                "Maintain backup transportation options",
                "Monitor weather forecasts closely",
                "Implement quality control checkpoints"
            ]
        }
    
    def _translate_message(self, message: str, language: str) -> str:
        """Translate messages to specified language"""
        if language == "hi":
            translations = {
                "Cold storage facilities found successfully": "कोल्ड स्टोरेज सुविधाएं सफलतापूर्वक मिलीं",
                "Failed to find cold storage facilities": "कोल्ड स्टोरेज सुविधाएं खोजने में विफल",
                "Route optimization completed successfully": "रूट अनुकूलन सफलतापूर्वक पूर्ण",
                "Failed to optimize transportation route": "परिवहन मार्ग अनुकूलन में विफल",
                "Loss tracking and analysis completed": "नुकसान ट्रैकिंग और विश्लेषण पूर्ण",
                "Failed to track and analyze loss": "नुकसान ट्रैकिंग और विश्लेषण में विफल",
                "Supply chain monitoring completed": "आपूर्ति श्रृंखला निगरानी पूर्ण",
                "Failed to monitor supply chain": "आपूर्ति श्रृंखला निगरानी में विफल",
                "Logistics cost calculation completed": "लॉजिस्टिक्स लागत गणना पूर्ण",
                "Failed to calculate logistics costs": "लॉजिस्टिक्स लागत गणना में विफल",
                "Comprehensive logistics plan created successfully": "व्यापक लॉजिस्टिक्स योजना सफलतापूर्वक बनाई गई",
                "Failed to create logistics plan": "लॉजिस्टिक्स योजना बनाने में विफल"
            }
            return translations.get(message, message)
        elif language == "kn":
            translations = {
                "Cold storage facilities found successfully": "ಕೋಲ್ಡ್ ಸ್ಟೋರೇಜ್ ಸೌಲಭ್ಯಗಳು ಯಶಸ್ವಿಯಾಗಿ ಕಂಡುಬಂದಿವೆ",
                "Failed to find cold storage facilities": "ಕೋಲ್ಡ್ ಸ್ಟೋರೇಜ್ ಸೌಲಭ್ಯಗಳನ್ನು ಹುಡುಕುವಲ್ಲಿ ವಿಫಲವಾಗಿದೆ",
                "Route optimization completed successfully": "ಮಾರ್ಗ ಅನುಕೂಲೀಕರಣ ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ",
                "Failed to optimize transportation route": "ಸಾರಿಗೆ ಮಾರ್ಗ ಅನುಕೂಲೀಕರಣದಲ್ಲಿ ವಿಫಲವಾಗಿದೆ",
                "Loss tracking and analysis completed": "ನಷ್ಟ ಟ್ರ್ಯಾಕಿಂಗ್ ಮತ್ತು ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ",
                "Failed to track and analyze loss": "ನಷ್ಟ ಟ್ರ್ಯಾಕಿಂಗ್ ಮತ್ತು ವಿಶ್ಲೇಷಣೆಯಲ್ಲಿ ವಿಫಲವಾಗಿದೆ",
                "Supply chain monitoring completed": "ಪೂರೈಕೆ ಸರಪಳಿ ಮೇಲ್ವಿಚಾರಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ",
                "Failed to monitor supply chain": "ಪೂರೈಕೆ ಸರಪಳಿ ಮೇಲ್ವಿಚಾರಣೆಯಲ್ಲಿ ವಿಫಲವಾಗಿದೆ",
                "Logistics cost calculation completed": "ಲಾಜಿಸ್ಟಿಕ್ಸ್ ವೆಚ್ಚ ಲೆಕ್ಕಾಚಾರ ಪೂರ್ಣಗೊಂಡಿದೆ",
                "Failed to calculate logistics costs": "ಲಾಜಿಸ್ಟಿಕ್ಸ್ ವೆಚ್ಚ ಲೆಕ್ಕಾಚಾರದಲ್ಲಿ ವಿಫಲವಾಗಿದೆ",
                "Comprehensive logistics plan created successfully": "ಸಮಗ್ರ ಲಾಜಿಸ್ಟಿಕ್ಸ್ ಯೋಜನೆಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ರಚಿಸಲಾಗಿದೆ",
                "Failed to create logistics plan": "ಲಾಜಿಸ್ಟಿಕ್ಸ್ ಯೋಜನೆ ರಚಿಸುವಲ್ಲಿ ವಿಫಲವಾಗಿದೆ"
            }
            return translations.get(message, message)
        return message

# Google ADK tool functions
def cold_storage_finder(produce_type: str, location: str, capacity_needed: float,
                       duration: int = 30, language: str = "en") -> str:
    """Tool function for finding cold storage facilities"""
    agent = LIAAgent()
    result = agent.cold_storage_finder(produce_type, location, capacity_needed, duration, language)
    return json.dumps(result, indent=2)

def route_optimizer(origin: str, destinations: List[str], produce_type: str,
                   vehicle_type: str = "truck", language: str = "en") -> str:
    """Tool function for route optimization"""
    agent = LIAAgent()
    result = agent.route_optimizer(origin, destinations, produce_type, vehicle_type, language)
    return json.dumps(result, indent=2)

def loss_tracker(produce_type: str, loss_stage: str, quantity_lost: float,
                loss_cause: str, language: str = "en") -> str:
    """Tool function for loss tracking"""
    agent = LIAAgent()
    result = agent.loss_tracker(produce_type, loss_stage, quantity_lost, loss_cause, language)
    return json.dumps(result, indent=2)

def supply_chain_monitor(batch_id: str, current_stage: str,
                        check_conditions: bool = True, language: str = "en") -> str:
    """Tool function for supply chain monitoring"""
    agent = LIAAgent()
    result = agent.supply_chain_monitor(batch_id, current_stage, check_conditions, language)
    return json.dumps(result, indent=2)

def cost_calculator(produce_type: str, quantity: float, origin: str,
                   destination: str, include_storage: bool = False, language: str = "en") -> str:
    """Tool function for cost calculation"""
    agent = LIAAgent()
    result = agent.cost_calculator(produce_type, quantity, origin, destination, include_storage, language)
    return json.dumps(result, indent=2)

def logistics_planner(fpo_id: str, produce_types: List[str], season: str,
                     planning_horizon: int = 90, language: str = "en") -> str:
    """Tool function for logistics planning"""
    agent = LIAAgent()
    result = agent.logistics_planner(fpo_id, produce_types, season, planning_horizon, language)
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    # Test the agent
    agent = LIAAgent()
    
    print("=== Testing LIA Agent ===")
    
    # Test cold storage finder
    print("\n1. Cold Storage Finder:")
    storage = agent.cold_storage_finder("tomato", "Bangalore", 50, 30, "en")
    print(json.dumps(storage, indent=2))
    
    # Test route optimizer
    print("\n2. Route Optimizer:")
    route = agent.route_optimizer("Bangalore", ["Kolar", "Hassan"], "tomato", "truck", "en")
    print(json.dumps(route, indent=2))
    
    # Test loss tracker
    print("\n3. Loss Tracker:")
    loss = agent.loss_tracker("tomato", "storage", 100, "spoilage", "en")
    print(json.dumps(loss, indent=2))
    
    # Test supply chain monitor
    print("\n4. Supply Chain Monitor:")
    monitor = agent.supply_chain_monitor("BATCH001", "transport", True, "en")
    print(json.dumps(monitor, indent=2))
    
    # Test cost calculator
    print("\n5. Cost Calculator:")
    cost = agent.cost_calculator("tomato", 10, "Bangalore", "Kolar", True, "en")
    print(json.dumps(cost, indent=2))
    
    # Test logistics planner
    print("\n6. Logistics Planner:")
    plan = agent.logistics_planner("FPO001", ["tomato", "onion"], "kharif", 90, "en")
    print(json.dumps(plan, indent=2))