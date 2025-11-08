#!/usr/bin/env python3
"""
Test script for ADK Service Manager batching and caching capabilities
"""

import asyncio
import logging
import sys
import os
import time
from typing import Dict, Any

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.adk_service_manager import get_adk_service_manager, initialize_adk_services
from services.batching import BatchConfig, BatchStrategy
from services.caching import CacheConfig, CacheStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_batching_functionality():
    """Test request batching functionality"""
    logger.info("=== Testing Batching Functionality ===")
    
    # Initialize and get service manager
    await initialize_adk_services()
    service_manager = get_adk_service_manager()
    
    # Configure batching
    service_manager.configure_batching(
        max_batch_size=3,
        max_wait_time_seconds=1.0,
        strategy=BatchStrategy.HYBRID
    )
    
    # Test data
    market_data = {"prices": [100, 110, 105], "volumes": [1000, 1200, 1100]}
    climate_data = {"temperature": 25, "rainfall": 50, "humidity": 60}
    yield_data = {"historical_yields": [5.2, 5.8, 5.5], "projected_yield": 5.6}
    
    # Submit multiple requests concurrently to test batching
    logger.info("Submitting multiple portfolio optimization requests...")
    
    start_time = time.time()
    
    tasks = []
    for i in range(5):
        # Vary the data slightly for each request
        modified_market_data = {**market_data, "request_id": i}
        
        task = service_manager.optimize_portfolio(
            market_data=modified_market_data,
            climate_data=climate_data,
            yield_data=yield_data,
            enable_batching=True,
            priority=i  # Different priorities
        )
        tasks.append(task)
    
    # Execute all requests
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    
    logger.info(f"Completed {len(results)} requests in {end_time - start_time:.2f} seconds")
    
    # Check results
    for i, result in enumerate(results):
        logger.info(f"Request {i}: Batched={result['processing_metadata']['batched']}")
    
    # Get batch statistics
    batch_stats = await service_manager.get_batch_stats()
    logger.info(f"Batch statistics: {batch_stats}")
    
    return service_manager

async def test_caching_functionality(service_manager: ADKServiceManager):
    """Test caching functionality"""
    logger.info("\n=== Testing Caching Functionality ===")
    
    # Test data
    farmer_profile = {
        "farmer_id": "F001",
        "name": "Test Farmer",
        "land_size": 10.5,
        "location": "Test Village"
    }
    alternative_data = {
        "satellite_data": {"ndvi": 0.8, "soil_moisture": 0.6},
        "weather_data": {"avg_temp": 25, "rainfall": 800}
    }
    
    # First request - should be a cache miss
    logger.info("Making first credit score request (cache miss expected)...")
    start_time = time.time()
    
    result1 = await service_manager.calculate_credit_score(
        farmer_profile=farmer_profile,
        alternative_data=alternative_data,
        enable_caching=True
    )
    
    first_request_time = time.time() - start_time
    logger.info(f"First request completed in {first_request_time:.3f} seconds")
    logger.info(f"Cached: {result1['processing_metadata']['cached']}")
    
    # Second request with same data - should be a cache hit
    logger.info("Making second credit score request (cache hit expected)...")
    start_time = time.time()
    
    result2 = await service_manager.calculate_credit_score(
        farmer_profile=farmer_profile,
        alternative_data=alternative_data,
        enable_caching=True
    )
    
    second_request_time = time.time() - start_time
    logger.info(f"Second request completed in {second_request_time:.3f} seconds")
    
    # Verify results are identical (from cache)
    if result1['credit_score'] == result2['credit_score']:
        logger.info("✓ Cache hit successful - identical results")
    else:
        logger.warning("✗ Cache miss - results differ")
    
    # Get cache statistics
    cache_stats = service_manager.get_cache_stats()
    logger.info(f"Cache hit rate: {cache_stats['hit_rate']:.2%}")
    logger.info(f"Cache entries: {cache_stats['entry_count']}")
    logger.info(f"Cache size: {cache_stats['size_mb']:.2f} MB")
    
    return service_manager

