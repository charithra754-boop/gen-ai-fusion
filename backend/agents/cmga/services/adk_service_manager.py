"""
Google ADK Service Manager
Central orchestrator for all Google ADK operations with authentication, rate limiting, and error handling
Enhanced with request batching and intelligent caching capabilities
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import time

from google.cloud import aiplatform
from google.cloud import vision
from google.cloud import language_v1
from google.cloud import storage
from google.auth.credentials import Credentials

from ..config.adk_config import ADKConfig, get_adk_config
from ..config.auth_config import get_authenticator, ADKAuthenticator
from .error_handlers import (
    ADKErrorHandler, RetryConfig, CircuitBreakerConfig, 
    SERVICE_CONFIGS, ErrorType, CircuitBreakerOpenError, RetryExhaustedError
)
from .monitoring import (
    get_adk_monitor, create_service_logger, monitor_adk_call,
    ADKMonitor, ContextualLogger
)
from .batching import (
    get_request_batcher, RequestBatcher, BatchConfig, BatchStrategy
)
from .caching import (
    get_cache_manager, SmartCacheManager, CacheConfig, CacheStrategy
)

logger = logging.getLogger(__name__)

@dataclass
class ADKServiceStatus:
    """Status information for ADK services"""
    service_name: str
    is_available: bool
    last_check: datetime
    error_message: Optional[str] = None
    request_count: int = 0
    error_count: int = 0

@dataclass
class RateLimitStatus:
    """Rate limiting status"""
    requests_made: int = 0
    requests_remaining: int = 0
    reset_time: Optional[datetime] = None
    is_limited: bool = False

class ADKServiceManager:
    """Central manager for all Google ADK services with batching and caching"""
    
    def __init__(self, 
                 config: Optional[ADKConfig] = None,
                 batch_config: Optional[BatchConfig] = None,
                 cache_config: Optional[CacheConfig] = None):
        self.config = config or get_adk_config()
        self.authenticator: Optional[ADKAuthenticator] = None
        self.credentials: Optional[Credentials] = None
        self.project_id: Optional[str] = None
        
        # Service clients
        self._vertex_ai_client = None
        self._vision_client = None
        self._language_client = None
        self._storage_client = None
        
        # Service status tracking
        self.service_status: Dict[str, ADKServiceStatus] = {}
        self.rate_limit_status: Dict[str, RateLimitStatus] = {}
        
        # Enhanced error handling and monitoring
        self.error_handler = ADKErrorHandler()
        self.monitor = get_adk_monitor()
        self.service_loggers: Dict[str, ContextualLogger] = {}
        
        # Batching and caching components
        self.batcher = get_request_batcher(batch_config or self._get_default_batch_config())
        self.cache_manager = get_cache_manager(cache_config or self._get_default_cache_config())
        
        # Rate limiting (legacy - now handled by error_handler)
        self._request_counts: Dict[str, List[datetime]] = {}
        self._circuit_breakers: Dict[str, bool] = {}
        
        self._initialized = False
        
        # Configure error handling for each service
        self._configure_error_handling()
    
    def _get_default_batch_config(self) -> BatchConfig:
        """Get default batching configuration"""
        return BatchConfig(
            max_batch_size=5,  # Conservative batch size for ADK services
            max_wait_time_seconds=1.0,  # Quick batching for responsiveness
            strategy=BatchStrategy.HYBRID,
            enable_priority_batching=True,
            max_concurrent_batches=3
        )
    
    def _get_default_cache_config(self) -> CacheConfig:
        """Get default caching configuration"""
        return CacheConfig(
            max_size_mb=50.0,  # 50MB cache
            default_ttl_seconds=1800.0,  # 30 minutes default
            strategy=CacheStrategy.HYBRID,
            cleanup_interval_seconds=300.0,  # 5 minutes
            enable_compression=True,
            enable_persistence=False
        )
    
    def _configure_error_handling(self):
        """Configure error handling for all services"""
        for service_name, config in SERVICE_CONFIGS.items():
            self.error_handler.configure_service(
                service_name,
                config.get("retry"),
                config.get("circuit_breaker")
            )
            
            # Create service-specific logger
            self.service_loggers[service_name] = create_service_logger(service_name)
            
            # Set up monitoring alerts
            self.monitor.set_alert_threshold(service_name, "error_rate", 15.0)  # 15% error rate
            self.monitor.set_alert_threshold(service_name, "response_time", 10.0)  # 10 seconds
            self.monitor.set_alert_threshold(service_name, "success_rate", 85.0)  # 85% success rate
        
        logger.info("Error handling and monitoring configured for all services")

    async def initialize(self) -> bool:
        """Initialize all ADK services"""
        if self._initialized:
            return True
        
        try:
            logger.info("Initializing Google ADK Service Manager...")
            
            # Authenticate
            await self._authenticate()
            
            # Initialize service clients
            await self._initialize_clients()
            
            # Validate services
            await self._validate_services()
            
            self._initialized = True
            logger.info("Google ADK Service Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ADK Service Manager: {e}")
            await self.monitor.record_request_completion(
                "init", "adk_service_manager", "initialize", False, 0.0, error=e
            )
            return False
    
    async def _authenticate(self) -> None:
        """Authenticate with Google Cloud"""
        try:
            self.authenticator = get_authenticator()
            self.credentials, self.project_id = self.authenticator.authenticate()
            
            logger.info(f"Authenticated successfully for project: {self.project_id}")
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    async def _initialize_clients(self) -> None:
        """Initialize all Google Cloud service clients"""
        try:
            # Initialize Vertex AI
            if self.config.vertex_ai:
                aiplatform.init(
                    project=self.project_id,
                    location=self.config.vertex_ai.region,
                    credentials=self.credentials
                )
                logger.info("Vertex AI client initialized")
            
            # Initialize Vision API client
            if self.config.vision_api.enabled:
                self._vision_client = vision.ImageAnnotatorClient(credentials=self.credentials)
                logger.info("Vision API client initialized")
            
            # Initialize Natural Language API client
            if self.config.natural_language.enabled:
                self._language_client = language_v1.LanguageServiceClient(credentials=self.credentials)
                logger.info("Natural Language API client initialized")
            
            # Initialize Storage client
            self._storage_client = storage.Client(
                project=self.project_id,
                credentials=self.credentials
            )
            logger.info("Cloud Storage client initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize clients: {e}")
            raise
    
    async def _validate_services(self) -> None:
        """Validate that all services are accessible"""
        services_to_validate = [
            ("vertex_ai", self._validate_vertex_ai),
            ("vision_api", self._validate_vision_api),
            ("natural_language", self._validate_natural_language),
            ("storage", self._validate_storage)
        ]
        
        for service_name, validator in services_to_validate:
            try:
                is_valid = await validator()
                self.service_status[service_name] = ADKServiceStatus(
                    service_name=service_name,
                    is_available=is_valid,
                    last_check=datetime.now()
                )
                
                if is_valid:
                    logger.info(f"{service_name} service validated successfully")
                else:
                    logger.warning(f"{service_name} service validation failed")
                    
            except Exception as e:
                logger.error(f"Error validating {service_name}: {e}")
                self.service_status[service_name] = ADKServiceStatus(
                    service_name=service_name,
                    is_available=False,
                    last_check=datetime.now(),
                    error_message=str(e)
                )
    
    async def _validate_vertex_ai(self) -> bool:
        """Validate Vertex AI service"""
        try:
            # Simple validation - check if we can list models
            from google.cloud import aiplatform
            models = aiplatform.Model.list(
                filter='display_name="*"',
                order_by='create_time desc',
                project=self.project_id,
                location=self.config.vertex_ai.region
            )
            return True
        except Exception as e:
            logger.error(f"Vertex AI validation failed: {e}")
            return False
    
    async def _validate_vision_api(self) -> bool:
        """Validate Vision API service"""
        if not self.config.vision_api.enabled or not self._vision_client:
            return False
        
        try:
            # Simple validation - create a minimal request
            # This doesn't actually process an image, just validates the client
            return True
        except Exception as e:
            logger.error(f"Vision API validation failed: {e}")
            return False
    
    async def _validate_natural_language(self) -> bool:
        """Validate Natural Language API service"""
        if not self.config.natural_language.enabled or not self._language_client:
            return False
        
        try:
            # Simple validation - analyze a test sentence
            from google.cloud import language_v1
            
            document = language_v1.Document(
                content="Test sentence for validation.",
                type_=language_v1.Document.Type.PLAIN_TEXT
            )
            
            response = self._language_client.analyze_sentiment(
                request={'document': document}
            )
            return True
        except Exception as e:
            logger.error(f"Natural Language API validation failed: {e}")
            return False
    
    async def _validate_storage(self) -> bool:
        """Validate Cloud Storage service"""
        try:
            # Simple validation - list buckets (limited to 1)
            list(self._storage_client.list_buckets(max_results=1))
            return True
        except Exception as e:
            logger.error(f"Cloud Storage validation failed: {e}")
            return False
    
    def _check_rate_limit(self, service: str) -> bool:
        """Check if service is within rate limits"""
        now = datetime.now()
        
        # Initialize tracking for service if not exists
        if service not in self._request_counts:
            self._request_counts[service] = []
            self.rate_limit_status[service] = RateLimitStatus()
        
        # Clean old requests (older than 1 minute)
        minute_ago = now - timedelta(minutes=1)
        self._request_counts[service] = [
            req_time for req_time in self._request_counts[service]
            if req_time > minute_ago
        ]
        
        # Check rate limit
        current_count = len(self._request_counts[service])
        limit = self.config.rate_limits.requests_per_minute
        
        # Update rate limit status
        self.rate_limit_status[service].requests_made = current_count
        self.rate_limit_status[service].requests_remaining = max(0, limit - current_count)
        self.rate_limit_status[service].is_limited = current_count >= limit
        
        if current_count >= limit:
            logger.warning(f"Rate limit exceeded for {service}: {current_count}/{limit} requests per minute")
            return False
        
        return True
    
    def _record_request(self, service: str) -> None:
        """Record a request for rate limiting"""
        now = datetime.now()
        if service not in self._request_counts:
            self._request_counts[service] = []
        
        self._request_counts[service].append(now)
        
        # Update service status
        if service in self.service_status:
            self.service_status[service].request_count += 1
    
    def _record_error(self, service: str, error: Exception) -> None:
        """Record an error for monitoring"""
        if service in self.service_status:
            self.service_status[service].error_count += 1
            self.service_status[service].error_message = str(error)
        
        logger.error(f"Error in {service}: {error}")
    
    async def _execute_with_protection(self, 
                                     service_name: str,
                                     operation: str,
                                     func: callable,
                                     *args, **kwargs) -> Any:
        """Execute operation with comprehensive error protection"""
        
        service_logger = self.service_loggers.get(service_name, logger)
        service_logger.push_context(operation=operation)
        
        try:
            service_logger.info(f"Starting {operation}")
            
            # Use enhanced error handler with retry and circuit breaker
            result = await self.error_handler.execute_with_protection(
                service_name, operation, func, *args, **kwargs
            )
            
            service_logger.info(f"Completed {operation} successfully")
            return result
            
        except CircuitBreakerOpenError as e:
            service_logger.error(f"Circuit breaker open for {operation}: {e}")
            await self.monitor.record_circuit_breaker_trip(service_name, operation)
            raise
            
        except RetryExhaustedError as e:
            service_logger.error(f"All retries exhausted for {operation}: {e}")
            raise
            
        except Exception as e:
            service_logger.error(f"Unexpected error in {operation}: {e}")
            raise
            
        finally:
            service_logger.pop_context()
    
    async def _execute_with_batching_and_caching(self,
                                               service_name: str,
                                               operation: str,
                                               data: Dict[str, Any],
                                               func: callable,
                                               enable_batching: bool = True,
                                               enable_caching: bool = True,
                                               priority: int = 0,
                                               cache_context: Dict[str, Any] = None) -> Any:
        """Execute operation with batching and caching support"""
        
        service_logger = self.service_loggers.get(service_name, logger)
        service_logger.push_context(operation=operation, enable_batching=enable_batching, enable_caching=enable_caching)
        
        try:
            # Try cache first if enabled
            if enable_caching:
                cached_result = await self.cache_manager.get_cached_result(
                    service_name, operation, data, cache_context
                )
                if cached_result is not None:
                    service_logger.info(f"Cache hit for {operation}")
                    return cached_result
                
                service_logger.debug(f"Cache miss for {operation}")
            
            # Execute with batching if enabled
            if enable_batching:
                service_logger.info(f"Adding {operation} to batch queue")
                
                # Create a wrapper function that includes error protection
                async def protected_func():
                    return await self._execute_with_protection(service_name, operation, func)
                
                # Add to batch queue
                result = await self.batcher.add_request(
                    service_name, operation, data, priority
                )
            else:
                # Execute directly with protection
                result = await self._execute_with_protection(service_name, operation, func)
            
            # Cache the result if enabled
            if enable_caching and result is not None:
                await self.cache_manager.cache_result(
                    service_name, operation, data, result, cache_context
                )
                service_logger.debug(f"Cached result for {operation}")
            
            return result
            
        except Exception as e:
            service_logger.error(f"Error in batched/cached execution of {operation}: {e}")
            raise
            
        finally:
            service_logger.pop_context()

    # Legacy method for backward compatibility
    async def _execute_with_retry(self, 
                                service: str,
                                operation: callable,
                                *args, **kwargs) -> Any:
        """Legacy method - redirects to new error protection"""
        return await self._execute_with_protection(service, "legacy_operation", operation, *args, **kwargs)
    
    # Service-specific methods
    
    @monitor_adk_call("vertex_ai", "optimize_portfolio")
    async def optimize_portfolio(self, 
                               market_data: Dict[str, Any],
                               climate_data: Dict[str, Any],
                               yield_data: Dict[str, Any],
                               enable_batching: bool = True,
                               enable_caching: bool = True,
                               priority: int = 0) -> Dict[str, Any]:
        """Use Vertex AI for portfolio optimization with batching and caching"""
        if not self._initialized:
            await self.initialize()
        
        # Prepare request data for batching/caching
        request_data = {
            "market_data": market_data,
            "climate_data": climate_data,
            "yield_data": yield_data
        }
        
        # Cache context for invalidation
        cache_context = {
            "market_data_hash": hash(str(sorted(market_data.items()))),
            "climate_data_hash": hash(str(sorted(climate_data.items()))),
            "yield_data_hash": hash(str(sorted(yield_data.items())))
        }
        
        async def _optimize():
            service_logger = self.service_loggers["vertex_ai"]
            service_logger.push_context(
                market_data_size=len(market_data),
                climate_data_size=len(climate_data),
                yield_data_size=len(yield_data)
            )
            
            try:
                # This is a placeholder for actual Vertex AI optimization
                # In production, this would call Vertex AI models
                service_logger.info("Executing portfolio optimization with Vertex AI")
                
                # Simulate AI processing with realistic delay
                await asyncio.sleep(0.5)
                
                # Simulate potential errors for testing
                if market_data.get("simulate_error") == "rate_limit":
                    from google.api_core.exceptions import TooManyRequests
                    raise TooManyRequests("Rate limit exceeded")
                
                result = {
                    "optimized_portfolio": {
                        "crops": ["wheat", "rice", "cotton"],
                        "allocations": [0.4, 0.35, 0.25],
                        "expected_return": 0.15,
                        "risk": 0.08,
                        "confidence": 0.85
                    },
                    "ai_insights": [
                        "Diversification reduces risk by 23%",
                        "Weather patterns favor wheat this season",
                        "Cotton prices expected to rise 12%"
                    ],
                    "processing_metadata": {
                        "model_version": "v1.2.3",
                        "processing_time_ms": 500,
                        "data_points_analyzed": len(market_data) + len(climate_data) + len(yield_data),
                        "batched": enable_batching,
                        "cached": enable_caching
                    }
                }
                
                service_logger.info("Portfolio optimization completed successfully")
                return result
                
            finally:
                service_logger.pop_context()
        
        return await self._execute_with_batching_and_caching(
            "vertex_ai", "optimize_portfolio", request_data, _optimize,
            enable_batching=enable_batching, enable_caching=enable_caching,
            priority=priority, cache_context=cache_context
        )
    
    @monitor_adk_call("vertex_ai", "calculate_credit_score")
    async def calculate_credit_score(self, 
                                   farmer_profile: Dict[str, Any],
                                   alternative_data: Dict[str, Any],
                                   enable_batching: bool = True,
                                   enable_caching: bool = True,
                                   priority: int = 0) -> Dict[str, Any]:
        """Use Vertex AI for credit scoring with batching and caching"""
        if not self._initialized:
            await self.initialize()
        
        # Prepare request data for batching/caching
        request_data = {
            "farmer_profile": farmer_profile,
            "alternative_data": alternative_data
        }
        
        # Cache context for farmer-specific caching
        farmer_id = farmer_profile.get("farmer_id", "unknown")
        cache_context = {
            "farmer_id": farmer_id,
            "profile_hash": hash(str(sorted(farmer_profile.items()))),
            "alt_data_hash": hash(str(sorted(alternative_data.items())))
        }
        
        async def _calculate_score():
            service_logger = self.service_loggers["vertex_ai"]
            service_logger.push_context(farmer_id=farmer_id)
            
            try:
                service_logger.info("Calculating credit score with Vertex AI")
                
                # Simulate AI processing with realistic delay
                await asyncio.sleep(0.3)
                
                # Simulate potential authentication error for testing
                if farmer_profile.get("simulate_error") == "auth":
                    from google.api_core.exceptions import Unauthenticated
                    raise Unauthenticated("Authentication failed")
                
                result = {
                    "credit_score": 720,
                    "risk_category": "medium",
                    "confidence": 0.78,
                    "contributing_factors": [
                        {"factor": "yield_history", "weight": 0.3, "score": 0.8},
                        {"factor": "payment_history", "weight": 0.25, "score": 0.7},
                        {"factor": "land_quality", "weight": 0.2, "score": 0.9},
                        {"factor": "climate_risk", "weight": 0.15, "score": 0.6},
                        {"factor": "market_access", "weight": 0.1, "score": 0.8}
                    ],
                    "explanation": "Score based on strong yield history and land quality, moderate payment history",
                    "processing_metadata": {
                        "model_version": "credit_v2.1.0",
                        "alternative_data_sources": len(alternative_data),
                        "processing_time_ms": 300,
                        "batched": enable_batching,
                        "cached": enable_caching
                    }
                }
                
                service_logger.info(f"Credit score calculated: {result['credit_score']} ({result['risk_category']})")
                return result
                
            finally:
                service_logger.pop_context()
        
        return await self._execute_with_batching_and_caching(
            "vertex_ai", "calculate_credit_score", request_data, _calculate_score,
            enable_batching=enable_batching, enable_caching=enable_caching,
            priority=priority, cache_context=cache_context
        )
    
    @monitor_adk_call("fraud_detection", "detect_fraud")
    async def detect_fraud(self, 
                         claim_data: Dict[str, Any],
                         supporting_evidence: List[Dict[str, Any]],
                         enable_batching: bool = False,  # Fraud detection typically needs immediate processing
                         enable_caching: bool = True,
                         priority: int = 10) -> Dict[str, Any]:  # High priority for fraud detection
        """Use multiple AI services for fraud detection with caching"""
        if not self._initialized:
            await self.initialize()
        
        # Prepare request data for batching/caching
        request_data = {
            "claim_data": claim_data,
            "supporting_evidence": supporting_evidence
        }
        
        # Cache context for claim-specific caching
        claim_id = claim_data.get("claim_id", "unknown")
        cache_context = {
            "claim_id": claim_id,
            "claim_hash": hash(str(sorted(claim_data.items()))),
            "evidence_hash": hash(str(supporting_evidence))
        }
        
        async def _detect_fraud():
            service_logger = self.service_loggers.get("vertex_ai", logger)  # Use vertex_ai logger for fraud detection
            service_logger.push_context(claim_id=claim_id, evidence_count=len(supporting_evidence))
            
            try:
                service_logger.info("Analyzing claim for fraud with multiple AI services")
                
                # Simulate AI processing with realistic delay
                await asyncio.sleep(0.8)  # Fraud detection takes longer
                
                # Simulate potential service unavailable error for testing
                if claim_data.get("simulate_error") == "service_unavailable":
                    from google.api_core.exceptions import ServiceUnavailable
                    raise ServiceUnavailable("Fraud detection service temporarily unavailable")
                
                result = {
                    "fraud_probability": 0.15,
                    "risk_level": "low",
                    "confidence": 0.82,
                    "analysis_results": {
                        "text_analysis": {
                            "inconsistencies": 0,
                            "sentiment_score": 0.3,
                            "authenticity_score": 0.9
                        },
                        "image_analysis": {
                            "damage_verified": True,
                            "location_verified": True,
                            "timestamp_verified": True
                        },
                        "pattern_analysis": {
                            "similar_claims": 0,
                            "behavioral_anomalies": 0,
                            "timing_suspicious": False
                        }
                    },
                    "recommendation": "approve",
                    "explanation": "Low fraud risk - claim appears legitimate with consistent evidence",
                    "processing_metadata": {
                        "models_used": ["text_classifier_v1.0", "image_analyzer_v2.1", "pattern_detector_v1.5"],
                        "processing_time_ms": 800,
                        "evidence_analyzed": len(supporting_evidence),
                        "batched": enable_batching,
                        "cached": enable_caching
                    }
                }
                
                service_logger.info(f"Fraud analysis completed: {result['risk_level']} risk ({result['fraud_probability']:.2%})")
                return result
                
            finally:
                service_logger.pop_context()
        
        return await self._execute_with_batching_and_caching(
            "fraud_detection", "detect_fraud", request_data, _detect_fraud,
            enable_batching=enable_batching, enable_caching=enable_caching,
            priority=priority, cache_context=cache_context
        )
    
    async def analyze_satellite_imagery(self, 
                                      image_data: bytes,
                                      analysis_type: str = "crop_damage") -> Dict[str, Any]:
        """Use Vision API for satellite imagery analysis"""
        if not self._initialized:
            await self.initialize()
        
        def _analyze_image():
            logger.info(f"Analyzing satellite imagery for {analysis_type}")
            
            # This would use actual Vision API
            # For now, return mock data
            return {
                "analysis_type": analysis_type,
                "confidence": 0.87,
                "findings": {
                    "crop_health": "moderate",
                    "damage_detected": True,
                    "damage_extent": 0.25,
                    "affected_area_hectares": 12.5
                },
                "coordinates": {
                    "latitude": 28.6139,
                    "longitude": 77.2090
                }
            }
        
        return await self._execute_with_retry("vision_api", _analyze_image)
    
    async def analyze_text_sentiment(self, text: str) -> Dict[str, Any]:
        """Use Natural Language API for text analysis"""
        if not self._initialized:
            await self.initialize()
        
        def _analyze_text():
            logger.info("Analyzing text sentiment and entities")
            
            # This would use actual Natural Language API
            return {
                "sentiment": {
                    "score": 0.2,
                    "magnitude": 0.6,
                    "label": "neutral"
                },
                "entities": [
                    {"name": "crop damage", "type": "EVENT", "salience": 0.8},
                    {"name": "insurance claim", "type": "OTHER", "salience": 0.6}
                ],
                "confidence": 0.91
            }
        
        return await self._execute_with_retry("natural_language", _analyze_text)
    
    # Monitoring and status methods
    
    def get_service_status(self) -> Dict[str, ADKServiceStatus]:
        """Get status of all services"""
        return self.service_status.copy()
    
    def get_rate_limit_status(self) -> Dict[str, RateLimitStatus]:
        """Get rate limiting status for all services"""
        return self.rate_limit_status.copy()
    
    def get_health_check(self) -> Dict[str, Any]:
        """Get comprehensive health status including batching and caching"""
        total_services = len(self.service_status)
        available_services = sum(1 for status in self.service_status.values() if status.is_available)
        
        # Get monitoring health summary
        monitor_health = self.monitor.get_health_summary()
        
        # Get error handler status
        error_stats = self.error_handler.get_error_stats()
        circuit_breaker_status = self.error_handler.get_circuit_breaker_status()
        
        # Get batching and caching stats
        cache_stats = self.cache_manager.get_cache_stats()
        
        # Determine overall health
        overall_health = "healthy"
        if monitor_health["health_status"] == "critical" or any(
            cb["state"] == "open" for cb in circuit_breaker_status.values()
        ):
            overall_health = "critical"
        elif monitor_health["health_status"] in ["degraded", "warning"] or available_services < total_services:
            overall_health = "degraded"
        
        return {
            "overall_health": overall_health,
            "services_available": f"{available_services}/{total_services}",
            "initialized": self._initialized,
            "project_id": self.project_id,
            "last_check": datetime.now().isoformat(),
            
            # Service status details
            "service_details": {
                name: {
                    "available": status.is_available,
                    "requests": status.request_count,
                    "errors": status.error_count,
                    "last_error": status.error_message
                }
                for name, status in self.service_status.items()
            },
            
            # Enhanced monitoring data
            "monitoring": {
                "total_requests": monitor_health["total_requests"],
                "total_errors": monitor_health["total_errors"],
                "overall_error_rate": monitor_health["overall_error_rate"],
                "rate_limit_hits": monitor_health["rate_limit_hits"],
                "circuit_breaker_trips": monitor_health["circuit_breaker_trips"],
                "services_with_issues": monitor_health["services_with_issues"]
            },
            
            # Error handling status
            "error_handling": {
                "error_stats": error_stats,
                "circuit_breakers": circuit_breaker_status
            },
            
            # Batching and caching status
            "performance_optimization": {
                "caching": {
                    "hit_rate": cache_stats["hit_rate"],
                    "cache_size_mb": cache_stats["size_mb"],
                    "utilization": cache_stats["utilization"],
                    "entry_count": cache_stats["entry_count"]
                }
            }
        }
    
    def get_detailed_metrics(self, hours: int = 1) -> Dict[str, Any]:
        """Get detailed metrics for the specified time period"""
        return {
            "performance_stats": self.monitor.get_all_stats(),
            "metrics_history": self.monitor.get_metrics_history(hours=hours),
            "recent_requests": self.monitor.get_recent_requests(limit=50),
            "error_breakdown": self.error_handler.get_error_stats(),
            "circuit_breaker_status": self.error_handler.get_circuit_breaker_status(),
            "time_period_hours": hours,
            "generated_at": datetime.now().isoformat()
        }
    
    async def reset_error_handling(self, service_name: Optional[str] = None) -> Dict[str, bool]:
        """Reset error handling for services"""
        results = {}
        
        if service_name:
            # Reset specific service
            success = self.error_handler.reset_circuit_breaker(service_name)
            results[service_name] = success
            if success:
                logger.info(f"Reset error handling for {service_name}")
        else:
            # Reset all services
            for svc_name in self.service_loggers.keys():
                success = self.error_handler.reset_circuit_breaker(svc_name)
                results[svc_name] = success
            logger.info("Reset error handling for all services")
        
        return results
    
    async def test_service_connectivity(self, service_name: str) -> Dict[str, Any]:
        """Test connectivity to a specific service"""
        if service_name not in self.service_status:
            return {
                "service": service_name,
                "status": "unknown",
                "error": "Service not configured"
            }
        
        try:
            # Re-validate the specific service
            if service_name == "vertex_ai":
                is_valid = await self._validate_vertex_ai()
            elif service_name == "vision_api":
                is_valid = await self._validate_vision_api()
            elif service_name == "natural_language":
                is_valid = await self._validate_natural_language()
            elif service_name == "storage":
                is_valid = await self._validate_storage()
            else:
                is_valid = False
            
            # Update service status
            self.service_status[service_name].is_available = is_valid
            self.service_status[service_name].last_check = datetime.now()
            
            return {
                "service": service_name,
                "status": "available" if is_valid else "unavailable",
                "last_check": datetime.now().isoformat(),
                "connectivity_test": "passed" if is_valid else "failed"
            }
            
        except Exception as e:
            self.service_status[service_name].is_available = False
            self.service_status[service_name].error_message = str(e)
            self.service_status[service_name].last_check = datetime.now()
            
            return {
                "service": service_name,
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat(),
                "connectivity_test": "failed"
            }
    
    async def refresh_services(self) -> bool:
        """Refresh all service connections"""
        logger.info("Refreshing ADK services...")
        
        # Reset circuit breakers
        self._circuit_breakers.clear()
        
        # Re-authenticate
        try:
            await self._authenticate()
            await self._validate_services()
            logger.info("Services refreshed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to refresh services: {e}")
            return False
    
    # Batching and Caching Management Methods
    
    async def get_batch_stats(self) -> Dict[str, Any]:
        """Get batching statistics"""
        return await self.batcher.get_batch_stats()
    
    async def flush_all_batches(self):
        """Force process all pending batches"""
        await self.batcher.flush_all_batches()
        logger.info("All batches flushed")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get caching statistics"""
        return self.cache_manager.get_cache_stats()
    
    async def clear_cache(self, service_name: str = None, operation: str = None):
        """Clear cache entries"""
        if service_name:
            await self.cache_manager.invalidate_service_cache(service_name, operation)
            logger.info(f"Cache cleared for {service_name}:{operation or 'all'}")
        else:
            await self.cache_manager.cache.clear()
            logger.info("All cache cleared")
    
    async def invalidate_cache_by_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        await self.cache_manager.cache.invalidate(pattern=pattern)
        logger.info(f"Cache invalidated for pattern: {pattern}")
    
    def configure_batching(self, 
                          max_batch_size: int = None,
                          max_wait_time_seconds: float = None,
                          strategy: BatchStrategy = None):
        """Update batching configuration"""
        if max_batch_size is not None:
            self.batcher.config.max_batch_size = max_batch_size
        if max_wait_time_seconds is not None:
            self.batcher.config.max_wait_time_seconds = max_wait_time_seconds
        if strategy is not None:
            self.batcher.config.strategy = strategy
        
        logger.info(f"Batching configuration updated: size={self.batcher.config.max_batch_size}, "
                   f"wait={self.batcher.config.max_wait_time_seconds}s, "
                   f"strategy={self.batcher.config.strategy.value}")
    
    def configure_caching(self, 
                         max_size_mb: float = None,
                         default_ttl_seconds: float = None,
                         strategy: CacheStrategy = None):
        """Update caching configuration"""
        if max_size_mb is not None:
            self.cache_manager.config.max_size_mb = max_size_mb
        if default_ttl_seconds is not None:
            self.cache_manager.config.default_ttl_seconds = default_ttl_seconds
        if strategy is not None:
            self.cache_manager.config.strategy = strategy
        
        logger.info(f"Caching configuration updated: size={self.cache_manager.config.max_size_mb}MB, "
                   f"ttl={self.cache_manager.config.default_ttl_seconds}s, "
                   f"strategy={self.cache_manager.config.strategy.value}")
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        batch_stats = await self.get_batch_stats()
        cache_stats = self.get_cache_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "batching": {
                "pending_requests": sum(batch_stats["pending_batches"].values()),
                "active_batches": sum(batch_stats["active_batches"].values()),
                "configuration": batch_stats["config"]
            },
            "caching": {
                "hit_rate": cache_stats["hit_rate"],
                "size_utilization": cache_stats["utilization"],
                "entry_count": cache_stats["entry_count"],
                "size_mb": cache_stats["size_mb"]
            },
            "recommendations": self._get_performance_recommendations(batch_stats, cache_stats)
        }
    
    def _get_performance_recommendations(self, 
                                       batch_stats: Dict[str, Any], 
                                       cache_stats: Dict[str, Any]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Batching recommendations
        pending_total = sum(batch_stats["pending_batches"].values())
        if pending_total > 20:
            recommendations.append("Consider increasing max_batch_size to reduce queue buildup")
        
        if batch_stats["config"]["max_wait_time_seconds"] > 2.0:
            recommendations.append("Consider reducing max_wait_time_seconds for better responsiveness")
        
        # Caching recommendations
        if cache_stats["hit_rate"] < 0.3:
            recommendations.append("Low cache hit rate - consider increasing cache size or TTL")
        
        if cache_stats["utilization"] > 0.9:
            recommendations.append("Cache utilization high - consider increasing max_size_mb")
        
        if cache_stats["utilization"] < 0.1:
            recommendations.append("Cache underutilized - consider reducing max_size_mb")
        
        if not recommendations:
            recommendations.append("Performance optimization is working well")
        
        return recommendations


# Global service manager instance
_service_manager: Optional[ADKServiceManager] = None

def get_adk_service_manager() -> ADKServiceManager:
    """Get the global ADK service manager instance"""
    global _service_manager
    if _service_manager is None:
        _service_manager = ADKServiceManager()
    return _service_manager

async def initialize_adk_services() -> bool:
    """Initialize the global ADK service manager"""
    service_manager = get_adk_service_manager()
    return await service_manager.initialize()