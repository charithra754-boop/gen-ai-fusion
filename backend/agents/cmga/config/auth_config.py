"""
Google ADK Authentication Configuration
Handles service account credentials, OAuth 2.0, and secure authentication
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass
from google.auth import default
from google.auth.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

@dataclass
class AuthConfig:
    """Authentication configuration for Google ADK"""
    auth_type: str = "service_account"  # "service_account" or "default"
    credentials_path: Optional[str] = None
    scopes: list = None
    project_id: Optional[str] = None
    
    def __post_init__(self):
        if self.scopes is None:
            self.scopes = [
                'https://www.googleapis.com/auth/cloud-platform',
                'https://www.googleapis.com/auth/cloud-platform.read-only',
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write',
                'https://www.googleapis.com/auth/monitoring.write',
                'https://www.googleapis.com/auth/trace.append'
            ]


class ADKAuthenticator:
    """Handles Google ADK authentication and credential management"""
    
    def __init__(self, auth_config: Optional[AuthConfig] = None):
        self.auth_config = auth_config or self._create_default_auth_config()
        self._credentials: Optional[Credentials] = None
        self._project_id: Optional[str] = None
    
    def _create_default_auth_config(self) -> AuthConfig:
        """Create default authentication configuration"""
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        
        return AuthConfig(
            credentials_path=credentials_path,
            project_id=project_id
        )
    
    def authenticate(self) -> tuple[Credentials, str]:
        """Authenticate and return credentials and project ID"""
        if self._credentials is None:
            self._credentials, self._project_id = self._get_credentials()
        
        # Refresh credentials if needed
        if self._credentials.expired and self._credentials.refresh_token:
            self._credentials.refresh(Request())
        
        return self._credentials, self._project_id
    
    def _get_credentials(self) -> tuple[Credentials, str]:
        """Get Google Cloud credentials"""
        try:
            if self.auth_config.auth_type == "service_account" and self.auth_config.credentials_path:
                return self._get_service_account_credentials()
            else:
                return self._get_default_credentials()
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    def _get_service_account_credentials(self) -> tuple[Credentials, str]:
        """Get service account credentials from file"""
        credentials_path = self.auth_config.credentials_path
        
        if not credentials_path or not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Service account credentials file not found: {credentials_path}")
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=self.auth_config.scopes
            )
            
            # Get project ID from credentials file
            with open(credentials_path, 'r') as f:
                service_account_info = json.load(f)
            
            project_id = service_account_info.get('project_id') or self.auth_config.project_id
            
            if not project_id:
                raise ValueError("Project ID not found in credentials file or configuration")
            
            logger.info(f"Successfully authenticated with service account for project: {project_id}")
            return credentials, project_id
            
        except Exception as e:
            logger.error(f"Failed to load service account credentials: {e}")
            raise
    
    def _get_default_credentials(self) -> tuple[Credentials, str]:
        """Get default credentials (ADC)"""
        try:
            credentials, project_id = default(scopes=self.auth_config.scopes)
            
            if not project_id:
                project_id = self.auth_config.project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
            
            if not project_id:
                raise ValueError("Project ID not found in default credentials or configuration")
            
            logger.info(f"Successfully authenticated with default credentials for project: {project_id}")
            return credentials, project_id
            
        except Exception as e:
            logger.error(f"Failed to get default credentials: {e}")
            raise
    
    def validate_credentials(self) -> bool:
        """Validate that credentials are working"""
        try:
            credentials, project_id = self.authenticate()
            
            # Test credentials by making a simple API call
            from google.cloud import storage
            client = storage.Client(credentials=credentials, project=project_id)
            
            # This will raise an exception if credentials are invalid
            list(client.list_buckets(max_results=1))
            
            logger.info("Credentials validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Credentials validation failed: {e}")
            return False
    
    def get_credentials_info(self) -> Dict[str, Any]:
        """Get information about current credentials"""
        try:
            credentials, project_id = self.authenticate()
            
            info = {
                'project_id': project_id,
                'auth_type': self.auth_config.auth_type,
                'scopes': self.auth_config.scopes,
                'valid': not credentials.expired if credentials else False
            }
            
            if hasattr(credentials, 'service_account_email'):
                info['service_account_email'] = credentials.service_account_email
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get credentials info: {e}")
            return {'error': str(e)}
    
    def refresh_credentials(self) -> None:
        """Force refresh of credentials"""
        self._credentials = None
        self._project_id = None
        self.authenticate()


class CredentialsManager:
    """Manages multiple credential configurations for different environments"""
    
    def __init__(self, config_dir: str = "backend/agents/cmga/config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._authenticators: Dict[str, ADKAuthenticator] = {}
    
    def get_authenticator(self, environment: str = None) -> ADKAuthenticator:
        """Get authenticator for specific environment"""
        env = environment or os.getenv('ENVIRONMENT', 'development')
        
        if env not in self._authenticators:
            auth_config = self._load_auth_config(env)
            self._authenticators[env] = ADKAuthenticator(auth_config)
        
        return self._authenticators[env]
    
    def _load_auth_config(self, environment: str) -> AuthConfig:
        """Load authentication configuration for environment"""
        config_file = self.config_dir / f"auth_config_{environment}.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                return AuthConfig(**config_data)
                
            except Exception as e:
                logger.warning(f"Failed to load auth config from {config_file}: {e}")
        
        # Return default configuration
        return AuthConfig()
    
    def save_auth_config(self, environment: str, auth_config: AuthConfig) -> None:
        """Save authentication configuration for environment"""
        config_file = self.config_dir / f"auth_config_{environment}.json"
        
        config_data = {
            'auth_type': auth_config.auth_type,
            'credentials_path': auth_config.credentials_path,
            'scopes': auth_config.scopes,
            'project_id': auth_config.project_id
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        logger.info(f"Auth configuration saved for environment: {environment}")
    
    def setup_service_account(self, 
                            environment: str,
                            credentials_path: str,
                            project_id: str = None) -> bool:
        """Set up service account authentication for environment"""
        try:
            # Validate credentials file exists
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
            
            # Load and validate service account info
            with open(credentials_path, 'r') as f:
                service_account_info = json.load(f)
            
            if 'private_key' not in service_account_info:
                raise ValueError("Invalid service account file: missing private_key")
            
            project_id = project_id or service_account_info.get('project_id')
            if not project_id:
                raise ValueError("Project ID must be provided or present in credentials file")
            
            # Create and save auth configuration
            auth_config = AuthConfig(
                auth_type="service_account",
                credentials_path=credentials_path,
                project_id=project_id
            )
            
            self.save_auth_config(environment, auth_config)
            
            # Test authentication
            authenticator = ADKAuthenticator(auth_config)
            if not authenticator.validate_credentials():
                raise ValueError("Credentials validation failed")
            
            logger.info(f"Service account authentication set up successfully for {environment}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set up service account authentication: {e}")
            return False
    
    def validate_all_environments(self) -> Dict[str, bool]:
        """Validate credentials for all configured environments"""
        results = {}
        
        for config_file in self.config_dir.glob("auth_config_*.json"):
            env = config_file.stem.replace("auth_config_", "")
            try:
                authenticator = self.get_authenticator(env)
                results[env] = authenticator.validate_credentials()
            except Exception as e:
                logger.error(f"Validation failed for environment {env}: {e}")
                results[env] = False
        
        return results


# Global credentials manager instance
credentials_manager = CredentialsManager()

def get_authenticator(environment: str = None) -> ADKAuthenticator:
    """Get authenticator for the specified environment"""
    return credentials_manager.get_authenticator(environment)

def validate_authentication(environment: str = None) -> bool:
    """Validate authentication for the specified environment"""
    try:
        authenticator = get_authenticator(environment)
        return authenticator.validate_credentials()
    except Exception as e:
        logger.error(f"Authentication validation failed: {e}")
        return False