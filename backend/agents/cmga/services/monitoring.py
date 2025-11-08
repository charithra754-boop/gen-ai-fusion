"""
Monitoring and logging system for Google ADK service interactions
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import time
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics to track"""
    REQUEST_COUNT = "request_count"
    ERROR_COUNT = "error_count"
    RESPONSE_TIME = "response_time"
    SUCCESS_RATE = "success_rate"
    RATE_LIMIT_HITS = "rate_limit_hits"
    CIRCUIT_BREAKER_TRIPS = "circuit_breaker_trips"

@dataclass
class ServiceMetric:
    """Individual service metric"""
    service_name: str
    operation: str
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceStats:
    """Performance statistics for a service operation"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    rate_limit_hits: int = 0
    circuit_breaker_trips: int = 0
    last_request_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time"""
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_time / self.successful_requests
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100

class RequestTracker:
    """Tracks individual requests for detailed monitoring"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.request_history: deque = deque(maxlen=max_history)
        self._lock = asyncio.Lock()
    
    async def start_request(self, service_name: str, operation: str, request_data: Dict[str, Any] = None) -> str:
        """Start tracking a request"""
        request_id = f"{service_name}_{operation}_{int(time.time() * 1000000)}"
        
        request_info = {
            "request_id": request_id,
            "service_name": service_name,
            "operation": operation,
            "start_time": datetime.now(),
            "request_data": request_data or {},
            "status": "in_progress"
        }
        
        async with self._lock:
            self.request_history.append(request_info)
        
        return request_id
    
    async def complete_request(self, request_id: str, success: bool, response_data: Dict[str, Any] = None, error: Exception = None):
        """Complete tracking a request"""
        async with self._lock:
            # Find the request in history
            for request_info in reversed(self.request_history):
                if request_info["request_id"] == request_id:
                    request_info["end_time"] = datetime.now()
                    request_info["duration"] = (request_info["end_time"] - request_info["start_time"]).total_seconds()
                    request_info["success"] = success
                    request_info["status"] = "completed"
                    
                    if success:
                        request_info["response_data"] = response_data or {}
                    else:
                        request_info["error"] = str(error) if error else "Unknown error"
                        request_info["error_type"] = type(error).__name__ if error else "UnknownError"
                    
                    break
    
    def get_recent_requests(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent requests"""
        return list(self.request_history)[-limit:]
    
    def get_requests_by_service(self, service_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent requests for a specific service"""
        service_requests = [
            req for req in self.request_history
            if req["service_name"] == service_name
        ]
        return service_requests[-limit:]

class ADKMonitor:
    """Main monitoring system for ADK services"""
    
    def __init__(self, metrics_retention_hours: int = 24):
        self.metrics_retention_hours = metrics_retention_hours
        self.performance_stats: Dict[str, Dict[str, PerformanceStats]] = defaultdict(lambda: defaultdict(PerformanceStats))
        self.metrics_history: List[ServiceMetric] = []
        self.request_tracker = RequestTracker()
        self.alert_thresholds: Dict[str, Dict[str, float]] = {}
        self.alert_callbacks: List[Callable] = []
        self._lock = asyncio.Lock()
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_old_metrics())
    
    def set_alert_threshold(self, service_name: str, metric_type: MetricType, threshold: float):
        """Set alert threshold for a service metric"""
        if service_name not in self.alert_thresholds:
            self.alert_thresholds[service_name] = {}
        self.alert_thresholds[service_name][metric_type.value] = threshold
    
    def add_alert_callback(self, callback: Callable[[str, MetricType, float, float], None]):
        """Add callback for alerts"""
        self.alert_callbacks.append(callback)
    
    async def record_request_start(self, service_name: str, operation: str, request_data: Dict[str, Any] = None) -> str:
        """Record the start of a request"""
        return await self.request_tracker.start_request(service_name, operation, request_data)
    
    async def record_request_completion(self, 
                                      request_id: str,
                                      service_name: str, 
                                      operation: str,
                                      success: bool,
                                      response_time: float,
                                      response_data: Dict[str, Any] = None,
                                      error: Exception = None):
        """Record the completion of a request"""
        
        # Complete request tracking
        await self.request_tracker.complete_request(request_id, success, response_data, error)
        
        # Update performance stats
        async with self._lock:
            stats = self.performance_stats[service_name][operation]
            
            stats.total_requests += 1
            stats.last_request_time = datetime.now()
            
            if success:
                stats.successful_requests += 1
                stats.total_response_time += response_time
                stats.min_response_time = min(stats.min_response_time, response_time)
                stats.max_response_time = max(stats.max_response_time, response_time)
            else:
                stats.failed_requests += 1
        
        # Record metrics
        await self._record_metric(service_name, operation, MetricType.REQUEST_COUNT, 1)
        await self._record_metric(service_name, operation, MetricType.RESPONSE_TIME, response_time)
        
        if not success:
            await self._record_metric(service_name, operation, MetricType.ERROR_COUNT, 1)
        
        # Check alerts
        await self._check_alerts(service_name, operation)
    
    async def record_rate_limit_hit(self, service_name: str, operation: str = "general"):
        """Record a rate limit hit"""
        async with self._lock:
            self.performance_stats[service_name][operation].rate_limit_hits += 1
        
        await self._record_metric(service_name, operation, MetricType.RATE_LIMIT_HITS, 1)
        await self._check_alerts(service_name, operation)
    
    async def record_circuit_breaker_trip(self, service_name: str, operation: str = "general"):
        """Record a circuit breaker trip"""
        async with self._lock:
            self.performance_stats[service_name][operation].circuit_breaker_trips += 1
        
        await self._record_metric(service_name, operation, MetricType.CIRCUIT_BREAKER_TRIPS, 1)
        await self._check_alerts(service_name, operation)
    
    async def _record_metric(self, service_name: str, operation: str, metric_type: MetricType, value: float, metadata: Dict[str, Any] = None):
        """Record a metric"""
        metric = ServiceMetric(
            service_name=service_name,
            operation=operation,
            metric_type=metric_type,
            value=value,
            metadata=metadata or {}
        )
        
        async with self._lock:
            self.metrics_history.append(metric)
    
    async def _check_alerts(self, service_name: str, operation: str):
        """Check if any alert thresholds are exceeded"""
        if service_name not in self.alert_thresholds:
            return
        
        stats = self.performance_stats[service_name][operation]
        thresholds = self.alert_thresholds[service_name]
        
        # Check error rate
        if MetricType.ERROR_COUNT.value in thresholds:
            error_rate = stats.error_rate
            threshold = thresholds[MetricType.ERROR_COUNT.value]
            if error_rate > threshold:
                await self._trigger_alert(service_name, MetricType.ERROR_COUNT, error_rate, threshold)
        
        # Check response time
        if MetricType.RESPONSE_TIME.value in thresholds:
            avg_response_time = stats.average_response_time
            threshold = thresholds[MetricType.RESPONSE_TIME.value]
            if avg_response_time > threshold:
                await self._trigger_alert(service_name, MetricType.RESPONSE_TIME, avg_response_time, threshold)
        
        # Check success rate
        if MetricType.SUCCESS_RATE.value in thresholds:
            success_rate = stats.success_rate
            threshold = thresholds[MetricType.SUCCESS_RATE.value]
            if success_rate < threshold:
                await self._trigger_alert(service_name, MetricType.SUCCESS_RATE, success_rate, threshold)
    
    async def _trigger_alert(self, service_name: str, metric_type: MetricType, current_value: float, threshold: float):
        """Trigger an alert"""
        logger.warning(
            f"ALERT: {service_name} {metric_type.value} = {current_value:.2f} "
            f"(threshold: {threshold:.2f})"
        )
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(service_name, metric_type, current_value, threshold)
                else:
                    callback(service_name, metric_type, current_value, threshold)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def get_service_stats(self, service_name: str) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for a service"""
        if service_name not in self.performance_stats:
            return {}
        
        service_stats = {}
        for operation, stats in self.performance_stats[service_name].items():
            service_stats[operation] = {
                "total_requests": stats.total_requests,
                "successful_requests": stats.successful_requests,
                "failed_requests": stats.failed_requests,
                "success_rate": round(stats.success_rate, 2),
                "error_rate": round(stats.error_rate, 2),
                "average_response_time": round(stats.average_response_time, 3),
                "min_response_time": round(stats.min_response_time, 3) if stats.min_response_time != float('inf') else 0,
                "max_response_time": round(stats.max_response_time, 3),
                "rate_limit_hits": stats.rate_limit_hits,
                "circuit_breaker_trips": stats.circuit_breaker_trips,
                "last_request_time": stats.last_request_time.isoformat() if stats.last_request_time else None
            }
        
        return service_stats
    
    def get_all_stats(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Get performance statistics for all services"""
        all_stats = {}
        for service_name in self.performance_stats:
            all_stats[service_name] = self.get_service_stats(service_name)
        return all_stats
    
    def get_metrics_history(self, 
                          service_name: Optional[str] = None,
                          metric_type: Optional[MetricType] = None,
                          hours: int = 1) -> List[Dict[str, Any]]:
        """Get metrics history"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_metrics = []
        for metric in self.metrics_history:
            if metric.timestamp < cutoff_time:
                continue
            
            if service_name and metric.service_name != service_name:
                continue
            
            if metric_type and metric.metric_type != metric_type:
                continue
            
            filtered_metrics.append({
                "service_name": metric.service_name,
                "operation": metric.operation,
                "metric_type": metric.metric_type.value,
                "value": metric.value,
                "timestamp": metric.timestamp.isoformat(),
                "metadata": metric.metadata
            })
        
        return filtered_metrics
    
    def get_recent_requests(self, service_name: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent requests"""
        if service_name:
            return self.request_tracker.get_requests_by_service(service_name, limit)
        else:
            return self.request_tracker.get_recent_requests(limit)
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        total_requests = 0
        total_errors = 0
        total_rate_limits = 0
        total_circuit_breaker_trips = 0
        services_with_issues = []
        
        for service_name, operations in self.performance_stats.items():
            service_requests = 0
            service_errors = 0
            service_rate_limits = 0
            service_cb_trips = 0
            
            for operation, stats in operations.items():
                service_requests += stats.total_requests
                service_errors += stats.failed_requests
                service_rate_limits += stats.rate_limit_hits
                service_cb_trips += stats.circuit_breaker_trips
            
            total_requests += service_requests
            total_errors += service_errors
            total_rate_limits += service_rate_limits
            total_circuit_breaker_trips += service_cb_trips
            
            # Check if service has issues
            if service_requests > 0:
                error_rate = (service_errors / service_requests) * 100
                if error_rate > 10 or service_rate_limits > 0 or service_cb_trips > 0:
                    services_with_issues.append({
                        "service": service_name,
                        "error_rate": round(error_rate, 2),
                        "rate_limit_hits": service_rate_limits,
                        "circuit_breaker_trips": service_cb_trips
                    })
        
        overall_error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        health_status = "healthy"
        if overall_error_rate > 20 or total_circuit_breaker_trips > 0:
            health_status = "critical"
        elif overall_error_rate > 10 or total_rate_limits > 5:
            health_status = "degraded"
        elif overall_error_rate > 5 or total_rate_limits > 0:
            health_status = "warning"
        
        return {
            "health_status": health_status,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "overall_error_rate": round(overall_error_rate, 2),
            "rate_limit_hits": total_rate_limits,
            "circuit_breaker_trips": total_circuit_breaker_trips,
            "services_monitored": len(self.performance_stats),
            "services_with_issues": services_with_issues,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _cleanup_old_metrics(self):
        """Cleanup old metrics periodically"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                cutoff_time = datetime.now() - timedelta(hours=self.metrics_retention_hours)
                
                async with self._lock:
                    self.metrics_history = [
                        metric for metric in self.metrics_history
                        if metric.timestamp > cutoff_time
                    ]
                
                logger.info(f"Cleaned up old metrics, retained {len(self.metrics_history)} metrics")
                
            except Exception as e:
                logger.error(f"Error during metrics cleanup: {e}")

class ContextualLogger:
    """Enhanced logger with context for ADK operations"""
    
    def __init__(self, service_name: str, logger_instance: logging.Logger = None):
        self.service_name = service_name
        self.logger = logger_instance or logging.getLogger(f"adk.{service_name}")
        self.context_stack: List[Dict[str, Any]] = []
    
    def push_context(self, **context):
        """Push context for logging"""
        self.context_stack.append(context)
    
    def pop_context(self):
        """Pop context from logging"""
        if self.context_stack:
            self.context_stack.pop()
    
    def _format_message(self, message: str) -> str:
        """Format message with context"""
        if not self.context_stack:
            return f"[{self.service_name}] {message}"
        
        context_parts = []
        for context in self.context_stack:
            for key, value in context.items():
                context_parts.append(f"{key}={value}")
        
        context_str = " ".join(context_parts)
        return f"[{self.service_name}] [{context_str}] {message}"
    
    def info(self, message: str, **kwargs):
        """Log info message with context"""
        self.logger.info(self._format_message(message), **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context"""
        self.logger.warning(self._format_message(message), **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with context"""
        self.logger.error(self._format_message(message), **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context"""
        self.logger.debug(self._format_message(message), **kwargs)

# Global monitor instance
_monitor: Optional[ADKMonitor] = None

def get_adk_monitor() -> ADKMonitor:
    """Get the global ADK monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = ADKMonitor()
    return _monitor

def create_service_logger(service_name: str) -> ContextualLogger:
    """Create a contextual logger for a service"""
    return ContextualLogger(service_name)

# Decorator for monitoring function calls
def monitor_adk_call(service_name: str, operation: str):
    """Decorator to monitor ADK service calls"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            monitor = get_adk_monitor()
            request_id = await monitor.record_request_start(service_name, operation)
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                response_time = time.time() - start_time
                
                await monitor.record_request_completion(
                    request_id, service_name, operation, True, response_time
                )
                return result
                
            except Exception as e:
                response_time = time.time() - start_time
                await monitor.record_request_completion(
                    request_id, service_name, operation, False, response_time, error=e
                )
                raise
        
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we'll use asyncio.create_task if in async context
            return asyncio.create_task(async_wrapper(*args, **kwargs))
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator