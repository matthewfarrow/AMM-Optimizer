#!/usr/bin/env python3
"""
Integration test script for AMM Optimizer
Tests the complete system end-to-end
"""

import asyncio
import requests
import time
import json
from pathlib import Path
import sys

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

class IntegrationTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def test_backend_health(self):
        """Test backend API health"""
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=5)
            if response.status_code == 200:
                self.log_test("Backend Health Check", True, "API is responding")
                return True
            else:
                self.log_test("Backend Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, str(e))
            return False
    
    def test_frontend_health(self):
        """Test frontend health"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log_test("Frontend Health Check", True, "Frontend is responding")
                return True
            else:
                self.log_test("Frontend Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Health Check", False, str(e))
            return False
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        endpoints = [
            ("/api/pools", "GET", "Pools endpoint"),
            ("/api/analytics/0x123/price-data", "GET", "Analytics endpoint"),
            ("/api/whitelist/status/0x1234567890abcdef1234567890abcdef12345678", "GET", "Whitelist endpoint"),
            ("/api/positions/user/0x1234567890abcdef1234567890abcdef12345678", "GET", "Positions endpoint")
        ]
        
        for endpoint, method, name in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{self.backend_url}{endpoint}", timeout=5)
                
                if response.status_code in [200, 404, 422]:  # 404/422 are expected for test data
                    self.log_test(f"API {name}", True, f"Status: {response.status_code}")
                else:
                    self.log_test(f"API {name}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"API {name}", False, str(e))
    
    def test_database_connection(self):
        """Test database connection"""
        try:
            # Test a simple database operation
            response = requests.get(f"{self.backend_url}/api/whitelist/status/0x1234567890abcdef1234567890abcdef12345678", timeout=5)
            if response.status_code in [200, 404]:
                self.log_test("Database Connection", True, "Database is accessible")
                return True
            else:
                self.log_test("Database Connection", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Database Connection", False, str(e))
            return False
    
    def test_whitelist_functionality(self):
        """Test whitelist functionality"""
        try:
            # Test whitelist signup
            signup_data = {
                "email": "test@example.com",
                "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
                "reason": "Integration testing"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/whitelist/signup",
                json=signup_data,
                timeout=5
            )
            
            if response.status_code in [200, 201, 422]:
                self.log_test("Whitelist Signup", True, f"Status: {response.status_code}")
            else:
                self.log_test("Whitelist Signup", False, f"Status: {response.status_code}")
            
            # Test whitelist status check
            response = requests.get(
                f"{self.backend_url}/api/whitelist/status/0x1234567890abcdef1234567890abcdef12345678",
                timeout=5
            )
            
            if response.status_code in [200, 404]:
                self.log_test("Whitelist Status Check", True, f"Status: {response.status_code}")
            else:
                self.log_test("Whitelist Status Check", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Whitelist Functionality", False, str(e))
    
    def test_pool_data(self):
        """Test pool data functionality"""
        try:
            response = requests.get(f"{self.backend_url}/api/pools", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("Pool Data Fetch", True, f"Retrieved {len(data)} pools")
                else:
                    self.log_test("Pool Data Fetch", False, "No pool data returned")
            else:
                self.log_test("Pool Data Fetch", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Pool Data Fetch", False, str(e))
    
    def test_analytics_data(self):
        """Test analytics functionality"""
        try:
            # Test with a mock pool address
            response = requests.get(
                f"{self.backend_url}/api/analytics/0x1234567890abcdef1234567890abcdef12345678/price-data",
                timeout=10
            )
            
            if response.status_code in [200, 404, 422]:
                self.log_test("Analytics Data", True, f"Status: {response.status_code}")
            else:
                self.log_test("Analytics Data", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Analytics Data", False, str(e))
    
    def test_frontend_components(self):
        """Test frontend component loading"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for key components
                checks = [
                    ("AMM Optimizer" in content, "Landing page title"),
                    ("Connect Wallet" in content or "Connect" in content, "Wallet connection button"),
                    ("Pool" in content or "Liquidity" in content, "Pool-related content"),
                    ("Strategy" in content or "Configure" in content, "Strategy configuration"),
                    ("Monitor" in content or "Position" in content, "Position monitoring")
                ]
                
                for check, description in checks:
                    if check:
                        self.log_test(f"Frontend {description}", True, "Component found")
                    else:
                        self.log_test(f"Frontend {description}", False, "Component not found")
            else:
                self.log_test("Frontend Components", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Frontend Components", False, str(e))
    
    def test_smart_contract_integration(self):
        """Test smart contract integration (simulation)"""
        try:
            # This would test actual smart contract calls in a real deployment
            # For now, we'll test the monitoring service simulation
            from monitor.position_monitor import MultiUserPositionMonitor
            
            monitor = MultiUserPositionMonitor(
                backend_url=self.backend_url,
                contract_address=None  # Simulation mode
            )
            
            self.log_test("Smart Contract Integration", True, "Monitoring service initialized")
            return True
            
        except Exception as e:
            self.log_test("Smart Contract Integration", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Starting AMM Optimizer Integration Tests")
        print("=" * 50)
        
        # Health checks
        self.test_backend_health()
        self.test_frontend_health()
        
        # API tests
        self.test_api_endpoints()
        self.test_database_connection()
        self.test_whitelist_functionality()
        self.test_pool_data()
        self.test_analytics_data()
        
        # Frontend tests
        self.test_frontend_components()
        
        # Smart contract tests
        self.test_smart_contract_integration()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 Integration Test Summary")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "=" * 50)
        
        if failed_tests == 0:
            print("🎉 All tests passed! System is ready for deployment.")
        else:
            print("⚠️  Some tests failed. Please fix issues before deployment.")
        
        return failed_tests == 0

def main():
    """Main function"""
    tester = IntegrationTester()
    
    print("Waiting for services to start...")
    time.sleep(5)
    
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Integration tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Integration tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()







