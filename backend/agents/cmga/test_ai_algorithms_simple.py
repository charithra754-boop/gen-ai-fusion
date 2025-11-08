"""
Simple test for AI optimization algorithms functionality
Tests core methods without full integration
"""

import asyncio
import sys
import os

# Add the parent directory to the path to handle imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_ai_optimization_methods():
    """Test individual AI optimization methods"""
    
    # Mock the ADK service manager to avoid import issues
    class MockADKService:
        async def initialize(self):
            return True
        
        async def optimize_portfolio(self, **kwargs):
            return {
                "optimized_portfolio": {
                    "crops": ["wheat", "rice", "cotton"],
                    "allocations": [0.4, 0.35, 0.25],
                    "expected_return": 0.18,
                    "risk": 0.12,
                    "confidence": 0.85
                },
                "ai_insights": [
                    "Diversification reduces risk by 23%",
                    "Weather patterns favor wheat this season",
                    "Cotton prices expected to rise 12%"
                ],
                "processing_metadata": {
                    "processing_time_ms": 750,
                    "iterations": 500
                }
            }
    
    # Import and test the optimizer with mocked service
    try:
        from portfolio_optimizer_adk import PortfolioOptimizerADK, PortfolioConstraints, CropOption
        
        # Create optimizer with mock service
        optimizer = PortfolioOptimizerADK(adk_service_manager=MockADKService())
        
        # Test data preprocessing pipeline
        constraints = PortfolioConstraints(
            total_land=100.0, total_water=50000.0, total_labor=500.0,
            total_budget=500000.0, max_crop_diversity=3, min_crop_diversity=2,
            risk_tolerance=0.3
        )
        
        crop_options = [
            CropOption(
                name="wheat", family="gramineae", season="rabi",
                avg_yield=30.0, yield_std_dev=5.0, avg_price=2000.0,
                cultivation_cost=25000.0, water_requirement=400.0,
                labor_days=15.0, growing_duration=120,
                soil_types=["loamy"], min_temp=10.0, max_temp=25.0
            ),
            CropOption(
                name="rice", family="gramineae", season="kharif",
                avg_yield=40.0, yield_std_dev=8.0, avg_price=1800.0,
                cultivation_cost=30000.0, water_requirement=800.0,
                labor_days=20.0, growing_duration=150,
                soil_types=["clay"], min_temp=20.0, max_temp=35.0
            )
        ]
        
        # Test helper methods
        print("Testing AI optimization helper methods...")
        
        # Test seasonal factor calculation
        seasonal_factor = optimizer._get_seasonal_factor("rabi")
        assert seasonal_factor == 1.0
        print(f"✅ Seasonal factor for rabi: {seasonal_factor}")
        
        # Test diversification benefit calculation
        div_benefit = optimizer._calculate_diversification_benefit(crop_options[0], crop_options)
        assert 0 < div_benefit <= 1.0
        print(f"✅ Diversification benefit: {div_benefit:.3f}")
        
        # Test correlation matrix calculation
        feature_matrix = [[0.15, 0.2, 0.8], [0.12, 0.25, 0.7]]
        correlation_matrix = optimizer._calculate_correlation_matrix(feature_matrix)
        assert len(correlation_matrix) == 2
        assert len(correlation_matrix[0]) == 2
        print(f"✅ Correlation matrix calculated: {len(correlation_matrix)}x{len(correlation_matrix[0])}")
        
        # Test Sharpe ratio calculation
        sharpe_ratio = optimizer._calculate_sharpe_ratio(0.15, 0.08)
        assert sharpe_ratio > 0
        print(f"✅ Sharpe ratio: {sharpe_ratio:.2f}")
        
        # Test risk categorization
        risk_category = optimizer._categorize_risk(0.4)
        assert risk_category in ["low", "medium", "high"]
        print(f"✅ Risk category for 0.4: {risk_category}")
        
        # Test Sharpe percentile calculation
        sharpe_percentile = optimizer._calculate_sharpe_percentile(1.5)
        assert 0 <= sharpe_percentile <= 100
        print(f"✅ Sharpe percentile for 1.5: {sharpe_percentile}%")
        
        # Test data preprocessing pipeline
        print("\nTesting data preprocessing pipeline...")
        preprocessed_data = await optimizer._preprocess_optimization_data(
            constraints, crop_options, {}, {}, {}
        )
        
        assert "crops" in preprocessed_data
        assert "feature_matrix" in preprocessed_data
        assert "correlation_matrix" in preprocessed_data
        assert len(preprocessed_data["crops"]) == 2
        print(f"✅ Preprocessed {len(preprocessed_data['crops'])} crops")
        print(f"✅ Feature matrix shape: {len(preprocessed_data['feature_matrix'])}x{len(preprocessed_data['feature_matrix'][0]) if preprocessed_data['feature_matrix'] else 0}")
        
        # Test confidence interval calculation
        print("\nTesting confidence interval calculation...")
        from portfolio_optimizer_adk import CropAllocation
        
        mock_allocations = [
            CropAllocation(
                crop_index=0, crop_name="wheat", land_area=40.0,
                expected_return=0.15, risk=0.2, water_needed=16000.0,
                labor_needed=600.0, cost_required=1000000.0,
                confidence_interval=(0.12, 0.18), ai_rationale="Test allocation"
            )
        ]
        
        portfolio_metrics = {"expected_return": 0.15, "portfolio_risk": 0.08}
        confidence_intervals = await optimizer._calculate_confidence_intervals(
            portfolio_metrics, mock_allocations, preprocessed_data
        )
        
        assert "expected_return" in confidence_intervals
        assert "portfolio_risk" in confidence_intervals
        assert "sharpe_ratio" in confidence_intervals
        print(f"✅ Confidence intervals calculated for {len(confidence_intervals)} metrics")
        
        print("\n🎉 All AI optimization algorithm tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_optimization_methods())
    if success:
        print("\n✅ AI-powered optimization algorithms implementation verified!")
    else:
        print("\n❌ AI-powered optimization algorithms test failed!")
        sys.exit(1)