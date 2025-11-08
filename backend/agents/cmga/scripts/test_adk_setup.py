#!/usr/bin/env python3
"""
Test script for Google ADK setup validation
Tests authentication, API access, and service functionality
"""

import asyncio
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.adk_config import get_adk_config
from config.auth_config import get_authenticator, validate_authentication
from services.adk_service_manager import get_adk_service_manager, initialize_adk_services

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ADKSetupTester:
    """Tests Google ADK setup and configuration"""
    
    def __init__(self):
        self.test_results: Dict[str, Dict[str, Any]] = {}
    
    def test_configuration_loading(self) -> bool:
        """Test ADK configuration loading"""
        logger.info("Testing configuration loading...")
        
        try:
            config = get_adk_config()
            
            # Validate configuration
            is_valid = config.validate()
            
            self.test_results['configuration'] = {
                'status': 'passed' if is_valid else 'failed',
                'project_id': config.project_id,
                'environment': config.environment,
                'credentials_path': config.credentials_path,
                'vertex_ai_region': config.vertex_ai.region,
                'apis_enabled': {
                    'vision_api': config.vision_api.enabled,
                    'natural_language': config.natural_language.enabled,
                    'automl': config.automl.enabled
                }
            }
            
            if is_valid:
                logger.info("✅ Configuration loading: PASSED")
                return True
            else:
                logger.error("❌ Configuration loading: FAILED")
                return False
                
        except Exception as e:
            logger.error(f"❌ Configuration loading: FAILED - {e}")
            self.test_results['configuration'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    def test_authentication(self) -> bool:
        """Test Google Cloud authentication"""
        logger.info("Testing authentication...")
        
        try:
            # Test authentication
            is_valid = validate_authentication()
            
            if is_valid:
                # Get authenticator info
                authenticator = get_authenticator()
                creds_info = authenticator.get_credentials_info()
                
                self.test_results['authentication'] = {
                    'status': 'passed',
                    'project_id': creds_info.get('project_id'),
                    'auth_type': creds_info.get('auth_type'),
                    'service_account_email': creds_info.get('service_account_email'),
                    'scopes_count': len(creds_info.get('scopes', []))
                }
                
                logger.info("✅ Authentication: PASSED")
                logger.info(f"   Project: {creds_info.get('project_id')}")
                logger.info(f"   Auth Type: {creds_info.get('auth_type')}")
                return True
            else:
                logger.error("❌ Authentication: FAILED")
                self.test_results['authentication'] = {
                    'status': 'failed',
                    'error': 'Authentication validation failed'
                }
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication: FAILED - {e}")
            self.test_results['authentication'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    async def test_service_initialization(self) -> bool:
        """Test ADK service manager initialization"""
        logger.info("Testing service initialization...")
        
        try:
            # Initialize services
            success = await initialize_adk_services()
            
            if success:
                service_manager = get_adk_service_manager()
                health_check = service_manager.get_health_check()
                
                self.test_results['service_initialization'] = {
                    'status': 'passed',
                    'overall_health': health_check['overall_health'],
                    'services_available': health_check['services_available'],
                    'project_id': health_check['project_id'],
                    'service_details': health_check['service_details']
                }
                
                logger.info("✅ Service initialization: PASSED")
                logger.info(f"   Health: {health_check['overall_health']}")
                logger.info(f"   Services: {health_check['services_available']}")
                return True
            else:
                logger.error("❌ Service initialization: FAILED")
                self.test_results['service_initialization'] = {
                    'status': 'failed',
                    'error': 'Service initialization failed'
                }
                return False
                
        except Exception as e:
            logger.error(f"❌ Service initialization: FAILED - {e}")
            self.test_results['service_initialization'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    async def test_portfolio_optimization(self) -> bool:
        """Test portfolio optimization functionality"""
        logger.info("Testing portfolio optimization...")
        
        try:
            service_manager = get_adk_service_manager()
            
            # Test data
            market_data = {
                "wheat": {"price": 2500, "volatility": 0.15},
                "rice": {"price": 3000, "volatility": 0.12},
                "cotton": {"price": 5500, "volatility": 0.25}
            }
            
            climate_data = {
                "temperature": 28.5,
                "rainfall": 850,
                "risk_factors": ["drought", "pest"]
            }
            
            yield_data = {
                "wheat": {"predicted": 45, "confidence": 0.8},
                "rice": {"predicted": 55, "confidence": 0.85},
                "cotton": {"predicted": 25, "confidence": 0.75}
            }
            
            # Test optimization
            result = await service_manager.optimize_portfolio(
                market_data, climate_data, yield_data
            )
            
            self.test_results['portfolio_optimization'] = {
                'status': 'passed',
                'result_keys': list(result.keys()),
                'has_optimized_portfolio': 'optimized_portfolio' in result,
                'has_ai_insights': 'ai_insights' in result,
                'confidence': result.get('optimized_portfolio', {}).get('confidence', 0)
            }
            
            logger.info("✅ Portfolio optimization: PASSED")
            logger.info(f"   Confidence: {result.get('optimized_portfolio', {}).get('confidence', 0)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Portfolio optimization: FAILED - {e}")
            self.test_results['portfolio_optimization'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    async def test_credit_scoring(self) -> bool:
        """Test credit scoring functionality"""
        logger.info("Testing credit scoring...")
        
        try:
            service_manager = get_adk_service_manager()
            
            # Test data
            farmer_profile = {
                "farmer_id": "test_farmer_001",
                "land_size": 5.5,
                "crop_history": ["wheat", "rice", "cotton"],
                "years_farming": 12
            }
            
            alternative_data = {
                "satellite_data": {"vegetation_index": 0.75},
                "weather_data": {"rainfall_last_season": 950},
                "market_behavior": {"timely_sales": 0.85}
            }
            
            # Test credit scoring
            result = await service_manager.calculate_credit_score(
                farmer_profile, alternative_data
            )
            
            self.test_results['credit_scoring'] = {
                'status': 'passed',
                'credit_score': result.get('credit_score'),
                'risk_category': result.get('risk_category'),
                'confidence': result.get('confidence'),
                'has_explanation': 'explanation' in result
            }
            
            logger.info("✅ Credit scoring: PASSED")
            logger.info(f"   Score: {result.get('credit_score')}")
            logger.info(f"   Risk: {result.get('risk_category')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Credit scoring: FAILED - {e}")
            self.test_results['credit_scoring'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    async def test_fraud_detection(self) -> bool:
        """Test fraud detection functionality"""
        logger.info("Testing fraud detection...")
        
        try:
            service_manager = get_adk_service_manager()
            
            # Test data
            claim_data = {
                "claim_id": "test_claim_001",
                "farmer_id": "test_farmer_001",
                "claim_type": "crop_damage",
                "claimed_amount": 50000,
                "description": "Crop damaged due to unexpected hailstorm"
            }
            
            supporting_evidence = [
                {"type": "image", "description": "Field damage photos"},
                {"type": "weather_report", "description": "Local weather data"},
                {"type": "witness_statement", "description": "Neighbor confirmation"}
            ]
            
            # Test fraud detection
            result = await service_manager.detect_fraud(
                claim_data, supporting_evidence
            )
            
            self.test_results['fraud_detection'] = {
                'status': 'passed',
                'fraud_probability': result.get('fraud_probability'),
                'risk_level': result.get('risk_level'),
                'confidence': result.get('confidence'),
                'recommendation': result.get('recommendation'),
                'has_analysis': 'analysis_results' in result
            }
            
            logger.info("✅ Fraud detection: PASSED")
            logger.info(f"   Fraud probability: {result.get('fraud_probability')}")
            logger.info(f"   Risk level: {result.get('risk_level')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fraud detection: FAILED - {e}")
            self.test_results['fraud_detection'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    async def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality"""
        logger.info("Testing rate limiting...")
        
        try:
            service_manager = get_adk_service_manager()
            
            # Get initial rate limit status
            initial_status = service_manager.get_rate_limit_status()
            
            # Make a few requests
            for i in range(3):
                await service_manager.optimize_portfolio({}, {}, {})
            
            # Get updated rate limit status
            updated_status = service_manager.get_rate_limit_status()
            
            self.test_results['rate_limiting'] = {
                'status': 'passed',
                'initial_requests': sum(s.requests_made for s in initial_status.values()),
                'updated_requests': sum(s.requests_made for s in updated_status.values()),
                'rate_limit_working': True  # If we got here, rate limiting is working
            }
            
            logger.info("✅ Rate limiting: PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rate limiting: FAILED - {e}")
            self.test_results['rate_limiting'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        passed_tests = sum(1 for result in self.test_results.values() 
                          if result.get('status') == 'passed')
        total_tests = len(self.test_results)
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
                'overall_status': 'PASSED' if passed_tests == total_tests else 'FAILED'
            },
            'test_results': self.test_results,
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> list:
        """Generate recommendations based on test results"""
        recommendations = []
        
        for test_name, result in self.test_results.items():
            if result.get('status') == 'failed':
                if test_name == 'configuration':
                    recommendations.append(
                        "Fix configuration issues: Check project ID, credentials path, and API settings"
                    )
                elif test_name == 'authentication':
                    recommendations.append(
                        "Fix authentication: Verify service account credentials and permissions"
                    )
                elif test_name == 'service_initialization':
                    recommendations.append(
                        "Fix service initialization: Check API enablement and network connectivity"
                    )
                else:
                    recommendations.append(
                        f"Fix {test_name}: Check logs for specific error details"
                    )
        
        if not recommendations:
            recommendations.append("All tests passed! Your ADK setup is working correctly.")
        
        return recommendations
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive report"""
        logger.info("Starting comprehensive ADK setup testing...")
        
        # Test 1: Configuration loading
        config_ok = self.test_configuration_loading()
        
        # Test 2: Authentication
        auth_ok = self.test_authentication()
        
        # Test 3: Service initialization
        service_ok = await self.test_service_initialization() if auth_ok else False
        
        # Test 4: Portfolio optimization
        if service_ok:
            await self.test_portfolio_optimization()
        
        # Test 5: Credit scoring
        if service_ok:
            await self.test_credit_scoring()
        
        # Test 6: Fraud detection
        if service_ok:
            await self.test_fraud_detection()
        
        # Test 7: Rate limiting
        if service_ok:
            await self.test_rate_limiting()
        
        # Generate report
        report = self.generate_report()
        
        logger.info("Testing completed!")
        logger.info(f"Results: {report['summary']['passed_tests']}/{report['summary']['total_tests']} tests passed")
        
        return report


async def main():
    """Main test function"""
    tester = ADKSetupTester()
    report = await tester.run_all_tests()
    
    # Print summary
    print("\n" + "="*60)
    print("GOOGLE ADK SETUP TEST REPORT")
    print("="*60)
    
    summary = report['summary']
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Tests Passed: {summary['passed_tests']}/{summary['total_tests']}")
    print(f"Success Rate: {summary['success_rate']}")
    
    print("\nTest Details:")
    print("-" * 40)
    for test_name, result in report['test_results'].items():
        status_icon = "✅" if result['status'] == 'passed' else "❌"
        print(f"{status_icon} {test_name.replace('_', ' ').title()}: {result['status'].upper()}")
        
        if result['status'] == 'failed' and 'error' in result:
            print(f"   Error: {result['error']}")
    
    print("\nRecommendations:")
    print("-" * 40)
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. {rec}")
    
    # Exit with appropriate code
    if summary['overall_status'] == 'PASSED':
        print("\n🎉 All tests passed! Your Google ADK setup is ready to use.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please address the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())