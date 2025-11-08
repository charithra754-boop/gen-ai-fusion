"""
Caching System for Google ADK Services
Implements intelligent caching for frequently requested model predictions
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
import pickle
from collections import OrderedDict
import weakref

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Caching strategies"""
    LRU = "lru"  # Least Recently Used
    TTL = "ttl"  # Time To Live
    LFU = "lfu"  # Least Frequently Used
    HYBRID = "hybrid"  # Combine TTL with LRU

class CacheLevel(Enum):
    """Cache levels for different types of data"""
    MEMORY = "memory"  # In-memory cache
    PERSISTENT = "persistent"  # File-based cache
    DISTRIBUTED = "distributed"  # Redis/external cache

@dataclass
class CacheEntry:
    """Individual cache entry"""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    ttl_seconds: Optional[float] = None
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl_seconds is None:
            return False
        
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds
    
    def touch(self):
        """Update access information"""
        self.last_accessed = datetime.now()
        self.access_count += 1

@dataclass
class CacheConfig:
    """Configuration for caching behavior"""
    max_size_mb: float = 100.0  # Maximum cache size in MB
    default_ttl_seconds: float = 3600.0  # 1 hour default TTL
    strategy: CacheStrategy = CacheStrategy.HYBRID
    cleanup_interval_seconds: float = 300.0  # 5 minutes
    enable_compression: bool = True
    enable_persistence: bool = False
    persistence_path: Optional[str] = None

