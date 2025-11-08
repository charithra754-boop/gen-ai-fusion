"""
Test AI-powered optimization algorithms implementation
Tests the enhanced portfolio optimization with data preprocessing, Vertex AI integration, and confidence intervals
"""

import asyncio
import pytest
from portfolio_optimizer_adk import (
    PortfolioOptimizerADK, PortfolioConstraints, CropOption, 
    OptimizedPortfolioWithConfidence
)

@pytest.mark.asyncio
async def test_ai_powered_optimization_algorithms():
    """Test the complete AI-powered optimization pipeline"""
    
    # Initialize optimizer
    optimizer = PortfolioOptimizerADK()
    
    # Test constraints
    constraints = PortfolioConstraints(
        total_land=100.0,
        total_water=50000.0,
        total_labor=500.0,
        total_budget=500000.0,
        max_crop_diversity=4,
        min_crop_diversity=2,
        risk_tolerance=0.3
    )
    
    # Test crop options
    crop_options = [
        CropOption(
            name="wheat",
            family="gramineae",
            season="rabi",
            avg_yield=30.0,
            yield_std_dev=5.0,
            avg_price=2000.0,
            cultivation_cost=25000.0,
            water_requirement=400.0,
            labor_days=15.0,
            growing_duration=120,
            soil_types=["loamy", "clay"],
            min_temp=10.0,
            max_temp=25.0
        ),
        CropOption(
            name="rice",
            family="gramineae", 
            season="kharif",
            avg_yield=40.0,
            yield_std_dev=8.0,
            avg_price=1800.0,
            cultivation_cost=30000.0,
            water_requirement=800.0,
            labor_days=20.0,
            growing_duration=150,
            soil_types=["clay", "alluvial"],
            min_temp=20.0,
            max_temp=35.0
        ),
        CropOption(
            name="cotton",
            family="malvaceae",
            season="kharif", 
            avg_yield=15.0,
            yield_std_dev=3.0,
            avg_price=5000.0,
            cultivation_cost=40000.0,
            water_requirement=600.0,
            labor_days=25.0,
            growing_duration=180,
            soil_types=["black", "alluvial"],
            min_temp=18.0,
            max_temp=32.0
        )
    ]
    
    # Test market data
    market_data = {
        "price_history": {
            "wheat": [1800, 1900, 2000, 2100],
            "rice": [1600, 1700, 1800, 1900],
            "cotton": [4500, 4800, 5000, 5200]
        },
        "demand_index": {
            "wheat": 0.8,
            "rice": 0.7,
            "cotton": 0.9
        },
        "volatility": {
            "wheat": 0.15,
            "rice": 0.20,
            "cotton": 0.25
        }
    }
    
    # Test climate data
    climate_data = {
        "temperature_forecast": {
            "min": 15.0,
            "max": 30.0,
            "avgRainfall": 800
        },
        "water_availability": 0.8,
        "risk_score": {
            "wheat": 0.2,
            "rice": 0.3,
            "cotton": 0.4
        },
        "anomaly_detected": False
    }
    
    # Test yield forecasts
    yield_forecasts = {
        "wheat": {"predicted": 32.0, "confidence": 0.8},
        "rice": {"predicted": 42.0, "confidence": 0.7},
        "cotton": {"predicted": 16.0, "confidence": 0.9}
    }
    
    # Execute AI-powered optimization
    result = await optimizer.optimize_collective_portfolio(
        constraints=constraints,
        crop_options=crop_options,
        market_data=market_data,
        climate_data=climate_data,
        yield_forecasts=yield_forecasts
    )
    
    # Verify result structure and AI enhancements
    assert isinstance(result, OptimizedPortfolioWithConfidence)
    assert len(result.crops) > 0
    assert result.expected_return > 0
    assert result.portfolio_risk > 0
    assert result.sharpe_ratio > 0
    
    # Verify AI-powered features
    assert "confidence_intervals" in result.confidence_intervals
    assert "expected_return" in result.confidence_intervals
    assert "portfolio_risk" in result.confidence_intervals
    assert "sharpe_ratio" in result.confidence_intervals
    
    # Verify model explanations
    assert len(result.model_explanations) > 0
    assert "portfolio_composition" in result.model_explanations
    assert "risk_management" in result.model_explanations
    
    # Verify AI recommendations with confidence scores (Requirement 1.5)
    assert len(result.ai_recommendations) > 0
    
    # Verify processing metadata includes AI model versions
    assert "model_versions" in result.processing_metadata
    assert "overall_confidence" in result.processing_metadata
    assert result.processing_metadata["overall_confidence"] > 0
    
    # Verify Sharpe ratio optimization (Requirement 1.4)
    assert result.sharpe_ratio >= 0.5  # Minimum acceptable Sharpe ratio
    
    # Verify confidence intervals are reasonable
    for metric, (lower, upper) in result.confidence_intervals.items():
        assert lower < upper, f"Invalid confidence interval for {metric}"
        assert lower >= 0, f"Negative lower bound for {metric}"
    
    # Verify crop allocations have AI rationale
    for crop_allocation in result.crops:
        assert crop_allocation.ai_rationale is not None
        assert len(crop_allocation.ai_rationale) > 0
        assert crop_allocation.confidence_interval[0] < crop_allocation.confidence_interval[1]
    
    print("✅ AI-powered optimization algorithms test passed!")
    print(f"   Portfolio Return: {result.expected_return:.2%}")
    print(f"   Portfolio Risk: {result.portfolio_risk:.2%}")
    print(f"   Sharpe Ratio: {result.sharpe_ratio:.2f}")
    print(f"   AI Confidence: {result.processing_metadata['overall_confidence']:.2%}")
    print(f"   Crops Allocated: {len(result.crops)}")
    print(f"   AI Recommendations: {len(result.ai_recommendations)}")

