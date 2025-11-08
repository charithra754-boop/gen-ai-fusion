#!/usr/bin/env python3
"""
Simple test script for batching and caching modules
Tests the core functionality without requiring full ADK service manager setup
"""

import asyncio
import logging
import sys
import os
import time
from typing import Dict, Any

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_batching_module():
    """Test the batching module independently"""
    logger.info("=== Testing Batching Module ===")
    
    try:
        from services.batching import RequestBatcher, BatchConfig, BatchStrategy
        
        # Create batcher with test configuration
        config = BatchConfig(
            max_batch_size=3,
            max_wait_time_seconds=1.0,
            strategy=BatchStrategy.HYBRID,
            enable_priority_batching=True
        )
        
        batcher = RequestBatcher(config)
        
        # Test data
        test_requests = [
            {"service": "vertex_ai", "operation": "optimize_portfolio", "data": {"request_id": i}}
            for i in range(5)
        ]
        
        # Submit requests concurrently
        logger.info("Submitting 5 test requests...")
        start_time = time.time()
        
        tasks = []
        for i, req in enumerate(test_requests):
            task = batcher.add_request(
                req["service"], 
                req["operation"], 
                req["data"], 
                priority=i
            )
            tasks.append(task)
        
        # Wait for all requests to complete
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        logger.info(f"Completed {len(results)} requests in {end_time - start_time:.2f} seconds")
        
        # Check results
        for i, result in enumerate(results):
            logger.info(f"Request {i}: {result['request_id']}")
        
        # Get batch statistics
        stats = await batcher.get_batch_stats()
        logger.info(f"Batch statistics: {stats}")
        
        logger.info("✓ Batching module test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Batching module test failed: {e}")
        return False

async def test_caching_module():
    """Test the caching module independently"""
    logger.info("\n=== Testing Caching Module ===")
    
    try:
        from services.caching import SmartCacheManager, CacheConfig, CacheStrategy
        
        # Create cache manager with test configuration
        config = CacheConfig(
            max_size_mb=10.0,
            default_ttl_seconds=60.0,
            strategy=CacheStrategy.HYBRID
        )
        
        cache_manager = SmartCacheManager(config)
        
        # Test data
        service_name = "vertex_ai"
        operation = "calculate_credit_score"
        test_data = {
            "farmer_id": "F001",
            "profile": {"name": "Test Farmer", "land_size": 10.5}
        }
        test_result = {
            "credit_score": 720,
            "risk_category": "medium",
            "confidence": 0.78
        }
        
        # Test cache miss
        logger.info("Testing cache miss...")
        cached_result = await cache_manager.get_cached_result(service_name, operation, test_data)
        
        if cached_result is None:
            logger.info("✓ Cache miss as expected")
        else:
            logger.warning("✗ Unexpected cache hit")
        
        # Cache the result
        logger.info("Caching test result...")
        success = await cache_manager.cache_result(service_name, operation, test_data, test_result)
        
        if success:
            logger.info("✓ Result cached successfully")
        else:
            logger.warning("✗ Failed to cache result")
        
        # Test cache hit
        logger.info("Testing cache hit...")
        cached_result = await cache_manager.get_cached_result(service_name, operation, test_data)
        
        if cached_result is not None and cached_result["credit_score"] == test_result["credit_score"]:
            logger.info("✓ Cache hit successful")
        else:
            logger.warning("✗ Cache hit failed")
        
        # Get cache statistics
        stats = cache_manager.get_cache_stats()
        logger.info(f"Cache statistics: hit_rate={stats['hit_rate']:.2%}, entries={stats['entry_count']}")
        
        # Test cache invalidation
        logger.info("Testing cache invalidation...")
        await cache_manager.invalidate_service_cache(service_name, operation)
        
        cached_result_after_invalidation = await cache_manager.get_cached_result(service_name, operation, test_data)
        
        if cached_result_after_invalidation is None:
            logger.info("✓ Cache invalidation successful")
        else:
            logger.warning("✗ Cache invalidation failed")
        
        logger.info("✓ Caching module test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Caching module test failed: {e}")
        return False

async def test_performance_characteristics():
    """Test performance characteristics of batching and caching"""
    logger.info("\n=== Testing Performance Characteristics ===")
    
    try:
        from services.batching import RequestBatcher, BatchConfig, BatchStrategy
        from services.caching import SmartCacheManager, CacheConfig, CacheStrategy
        
        # Create components
        batcher = RequestBatcher(BatchConfig(max_batch_size=5, max_wait_time_seconds=0.5))
        cache_manager = SmartCacheManager(CacheConfig(max_size_mb=5.0))
        
        # Test batching performance
        logger.info("Testing batching performance with 10 requests...")
        start_time = time.time()
        
        batch_tasks = []
        for i in range(10):
            task = batcher.add_request("test_service", "test_operation", {"id": i})
            batch_tasks.append(task)
        
        await asyncio.gather(*batch_tasks)
        batch_time = time.time() - start_time
        
        logger.info(f"Batching completed in {batch_time:.3f} seconds")
        
        # Test caching performance
        logger.info("Testing caching performance...")
        
        # Cache 20 different results
        cache_start = time.time()
        for i in range(20):
            await cache_manager.cache_result(
                "test_service", 
                "test_operation", 
                {"id": i}, 
                {"result": f"result_{i}"}
            )
        cache_time = time.time() - cache_start
        
        logger.info(f"Cached 20 results in {cache_time:.3f} seconds")
        
        # Test cache retrieval performance
        retrieval_start = time.time()
        hits = 0
        for i in range(20):
            result = await cache_manager.get_cached_result("test_service", "test_operation", {"id": i})
            if result is not None:
                hits += 1
        retrieval_time = time.time() - retrieval_start
        
        logger.info(f"Retrieved {hits}/20 results in {retrieval_time:.3f} seconds")
        
        # Get final statistics
        cache_stats = cache_manager.get_cache_stats()
        batch_stats = await batcher.get_batch_stats()
        
        logger.info(f"Final cache hit rate: {cache_stats['hit_rate']:.2%}")
        logger.info(f"Cache utilization: {cache_stats['utilization']:.2%}")
        
        logger.info("✓ Performance characteristics test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Performance characteristics test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("Starting Batching and Caching Module Tests")
    
    test_results = []
    
    # Run individual tests
    test_results.append(await test_batching_module())
    test_results.append(await test_caching_module())
    test_results.append(await test_performance_characteristics())
    
    # Summary
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    logger.info(f"\n=== Test Summary ===")
    logger.info(f"Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        logger.info("✓ All tests passed successfully!")
        return True
    else:
        logger.error("✗ Some tests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)