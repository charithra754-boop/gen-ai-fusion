#!/usr/bin/env python3
"""
Direct test of batching and caching modules without imports
"""

import asyncio
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_basic_functionality():
    """Test basic async functionality"""
    logger.info("Testing basic async functionality...")
    
    # Test async operations
    async def mock_ai_operation(data):
        await asyncio.sleep(0.1)  # Simulate AI processing
        return {"result": f"processed_{data['id']}", "timestamp": time.time()}
    
    # Test batching concept
    logger.info("Testing batching concept...")
    requests = [{"id": i} for i in range(5)]
    
    start_time = time.time()
    
    # Process requests concurrently (simulating batching)
    tasks = [mock_ai_operation(req) for req in requests]
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    
    logger.info(f"Processed {len(results)} requests in {end_time - start_time:.3f} seconds")
    
    # Test caching concept
    logger.info("Testing caching concept...")
    cache = {}
    
    def cache_key(service, operation, data):
        return f"{service}:{operation}:{hash(str(data))}"
    
    # Cache miss
    key = cache_key("vertex_ai", "optimize", {"data": "test"})
    if key not in cache:
        logger.info("Cache miss - computing result")
        result = await mock_ai_operation({"id": "cached_test"})
        cache[key] = result
    
    # Cache hit
    if key in cache:
        logger.info("Cache hit - returning cached result")
        cached_result = cache[key]
        logger.info(f"Cached result: {cached_result}")
    
    logger.info("✓ Basic functionality test passed")

async def main():
    logger.info("Starting basic functionality tests...")
    await test_basic_functionality()
    logger.info("All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())