#!/usr/bin/env python3
"""
FINAL HACKATHON TEST - READY FOR REAL MONEY
Tests the app with correct pool addresses
"""

import requests
import json
import time
from web3 import Web3

class FinalHackathonTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_address = "0x8a679aCf39c06682072C4a2A833eb437A0CC0bdb"
        
        # Real pool addresses from Factory
        self.real_pools = {
            "WETH-USDC 0.05%": "0xd0b53D9277642d899DF5C87A3966A349A798F224",
            "WETH-USDC 0.3%": "0x6c561B446416E1A00E8E93E221854d6eA4171372",
            "WETH-DAI 0.05%": "0x93e8542E6CA0eFFfb9D57a270b76712b968A38f5",
            "WETH-DAI 0.3%": "0xDcf81663E68f076EF9763442DE134Fd0699de4ef"
        }
        
        # Base network
        self.rpc_url = "https://mainnet.base.org"
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_backend_pools(self):
        """Test that backend returns correct pool addresses"""
        self.log("🔍 Testing backend pool addresses...")
        
        try:
            response = requests.get(f"{self.base_url}/api/pools/?limit=4", timeout=10)
            if response.status_code == 200:
                pools = response.json()
                
                all_correct = True
                for pool in pools:
                    pool_name = f"{pool['name']} {pool['fee_tier']/10000}%"
                    expected_address = self.real_pools.get(pool_name)
                    
                    if expected_address and pool['address'].lower() == expected_address.lower():
                        self.log(f"✅ {pool_name}: {pool['address']} (CORRECT)")
                    else:
                        self.log(f"❌ {pool_name}: {pool['address']} (WRONG - Expected: {expected_address})", "ERROR")
                        all_correct = False
                
                return all_correct
            else:
                self.log(f"❌ Backend error: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing backend: {e}", "ERROR")
            return False
    
    def test_pool_contracts(self):
        """Test that all pool contracts exist on-chain"""
        self.log("🏊 Testing pool contracts on-chain...")
        
        all_exist = True
        for name, address in self.real_pools.items():
            try:
                checksum_address = self.w3.to_checksum_address(address)
                code = self.w3.eth.get_code(checksum_address)
                
                if len(code) > 2:
                    self.log(f"✅ {name}: {address} (EXISTS)")
                else:
                    self.log(f"❌ {name}: {address} (DOES NOT EXIST)", "ERROR")
                    all_exist = False
                    
            except Exception as e:
                self.log(f"❌ {name}: Error checking {address} - {e}", "ERROR")
                all_exist = False
        
        return all_exist
    
    def test_position_manager(self):
        """Test NonfungiblePositionManager contract"""
        self.log("🔧 Testing NonfungiblePositionManager...")
        
        position_manager = "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1"
        
        try:
            checksum_address = self.w3.to_checksum_address(position_manager)
            code = self.w3.eth.get_code(checksum_address)
            
            if len(code) > 2:
                self.log(f"✅ PositionManager exists at {position_manager}")
                return True
            else:
                self.log(f"❌ PositionManager does not exist at {position_manager}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error checking PositionManager: {e}", "ERROR")
            return False
    
    def test_wallet_balance(self):
        """Test wallet has sufficient balance"""
        self.log("💰 Testing wallet balance...")
        
        try:
            # Check ETH balance
            eth_balance = self.w3.eth.get_balance(self.test_address)
            eth_balance_ether = self.w3.from_wei(eth_balance, 'ether')
            
            self.log(f"ETH Balance: {eth_balance_ether:.6f} ETH")
            
            if eth_balance_ether > 0.001:  # Need at least 0.001 ETH for gas
                self.log("✅ Sufficient ETH for gas")
                return True
            else:
                self.log("❌ Insufficient ETH for gas", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error checking balance: {e}", "ERROR")
            return False
    
    def test_price_data(self):
        """Test price data is working"""
        self.log("📊 Testing price data...")
        
        # Test with the first pool
        test_pool = "0xd0b53D9277642d899DF5C87A3966A349A798F224"
        
        try:
            response = requests.get(f"{self.base_url}/api/analytics/{test_pool}/price-data?timeframe=1d", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    latest_price = data['data'][-1]['price']
                    self.log(f"✅ Price data working - Latest: ${latest_price:,.2f}")
                    return True
                else:
                    self.log("❌ Price data empty", "ERROR")
                    return False
            else:
                self.log(f"❌ Price data failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing price data: {e}", "ERROR")
            return False
    
    def run_final_test(self):
        """Run the final comprehensive test"""
        self.log("🚀 FINAL HACKATHON TEST - READY FOR REAL MONEY")
        self.log("=" * 60)
        
        tests = [
            ("Backend Pool Addresses", self.test_backend_pools),
            ("Pool Contracts On-Chain", self.test_pool_contracts),
            ("Position Manager", self.test_position_manager),
            ("Wallet Balance", self.test_wallet_balance),
            ("Price Data", self.test_price_data)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"🧪 Running {test_name}...")
            try:
                if test_func():
                    self.log(f"✅ {test_name} - PASSED")
                    passed += 1
                else:
                    self.log(f"❌ {test_name} - FAILED", "ERROR")
            except Exception as e:
                self.log(f"❌ {test_name} - ERROR: {e}", "ERROR")
            
            time.sleep(1)
        
        self.log("=" * 60)
        self.log("📊 FINAL TEST RESULTS")
        self.log("=" * 60)
        self.log(f"🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED! READY FOR HACKATHON!")
            self.log("")
            self.log("💡 REAL MONEY TESTING INSTRUCTIONS:")
            self.log("1. Open http://localhost:3000/app")
            self.log("2. Connect your wallet")
            self.log("3. Select WETH-USDC 0.05% pool (0xd0b53D9277642d899DF5C87A3966A349A798F224)")
            self.log("4. Enter $0.01 (1 cent) amount")
            self.log("5. Click 'Create Position'")
            self.log("6. Watch console logs for debugging")
            self.log("7. Gas should be under $0.01 on Base")
            self.log("")
            self.log("🔍 DEBUGGING:")
            self.log("- Open browser dev tools (F12)")
            self.log("- Check Console tab for emoji logs")
            self.log("- Look for 🚀, 💰, 🎯, 📋 indicators")
            self.log("- If rate limited, wait 1-2 minutes and retry")
            self.log("")
            self.log("🏆 SUCCESS CRITERIA:")
            self.log("- Transaction succeeds (no 'likely to fail')")
            self.log("- Gas fee < $0.01")
            self.log("- Position appears on Uniswap")
            self.log("- Console logs show success")
            
            return True
        else:
            self.log(f"⚠️  {total-passed} tests failed. Fix these issues first!")
            return False

def main():
    print("🏆 FINAL HACKATHON TEST")
    print("=" * 60)
    print("Testing with REAL pool addresses from Uniswap V3 Factory")
    print("=" * 60)
    
    tester = FinalHackathonTest()
    success = tester.run_final_test()
    
    if success:
        print("\n🎉 READY FOR HACKATHON!")
        print("The app is now fixed and ready for real money testing.")
    else:
        print("\n⚠️  ISSUES DETECTED!")
        print("Please fix the failing tests before proceeding.")

if __name__ == "__main__":
    main()
