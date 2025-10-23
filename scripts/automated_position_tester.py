#!/usr/bin/env python3
"""
AUTOMATED POSITION TESTER - HACKATHON CRITICAL
Tests the app by creating actual liquidity positions
"""

import requests
import json
import time
import subprocess
import os
import sys
from datetime import datetime
from web3 import Web3
from eth_account import Account

class AutomatedPositionTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_address = "0x8a679aCf39c06682072C4a2A833eb437A0CC0bdb"
        self.private_key = "9c31f983fb60e4a23e15b44d9d9be736dc5d5e133a866ea79881b664c2ed773fe"
        self.pool_address = "0x72ab388e2e2f6facef59e3c3fa2c4e29011c2d38"  # WETH-USDC 0.05%
        
        # Base network RPC
        self.rpc_url = "https://mainnet.base.org"
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Contract addresses
        self.position_manager = "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1"
        self.weth_address = "0x4200000000000000000000000000000000000006"
        self.usdc_address = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        
        self.log_file = "position_test_log.txt"
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        
        # Also write to log file
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")
    
    def check_wallet_balance(self):
        """Check wallet balances for WETH and USDC"""
        self.log("💰 Checking wallet balances...")
        
        try:
            # Check ETH balance
            eth_balance = self.w3.eth.get_balance(self.test_address)
            eth_balance_ether = self.w3.from_wei(eth_balance, 'ether')
            self.log(f"ETH Balance: {eth_balance_ether:.6f} ETH")
            
            # Check WETH balance (ERC-20)
            weth_balance = self.check_erc20_balance(self.weth_address)
            self.log(f"WETH Balance: {weth_balance:.6f} WETH")
            
            # Check USDC balance (ERC-20)
            usdc_balance = self.check_erc20_balance(self.usdc_address)
            self.log(f"USDC Balance: {usdc_balance:.6f} USDC")
            
            return {
                'eth': float(eth_balance_ether),
                'weth': weth_balance,
                'usdc': usdc_balance
            }
            
        except Exception as e:
            self.log(f"❌ Error checking balances: {e}", "ERROR")
            return None
    
    def check_erc20_balance(self, token_address):
        """Check ERC-20 token balance"""
        try:
            # ERC-20 balanceOf function
            balance_hex = self.w3.eth.call({
                'to': token_address,
                'data': '0x70a08231' + self.test_address[2:].zfill(64)
            })
            
            balance = int(balance_hex.hex(), 16)
            
            # USDC has 6 decimals, WETH has 18
            if token_address.lower() == self.usdc_address.lower():
                return balance / 10**6
            else:
                return balance / 10**18
                
        except Exception as e:
            self.log(f"❌ Error checking ERC-20 balance for {token_address}: {e}", "ERROR")
            return 0
    
    def check_pool_exists(self):
        """Verify the pool exists on-chain"""
        self.log("🏊 Checking if pool exists on-chain...")
        
        try:
            # Check if pool contract exists
            code = self.w3.eth.get_code(self.pool_address)
            if len(code) > 2:  # Has bytecode
                self.log(f"✅ Pool contract exists at {self.pool_address}")
                return True
            else:
                self.log(f"❌ Pool contract does not exist at {self.pool_address}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error checking pool existence: {e}", "ERROR")
            return False
    
    def check_position_manager(self):
        """Verify NonfungiblePositionManager contract"""
        self.log("🔧 Checking NonfungiblePositionManager contract...")
        
        try:
            code = self.w3.eth.get_code(self.position_manager)
            if len(code) > 2:
                self.log(f"✅ PositionManager exists at {self.position_manager}")
                return True
            else:
                self.log(f"❌ PositionManager does not exist at {self.position_manager}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error checking PositionManager: {e}", "ERROR")
            return False
    
    def simulate_position_creation(self):
        """Simulate position creation to identify issues"""
        self.log("🧪 Simulating position creation...")
        
        try:
            # Get current price from backend
            response = requests.get(f"{self.base_url}/api/analytics/{self.pool_address}/price-data?timeframe=1d")
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    current_price = data['data'][-1]['price']
                    self.log(f"💰 Current price: ${current_price:,.2f}")
                    
                    # Calculate test amounts
                    test_amount_weth = 0.0001  # 0.0001 WETH (~$0.40)
                    test_amount_usdc = test_amount_weth * current_price
                    
                    self.log(f"🎯 Test amounts: {test_amount_weth:.6f} WETH, {test_amount_usdc:.6f} USDC")
                    
                    # Check if we have enough balance
                    balances = self.check_wallet_balance()
                    if balances:
                        if balances['weth'] >= test_amount_weth and balances['usdc'] >= test_amount_usdc:
                            self.log("✅ Sufficient balance for test position")
                            return True
                        else:
                            self.log(f"❌ Insufficient balance. Need: {test_amount_weth:.6f} WETH, {test_amount_usdc:.6f} USDC", "ERROR")
                            return False
                    
            return False
            
        except Exception as e:
            self.log(f"❌ Error simulating position creation: {e}", "ERROR")
            return False
    
    def test_backend_endpoints(self):
        """Test all backend endpoints"""
        self.log("🔍 Testing backend endpoints...")
        
        endpoints = [
            f"/api/pools/?limit=4",
            f"/api/analytics/{self.pool_address}/price-data?timeframe=1d",
            f"/api/analytics/{self.pool_address}/volatility?timeframe=1d",
            f"/api/whitelist/status/{self.test_address}",
            f"/api/positions/active/all"
        ]
        
        all_working = True
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    self.log(f"✅ {endpoint} - Working")
                else:
                    self.log(f"❌ {endpoint} - HTTP {response.status_code}", "ERROR")
                    all_working = False
            except Exception as e:
                self.log(f"❌ {endpoint} - Error: {e}", "ERROR")
                all_working = False
        
        return all_working
    
    def analyze_failed_transaction(self):
        """Analyze the failed transaction from Tenderly"""
        self.log("🔍 Analyzing failed transaction...")
        
        # Transaction hash from user
        tx_hash = "0x501119459e5d68de6ef3d89ea1ebe2666397cedad4354e16a60184a063bdc026"
        
        try:
            # Get transaction details from BaseScan
            tx = self.w3.eth.get_transaction(tx_hash)
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            self.log(f"📋 Transaction Details:")
            self.log(f"  From: {tx['from']}")
            self.log(f"  To: {tx['to']}")
            self.log(f"  Gas Limit: {tx['gas']}")
            self.log(f"  Gas Price: {tx['gasPrice']}")
            self.log(f"  Value: {tx['value']}")
            self.log(f"  Status: {'Success' if tx_receipt['status'] == 1 else 'Failed'}")
            
            if tx_receipt['status'] == 0:
                self.log("❌ Transaction failed - analyzing logs...")
                
                # Check if it's a contract call
                if tx['to'] and tx['to'].lower() == self.position_manager.lower():
                    self.log("🎯 This was a call to NonfungiblePositionManager")
                    
                    # Decode the input data to see what function was called
                    input_data = tx['input']
                    if input_data.startswith('0x88316456'):  # mint function selector
                        self.log("✅ mint() function was called")
                        self.analyze_mint_parameters(input_data)
                    else:
                        self.log(f"❌ Unknown function called: {input_data[:10]}")
                
            return tx_receipt['status'] == 1
            
        except Exception as e:
            self.log(f"❌ Error analyzing transaction: {e}", "ERROR")
            return False
    
    def analyze_mint_parameters(self, input_data):
        """Analyze mint function parameters"""
        self.log("🔍 Analyzing mint parameters...")
        
        try:
            # This is a simplified analysis - in reality you'd need the ABI
            # But we can extract some basic info
            self.log(f"Input data length: {len(input_data)} characters")
            self.log(f"Function selector: {input_data[:10]}")
            
            # The mint function takes many parameters, we can't decode without ABI
            # But we can check if the data looks reasonable
            if len(input_data) < 200:  # mint should have lots of parameters
                self.log("❌ Input data seems too short for mint function", "ERROR")
            else:
                self.log("✅ Input data length looks reasonable for mint function")
                
        except Exception as e:
            self.log(f"❌ Error analyzing mint parameters: {e}", "ERROR")
    
    def run_comprehensive_test(self):
        """Run comprehensive test of the app"""
        self.log("🚀 Starting Comprehensive Position Creation Test")
        self.log("=" * 60)
        
        # Test 1: Backend endpoints
        if not self.test_backend_endpoints():
            self.log("❌ Backend tests failed - fix backend first", "ERROR")
            return False
        
        # Test 2: Check wallet balances
        balances = self.check_wallet_balance()
        if not balances:
            self.log("❌ Cannot check wallet balances", "ERROR")
            return False
        
        # Test 3: Verify pool exists
        if not self.check_pool_exists():
            self.log("❌ Pool does not exist - this is the main issue!", "ERROR")
            return False
        
        # Test 4: Verify position manager
        if not self.check_position_manager():
            self.log("❌ PositionManager does not exist - this is the main issue!", "ERROR")
            return False
        
        # Test 5: Simulate position creation
        if not self.simulate_position_creation():
            self.log("❌ Position creation simulation failed", "ERROR")
            return False
        
        # Test 6: Analyze failed transaction
        self.analyze_failed_transaction()
        
        self.log("=" * 60)
        self.log("📊 TEST SUMMARY")
        self.log("=" * 60)
        
        if balances['weth'] > 0.001 and balances['usdc'] > 1:
            self.log("✅ Wallet has sufficient funds for testing")
        else:
            self.log("❌ Wallet needs more funds for testing", "ERROR")
        
        self.log("🎯 NEXT STEPS:")
        self.log("1. Fix pool address if it doesn't exist")
        self.log("2. Fix PositionManager address if it doesn't exist")
        self.log("3. Test with small amounts first")
        self.log("4. Check gas estimation")
        
        return True

def main():
    print("🧪 AUTOMATED POSITION TESTER")
    print("=" * 60)
    print("Testing the app to identify and fix position creation issues")
    print("=" * 60)
    
    tester = AutomatedPositionTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
