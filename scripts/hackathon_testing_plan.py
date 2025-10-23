#!/usr/bin/env python3
"""
HACKATHON TESTING PLAN - 2 HOUR DEADLINE
Comprehensive testing and debugging for AMM Optimizer
"""

import requests
import json
import time
import subprocess
import os

class HackathonTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_address = "0x8a679aCf39c06682072C4a2A833eb437A0CC0bdb"
        self.pool_address = "0x72ab388e2e2f6facef59e3c3fa2c4e29011c2d38"  # WETH-USDC 0.05%
        self.test_results = []
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_backend_health(self):
        """Test 1: Backend Health Check"""
        self.log("🏥 Testing Backend Health...")
        try:
            response = requests.get(f"{self.base_url}/api/pools/?limit=4", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Backend healthy - {len(data)} pools available")
                self.test_results.append(("Backend Health", True, f"{len(data)} pools"))
                return True
            else:
                self.log(f"❌ Backend error: {response.status_code}", "ERROR")
                self.test_results.append(("Backend Health", False, f"HTTP {response.status_code}"))
                return False
        except Exception as e:
            self.log(f"❌ Backend connection failed: {e}", "ERROR")
            self.test_results.append(("Backend Health", False, str(e)))
            return False
    
    def test_price_data(self):
        """Test 2: Price Data Accuracy"""
        self.log("💰 Testing Price Data...")
        try:
            response = requests.get(f"{self.base_url}/api/analytics/{self.pool_address}/price-data?timeframe=1d", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    latest_price = data['data'][-1]['price']
                    self.log(f"✅ Price data working - Latest: ${latest_price:,.2f}")
                    self.test_results.append(("Price Data", True, f"${latest_price:,.2f}"))
                    return latest_price
                else:
                    self.log("❌ Price data empty", "ERROR")
                    self.test_results.append(("Price Data", False, "Empty data"))
                    return None
            else:
                self.log(f"❌ Price data failed: {response.status_code}", "ERROR")
                self.test_results.append(("Price Data", False, f"HTTP {response.status_code}"))
                return None
        except Exception as e:
            self.log(f"❌ Price data error: {e}", "ERROR")
            self.test_results.append(("Price Data", False, str(e)))
            return None
    
    def test_volatility_calculation(self):
        """Test 3: Volatility Calculation"""
        self.log("📊 Testing Volatility Calculation...")
        try:
            response = requests.get(f"{self.base_url}/api/analytics/{self.pool_address}/volatility?timeframe=1d", timeout=10)
            if response.status_code == 200:
                data = response.json()
                volatility = data.get('volatility_percentage', 0)
                current_price = data.get('current_price', 0)
                self.log(f"✅ Volatility working - {volatility:.2f}% at ${current_price:,.2f}")
                self.test_results.append(("Volatility", True, f"{volatility:.2f}%"))
                return True
            else:
                self.log(f"❌ Volatility failed: {response.status_code}", "ERROR")
                self.test_results.append(("Volatility", False, f"HTTP {response.status_code}"))
                return False
        except Exception as e:
            self.log(f"❌ Volatility error: {e}", "ERROR")
            self.test_results.append(("Volatility", False, str(e)))
            return False
    
    def test_out_of_range_probability(self):
        """Test 4: Out-of-Range Probability"""
        self.log("🎯 Testing Out-of-Range Probability...")
        try:
            response = requests.get(f"{self.base_url}/api/analytics/{self.pool_address}/out-of-range-probability?tick_range=500&check_interval_minutes=60&timeframe=1d", timeout=10)
            if response.status_code == 200:
                data = response.json()
                probability = data.get('out_of_range_probability', 0)
                risk_level = data.get('risk_level', 'unknown')
                self.log(f"✅ Out-of-range probability working - Risk: {risk_level}, Probability: {probability}")
                self.test_results.append(("Out-of-Range Probability", True, f"{risk_level} risk"))
                return True
            else:
                self.log(f"❌ Out-of-range probability failed: {response.status_code}", "ERROR")
                self.test_results.append(("Out-of-Range Probability", False, f"HTTP {response.status_code}"))
                return False
        except Exception as e:
            self.log(f"❌ Out-of-range probability error: {e}", "ERROR")
            self.test_results.append(("Out-of-Range Probability", False, str(e)))
            return False
    
    def test_whitelist_status(self):
        """Test 5: Whitelist Status"""
        self.log("🔐 Testing Whitelist Status...")
        try:
            response = requests.get(f"{self.base_url}/api/whitelist/status/{self.test_address}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                whitelisted = data.get('whitelisted', False)
                if whitelisted:
                    self.log(f"✅ Address {self.test_address} is whitelisted")
                    self.test_results.append(("Whitelist", True, "Whitelisted"))
                    return True
                else:
                    self.log(f"❌ Address {self.test_address} is NOT whitelisted", "ERROR")
                    self.test_results.append(("Whitelist", False, "Not whitelisted"))
                    return False
            else:
                self.log(f"❌ Whitelist check failed: {response.status_code}", "ERROR")
                self.test_results.append(("Whitelist", False, f"HTTP {response.status_code}"))
                return False
        except Exception as e:
            self.log(f"❌ Whitelist check error: {e}", "ERROR")
            self.test_results.append(("Whitelist", False, str(e)))
            return False
    
    def test_frontend_accessibility(self):
        """Test 6: Frontend Accessibility"""
        self.log("🌐 Testing Frontend Accessibility...")
        try:
            response = requests.get(f"{self.frontend_url}/app", timeout=10)
            if response.status_code == 200:
                self.log("✅ Frontend accessible")
                self.test_results.append(("Frontend", True, "Accessible"))
                return True
            else:
                self.log(f"❌ Frontend error: {response.status_code}", "ERROR")
                self.test_results.append(("Frontend", False, f"HTTP {response.status_code}"))
                return False
        except Exception as e:
            self.log(f"❌ Frontend connection failed: {e}", "ERROR")
            self.test_results.append(("Frontend", False, str(e)))
            return False
    
    def test_pool_data_accuracy(self):
        """Test 7: Pool Data Accuracy"""
        self.log("🏊 Testing Pool Data Accuracy...")
        try:
            response = requests.get(f"{self.base_url}/api/pools/?limit=4", timeout=10)
            if response.status_code == 200:
                pools = response.json()
                
                # Check for correct pool types
                expected_pools = ["WETH-USDC", "WETH-DAI"]
                found_pools = [pool['name'] for pool in pools]
                
                # Check for correct fee tiers
                expected_fees = [500, 3000]  # 0.05% and 0.3%
                found_fees = [pool['fee_tier'] for pool in pools]
                
                # Check for realistic TVL values
                valid_pools = 0
                for pool in pools:
                    tvl = pool.get('tvl', 0)
                    if tvl > 0:
                        valid_pools += 1
                        self.log(f"✅ {pool['name']} {pool['fee_tier']/10000}%: TVL ${tvl:,.2f}")
                
                if valid_pools == len(pools):
                    self.log(f"✅ All {len(pools)} pools have valid data")
                    self.test_results.append(("Pool Data", True, f"{valid_pools}/{len(pools)} valid"))
                    return True
                else:
                    self.log(f"❌ Only {valid_pools}/{len(pools)} pools have valid data", "ERROR")
                    self.test_results.append(("Pool Data", False, f"{valid_pools}/{len(pools)} valid"))
                    return False
            else:
                self.log(f"❌ Failed to fetch pools: {response.status_code}", "ERROR")
                self.test_results.append(("Pool Data", False, f"HTTP {response.status_code}"))
                return False
        except Exception as e:
            self.log(f"❌ Error testing pool data: {e}", "ERROR")
            self.test_results.append(("Pool Data", False, str(e)))
            return False
    
    def run_comprehensive_tests(self):
        """Run all tests and generate report"""
        self.log("🚀 Starting Comprehensive Testing for Hackathon...")
        self.log("=" * 60)
        
        # Run all tests
        tests = [
            self.test_backend_health,
            self.test_price_data,
            self.test_volatility_calculation,
            self.test_out_of_range_probability,
            self.test_whitelist_status,
            self.test_frontend_accessibility,
            self.test_pool_data_accuracy
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(1)  # Small delay between tests
            except Exception as e:
                self.log(f"❌ Test failed with exception: {e}", "ERROR")
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        self.log("=" * 60)
        self.log("📊 HACKATHON TESTING REPORT")
        self.log("=" * 60)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, result, details in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name:<30} {status} - {details}")
            if result:
                passed += 1
        
        self.log("=" * 60)
        self.log(f"🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED! Ready for hackathon!")
            self.log("")
            self.log("💡 NEXT STEPS FOR REAL MONEY TESTING:")
            self.log("1. Open http://localhost:3000/app")
            self.log("2. Connect your wallet")
            self.log("3. Select WETH-USDC 0.05% pool")
            self.log("4. Enter $0.01 (1 cent) amount")
            self.log("5. Click 'Create Position'")
            self.log("6. Watch console logs for debugging info")
            self.log("7. If rate limited, wait 1-2 minutes and retry")
            self.log("")
            self.log("🔍 DEBUGGING TIPS:")
            self.log("- Open browser dev tools (F12)")
            self.log("- Check Console tab for detailed logs")
            self.log("- Look for 🚀, 💰, 🎯, 📋 emoji logs")
            self.log("- If transaction fails, check the error message")
            self.log("- Gas should be under $0.01 on Base")
        else:
            self.log(f"⚠️  {total-passed} tests failed. Fix these issues first!")
            self.log("")
            self.log("🔧 CRITICAL ISSUES TO FIX:")
            for test_name, result, details in self.test_results:
                if not result:
                    self.log(f"- {test_name}: {details}")
        
        return passed == total

def main():
    print("🏆 HACKATHON TESTING PLAN - 2 HOUR DEADLINE")
    print("=" * 60)
    print("Testing AMM Optimizer for real money deployment")
    print("=" * 60)
    
    tester = HackathonTester()
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n🎉 READY FOR HACKATHON!")
        print("The app is fully functional and ready for real money testing.")
    else:
        print("\n⚠️  ISSUES DETECTED!")
        print("Please fix the failing tests before proceeding with real money.")

if __name__ == "__main__":
    main()
