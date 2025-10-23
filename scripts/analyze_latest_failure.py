#!/usr/bin/env python3
"""
ANALYZE LATEST FAILURE - CRITICAL DEBUG
Analyzes the latest failed transaction to identify the exact issue
"""

import requests
import json
from web3 import Web3

class LatestFailureAnalyzer:
    def __init__(self):
        self.rpc_url = "https://mainnet.base.org"
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.user_address = "0x8a679aCf39c06682072C4a2A833eb437A0CC0bdb"
        
        # Transaction hashes from user
        self.approval_tx = "0xea054f394c950fddac04c34733e625bca8efc3b827d7e6ea40f8e0a9574285e8"
        self.position_tx = "0xade0fa20158745c8bb39631c3e40b3fd1ff7fb7cdcba0ca9eade85a320ae68bd"
        
        # Contract addresses
        self.position_manager = "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1"
        self.weth_address = "0x4200000000000000000000000000000000000006"
        self.usdc_address = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        
    def log(self, message, level="INFO"):
        print(f"[{level}] {message}")
    
    def analyze_transaction(self, tx_hash, tx_name):
        """Analyze a specific transaction"""
        self.log(f"🔍 Analyzing {tx_name}: {tx_hash}")
        
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            self.log(f"📋 {tx_name} Details:")
            self.log(f"  From: {tx['from']}")
            self.log(f"  To: {tx['to']}")
            self.log(f"  Gas Limit: {tx['gas']}")
            self.log(f"  Gas Used: {tx_receipt['gasUsed']}")
            self.log(f"  Status: {'Success' if tx_receipt['status'] == 1 else 'Failed'}")
            self.log(f"  Value: {tx['value']} wei")
            
            # Check if it's a call to NonfungiblePositionManager
            if tx['to'] and tx['to'].lower() == self.position_manager.lower():
                self.log("✅ This was a call to NonfungiblePositionManager")
                self.analyze_mint_call(tx['input'], tx_name)
            else:
                self.log(f"📝 This was a call to: {tx['to']}")
                if tx['to'].lower() in [self.weth_address.lower(), self.usdc_address.lower()]:
                    self.log("✅ This was a token approval")
                    self.analyze_approval_call(tx['input'], tx_name)
            
            # Check transaction logs
            if tx_receipt['logs']:
                self.log(f"📝 Transaction had {len(tx_receipt['logs'])} logs")
                for i, log in enumerate(tx_receipt['logs']):
                    self.log(f"  Log {i}: {log['address']} - {len(log['data'])} bytes")
            else:
                self.log("❌ No logs - transaction failed before any events")
            
            return tx_receipt['status'] == 1
            
        except Exception as e:
            self.log(f"❌ Error analyzing {tx_name}: {e}", "ERROR")
            return False
    
    def analyze_approval_call(self, input_data, tx_name):
        """Analyze approval function call"""
        self.log(f"🔍 Analyzing approval call for {tx_name}")
        
        # approve function selector: 0x095ea7b3
        if input_data.startswith('0x095ea7b3'):
            self.log("✅ approve() function was called")
            
            # Extract spender and amount
            if len(input_data) >= 138:  # 4 + 32 + 32 + 32
                spender = "0x" + input_data[34:74]  # Skip function selector and padding
                amount_hex = input_data[74:138]
                amount = int(amount_hex, 16)
                
                self.log(f"  Spender: {spender}")
                self.log(f"  Amount: {amount} wei")
                
                # Check if spender is correct
                if spender.lower() == self.position_manager.lower():
                    self.log("✅ Spender is correct (NonfungiblePositionManager)")
                else:
                    self.log(f"❌ Wrong spender: {spender}", "ERROR")
        else:
            self.log(f"❌ Unknown function: {input_data[:10]}")
    
    def analyze_mint_call(self, input_data, tx_name):
        """Analyze mint function call"""
        self.log(f"🔍 Analyzing mint call for {tx_name}")
        
        # mint function selector: 0x88316456
        if input_data.startswith('0x88316456'):
            self.log("✅ mint() function was called")
            
            # Try to extract basic parameters
            if len(input_data) > 10:
                params_data = input_data[10:]
                self.log(f"📊 Parameters data length: {len(params_data)} characters")
                
                # Extract token addresses (first two addresses in the call)
                if len(params_data) >= 128:  # 2 addresses = 64 chars each
                    token0 = "0x" + params_data[24:64]  # Skip first 24 chars (padding)
                    token1 = "0x" + params_data[88:128]  # Skip first 88 chars
                    
                    self.log(f"🎯 Token0: {token0}")
                    self.log(f"🎯 Token1: {token1}")
                    
                    # Check if these are the expected tokens
                    if token0.lower() == self.weth_address.lower():
                        self.log("✅ Token0 is WETH (correct)")
                    elif token0.lower() == self.usdc_address.lower():
                        self.log("✅ Token0 is USDC (correct)")
                    else:
                        self.log(f"❌ Token0 is unexpected: {token0}", "ERROR")
                    
                    if token1.lower() == self.weth_address.lower():
                        self.log("✅ Token1 is WETH (correct)")
                    elif token1.lower() == self.usdc_address.lower():
                        self.log("✅ Token1 is USDC (correct)")
                    else:
                        self.log(f"❌ Token1 is unexpected: {token1}", "ERROR")
                    
                    # Check token ordering
                    if token0.lower() < token1.lower():
                        self.log("✅ Token ordering is correct (token0 < token1)")
                    else:
                        self.log("❌ Token ordering is wrong (token0 should be < token1)", "ERROR")
                
                # Try to extract fee tier
                if len(params_data) >= 192:  # 3 * 64 chars
                    fee_hex = params_data[128:192]
                    fee = int(fee_hex, 16)
                    self.log(f"💰 Fee tier: {fee} (should be 500 or 3000)")
                    
                    if fee in [500, 3000]:
                        self.log("✅ Fee tier is correct")
                    else:
                        self.log(f"❌ Unexpected fee tier: {fee}", "ERROR")
        else:
            self.log(f"❌ Unknown function: {input_data[:10]}")
    
    def check_allowances(self):
        """Check current token allowances"""
        self.log("🔍 Checking current token allowances...")
        
        try:
            # Check WETH allowance
            weth_allowance_data = self.w3.eth.call({
                'to': self.weth_address,
                'data': '0xdd62ed3e' + self.user_address[2:].zfill(64) + self.position_manager[2:].zfill(64)
            })
            weth_allowance = int(weth_allowance_data.hex(), 16)
            self.log(f"💎 WETH Allowance: {weth_allowance} wei ({weth_allowance / 1e18:.6f} WETH)")
            
            # Check USDC allowance
            usdc_allowance_data = self.w3.eth.call({
                'to': self.usdc_address,
                'data': '0xdd62ed3e' + self.user_address[2:].zfill(64) + self.position_manager[2:].zfill(64)
            })
            usdc_allowance = int(usdc_allowance_data.hex(), 16)
            self.log(f"💵 USDC Allowance: {usdc_allowance} wei ({usdc_allowance / 1e6:.6f} USDC)")
            
            return weth_allowance > 0 and usdc_allowance > 0
            
        except Exception as e:
            self.log(f"❌ Error checking allowances: {e}", "ERROR")
            return False
    
    def check_balances(self):
        """Check current token balances"""
        self.log("💰 Checking current token balances...")
        
        try:
            # Check WETH balance
            weth_balance_data = self.w3.eth.call({
                'to': self.weth_address,
                'data': '0x70a08231' + self.user_address[2:].zfill(64)
            })
            weth_balance = int(weth_balance_data.hex(), 16)
            self.log(f"💎 WETH Balance: {weth_balance} wei ({weth_balance / 1e18:.6f} WETH)")
            
            # Check USDC balance
            usdc_balance_data = self.w3.eth.call({
                'to': self.usdc_address,
                'data': '0x70a08231' + self.user_address[2:].zfill(64)
            })
            usdc_balance = int(usdc_balance_data.hex(), 16)
            self.log(f"💵 USDC Balance: {usdc_balance} wei ({usdc_balance / 1e6:.6f} USDC)")
            
            return weth_balance > 0 and usdc_balance > 0
            
        except Exception as e:
            self.log(f"❌ Error checking balances: {e}", "ERROR")
            return False
    
    def run_comprehensive_analysis(self):
        """Run comprehensive analysis of the failure"""
        self.log("🚀 COMPREHENSIVE FAILURE ANALYSIS")
        self.log("=" * 60)
        
        # Analyze approval transaction
        approval_success = self.analyze_transaction(self.approval_tx, "Approval Transaction")
        
        # Analyze position creation transaction
        position_success = self.analyze_transaction(self.position_tx, "Position Creation Transaction")
        
        # Check current state
        self.log("")
        self.log("🔍 Checking current state...")
        balances_ok = self.check_balances()
        allowances_ok = self.check_allowances()
        
        self.log("=" * 60)
        self.log("📊 ANALYSIS SUMMARY")
        self.log("=" * 60)
        
        if approval_success:
            self.log("✅ Approval transaction succeeded")
        else:
            self.log("❌ Approval transaction failed", "ERROR")
        
        if position_success:
            self.log("✅ Position creation succeeded")
        else:
            self.log("❌ Position creation failed", "ERROR")
        
        if balances_ok:
            self.log("✅ Wallet has sufficient balances")
        else:
            self.log("❌ Wallet has insufficient balances", "ERROR")
        
        if allowances_ok:
            self.log("✅ Token allowances are set")
        else:
            self.log("❌ Token allowances are not set", "ERROR")
        
        self.log("")
        self.log("🔧 LIKELY ISSUES:")
        if not position_success:
            self.log("1. ❌ Position creation transaction failed")
            self.log("   - Check if pool address exists")
            self.log("   - Check if tick range is valid")
            self.log("   - Check if amounts are sufficient")
            self.log("   - Check if gas limit is adequate")
        
        if not allowances_ok:
            self.log("2. ❌ Token allowances not set properly")
            self.log("   - Re-run approval transactions")
            self.log("   - Check approval amounts")
        
        if not balances_ok:
            self.log("3. ❌ Insufficient token balances")
            self.log("   - Get more WETH and USDC")
        
        return position_success and allowances_ok and balances_ok

def main():
    print("🔍 LATEST FAILURE ANALYZER")
    print("=" * 60)
    print("Analyzing the latest failed transaction to identify root cause")
    print("=" * 60)
    
    analyzer = LatestFailureAnalyzer()
    success = analyzer.run_comprehensive_analysis()
    
    if success:
        print("\n🎉 ALL SYSTEMS WORKING!")
    else:
        print("\n⚠️  ISSUES DETECTED!")
        print("Please fix the issues above before retrying.")

if __name__ == "__main__":
    main()