class IntelligentCache:
    """Intelligent caching system for ADK service responses"""
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size_bytes": 0,
            "entry_count": 0
        }
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Start cleanup task
        self._start_cleanup_task()
        
        logger.info(f"IntelligentCache initialized with strategy: {self.config.strategy.value}")
    
    def _start_cleanup_task(self):
        """Start the periodic cleanup task"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
    
    def _generate_cache_key(self, 
                          service_name: str, 
                          operation: str, 
                          data: Dict[str, Any],
                          additional_context: Dict[str, Any] = None) -> str:
        """Generate cache key for request"""
        # Create deterministic key from request parameters
        key_data = {
            "service": service_name,
            "operation": operation,
            "data": data
        }
        
        if additional_context:
            key_data["context"] = additional_context
        
        # Sort keys for consistent hashing
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        hash_obj = hashlib.sha256(key_string.encode())
        return f"{service_name}:{operation}:{hash_obj.hexdigest()[:16]}"
    
    async def get(self, 
                  service_name: str, 
                  operation: str, 
                  data: Dict[str, Any],
                  additional_context: Dict[str, Any] = None) -> Optional[Any]:
        """Get cached result if available"""
        
        cache_key = self._generate_cache_key(service_name, operation, data, additional_context)
        
        async with self._lock:
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                
                # Check if expired
                if entry.is_expired():
                    logger.debug(f"Cache entry expired: {cache_key}")
                    del self.cache[cache_key]
                    self.cache_stats["evictions"] += 1
                    self.cache_stats["entry_count"] -= 1
                    self.cache_stats["size_bytes"] -= entry.size_bytes
                    self.cache_stats["misses"] += 1
                    return None
                
                # Update access info
                entry.touch()
                
                # Move to end for LRU
                if self.config.strategy in [CacheStrategy.LRU, CacheStrategy.HYBRID]:
                    self.cache.move_to_end(cache_key)
                
                self.cache_stats["hits"] += 1
                
                logger.debug(f"Cache hit: {cache_key}")
                return entry.value
            
            else:
                self.cache_stats["misses"] += 1
                logger.debug(f"Cache miss: {cache_key}")
                return None
    
    async def set(self, 
                  service_name: str, 
                  operation: str, 
                  data: Dict[str, Any], 
                  result: Any,
                  ttl_seconds: Optional[float] = None,
                  additional_context: Dict[str, Any] = None,
                  metadata: Dict[str, Any] = None) -> bool:
        """Cache a result"""
        
        cache_key = self._generate_cache_key(service_name, operation, data, additional_context)
        
        # Calculate size
        try:
            if self.config.enable_compression:
                serialized = pickle.dumps(result, protocol=pickle.HIGHEST_PROTOCOL)
            else:
                serialized = json.dumps(result, default=str).encode()
            size_bytes = len(serialized)
        except Exception as e:
            logger.warning(f"Failed to serialize result for caching: {e}")
            return False
        
        # Check if result is too large
        max_size_bytes = self.config.max_size_mb * 1024 * 1024
        if size_bytes > max_size_bytes * 0.1:  # Don't cache items larger than 10% of max cache size
            logger.warning(f"Result too large to cache: {size_bytes} bytes")
            return False
        
        async with self._lock:
            # Create cache entry
            entry = CacheEntry(
                key=cache_key,
                value=result,
                ttl_seconds=ttl_seconds or self.config.default_ttl_seconds,
                size_bytes=size_bytes,
                metadata=metadata or {}
            )
            
            # Check if we need to evict entries
            await self._ensure_cache_space(size_bytes)
            
            # Add to cache
            self.cache[cache_key] = entry
            self.cache_stats["entry_count"] += 1
            self.cache_stats["size_bytes"] += size_bytes
            
            logger.debug(f"Cached result: {cache_key} ({size_bytes} bytes)")
            return True
    
    async def _ensure_cache_space(self, required_bytes: int):
        """Ensure there's enough space in cache"""
        max_size_bytes = self.config.max_size_mb * 1024 * 1024
        
        while (self.cache_stats["size_bytes"] + required_bytes) > max_size_bytes and self.cache:
            # Evict based on strategy
            if self.config.strategy == CacheStrategy.LRU:
                # Remove least recently used (first item in OrderedDict)
                key_to_remove = next(iter(self.cache))
            
            elif self.config.strategy == CacheStrategy.LFU:
                # Remove least frequently used
                key_to_remove = min(self.cache.keys(), 
                                  key=lambda k: self.cache[k].access_count)
            
            elif self.config.strategy == CacheStrategy.TTL:
                # Remove oldest entry
                key_to_remove = min(self.cache.keys(), 
                                  key=lambda k: self.cache[k].created_at)
            
            else:  # HYBRID - prefer expired, then LRU
                expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
                if expired_keys:
                    key_to_remove = expired_keys[0]
                else:
                    key_to_remove = next(iter(self.cache))
            
            # Remove the entry
            entry = self.cache[key_to_remove]
            del self.cache[key_to_remove]
            self.cache_stats["evictions"] += 1
            self.cache_stats["entry_count"] -= 1
            self.cache_stats["size_bytes"] -= entry.size_bytes
            
            logger.debug(f"Evicted cache entry: {key_to_remove}")
    
    async def invalidate(self, 
                        service_name: str = None, 
                        operation: str = None,
                        pattern: str = None):
        """Invalidate cache entries"""
        async with self._lock:
            keys_to_remove = []
            
            for key in self.cache.keys():
                should_remove = False
                
                if pattern:
                    if pattern in key:
                        should_remove = True
                elif service_name and operation:
                    if key.startswith(f"{service_name}:{operation}:"):
                        should_remove = True
                elif service_name:
                    if key.startswith(f"{service_name}:"):
                        should_remove = True
                
                if should_remove:
                    keys_to_remove.append(key)
            
            # Remove identified keys
            for key in keys_to_remove:
                entry = self.cache[key]
                del self.cache[key]
                self.cache_stats["evictions"] += 1
                self.cache_stats["entry_count"] -= 1
                self.cache_stats["size_bytes"] -= entry.size_bytes
            
            logger.info(f"Invalidated {len(keys_to_remove)} cache entries")
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired entries"""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval_seconds)
                
                async with self._lock:
                    keys_to_remove = []
                    
                    for key, entry in self.cache.items():
                        if entry.is_expired():
                            keys_to_remove.append(key)
                    
                    # Remove expired entries
                    for key in keys_to_remove:
                        entry = self.cache[key]
                        del self.cache[key]
                        self.cache_stats["evictions"] += 1
                        self.cache_stats["entry_count"] -= 1
                        self.cache_stats["size_bytes"] -= entry.size_bytes
                    
                    if keys_to_remove:
                        logger.debug(f"Cleaned up {len(keys_to_remove)} expired cache entries")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = 0.0
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        if total_requests > 0:
            hit_rate = self.cache_stats["hits"] / total_requests
        
        return {
            **self.cache_stats,
            "hit_rate": hit_rate,
            "size_mb": self.cache_stats["size_bytes"] / (1024 * 1024),
            "max_size_mb": self.config.max_size_mb,
            "utilization": (self.cache_stats["size_bytes"] / (1024 * 1024)) / self.config.max_size_mb
        }
    
    async def clear(self):
        """Clear all cache entries"""
        async with self._lock:
            self.cache.clear()
            self.cache_stats = {
                "hits": 0,
                "misses": 0,
                "evictions": 0,
                "size_bytes": 0,
                "entry_count": 0
            }
            logger.info("Cache cleared")
    
    def __del__(self):
        """Cleanup when cache is destroyed"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()


