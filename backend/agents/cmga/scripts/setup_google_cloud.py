#!/usr/bin/env python3
"""
Google Cloud Setup Script for CMGA ADK Integration
Automates the setup of Google Cloud project and required APIs
"""

import os
import sys
import json
import subprocess
import logging
from typing import List, Dict, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.adk_config import ADKConfig, ADKConfigManager
from config.auth_config import CredentialsManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleCloudSetup:
    """Handles Google Cloud project setup and API enablement"""
    
    def __init__(self, project_id: str, environment: str = "development"):
        self.project_id = project_id
        self.environment = environment
        self.required_apis = [
            "aiplatform.googleapis.com",      # Vertex AI
            "vision.googleapis.com",          # Vision API
            "language.googleapis.com",        # Natural Language API
            "automl.googleapis.com",          # AutoML
            "storage.googleapis.com",         # Cloud Storage
            "logging.googleapis.com",         # Cloud Logging
            "monitoring.googleapis.com",      # Cloud Monitoring
            "cloudtrace.googleapis.com"       # Cloud Trace
        ]
    
    def check_gcloud_installed(self) -> bool:
        """Check if gcloud CLI is installed"""
        try:
            result = subprocess.run(['gcloud', '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info("gcloud CLI is installed")
            logger.info(f"Version: {result.stdout.split()[0]}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("gcloud CLI is not installed or not in PATH")
            logger.error("Please install Google Cloud SDK: https://cloud.google.com/sdk/docs/install")
            return False
    
    def check_authentication(self) -> bool:
        """Check if user is authenticated with gcloud"""
        try:
            result = subprocess.run(['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=value(account)'],
                                  capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                logger.info(f"Authenticated as: {result.stdout.strip()}")
                return True
            else:
                logger.error("No active authentication found")
                return False
        except subprocess.CalledProcessError:
            logger.error("Failed to check authentication status")
            return False
    
    def authenticate_user(self) -> bool:
        """Authenticate user with gcloud"""
        try:
            logger.info("Starting authentication process...")
            subprocess.run(['gcloud', 'auth', 'login'], check=True)
            return self.check_authentication()
        except subprocess.CalledProcessError as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def create_or_select_project(self) -> bool:
        """Create or select Google Cloud project"""
        try:
            # Check if project exists
            result = subprocess.run(['gcloud', 'projects', 'describe', self.project_id],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Project {self.project_id} already exists")
            else:
                # Create project
                logger.info(f"Creating project {self.project_id}...")
                subprocess.run(['gcloud', 'projects', 'create', self.project_id,
                              '--name', f'KisaanMitra {self.environment.title()}'],
                              check=True)
                logger.info(f"Project {self.project_id} created successfully")
            
            # Set as active project
            subprocess.run(['gcloud', 'config', 'set', 'project', self.project_id], check=True)
            logger.info(f"Active project set to {self.project_id}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create/select project: {e}")
            return False
    
    def enable_apis(self) -> bool:
        """Enable required Google Cloud APIs"""
        try:
            logger.info("Enabling required APIs...")
            
            # Enable all APIs in batch
            cmd = ['gcloud', 'services', 'enable'] + self.required_apis
            subprocess.run(cmd, check=True)
            
            logger.info("All required APIs enabled successfully")
            
            # Verify APIs are enabled
            return self.verify_apis_enabled()
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to enable APIs: {e}")
            return False
    
    def verify_apis_enabled(self) -> bool:
        """Verify that all required APIs are enabled"""
        try:
            result = subprocess.run(['gcloud', 'services', 'list', '--enabled', '--format=value(name)'],
                                  capture_output=True, text=True, check=True)
            
            enabled_apis = set(result.stdout.strip().split('\n'))
            missing_apis = []
            
            for api in self.required_apis:
                if api not in enabled_apis:
                    missing_apis.append(api)
            
            if missing_apis:
                logger.error(f"Missing APIs: {missing_apis}")
                return False
            
            logger.info("All required APIs are enabled")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to verify APIs: {e}")
            return False
    
    def create_service_account(self, service_account_name: str = None) -> tuple[bool, str]:
        """Create service account for ADK integration"""
        if not service_account_name:
            service_account_name = f"cmga-adk-{self.environment}"
        
        service_account_email = f"{service_account_name}@{self.project_id}.iam.gserviceaccount.com"
        
        try:
            # Check if service account exists
            result = subprocess.run(['gcloud', 'iam', 'service-accounts', 'describe', service_account_email],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Service account {service_account_email} already exists")
            else:
                # Create service account
                logger.info(f"Creating service account {service_account_name}...")
                subprocess.run(['gcloud', 'iam', 'service-accounts', 'create', service_account_name,
                              '--display-name', f'CMGA ADK Service Account ({self.environment})',
                              '--description', 'Service account for CMGA Google ADK integration'],
                              check=True)
                logger.info(f"Service account {service_account_email} created successfully")
            
            # Assign required roles
            roles = [
                'roles/aiplatform.user',
                'roles/ml.developer',
                'roles/storage.objectAdmin',
                'roles/logging.logWriter',
                'roles/monitoring.metricWriter',
                'roles/cloudtrace.agent'
            ]
            
            for role in roles:
                subprocess.run(['gcloud', 'projects', 'add-iam-policy-binding', self.project_id,
                              '--member', f'serviceAccount:{service_account_email}',
                              '--role', role], check=True)
                logger.info(f"Assigned role {role} to service account")
            
            return True, service_account_email
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create service account: {e}")
            return False, ""
    
    def create_service_account_key(self, service_account_email: str) -> tuple[bool, str]:
        """Create and download service account key"""
        try:
            # Create credentials directory
            creds_dir = Path("backend/agents/cmga/config")
            creds_dir.mkdir(parents=True, exist_ok=True)
            
            # Key file path
            key_file = creds_dir / f"google-credentials-{self.environment}.json"
            
            # Create key
            logger.info(f"Creating service account key...")
            subprocess.run(['gcloud', 'iam', 'service-accounts', 'keys', 'create', str(key_file),
                          '--iam-account', service_account_email], check=True)
            
            logger.info(f"Service account key saved to {key_file}")
            
            # Set environment variable
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(key_file)
            
            return True, str(key_file)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create service account key: {e}")
            return False, ""
    
    def setup_vertex_ai_region(self) -> bool:
        """Set up Vertex AI in the specified region"""
        try:
            region = "us-central1"  # Default region
            
            logger.info(f"Setting up Vertex AI in region {region}...")
            
            # This is automatically handled when we enable the API
            # Additional setup can be added here if needed
            
            logger.info("Vertex AI setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Vertex AI: {e}")
            return False
    
    def run_full_setup(self) -> bool:
        """Run complete Google Cloud setup"""
        logger.info(f"Starting Google Cloud setup for project: {self.project_id}")
        logger.info(f"Environment: {self.environment}")
        
        # Step 1: Check prerequisites
        if not self.check_gcloud_installed():
            return False
        
        # Step 2: Authenticate
        if not self.check_authentication():
            if not self.authenticate_user():
                return False
        
        # Step 3: Create/select project
        if not self.create_or_select_project():
            return False
        
        # Step 4: Enable APIs
        if not self.enable_apis():
            return False
        
        # Step 5: Create service account
        success, service_account_email = self.create_service_account()
        if not success:
            return False
        
        # Step 6: Create service account key
        success, key_file = self.create_service_account_key(service_account_email)
        if not success:
            return False
        
        # Step 7: Setup Vertex AI
        if not self.setup_vertex_ai_region():
            return False
        
        # Step 8: Create ADK configuration
        self.create_adk_configuration(key_file)
        
        logger.info("Google Cloud setup completed successfully!")
        logger.info(f"Project ID: {self.project_id}")
        logger.info(f"Service Account: {service_account_email}")
        logger.info(f"Credentials File: {key_file}")
        
        return True
    
    def create_adk_configuration(self, credentials_path: str) -> None:
        """Create ADK configuration files"""
        try:
            config_manager = ADKConfigManager()
            
            # Create configuration
            config = ADKConfig(
                project_id=self.project_id,
                credentials_path=credentials_path,
                vertex_ai=config_manager._config.vertex_ai if config_manager._config else None,
                vision_api=config_manager._config.vision_api if config_manager._config else None,
                natural_language=config_manager._config.natural_language if config_manager._config else None,
                automl=config_manager._config.automl if config_manager._config else None,
                rate_limits=config_manager._config.rate_limits if config_manager._config else None,
                security=config_manager._config.security if config_manager._config else None,
                environment=self.environment
            )
            
            # Save configuration
            config_manager.save_config(config)
            
            # Setup authentication configuration
            creds_manager = CredentialsManager()
            success = creds_manager.setup_service_account(
                self.environment,
                credentials_path,
                self.project_id
            )
            
            if success:
                logger.info("ADK configuration created successfully")
            else:
                logger.warning("ADK configuration created but authentication setup failed")
                
        except Exception as e:
            logger.error(f"Failed to create ADK configuration: {e}")


def main():
    """Main setup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup Google Cloud for CMGA ADK Integration')
    parser.add_argument('--project-id', required=True, help='Google Cloud Project ID')
    parser.add_argument('--environment', default='development', 
                       choices=['development', 'staging', 'production'],
                       help='Environment (default: development)')
    
    args = parser.parse_args()
    
    setup = GoogleCloudSetup(args.project_id, args.environment)
    
    if setup.run_full_setup():
        print("\n✅ Google Cloud setup completed successfully!")
        print(f"Project: {args.project_id}")
        print(f"Environment: {args.environment}")
        print("\nNext steps:")
        print("1. Test the configuration by running: python -m backend.agents.cmga.scripts.test_adk_setup")
        print("2. Update any AutoML model IDs in the configuration files")
        print("3. Configure any additional security settings as needed")
    else:
        print("\n❌ Google Cloud setup failed!")
        print("Please check the logs above for error details.")
        sys.exit(1)


if __name__ == "__main__":
    main()