async def test_performance_optimization(service_manager: ADKServiceManager):
    """Test performance optimization features"""
    logger.info("\n=== Testing Performance Optimization ===")
    
    # Test mixed workload with different priorities
    tasks = []
    
    # High priority fraud detection (should not be batched)
    claim_data = {
        "claim_id": "C001",
        "amount": 50000,
        "type": "crop_damage"
    }
    supporting_evidence = [
        {"type": "image", "url": "satellite_image.jpg"},
        {"type": "report", "content": "Damage assessment report"}
    ]
    
    fraud_task = service_manager.detect_fraud(
        claim_data=claim_data,
        supporting_evidence=supporting_evidence,
        enable_batching=False,  # Fraud detection should be immediate
        enable_caching=True,
        priority=10
    )
    tasks.append(("fraud_detection", fraud_task))
    
    # Multiple portfolio optimization requests (can be batched)
    for i in range(3):
        market_data = {"prices": [100 + i, 110 + i, 105 + i]}
        climate_data = {"temperature": 25 + i, "rainfall": 50}
        yield_data = {"projected_yield": 5.5 + (i * 0.1)}
        
        portfolio_task = service_manager.optimize_portfolio(
            market_data=market_data,
            climate_data=climate_data,
            yield_data=yield_data,
            enable_batching=True,
            enable_caching=True,
            priority=i
        )
        tasks.append((f"portfolio_{i}", portfolio_task))
    
    # Execute all tasks
    logger.info("Executing mixed workload...")
    start_time = time.time()
    
    results = await asyncio.gather(*[task for _, task in tasks])
    
    end_time = time.time()
    logger.info(f"Mixed workload completed in {end_time - start_time:.2f} seconds")
    
    # Analyze results
    for i, (task_name, _) in enumerate(tasks):
        result = results[i]
        metadata = result.get('processing_metadata', {})
        logger.info(f"{task_name}: batched={metadata.get('batched', False)}, "
                   f"cached={metadata.get('cached', False)}")
    
    # Get performance summary
    performance_summary = await service_manager.get_performance_summary()
    logger.info("\nPerformance Summary:")
    logger.info(f"Batching: {performance_summary['batching']}")
    logger.info(f"Caching: {performance_summary['caching']}")
    logger.info("Recommendations:")
    for rec in performance_summary['recommendations']:
        logger.info(f"  - {rec}")

async def test_cache_invalidation(service_manager: ADKServiceManager):
    """Test cache invalidation functionality"""
    logger.info("\n=== Testing Cache Invalidation ===")
    
    # Create some cached entries
    farmer_profile = {"farmer_id": "F002", "name": "Test Farmer 2"}
    alternative_data = {"credit_history": "good"}
    
    # Cache a result
    await service_manager.calculate_credit_score(
        farmer_profile=farmer_profile,
        alternative_data=alternative_data,
        enable_caching=True
    )
    
    cache_stats_before = service_manager.get_cache_stats()
    logger.info(f"Cache entries before invalidation: {cache_stats_before['entry_count']}")
    
    # Invalidate vertex_ai cache
    await service_manager.clear_cache(service_name="vertex_ai", operation="calculate_credit_score")
    
    cache_stats_after = service_manager.get_cache_stats()
    logger.info(f"Cache entries after invalidation: {cache_stats_after['entry_count']}")
    
    if cache_stats_after['entry_count'] < cache_stats_before['entry_count']:
        logger.info("✓ Cache invalidation successful")
    else:
        logger.warning("✗ Cache invalidation may not have worked as expected")

async def main():
    """Main test function"""
    logger.info("Starting ADK Service Manager Batching and Caching Tests")
    
    try:
        # Test batching
        service_manager = await test_batching_functionality()
        
        # Test caching
        await test_caching_functionality(service_manager)
        
        # Test performance optimization
        await test_performance_optimization(service_manager)
        
        # Test cache invalidation
        await test_cache_invalidation(service_manager)
        
        # Final health check
        logger.info("\n=== Final Health Check ===")
        health_check = service_manager.get_health_check()
        logger.info(f"Overall health: {health_check['overall_health']}")
        logger.info(f"Cache hit rate: {health_check['performance_optimization']['caching']['hit_rate']:.2%}")
        
        logger.info("\n✓ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())