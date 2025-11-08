"""
Google ADK Configuration Management System
Handles API keys, endpoints, rate limits, and authentication settings
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class VertexAIConfig:
    """Configuration for Vertex AI services"""
    project_id: str
    region: str = "us-central1"
    model_endpoints: Dict[str, str] = None
    
    def __post_init__(self):
        if self.model_endpoints is None:
            self.model_endpoints = {
                "text-bison": "text-bison@001",
                "code-bison": "code-bison@001", 
                "chat-bison": "chat-bison@001",
                "textembedding-gecko": "textembedding-gecko@001"
            }

@dataclass
class VisionAPIConfig:
    """Configuration for Vision API"""
    enabled: bool = True
    features: list = None
    max_results: int = 10
    
    def __post_init__(self):
        if self.features is None:
            self.features = [
                "CROP_HINTS",
                "OBJECT_LOCALIZATION", 
                "IMAGE_PROPERTIES",
                "SAFE_SEARCH_DETECTION"
            ]

@dataclass
class NaturalLanguageConfig:
    """Configuration for Natural Language API"""
    enabled: bool = True
    features: list = None
    language: str = "en"
    
    def __post_init__(self):
        if self.features is None:
            self.features = [
                "EXTRACT_ENTITIES",
                "EXTRACT_DOCUMENT_SENTIMENT",
                "CLASSIFY_TEXT",
                "EXTRACT_SYNTAX"
            ]

@dataclass
class AutoMLConfig:
    """Configuration for AutoML services"""
    enabled: bool = True
    model_ids: Dict[str, str] = None
    
    def __post_init__(self):
        if self.model_ids is None:
            self.model_ids = {
                "crop_risk_assessment": "",
                "yield_prediction": "",
                "price_forecasting": "",
                "fraud_detection": ""
            }

@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_minute: int = 60
    requests_per_day: int = 1000
    concurrent_requests: int = 10
    retry_attempts: int = 3
    backoff_factor: float = 2.0
    max_backoff_time: int = 300  # 5 minutes

@dataclass
class SecurityConfig:
    """Security and privacy configuration"""
    encryption_enabled: bool = True
    data_residency_region: str = "us"
    audit_logging: bool = True
    differential_privacy: bool = True
    consent_required: bool = True
    data_retention_days: int = 365

@dataclass
class ADKConfig:
    """Main Google ADK configuration"""
    project_id: str
    credentials_path: str
    vertex_ai: VertexAIConfig
    vision_api: VisionAPIConfig
    natural_language: NaturalLanguageConfig
    automl: AutoMLConfig
    rate_limits: RateLimitConfig
    security: SecurityConfig
    environment: str = "development"
    
    @classmethod
    def from_env(cls) -> 'ADKConfig':
        """Create configuration from environment variables"""
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")
            
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 
                                   'config/google-credentials.json')
        
        region = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
        environment = os.getenv('ENVIRONMENT', 'development')
        
        return cls(
            project_id=project_id,
            credentials_path=credentials_path,
            vertex_ai=VertexAIConfig(project_id=project_id, region=region),
            vision_api=VisionAPIConfig(),
            natural_language=NaturalLanguageConfig(),
            automl=AutoMLConfig(),
            rate_limits=RateLimitConfig(),
            security=SecurityConfig(),
            environment=environment
        )
    
    @classmethod
    def from_file(cls, config_path: str) -> 'ADKConfig':
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            return cls(
                project_id=config_data['project_id'],
                credentials_path=config_data['credentials_path'],
                vertex_ai=VertexAIConfig(**config_data.get('vertex_ai', {})),
                vision_api=VisionAPIConfig(**config_data.get('vision_api', {})),
                natural_language=NaturalLanguageConfig(**config_data.get('natural_language', {})),
                automl=AutoMLConfig(**config_data.get('automl', {})),
                rate_limits=RateLimitConfig(**config_data.get('rate_limits', {})),
                security=SecurityConfig(**config_data.get('security', {})),
                environment=config_data.get('environment', 'development')
            )
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using environment variables")
            return cls.from_env()
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {e}")
            raise
    
    def to_file(self, config_path: str) -> None:
        """Save configuration to JSON file"""
        config_dir = Path(config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(asdict(self), f, indent=2)
        
        logger.info(f"Configuration saved to {config_path}")
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        errors = []
        
        # Check required fields
        if not self.project_id:
            errors.append("project_id is required")
        
        if not self.credentials_path:
            errors.append("credentials_path is required")
        
        # Check credentials file exists
        if not os.path.exists(self.credentials_path):
            errors.append(f"Credentials file not found: {self.credentials_path}")
        
        # Validate rate limits
        if self.rate_limits.requests_per_minute <= 0:
            errors.append("requests_per_minute must be positive")
        
        if self.rate_limits.concurrent_requests <= 0:
            errors.append("concurrent_requests must be positive")
        
        # Validate regions
        valid_regions = [
            'us-central1', 'us-east1', 'us-west1', 'us-west2',
            'europe-west1', 'europe-west2', 'europe-west3', 'europe-west4',
            'asia-east1', 'asia-northeast1', 'asia-southeast1'
        ]
        
        if self.vertex_ai.region not in valid_regions:
            errors.append(f"Invalid Vertex AI region: {self.vertex_ai.region}")
        
        if errors:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        logger.info("Configuration validation passed")
        return True
    
    def get_service_config(self, service: str) -> Dict[str, Any]:
        """Get configuration for a specific service"""
        service_configs = {
            'vertex_ai': asdict(self.vertex_ai),
            'vision_api': asdict(self.vision_api),
            'natural_language': asdict(self.natural_language),
            'automl': asdict(self.automl)
        }
        
        if service not in service_configs:
            raise ValueError(f"Unknown service: {service}")
        
        return service_configs[service]


class ADKConfigManager:
    """Manages Google ADK configuration loading and validation"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._config: Optional[ADKConfig] = None
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        env = os.getenv('ENVIRONMENT', 'development')
        return f"backend/agents/cmga/config/adk_config_{env}.json"
    
    def load_config(self) -> ADKConfig:
        """Load and validate configuration"""
        if self._config is None:
            try:
                self._config = ADKConfig.from_file(self.config_path)
            except Exception:
                logger.warning("Failed to load from file, using environment variables")
                self._config = ADKConfig.from_env()
            
            if not self._config.validate():
                raise ValueError("Invalid ADK configuration")
        
        return self._config
    
    def reload_config(self) -> ADKConfig:
        """Reload configuration from file"""
        self._config = None
        return self.load_config()
    
    def save_config(self, config: ADKConfig) -> None:
        """Save configuration to file"""
        config.to_file(self.config_path)
        self._config = config
    
    def create_default_config(self) -> ADKConfig:
        """Create and save default configuration"""
        try:
            config = ADKConfig.from_env()
        except ValueError as e:
            logger.error(f"Cannot create default config: {e}")
            raise
        
        self.save_config(config)
        return config


# Global configuration manager instance
config_manager = ADKConfigManager()

def get_adk_config() -> ADKConfig:
    """Get the current ADK configuration"""
    return config_manager.load_config()

def reload_adk_config() -> ADKConfig:
    """Reload ADK configuration"""
    return config_manager.reload_config()