@pytest.mark.asyncio
async def test_data_preprocessing_pipeline():
    """Test the data preprocessing pipeline for AI optimization"""
    
    optimizer = PortfolioOptimizerADK()
    
    # Simple test data
    constraints = PortfolioConstraints(
        total_land=50.0, total_water=25000.0, total_labor=250.0,
        total_budget=250000.0, max_crop_diversity=2, min_crop_diversity=1,
        risk_tolerance=0.4
    )
    
    crop_options = [
        CropOption(
            name="test_crop", family="test", season="rabi",
            avg_yield=25.0, yield_std_dev=3.0, avg_price=2500.0,
            cultivation_cost=30000.0, water_requirement=500.0,
            labor_days=18.0, growing_duration=100,
            soil_types=["loamy"], min_temp=12.0, max_temp=28.0
        )
    ]
    
    # Test preprocessing
    preprocessed_data = await optimizer._preprocess_optimization_data(
        constraints, crop_options, {}, {}, {}
    )
    
    # Verify preprocessing results
    assert "crops" in preprocessed_data
    assert "feature_matrix" in preprocessed_data
    assert "correlation_matrix" in preprocessed_data
    assert "constraints" in preprocessed_data
    assert "preprocessing_metadata" in preprocessed_data
    
    # Verify normalized crop data
    assert len(preprocessed_data["crops"]) == 1
    crop_data = preprocessed_data["crops"][0]
    assert "features" in crop_data
    assert "constraints" in crop_data
    
    # Verify feature vector
    features = crop_data["features"]
    required_features = [
        "expected_return", "risk_score", "water_efficiency",
        "labor_efficiency", "cost_efficiency", "yield_stability"
    ]
    for feature in required_features:
        assert feature in features
        assert isinstance(features[feature], (int, float))
    
    print("✅ Data preprocessing pipeline test passed!")

if __name__ == "__main__":
    asyncio.run(test_ai_powered_optimization_algorithms())
    asyncio.run(test_data_preprocessing_pipeline())