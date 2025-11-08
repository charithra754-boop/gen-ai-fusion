"""
Comprehensive error handling and retry mechanisms for Google ADK services
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Type, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import random
import json

from google.api_core import exceptions as google_exceptions
from google.auth.exceptions import GoogleAuthError
from requests.exceptions import RequestException, ConnectionError, Timeout

logger = logging.getLogger(__name__)

class ErrorType(Enum):
    """Types of errors that can occur"""
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    NETWORK = "network"
    API_ERROR = "api_error"
    QUOTA_EXCEEDED = "quota_exceeded"
    SERVICE_UNAVAILABLE = "service_unavailable"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"

class RetryStrategy(Enum):
    """Retry strategies"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    NO_RETRY = "no_retry"

@dataclass
class ErrorContext:
    """Context information for errors"""
    service_name: str
    operation: str
    attempt: int
    error_type: ErrorType
    original_error: Exception
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    retryable_errors: set = field(default_factory=lambda: {
        ErrorType.NETWORK,
        ErrorType.TIMEOUT,
        ErrorType.SERVICE_UNAVAILABLE,
        ErrorType.RATE_LIMIT
    })

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    success_threshold: int = 3
    half_open_max_calls: int = 5

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerStatus:
    """Circuit breaker status tracking"""
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None
    half_open_calls: int = 0

class ADKErrorClassifier:
    """Classifies different types of errors"""
    
    @staticmethod
    def classify_error(error: Exception) -> ErrorType:
        """Classify an error into an ErrorType"""
        
        # Google API Core exceptions
        if isinstance(error, google_exceptions.Unauthenticated):
            return ErrorType.AUTHENTICATION
        elif isinstance(error, google_exceptions.TooManyRequests):
            return ErrorType.RATE_LIMIT
        elif isinstance(error, google_exceptions.ResourceExhausted):
            return ErrorType.QUOTA_EXCEEDED
        elif isinstance(error, google_exceptions.ServiceUnavailable):
            return ErrorType.SERVICE_UNAVAILABLE
        elif isinstance(error, google_exceptions.DeadlineExceeded):
            return ErrorType.TIMEOUT
        elif isinstance(error, google_exceptions.GoogleAPIError):
            return ErrorType.API_ERROR
        
        # Google Auth exceptions
        elif isinstance(error, GoogleAuthError):
            return ErrorType.AUTHENTICATION
        
        # Network exceptions
        elif isinstance(error, (ConnectionError, Timeout)):
            return ErrorType.NETWORK
        elif isinstance(error, RequestException):
            return ErrorType.NETWORK
        
        # Default
        else:
            return ErrorType.UNKNOWN
    
    @staticmethod
    def is_retryable(error_type: ErrorType, retry_config: RetryConfig) -> bool:
        """Check if an error type is retryable"""
        return error_type in retry_config.retryable_errors
    
    @staticmethod
    def get_retry_delay(error: Exception) -> Optional[float]:
        """Extract retry delay from error if available"""
        if isinstance(error, google_exceptions.TooManyRequests):
            # Try to extract retry-after header
            if hasattr(error, 'response') and error.response:
                retry_after = error.response.headers.get('Retry-After')
                if retry_after:
                    try:
                        return float(retry_after)
                    except ValueError:
                        pass
        return None

