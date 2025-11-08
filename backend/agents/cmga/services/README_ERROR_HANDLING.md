# ADK Service Manager Error Handling and Monitoring

This document describes the comprehensive error handling and monitoring system implemented for the Google ADK Service Manager.

## Overview

The error handling system provides:
- **Retry mechanisms** with exponential backoff
- **Circuit breaker pattern** for service protection
- **Comprehensive monitoring** and metrics collection
- **Contextual logging** for debugging
- **Health checks** and diagnostics

## Components

### 1. Error Handlers (`error_handlers.py`)

#### ADKErrorHandler
Central error handling coordinator that manages retry logic and circuit breakers for all services.

**Key Features:**
- Service-specific retry configurations
- Circuit breaker protection
- Error classification and statistics
- Automatic recovery mechanisms

#### Error Classification
Errors are automatically classified into types:
- `AUTHENTICATION` - Authentication failures
- `RATE_LIMIT` - API rate limit exceeded
- `NETWORK` - Network connectivity issues
- `API_ERROR` - Google API errors
- `QUOTA_EXCEEDED` - Quota/billing limits
- `SERVICE_UNAVAILABLE` - Service temporarily down
- `TIMEOUT` - Request timeouts
- `UNKNOWN` - Unclassified errors

#### Retry Strategies
- **Exponential Backoff** (default) - Delay increases exponentially
- **Linear Backoff** - Delay increases linearly
- **Fixed Delay** - Constant delay between retries
- **No Retry** - For non-retryable errors

#### Circuit Breaker States
- **CLOSED** - Normal operation
- **OPEN** - Service blocked due to failures
- **HALF_OPEN** - Testing service recovery

### 2. Monitoring (`monitoring.py`)

#### ADKMonitor
Comprehensive monitoring system that tracks:
- Request counts and response times
- Success/error rates
- Rate limit hits
- Circuit breaker trips
- Service health metrics

#### Metrics Collection
- **Real-time metrics** - Live performance data
- **Historical data** - Configurable retention period
- **Request tracking** - Individual request lifecycle
- **Alert thresholds** - Configurable alerting

#### Performance Statistics
For each service and operation:
- Total/successful/failed request counts
- Average/min/max response times
- Success and error rates
- Rate limiting statistics
- Circuit breaker activity

### 3. Enhanced Service Manager (`adk_service_manager.py`)

The ADK Service Manager integrates all error handling and monitoring:
- Automatic retry with circuit breaker protection
- Comprehensive request/response logging
- Performance metrics collection
- Health status reporting

## Configuration

### Service-Specific Configurations

Each Google ADK service has optimized configurations:

```python
SERVICE_CONFIGS = {
    "vertex_ai": {
        "retry": RetryConfig(
            max_attempts=3,
            base_delay=2.0,
            max_delay=120.0,
            backoff_factor=2.0
        ),
        "circuit_breaker": CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=120.0
        )
    },
    "vision_api": {
        "retry": RetryConfig(
            max_attempts=2,
            base_delay=1.0,
            max_delay=30.0
        ),
        "circuit_breaker": CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60.0
        )
    }
    # ... other services
}
```

### Alert Thresholds

Default alert thresholds:
- **Error Rate**: 15%
- **Response Time**: 10 seconds
- **Success Rate**: 85%

## Usage Examples

### Basic Service Call with Error Protection

```python
from services import get_adk_service_manager

async def example_usage():
    service_manager = get_adk_service_manager()
    await service_manager.initialize()
    
    try:
        result = await service_manager.optimize_portfolio(
            market_data={"crop": "wheat", "price": 100},
            climate_data={"temperature": 25, "rainfall": 50},
            yield_data={"expected_yield": 1000}
        )
        print(f"Portfolio optimization successful: {result}")
        
    except CircuitBreakerOpenError:
        print("Service temporarily unavailable - circuit breaker open")
        
    except RetryExhaustedError as e:
        print(f"All retry attempts failed: {e.original_error}")
        
    except Exception as e:
        print(f"Unexpected error: {e}")
```

### Health Monitoring

```python
# Get comprehensive health status
health = service_manager.get_health_check()
print(f"Overall health: {health['overall_health']}")
print(f"Services available: {health['services_available']}")

# Get detailed metrics
metrics = service_manager.get_detailed_metrics(hours=24)
print(f"Performance stats: {metrics['performance_stats']}")

# Test specific service connectivity
connectivity = await service_manager.test_service_connectivity("vertex_ai")
print(f"Vertex AI status: {connectivity['status']}")
```

### Error Recovery

