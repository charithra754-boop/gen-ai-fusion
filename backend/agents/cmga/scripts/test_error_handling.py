#!/usr/bin/env python3
"""
Test script for ADK Service Manager error handling and retry mechanisms
"""

import asyncio
import logging
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.adk_service_manager import get_adk_service_manager, initialize_adk_services
from services.error_handlers import ErrorType, CircuitBreakerOpenError, RetryExhaustedError
from services.monitoring import get_adk_monitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ErrorHandlingTester:
    """Test suite for error handling mechanisms"""
    
    def __init__(self):
        self.service_manager = None
        self.monitor = get_adk_monitor()
        self.test_results = {}
    
    async def setup(self):
        """Setup test environment"""
        logger.info("Setting up test environment...")
        
        # Initialize service manager
        self.service_manager = get_adk_service_manager()
        
        # Note: We won't actually initialize Google services for testing
        # Instead, we'll test the error handling mechanisms directly
        logger.info("Test environment setup complete")
    
    async def test_retry_mechanism(self) -> Dict[str, Any]:
        """Test retry mechanism with simulated errors"""
        logger.info("Testing retry mechanism...")
        
        test_results = {
            "test_name": "retry_mechanism",
            "started_at": datetime.now().isoformat(),
            "tests": []
        }
        
        # Test 1: Rate limit error with retry
        try:
            result = await self.service_manager.optimize_portfolio(
                market_data={"simulate_error": "rate_limit"},
                climate_data={},
                yield_data={}
            )
            test_results["tests"].append({
                "name": "rate_limit_retry",
                "status": "failed",
                "error": "Expected rate limit error but got success"
            })
        except Exception as e:
            test_results["tests"].append({
                "name": "rate_limit_retry",
                "status": "passed" if "Rate limit" in str(e) else "failed",
                "error": str(e)
            })
        
        # Test 2: Authentication error (non-retryable)
        try:
            result = await self.service_manager.calculate_credit_score(
                farmer_profile={"simulate_error": "auth"},
                alternative_data={}
            )
            test_results["tests"].append({
                "name": "auth_error_no_retry",
                "status": "failed",
                "error": "Expected auth error but got success"
            })
        except Exception as e:
            test_results["tests"].append({
                "name": "auth_error_no_retry",
                "status": "passed" if "Authentication" in str(e) else "failed",
                "error": str(e)
            })
        
        # Test 3: Service unavailable with retry
        try:
            result = await self.service_manager.detect_fraud(
                claim_data={"simulate_error": "service_unavailable"},
                supporting_evidence=[]
            )
            test_results["tests"].append({
                "name": "service_unavailable_retry",
                "status": "failed",
                "error": "Expected service unavailable error but got success"
            })
        except Exception as e:
            test_results["tests"].append({
                "name": "service_unavailable_retry",
                "status": "passed" if "unavailable" in str(e) else "failed",
                "error": str(e)
            })
        
        test_results["completed_at"] = datetime.now().isoformat()
        return test_results
    
    async def test_circuit_breaker(self) -> Dict[str, Any]:
        """Test circuit breaker functionality"""
        logger.info("Testing circuit breaker...")
        
        test_results = {
            "test_name": "circuit_breaker",
            "started_at": datetime.now().isoformat(),
            "tests": []
        }
        
        # Simulate multiple failures to trip circuit breaker
        failure_count = 0
        for i in range(6):  # Should trip after 5 failures
            try:
                await self.service_manager.optimize_portfolio(
                    market_data={"simulate_error": "service_unavailable"},
                    climate_data={},
                    yield_data={}
                )
            except CircuitBreakerOpenError:
                test_results["tests"].append({
                    "name": "circuit_breaker_trip",
                    "status": "passed",
                    "message": f"Circuit breaker opened after {failure_count} failures"
                })
                break
            except Exception:
                failure_count += 1
        else:
            test_results["tests"].append({
                "name": "circuit_breaker_trip",
                "status": "failed",
                "error": "Circuit breaker did not trip after multiple failures"
            })
        
        test_results["completed_at"] = datetime.now().isoformat()
        return test_results
    
    async def test_monitoring_metrics(self) -> Dict[str, Any]:
        """Test monitoring and metrics collection"""
        logger.info("Testing monitoring metrics...")
        
        test_results = {
            "test_name": "monitoring_metrics",
            "started_at": datetime.now().isoformat(),
            "tests": []
        }
        
        # Make some successful requests
        try:
            await self.service_manager.optimize_portfolio(
                market_data={"test": "data"},
                climate_data={"test": "data"},
                yield_data={"test": "data"}
            )
            
            await self.service_manager.calculate_credit_score(
                farmer_profile={"farmer_id": "test_farmer"},
                alternative_data={"test": "data"}
            )
            
            # Check if metrics were recorded
            stats = self.monitor.get_all_stats()
            
            if "vertex_ai" in stats:
                test_results["tests"].append({
                    "name": "metrics_collection",
                    "status": "passed",
                    "message": f"Metrics collected for {len(stats)} services"
                })
            else:
                test_results["tests"].append({
                    "name": "metrics_collection",
                    "status": "failed",
                    "error": "No metrics collected"
                })
            
            # Check health summary
            health = self.monitor.get_health_summary()
            test_results["tests"].append({
                "name": "health_summary",
                "status": "passed",
                "data": health
            })
            
        except Exception as e:
            test_results["tests"].append({
                "name": "monitoring_test",
                "status": "failed",
                "error": str(e)
            })
        
        test_results["completed_at"] = datetime.now().isoformat()
        return test_results
    
    async def test_service_health_check(self) -> Dict[str, Any]:
        """Test service health check functionality"""
        logger.info("Testing service health check...")
        
        test_results = {
            "test_name": "service_health_check",
            "started_at": datetime.now().isoformat(),
            "tests": []
        }
        
        try:
            # Get health check
            health = self.service_manager.get_health_check()
            
            required_fields = [
                "overall_health", "services_available", "initialized",
                "monitoring", "error_handling"
            ]
            
            missing_fields = [field for field in required_fields if field not in health]
            
            if not missing_fields:
                test_results["tests"].append({
                    "name": "health_check_structure",
                    "status": "passed",
                    "message": "All required fields present in health check"
                })
            else:
                test_results["tests"].append({
                    "name": "health_check_structure",
                    "status": "failed",
                    "error": f"Missing fields: {missing_fields}"
                })
            
            # Test detailed metrics
            metrics = self.service_manager.get_detailed_metrics(hours=1)
            
            if "performance_stats" in metrics and "error_breakdown" in metrics:
                test_results["tests"].append({
                    "name": "detailed_metrics",
                    "status": "passed",
                    "message": "Detailed metrics available"
                })
            else:
                test_results["tests"].append({
                    "name": "detailed_metrics",
                    "status": "failed",
                    "error": "Detailed metrics incomplete"
                })
            
        except Exception as e:
            test_results["tests"].append({
                "name": "health_check_error",
                "status": "failed",
                "error": str(e)
            })
        
        test_results["completed_at"] = datetime.now().isoformat()
        return test_results
    
    async def test_error_recovery(self) -> Dict[str, Any]:
        """Test error recovery mechanisms"""
        logger.info("Testing error recovery...")
        
        test_results = {
            "test_name": "error_recovery",
            "started_at": datetime.now().isoformat(),
            "tests": []
        }
        
        try:
            # Reset error handling
            reset_results = await self.service_manager.reset_error_handling()
            
            if any(reset_results.values()):
                test_results["tests"].append({
                    "name": "error_handling_reset",
                    "status": "passed",
                    "message": f"Reset successful for services: {reset_results}"
                })
            else:
                test_results["tests"].append({
                    "name": "error_handling_reset",
                    "status": "warning",
                    "message": "No services were reset (may be expected if no errors occurred)"
                })
            
            # Test service connectivity
            connectivity_test = await self.service_manager.test_service_connectivity("vertex_ai")
            
            test_results["tests"].append({
                "name": "service_connectivity_test",
                "status": "passed",
                "data": connectivity_test
            })
            
        except Exception as e:
            test_results["tests"].append({
                "name": "error_recovery_test",
                "status": "failed",
                "error": str(e)
            })
        
        test_results["completed_at"] = datetime.now().isoformat()
        return test_results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all error handling tests"""
        logger.info("Starting comprehensive error handling tests...")
        
        await self.setup()
        
        all_results = {
            "test_suite": "adk_error_handling",
            "started_at": datetime.now().isoformat(),
            "tests": []
        }
        
        # Run individual test suites
        test_suites = [
            self.test_retry_mechanism,
            self.test_circuit_breaker,
            self.test_monitoring_metrics,
            self.test_service_health_check,
            self.test_error_recovery
        ]
        
        for test_suite in test_suites:
            try:
                result = await test_suite()
                all_results["tests"].append(result)
            except Exception as e:
                logger.error(f"Test suite {test_suite.__name__} failed: {e}")
                all_results["tests"].append({
                    "test_name": test_suite.__name__,
                    "status": "failed",
                    "error": str(e)
                })
        
        all_results["completed_at"] = datetime.now().isoformat()
        
        # Calculate summary
        total_tests = sum(len(test["tests"]) for test in all_results["tests"] if "tests" in test)
        passed_tests = sum(
            len([t for t in test["tests"] if t.get("status") == "passed"])
            for test in all_results["tests"] if "tests" in test
        )
        
        all_results["summary"] = {
            "total_test_suites": len(test_suites),
            "total_individual_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
        }
        
        return all_results
    
    def print_results(self, results: Dict[str, Any]):
        """Print test results in a readable format"""
        print("\n" + "="*80)
        print(f"ADK ERROR HANDLING TEST RESULTS")
        print("="*80)
        
        if "summary" in results:
            summary = results["summary"]
            print(f"Test Suites: {summary['total_test_suites']}")
            print(f"Individual Tests: {summary['total_individual_tests']}")
            print(f"Passed: {summary['passed_tests']}")
            print(f"Success Rate: {summary['success_rate']}")
            print("-"*80)
        
        for test_suite in results["tests"]:
            print(f"\n{test_suite.get('test_name', 'Unknown Test').upper()}")
            print("-" * 40)
            
            if "tests" in test_suite:
                for test in test_suite["tests"]:
                    status = test.get("status", "unknown").upper()
                    name = test.get("name", "unknown")
                    
                    status_symbol = "✓" if status == "PASSED" else "✗" if status == "FAILED" else "⚠"
                    print(f"{status_symbol} {name}: {status}")
                    
                    if "message" in test:
                        print(f"  Message: {test['message']}")
                    if "error" in test:
                        print(f"  Error: {test['error']}")
                    if "data" in test:
                        print(f"  Data: {json.dumps(test['data'], indent=2)}")
        
        print("\n" + "="*80)

async def main():
    """Main test execution"""
    tester = ErrorHandlingTester()
    
    try:
        results = await tester.run_all_tests()
        
        # Print results to console
        tester.print_results(results)
        
        # Save results to file
        output_file = f"error_handling_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nDetailed results saved to: {output_file}")
        
        # Return appropriate exit code
        if results.get("summary", {}).get("success_rate", "0%") == "100.0%":
            return 0
        else:
            return 1
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)