class CircuitBreaker:
    """Circuit breaker implementation for service protection"""
    
    def __init__(self, service_name: str, config: CircuitBreakerConfig):
        self.service_name = service_name
        self.config = config
        self.status = CircuitBreakerStatus()
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        async with self._lock:
            await self._check_state()
            
            if self.status.state == CircuitBreakerState.OPEN:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN for {self.service_name}"
                )
            
            if self.status.state == CircuitBreakerState.HALF_OPEN:
                if self.status.half_open_calls >= self.config.half_open_max_calls:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker HALF_OPEN call limit exceeded for {self.service_name}"
                    )
                self.status.half_open_calls += 1
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await self._on_success()
            return result
            
        except Exception as e:
            await self._on_failure(e)
            raise
    
    async def _check_state(self):
        """Check and update circuit breaker state"""
        now = datetime.now()
        
        if self.status.state == CircuitBreakerState.OPEN:
            if (self.status.next_attempt_time and 
                now >= self.status.next_attempt_time):
                self.status.state = CircuitBreakerState.HALF_OPEN
                self.status.half_open_calls = 0
                logger.info(f"Circuit breaker for {self.service_name} moved to HALF_OPEN")
    
    async def _on_success(self):
        """Handle successful call"""
        async with self._lock:
            if self.status.state == CircuitBreakerState.HALF_OPEN:
                self.status.success_count += 1
                if self.status.success_count >= self.config.success_threshold:
                    self.status.state = CircuitBreakerState.CLOSED
                    self.status.failure_count = 0
                    self.status.success_count = 0
                    logger.info(f"Circuit breaker for {self.service_name} moved to CLOSED")
            else:
                self.status.failure_count = 0
    
    async def _on_failure(self, error: Exception):
        """Handle failed call"""
        async with self._lock:
            self.status.failure_count += 1
            self.status.last_failure_time = datetime.now()
            
            if self.status.state == CircuitBreakerState.HALF_OPEN:
                self.status.state = CircuitBreakerState.OPEN
                self.status.next_attempt_time = (
                    datetime.now() + timedelta(seconds=self.config.recovery_timeout)
                )
                logger.warning(f"Circuit breaker for {self.service_name} moved to OPEN (half-open failure)")
            
            elif (self.status.state == CircuitBreakerState.CLOSED and 
                  self.status.failure_count >= self.config.failure_threshold):
                self.status.state = CircuitBreakerState.OPEN
                self.status.next_attempt_time = (
                    datetime.now() + timedelta(seconds=self.config.recovery_timeout)
                )
                logger.warning(f"Circuit breaker for {self.service_name} moved to OPEN (threshold exceeded)")
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            "service": self.service_name,
            "state": self.status.state.value,
            "failure_count": self.status.failure_count,
            "success_count": self.status.success_count,
            "last_failure": self.status.last_failure_time.isoformat() if self.status.last_failure_time else None,
            "next_attempt": self.status.next_attempt_time.isoformat() if self.status.next_attempt_time else None,
            "half_open_calls": self.status.half_open_calls
        }

class RetryHandler:
    """Handles retry logic with various strategies"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    async def execute_with_retry(self, 
                               func: Callable,
                               service_name: str,
                               operation: str,
                               *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        
        last_error = None
        
        for attempt in range(self.config.max_attempts):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
                    
            except Exception as error:
                last_error = error
                error_type = ADKErrorClassifier.classify_error(error)
                
                error_context = ErrorContext(
                    service_name=service_name,
                    operation=operation,
                    attempt=attempt + 1,
                    error_type=error_type,
                    original_error=error
                )
                
                # Log the error
                logger.warning(
                    f"Attempt {attempt + 1}/{self.config.max_attempts} failed for "
                    f"{service_name}.{operation}: {error_type.value} - {error}"
                )
                
                # Check if we should retry
                if attempt == self.config.max_attempts - 1:
                    # Last attempt, don't retry
                    break
                
                if not ADKErrorClassifier.is_retryable(error_type, self.config):
                    logger.error(f"Non-retryable error for {service_name}.{operation}: {error}")
                    break
                
                # Calculate delay
                delay = self._calculate_delay(attempt, error)
                
                logger.info(f"Retrying {service_name}.{operation} in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
        
        # All retries exhausted
        raise RetryExhaustedError(
            f"All {self.config.max_attempts} retry attempts exhausted for {service_name}.{operation}",
            last_error
        )
    
    def _calculate_delay(self, attempt: int, error: Exception) -> float:
        """Calculate delay for next retry attempt"""
        
        # Check if error specifies a retry delay
        suggested_delay = ADKErrorClassifier.get_retry_delay(error)
        if suggested_delay:
            return min(suggested_delay, self.config.max_delay)
        
        # Calculate based on strategy
        if self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (self.config.backoff_factor ** attempt)
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * (attempt + 1)
        elif self.config.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.config.base_delay
        else:
            delay = self.config.base_delay
        
        # Apply jitter if enabled
        if self.config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)
        
        # Ensure delay is within bounds
        return max(0, min(delay, self.config.max_delay))

class ADKErrorHandler:
    """Main error handler for ADK services"""
    
    def __init__(self):
        self.retry_configs: Dict[str, RetryConfig] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.error_stats: Dict[str, Dict[str, int]] = {}
        self._lock = asyncio.Lock()
    
    def configure_service(self, 
                         service_name: str,
                         retry_config: Optional[RetryConfig] = None,
                         circuit_breaker_config: Optional[CircuitBreakerConfig] = None):
        """Configure error handling for a service"""
        
        # Set retry configuration
        self.retry_configs[service_name] = retry_config or RetryConfig()
        
        # Set circuit breaker
        if circuit_breaker_config:
            self.circuit_breakers[service_name] = CircuitBreaker(
                service_name, circuit_breaker_config
            )
        
        # Initialize error stats
        self.error_stats[service_name] = {error_type.value: 0 for error_type in ErrorType}
        
        logger.info(f"Error handling configured for service: {service_name}")
    
    async def execute_with_protection(self,
                                    service_name: str,
                                    operation: str,
                                    func: Callable,
                                    *args, **kwargs) -> Any:
        """Execute function with full error protection (retry + circuit breaker)"""
        
        # Ensure service is configured
        if service_name not in self.retry_configs:
            self.configure_service(service_name)
        
        retry_handler = RetryHandler(self.retry_configs[service_name])
        
        # Wrap function with circuit breaker if available
        if service_name in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[service_name]
            
            async def protected_func(*args, **kwargs):
                return await circuit_breaker.call(func, *args, **kwargs)
            
            execution_func = protected_func
        else:
            execution_func = func
        
        try:
            return await retry_handler.execute_with_retry(
                execution_func, service_name, operation, *args, **kwargs
            )
        except Exception as error:
            await self._record_error(service_name, error)
            raise
    
    async def _record_error(self, service_name: str, error: Exception):
        """Record error statistics"""
        async with self._lock:
            error_type = ADKErrorClassifier.classify_error(error)
            
            if service_name not in self.error_stats:
                self.error_stats[service_name] = {et.value: 0 for et in ErrorType}
            
            self.error_stats[service_name][error_type.value] += 1
    
    def get_error_stats(self) -> Dict[str, Dict[str, int]]:
        """Get error statistics for all services"""
        return self.error_stats.copy()
    
    def get_circuit_breaker_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers"""
        return {
            name: breaker.get_status()
            for name, breaker in self.circuit_breakers.items()
        }
    
    def reset_circuit_breaker(self, service_name: str) -> bool:
        """Manually reset a circuit breaker"""
        if service_name in self.circuit_breakers:
            breaker = self.circuit_breakers[service_name]
            breaker.status = CircuitBreakerStatus()
            logger.info(f"Circuit breaker reset for {service_name}")
            return True
        return False
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        total_errors = sum(
            sum(errors.values()) for errors in self.error_stats.values()
        )
        
        circuit_breaker_states = {
            name: breaker.status.state.value
            for name, breaker in self.circuit_breakers.items()
        }
        
        open_breakers = sum(
            1 for state in circuit_breaker_states.values()
            if state == CircuitBreakerState.OPEN.value
        )
        
        return {
            "total_errors": total_errors,
            "services_monitored": len(self.error_stats),
            "circuit_breakers": len(self.circuit_breakers),
            "open_circuit_breakers": open_breakers,
            "circuit_breaker_states": circuit_breaker_states,
            "error_breakdown": self.error_stats,
            "timestamp": datetime.now().isoformat()
        }

