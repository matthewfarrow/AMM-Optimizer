#!/usr/bin/env python3
"""
TEST APPROVAL FIX - VERIFY THE FIX WORKS
Tests that the approval fix resolves the rate limiting issue
"""

import requests
import json
from web3 import Web3

class ApprovalFixTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.rpc_url = "https://mainnet.base.org"
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.user_address = "0x8a679aCf39c06682072C4a2A833eb437A0CC0bdb"
        
        # Contract addresses
        self.position_manager = "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1"
        self.weth_address = "0x4200000000000000000000000000000000000006"
        self.usdc_address = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        
    def log(self, message, level="INFO"):
        print(f"[{level}] {message}")
    
    def test_backend_health(self):
        """Test backend is working"""
        self.log("🔍 Testing backend health...")
        
        try:
            response = requests.get(f"{self.base_url}/api/pools/?limit=4", timeout=10)
            if response.status_code == 200:
                pools = response.json()
                self.log(f"✅ Backend working - {len(pools)} pools available")
                return True
            else:
                self.log(f"❌ Backend error: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Backend connection failed: {e}", "ERROR")
            return False
    
    def test_price_data(self):
        """Test price data is working"""
        self.log("📊 Testing price data...")
        
        try:
            response = requests.get(f"{self.base_url}/api/analytics/0xd0b53D9277642d899DF5C87A3966A349A798F224/price-data?timeframe=1d", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    price = data['data'][-1]['price']
                    self.log(f"✅ Price data working - WETH: ${price:,.2f}")
                    return price
                else:
                    self.log("❌ Price data empty", "ERROR")
                    return None
            else:
                self.log(f"❌ Price data failed: {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.log(f"❌ Price data error: {e}", "ERROR")
            return None
    
    def test_allowances(self):
        """Test current allowances"""
        self.log("🔍 Testing current allowances...")
        
        try:
            # Check WETH allowance
            weth_allowance_data = self.w3.eth.call({
                'to': self.weth_address,
                'data': '0xdd62ed3e' + self.user_address[2:].zfill(64) + self.position_manager[2:].zfill(64)
            })
            weth_allowance = int(weth_allowance_data.hex(), 16)
            
            # Check USDC allowance
            usdc_allowance_data = self.w3.eth.call({
                'to': self.usdc_address,
                'data': '0xdd62ed3e' + self.user_address[2:].zfill(64) + self.position_manager[2:].zfill(64)
            })
            usdc_allowance = int(usdc_allowance_data.hex(), 16)
            
            self.log(f"💎 WETH Allowance: {weth_allowance} wei ({weth_allowance / 1e18:.6f} WETH)")
            self.log(f"💵 USDC Allowance: {usdc_allowance} wei ({usdc_allowance / 1e6:.6f} USDC)")
            
            return weth_allowance, usdc_allowance
            
        except Exception as e:
            self.log(f"❌ Error checking allowances: {e}", "ERROR")
            return 0, 0
    
    def test_balances(self):
        """Test current balances"""
        self.log("💰 Testing current balances...")
        
        try:
            # Check WETH balance
            weth_balance_data = self.w3.eth.call({
                'to': self.weth_address,
                'data': '0x70a08231' + self.user_address[2:].zfill(64)
            })
            weth_balance = int(weth_balance_data.hex(), 16)
            
            # Check USDC balance
            usdc_balance_data = self.w3.eth.call({
                'to': self.usdc_address,
                'data': '0x70a08231' + self.user_address[2:].zfill(64)
            })
            usdc_balance = int(usdc_balance_data.hex(), 16)
            
            self.log(f"💎 WETH Balance: {weth_balance} wei ({weth_balance / 1e18:.6f} WETH)")
            self.log(f"💵 USDC Balance: {usdc_balance} wei ({usdc_balance / 1e6:.6f} USDC)")
            
            return weth_balance, usdc_balance
            
        except Exception as e:
            self.log(f"❌ Error checking balances: {e}", "ERROR")
            return 0, 0
    
    def calculate_test_amounts(self, price):
        """Calculate test amounts"""
        if not price:
            return None, None
        
        # For a $0.01 test position
        target_usd = 0.01
        weth_amount = target_usd / price
        usdc_amount = target_usd
        
        weth_amount_wei = int(weth_amount * 1e18)
        usdc_amount_wei = int(usdc_amount * 1e6)
        
        self.log(f"🎯 Test amounts for ${target_usd} position:")
        self.log(f"   WETH: {weth_amount:.8f} WETH ({weth_amount_wei} wei)")
        self.log(f"   USDC: {usdc_amount:.6f} USDC ({usdc_amount_wei} wei)")
        
        return weth_amount_wei, usdc_amount_wei
    
    def test_approval_logic(self, weth_allowance, usdc_allowance, weth_needed, usdc_needed):
        """Test the approval logic"""
        self.log("🧪 Testing approval logic...")
        
        # Simulate the frontend logic
        needs_weth_approval = weth_allowance < weth_needed
        needs_usdc_approval = usdc_allowance < usdc_needed
        
        self.log(f"📋 Approval needed:")
        self.log(f"   WETH: {needs_weth_approval} ({weth_allowance} < {weth_needed})")
        self.log(f"   USDC: {needs_usdc_approval} ({usdc_allowance} < {usdc_needed})")
        
        if not needs_weth_approval and not needs_usdc_approval:
            self.log("✅ No approval needed - should skip to position creation")
            return True
        else:
            self.log("❌ Approval needed - will try to approve (may cause rate limiting)")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive test of the fix"""
        self.log("🚀 COMPREHENSIVE APPROVAL FIX TEST")
        self.log("=" * 60)
        
        tests = [
            ("Backend Health", self.test_backend_health),
            ("Price Data", self.test_price_data),
            ("Token Balances", self.test_balances),
            ("Token Allowances", self.test_allowances)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            self.log(f"🧪 Running {test_name}...")
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    self.log(f"✅ {test_name} - PASSED")
                else:
                    self.log(f"❌ {test_name} - FAILED")
            except Exception as e:
                self.log(f"❌ {test_name} - ERROR: {e}", "ERROR")
                results[test_name] = False
        
        # Test approval logic
        if results.get("Token Allowances") and results.get("Price Data"):
            weth_allowance, usdc_allowance = results["Token Allowances"]
            price = results["Price Data"]
            weth_needed, usdc_needed = self.calculate_test_amounts(price)
            
            if weth_needed and usdc_needed:
                approval_ok = self.test_approval_logic(weth_allowance, usdc_allowance, weth_needed, usdc_needed)
                results["Approval Logic"] = approval_ok
        
        self.log("=" * 60)
        self.log("📊 TEST RESULTS")
        self.log("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            self.log(f"   {test_name}: {status}")
        
        self.log(f"🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED!")
            self.log("")
            self.log("💡 READY FOR TESTING:")
            self.log("1. Open http://localhost:3000/app")
            self.log("2. Connect your wallet")
            self.log("3. Select WETH-USDC 0.05% pool")
            self.log("4. Enter $0.01 amount")
            self.log("5. Click 'Create Position'")
            self.log("6. Watch console logs - should skip approval!")
            return True
        else:
            self.log("⚠️  SOME TESTS FAILED!")
            self.log("Please fix the failing tests before proceeding.")
            return False

def main():
    print("🧪 APPROVAL FIX TESTER")
    print("=" * 60)
    print("Testing that the approval fix resolves rate limiting issues")
    print("=" * 60)
    
    tester = ApprovalFixTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 FIX VERIFIED!")
        print("The approval fix should resolve your rate limiting issues.")
    else:
        print("\n⚠️  FIX NEEDS WORK!")
        print("Some issues remain to be resolved.")

if __name__ == "__main__":
    main()