```python
# Reset circuit breakers for all services
reset_results = await service_manager.reset_error_handling()
print(f"Reset results: {reset_results}")

# Reset specific service
reset_result = await service_manager.reset_error_handling("vertex_ai")
print(f"Vertex AI reset: {reset_result}")

# Refresh service connections
refresh_success = await service_manager.refresh_services()
print(f"Services refreshed: {refresh_success}")
```

## Monitoring and Alerting

### Real-time Monitoring

```python
from services.monitoring import get_adk_monitor

monitor = get_adk_monitor()

# Get current health summary
health = monitor.get_health_summary()
print(f"Health status: {health['health_status']}")
print(f"Total requests: {health['total_requests']}")
print(f"Error rate: {health['overall_error_rate']}%")

# Get service-specific stats
vertex_stats = monitor.get_service_stats("vertex_ai")
print(f"Vertex AI success rate: {vertex_stats['optimize_portfolio']['success_rate']}%")
```

### Custom Alert Callbacks

```python
async def custom_alert_handler(service_name, metric_type, current_value, threshold):
    print(f"ALERT: {service_name} {metric_type.value} = {current_value} (threshold: {threshold})")
    # Send notification, log to external system, etc.

monitor.add_alert_callback(custom_alert_handler)
```

## Testing

### Running Error Handling Tests

```bash
cd backend/agents/cmga
python scripts/test_error_handling.py
```

The test suite validates:
- Retry mechanisms with different error types
- Circuit breaker functionality
- Monitoring and metrics collection
- Health check accuracy
- Error recovery procedures

### Test Results

The test script generates:
- Console output with test results
- JSON file with detailed results
- Success/failure statistics
- Performance metrics

## Logging

### Contextual Logging

Each service has contextual logging that includes:
- Service name and operation
- Request context (IDs, data sizes)
- Performance metrics
- Error details

### Log Levels

- **INFO** - Normal operations, successful requests
- **WARNING** - Retries, rate limits, degraded performance
- **ERROR** - Failures, circuit breaker trips, authentication issues
- **DEBUG** - Detailed request/response data

### Log Format

```
[timestamp] - [service_name] - [level] - [context] message
```

Example:
```
2024-01-15 10:30:45 - vertex_ai - INFO - [operation=optimize_portfolio farmer_id=F123] Portfolio optimization completed successfully
2024-01-15 10:30:46 - vertex_ai - WARNING - [operation=calculate_credit_score] Attempt 1/3 failed, retrying in 2.0s: Rate limit exceeded
```

## Best Practices

### Error Handling
1. Always use the service manager's protected methods
2. Handle specific exceptions (CircuitBreakerOpenError, RetryExhaustedError)
3. Implement graceful degradation for non-critical operations
4. Monitor error rates and adjust thresholds as needed

### Performance
1. Use appropriate retry configurations for each service
2. Monitor response times and adjust timeouts
3. Implement caching for frequently requested data
4. Use batch operations when possible

### Monitoring
1. Set up alerts for critical metrics
2. Review error patterns regularly
3. Monitor circuit breaker activity
4. Track service health trends

### Recovery
1. Implement automatic recovery procedures
2. Have manual override capabilities
3. Test recovery scenarios regularly
4. Document incident response procedures

## Troubleshooting

### Common Issues

#### High Error Rates
1. Check Google Cloud service status
2. Verify authentication credentials
3. Review rate limiting configuration
4. Check network connectivity

#### Circuit Breaker Trips
1. Identify root cause of failures
2. Adjust failure thresholds if needed
3. Implement manual reset procedures
4. Monitor recovery patterns

#### Performance Issues
1. Review response time metrics
2. Check for rate limiting
3. Optimize request patterns
4. Consider caching strategies

### Diagnostic Commands

```python
# Get comprehensive health check
health = service_manager.get_health_check()

# Get error statistics
error_stats = service_manager.error_handler.get_error_stats()

# Get circuit breaker status
cb_status = service_manager.error_handler.get_circuit_breaker_status()

# Get recent requests
recent_requests = service_manager.monitor.get_recent_requests(limit=100)
```

## Future Enhancements

Planned improvements:
1. **Adaptive thresholds** - Dynamic adjustment based on historical data
2. **Predictive alerting** - ML-based anomaly detection
3. **Advanced caching** - Intelligent cache invalidation
4. **Load balancing** - Multiple endpoint support
5. **Metrics export** - Integration with external monitoring systems

## Support

For issues or questions:
1. Check the test results and logs
2. Review the health check output
3. Consult the troubleshooting guide
4. Contact the development team with diagnostic information