# Custom exceptions
class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass

class RetryExhaustedError(Exception):
    """Raised when all retry attempts are exhausted"""
    
    def __init__(self, message: str, original_error: Exception):
        super().__init__(message)
        self.original_error = original_error

# Default configurations
DEFAULT_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    max_delay=60.0,
    backoff_factor=2.0,
    jitter=True,
    strategy=RetryStrategy.EXPONENTIAL_BACKOFF
)

DEFAULT_CIRCUIT_BREAKER_CONFIG = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=60.0,
    success_threshold=3,
    half_open_max_calls=5
)

# Service-specific configurations
SERVICE_CONFIGS = {
    "vertex_ai": {
        "retry": RetryConfig(
            max_attempts=3,
            base_delay=2.0,
            max_delay=120.0,
            backoff_factor=2.0,
            retryable_errors={
                ErrorType.NETWORK,
                ErrorType.TIMEOUT,
                ErrorType.SERVICE_UNAVAILABLE,
                ErrorType.RATE_LIMIT
            }
        ),
        "circuit_breaker": CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=120.0,
            success_threshold=2
        )
    },
    "vision_api": {
        "retry": RetryConfig(
            max_attempts=2,
            base_delay=1.0,
            max_delay=30.0,
            retryable_errors={
                ErrorType.NETWORK,
                ErrorType.TIMEOUT,
                ErrorType.RATE_LIMIT
            }
        ),
        "circuit_breaker": CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60.0
        )
    },
    "natural_language": {
        "retry": RetryConfig(
            max_attempts=2,
            base_delay=1.0,
            max_delay=30.0,
            retryable_errors={
                ErrorType.NETWORK,
                ErrorType.TIMEOUT,
                ErrorType.RATE_LIMIT
            }
        ),
        "circuit_breaker": CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60.0
        )
    },
    "storage": {
        "retry": RetryConfig(
            max_attempts=3,
            base_delay=0.5,
            max_delay=10.0,
            retryable_errors={
                ErrorType.NETWORK,
                ErrorType.TIMEOUT,
                ErrorType.SERVICE_UNAVAILABLE
            }
        ),
        "circuit_breaker": CircuitBreakerConfig(
            failure_threshold=10,
            recovery_timeout=30.0
        )
    }
}