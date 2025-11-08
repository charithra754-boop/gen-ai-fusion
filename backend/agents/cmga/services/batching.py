"""
Request Batching System for Google ADK Services
Implements efficient batching of API requests to optimize usage and reduce costs
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json

logger = logging.getLogger(__name__)

class BatchStrategy(Enum):
    """Batching strategies"""
    TIME_BASED = "time_based"  # Batch requests within time window
    SIZE_BASED = "size_based"  # Batch when reaching size limit
    HYBRID = "hybrid"  # Combine time and size based batching

@dataclass
class BatchRequest:
    """Individual request in a batch"""
    request_id: str
    service_name: str
    operation: str
    data: Dict[str, Any]
    future: asyncio.Future
    created_at: datetime = field(default_factory=datetime.now)
    priority: int = 0  # Higher number = higher priority

@dataclass
class BatchConfig:
    """Configuration for batching behavior"""
    max_batch_size: int = 10
    max_wait_time_seconds: float = 2.0
    strategy: BatchStrategy = BatchStrategy.HYBRID
    enable_priority_batching: bool = True
    max_concurrent_batches: int = 5

class RequestBatcher:
    """Manages batching of requests for efficient API usage"""
    
    def __init__(self, config: BatchConfig = None):
        self.config = config or BatchConfig()
        self.pending_requests: Dict[str, List[BatchRequest]] = {}  # service_operation -> requests
        self.batch_timers: Dict[str, asyncio.Task] = {}
        self.active_batches: Dict[str, int] = {}  # Track concurrent batches per service
        self._lock = asyncio.Lock()
        
        logger.info(f"RequestBatcher initialized with strategy: {self.config.strategy.value}")
    
    def _get_batch_key(self, service_name: str, operation: str) -> str:
        """Generate batch key for service and operation"""
        return f"{service_name}:{operation}"
    
    async def add_request(self, 
                         service_name: str,
                         operation: str,
                         data: Dict[str, Any],
                         priority: int = 0) -> Any:
        """Add a request to the batch queue"""
        
        batch_key = self._get_batch_key(service_name, operation)
        request_id = self._generate_request_id(service_name, operation, data)
        
        # Create future for the result
        future = asyncio.Future()
        
        batch_request = BatchRequest(
            request_id=request_id,
            service_name=service_name,
            operation=operation,
            data=data,
            future=future,
            priority=priority
        )
        
        async with self._lock:
            # Initialize batch queue if needed
            if batch_key not in self.pending_requests:
                self.pending_requests[batch_key] = []
                self.active_batches[batch_key] = 0
            
            # Add request to batch
            self.pending_requests[batch_key].append(batch_request)
            
            # Sort by priority if enabled
            if self.config.enable_priority_batching:
                self.pending_requests[batch_key].sort(key=lambda x: x.priority, reverse=True)
            
            logger.debug(f"Added request {request_id} to batch {batch_key} (queue size: {len(self.pending_requests[batch_key])})")
            
            # Check if we should process the batch
            should_process = await self._should_process_batch(batch_key)
            
            if should_process:
                # Cancel existing timer if any
                if batch_key in self.batch_timers:
                    self.batch_timers[batch_key].cancel()
                    del self.batch_timers[batch_key]
                
                # Process batch immediately
                asyncio.create_task(self._process_batch(batch_key))
            
            elif batch_key not in self.batch_timers:
                # Start timer for time-based batching
                self.batch_timers[batch_key] = asyncio.create_task(
                    self._batch_timer(batch_key)
                )
        
        # Wait for result
        return await future
    
    async def _should_process_batch(self, batch_key: str) -> bool:
        """Determine if batch should be processed now"""
        if batch_key not in self.pending_requests:
            return False
        
        requests = self.pending_requests[batch_key]
        
        # Check concurrent batch limit
        if self.active_batches[batch_key] >= self.config.max_concurrent_batches:
            return False
        
        # Size-based check
        if len(requests) >= self.config.max_batch_size:
            return True
        
        # Time-based check (for hybrid strategy)
        if self.config.strategy in [BatchStrategy.TIME_BASED, BatchStrategy.HYBRID]:
            oldest_request = min(requests, key=lambda x: x.created_at)
            age = (datetime.now() - oldest_request.created_at).total_seconds()
            if age >= self.config.max_wait_time_seconds:
                return True
        
        return False
    
    async def _batch_timer(self, batch_key: str):
        """Timer for time-based batching"""
        try:
            await asyncio.sleep(self.config.max_wait_time_seconds)
            
            async with self._lock:
                if batch_key in self.pending_requests and self.pending_requests[batch_key]:
                    logger.debug(f"Timer triggered for batch {batch_key}")
                    asyncio.create_task(self._process_batch(batch_key))
                
                # Clean up timer
                if batch_key in self.batch_timers:
                    del self.batch_timers[batch_key]
                    
        except asyncio.CancelledError:
            logger.debug(f"Batch timer cancelled for {batch_key}")
    
    async def _process_batch(self, batch_key: str):
        """Process a batch of requests"""
        async with self._lock:
            if batch_key not in self.pending_requests or not self.pending_requests[batch_key]:
                return
            
            # Extract requests to process
            requests_to_process = self.pending_requests[batch_key][:self.config.max_batch_size]
            self.pending_requests[batch_key] = self.pending_requests[batch_key][self.config.max_batch_size:]
            
            # Update active batch count
            self.active_batches[batch_key] += 1
        
        try:
            logger.info(f"Processing batch {batch_key} with {len(requests_to_process)} requests")
            
            # Group requests by service and operation for actual processing
            service_name = requests_to_process[0].service_name
            operation = requests_to_process[0].operation
            
            # Execute batch processing
            results = await self._execute_batch(service_name, operation, requests_to_process)
            
            # Distribute results to futures
            for request, result in zip(requests_to_process, results):
                if isinstance(result, Exception):
                    request.future.set_exception(result)
                else:
                    request.future.set_result(result)
            
            logger.info(f"Completed batch {batch_key} successfully")
            
        except Exception as e:
            logger.error(f"Error processing batch {batch_key}: {e}")
            
            # Set exception for all requests in batch
            for request in requests_to_process:
                if not request.future.done():
                    request.future.set_exception(e)
        
        finally:
            async with self._lock:
                self.active_batches[batch_key] -= 1
                
                # Process remaining requests if any
                if self.pending_requests[batch_key]:
                    should_process = await self._should_process_batch(batch_key)
                    if should_process:
                        asyncio.create_task(self._process_batch(batch_key))
    
    async def _execute_batch(self, 
                           service_name: str, 
                           operation: str, 
                           requests: List[BatchRequest]) -> List[Any]:
        """Execute a batch of requests - to be implemented by specific services"""
        # This is a placeholder - actual implementation would depend on the specific
        # Google ADK service and operation being batched
        
        results = []
        for request in requests:
            try:
                # For now, simulate batch processing
                # In real implementation, this would make optimized batch API calls
                await asyncio.sleep(0.1)  # Simulate processing time
                
                result = {
                    "request_id": request.request_id,
                    "processed_at": datetime.now().isoformat(),
                    "batch_size": len(requests),
                    "data": request.data
                }
                results.append(result)
                
            except Exception as e:
                results.append(e)
        
        return results
    
    def _generate_request_id(self, service_name: str, operation: str, data: Dict[str, Any]) -> str:
        """Generate unique request ID"""
        content = f"{service_name}:{operation}:{json.dumps(data, sort_keys=True)}"
        hash_obj = hashlib.md5(content.encode())
        timestamp = int(datetime.now().timestamp() * 1000000)
        return f"{hash_obj.hexdigest()[:8]}_{timestamp}"
    
    async def get_batch_stats(self) -> Dict[str, Any]:
        """Get batching statistics"""
        async with self._lock:
            return {
                "pending_batches": {
                    batch_key: len(requests) 
                    for batch_key, requests in self.pending_requests.items()
                },
                "active_batches": self.active_batches.copy(),
                "active_timers": list(self.batch_timers.keys()),
                "config": {
                    "max_batch_size": self.config.max_batch_size,
                    "max_wait_time_seconds": self.config.max_wait_time_seconds,
                    "strategy": self.config.strategy.value,
                    "max_concurrent_batches": self.config.max_concurrent_batches
                }
            }
    
    async def flush_all_batches(self):
        """Force process all pending batches"""
        async with self._lock:
            batch_keys = list(self.pending_requests.keys())
        
        for batch_key in batch_keys:
            if batch_key in self.pending_requests and self.pending_requests[batch_key]:
                await self._process_batch(batch_key)
        
        logger.info("Flushed all pending batches")


class ServiceSpecificBatcher:
    """Service-specific batching implementations"""
    
    @staticmethod
    async def batch_vertex_ai_predictions(requests: List[BatchRequest]) -> List[Any]:
        """Batch Vertex AI prediction requests"""
        # Combine multiple prediction requests into a single batch call
        batch_data = [req.data for req in requests]
        
        # Simulate batch prediction call
        await asyncio.sleep(0.5)  # Simulate API call time
        
        results = []
        for i, request in enumerate(requests):
            result = {
                "request_id": request.request_id,
                "prediction": f"batch_prediction_{i}",
                "confidence": 0.85 + (i * 0.01),  # Simulate varying confidence
                "batch_processed": True
            }
            results.append(result)
        
        return results
    
    @staticmethod
    async def batch_vision_api_analysis(requests: List[BatchRequest]) -> List[Any]:
        """Batch Vision API analysis requests"""
        # Group similar image analysis requests
        results = []
        
        for request in requests:
            # Simulate image analysis
            await asyncio.sleep(0.2)
            
            result = {
                "request_id": request.request_id,
                "analysis": {
                    "objects_detected": ["crop", "field", "damage"],
                    "confidence": 0.78,
                    "processing_time_ms": 200
                },
                "batch_processed": True
            }
            results.append(result)
        
        return results
    
    @staticmethod
    async def batch_nlp_analysis(requests: List[BatchRequest]) -> List[Any]:
        """Batch Natural Language API requests"""
        # Combine text analysis requests
        texts = [req.data.get("text", "") for req in requests]
        
        # Simulate batch text analysis
        await asyncio.sleep(0.3)
        
        results = []
        for i, request in enumerate(requests):
            result = {
                "request_id": request.request_id,
                "sentiment": {
                    "score": 0.1 + (i * 0.05),
                    "magnitude": 0.6,
                    "label": "neutral"
                },
                "entities": [],
                "batch_processed": True
            }
            results.append(result)
        
        return results


# Global batcher instance
_request_batcher: Optional[RequestBatcher] = None

def get_request_batcher(config: BatchConfig = None) -> RequestBatcher:
    """Get the global request batcher instance"""
    global _request_batcher
    if _request_batcher is None:
        _request_batcher = RequestBatcher(config)
    return _request_batcher