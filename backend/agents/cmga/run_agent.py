#!/usr/bin/env python3
"""
Simple runner for the CMGA Portfolio Optimizer Agent
This script helps you test and run the Google ADK integrated agent
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('cmga_agent.log')
        ]
    )

def check_environment():
    """Check if environment is properly configured"""
    logger = logging.getLogger(__name__)
    
    # Check if .env file exists
    env_file = current_dir / '.env'
    if not env_file.exists():
        logger.warning("⚠️  .env file not found. Creating from template...")
        
        # Copy .env.example to .env
        env_example = current_dir / '.env.example'
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            logger.info("✅ Created .env file from template")
        else:
            logger.error("❌ .env.example not found")
            return False
    
    # Check Google credentials
    creds_file = current_dir / 'config' / 'google-credentials-dev.json'
    if not creds_file.exists():
        logger.warning("⚠️  Google credentials file not found")
        logger.info("   Using placeholder credentials for demo mode")
    
    return True

async def run_integration_demo():
    """Run the integration demonstration"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 Starting CMGA Agent Integration Demo")
        
        # Import and run the integration example
        from integration_example import demonstrate_integration
        await demonstrate_integration()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration demo failed: {e}")
        return False

async def run_portfolio_optimizer():
    """Run the portfolio optimizer directly"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🎯 Starting Portfolio Optimizer Demo")
        
        # Import and run the portfolio optimizer
        from portfolio_optimizer_adk import PortfolioOptimizerADK, CropOption, PortfolioConstraints
        
        # Create sample data
        constraints = PortfolioConstraints(
            total_land=100.0,
            total_water=50000.0,
            total_labor=2500.0,
            total_budget=3500000.0,
            max_crop_diversity=5,
            min_crop_diversity=2,
            risk_tolerance=0.6
        )
        
        crop_options = [
            CropOption(
                name="wheat",
                family="poaceae",
                season="rabi",
                avg_yield=40.0,
                yield_std_dev=5.0,
                avg_price=2000.0,
                cultivation_cost=30000.0,
                water_requirement=400.0,
                labor_days=25.0,
                growing_duration=120,
                soil_types=["loamy", "clay"],
                min_temp=10.0,
                max_temp=25.0
            ),
            CropOption(
                name="rice",
                family="poaceae",
                season="kharif",
                avg_yield=50.0,
                yield_std_dev=8.0,
                avg_price=1800.0,
                cultivation_cost=35000.0,
                water_requirement=800.0,
                labor_days=30.0,
                growing_duration=140,
                soil_types=["clay", "alluvial"],
                min_temp=20.0,
                max_temp=35.0
            )
        ]
        
        market_data = {
            "price_forecast": {"wheat": 2100.0, "rice": 1900.0},
            "volatility": {"wheat": 0.15, "rice": 0.20}
        }
        
        climate_data = {
            "risk_score": {"wheat": 0.2, "rice": 0.3},
            "water_availability": 0.8
        }
        
        yield_forecasts = {
            "wheat": {"predicted": 42.0, "confidence": 0.85},
            "rice": {"predicted": 52.0, "confidence": 0.80}
        }
        
        # Create optimizer and run
        optimizer = PortfolioOptimizerADK()
        
        logger.info("🔄 Running AI-enhanced portfolio optimization...")
        result = await optimizer.optimize_collective_portfolio(
            constraints=constraints,
            crop_options=crop_options,
            market_data=market_data,
            climate_data=climate_data,
            yield_forecasts=yield_forecasts
        )
        
        # Display results
        logger.info("📊 Optimization Results:")
        logger.info(f"   Expected Return: {result.expected_return:.2%}")
        logger.info(f"   Portfolio Risk: {result.portfolio_risk:.2%}")
        logger.info(f"   Sharpe Ratio: {result.sharpe_ratio:.2f}")
        logger.info(f"   AI Confidence: {result.processing_metadata.get('overall_confidence', 0):.2f}")
        
        logger.info("🌾 Crop Allocations:")
        for crop in result.crops:
            logger.info(f"   • {crop.crop_name}: {crop.land_area:.1f} hectares ({crop.expected_return:.2%} return)")
        
        logger.info("💡 AI Recommendations:")
        for rec in result.ai_recommendations:
            logger.info(f"   • {rec}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Portfolio optimizer demo failed: {e}")
        logger.error("   This might be due to missing Google ADK services")
        logger.info("   Try running the integration demo instead: python run_agent.py --demo")
        return False

async def run_simple_test():
    """Run a simple functionality test"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🧪 Running Simple Functionality Test")
        
        # Import test module
        from test_modules_direct import test_basic_functionality
        await test_basic_functionality()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Simple test failed: {e}")
        return False

def main():
    """Main entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="CMGA Portfolio Optimizer Agent Runner")
    parser.add_argument("--demo", action="store_true", help="Run integration demonstration")
    parser.add_argument("--optimizer", action="store_true", help="Run portfolio optimizer directly")
    parser.add_argument("--test", action="store_true", help="Run simple functionality test")
    
    args = parser.parse_args()
    
    logger.info("🎯 CMGA Portfolio Optimizer Agent")
    logger.info("=" * 50)
    
    # Check environment
    if not check_environment():
        logger.error("❌ Environment check failed")
        sys.exit(1)
    
    # Determine what to run
    if args.demo:
        success = asyncio.run(run_integration_demo())
    elif args.optimizer:
        success = asyncio.run(run_portfolio_optimizer())
    elif args.test:
        success = asyncio.run(run_simple_test())
    else:
        # Default: run integration demo
        logger.info("🚀 Running default integration demonstration")
        logger.info("   Use --help to see other options")
        success = asyncio.run(run_integration_demo())
    
    if success:
        logger.info("✅ Agent execution completed successfully!")
    else:
        logger.error("❌ Agent execution failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()