class SmartCacheManager:
    """Smart cache manager with service-specific caching strategies"""
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self.cache = IntelligentCache(config)
        self.service_configs: Dict[str, Dict[str, Any]] = {}
        
        # Configure service-specific caching
        self._configure_service_caching()
    
    def _configure_service_caching(self):
        """Configure caching strategies for different services"""
        self.service_configs = {
            "vertex_ai": {
                "portfolio_optimization": {
                    "ttl_seconds": 1800,  # 30 minutes
                    "cache_probability": 0.9,  # Cache 90% of requests
                    "invalidate_on_market_change": True
                },
                "credit_scoring": {
                    "ttl_seconds": 3600,  # 1 hour
                    "cache_probability": 0.8,
                    "invalidate_on_profile_change": True
                }
            },
            "vision_api": {
                "satellite_analysis": {
                    "ttl_seconds": 7200,  # 2 hours
                    "cache_probability": 0.95,  # High cache rate for expensive operations
                    "invalidate_on_image_change": True
                }
            },
            "natural_language": {
                "sentiment_analysis": {
                    "ttl_seconds": 1800,  # 30 minutes
                    "cache_probability": 0.7,
                    "invalidate_on_text_change": True
                }
            }
        }
    
    async def get_cached_result(self, 
                              service_name: str, 
                              operation: str, 
                              data: Dict[str, Any],
                              context: Dict[str, Any] = None) -> Optional[Any]:
        """Get cached result with service-specific logic"""
        
        # Check if caching is enabled for this service/operation
        service_config = self.service_configs.get(service_name, {}).get(operation, {})
        cache_probability = service_config.get("cache_probability", 1.0)
        
        # Probabilistic caching (for A/B testing or gradual rollout)
        import random
        if random.random() > cache_probability:
            return None
        
        return await self.cache.get(service_name, operation, data, context)
    
    async def cache_result(self, 
                         service_name: str, 
                         operation: str, 
                         data: Dict[str, Any], 
                         result: Any,
                         context: Dict[str, Any] = None) -> bool:
        """Cache result with service-specific configuration"""
        
        # Get service-specific configuration
        service_config = self.service_configs.get(service_name, {}).get(operation, {})
        ttl_seconds = service_config.get("ttl_seconds", self.config.default_ttl_seconds)
        
        # Add service-specific metadata
        metadata = {
            "service_name": service_name,
            "operation": operation,
            "cached_at": datetime.now().isoformat()
        }
        
        return await self.cache.set(
            service_name, operation, data, result, 
            ttl_seconds=ttl_seconds, 
            additional_context=context,
            metadata=metadata
        )
    
    async def invalidate_service_cache(self, service_name: str, operation: str = None):
        """Invalidate cache for specific service/operation"""
        await self.cache.invalidate(service_name, operation)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        base_stats = self.cache.get_stats()
        
        return {
            **base_stats,
            "service_configs": self.service_configs,
            "config": {
                "max_size_mb": self.config.max_size_mb,
                "default_ttl_seconds": self.config.default_ttl_seconds,
                "strategy": self.config.strategy.value,
                "cleanup_interval_seconds": self.config.cleanup_interval_seconds
            }
        }


# Global cache manager instance
_cache_manager: Optional[SmartCacheManager] = None

def get_cache_manager(config: CacheConfig = None) -> SmartCacheManager:
    """Get the global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = SmartCacheManager(config)
    return _cache_manager