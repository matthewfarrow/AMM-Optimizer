#!/usr/bin/env python3
"""
ANALYZE FAILED TRANSACTION - CRITICAL DEBUG
Analyzes the failed transaction to identify the exact issue
"""

import requests
import json
from web3 import Web3

class TransactionAnalyzer:
    def __init__(self):
        self.rpc_url = "https://mainnet.base.org"
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.tx_hash = "0x501119459e5d68de6ef3d89ea1ebe2666397cedad4354e16a60184a063bdc026"
        
    def log(self, message, level="INFO"):
        print(f"[{level}] {message}")
    
    def analyze_transaction(self):
        """Analyze the failed transaction"""
        self.log("🔍 Analyzing failed transaction...")
        
        try:
            # Get transaction details
            tx = self.w3.eth.get_transaction(self.tx_hash)
            tx_receipt = self.w3.eth.get_transaction_receipt(self.tx_hash)
            
            self.log(f"📋 Transaction Details:")
            self.log(f"  Hash: {self.tx_hash}")
            self.log(f"  From: {tx['from']}")
            self.log(f"  To: {tx['to']}")
            self.log(f"  Gas Limit: {tx['gas']}")
            self.log(f"  Gas Price: {tx['gasPrice']} wei ({self.w3.from_wei(tx['gasPrice'], 'gwei')} gwei)")
            self.log(f"  Value: {tx['value']} wei")
            self.log(f"  Status: {'Success' if tx_receipt['status'] == 1 else 'Failed'}")
            self.log(f"  Gas Used: {tx_receipt['gasUsed']}")
            
            # Check if it's a call to NonfungiblePositionManager
            position_manager = "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1"
            if tx['to'] and tx['to'].lower() == position_manager.lower():
                self.log("✅ This was a call to NonfungiblePositionManager")
                self.analyze_mint_call(tx['input'])
            else:
                self.log(f"❌ This was NOT a call to NonfungiblePositionManager")
                self.log(f"   Expected: {position_manager}")
                self.log(f"   Actual: {tx['to']}")
            
            # Check transaction logs for errors
            if tx_receipt['logs']:
                self.log(f"📝 Transaction had {len(tx_receipt['logs'])} logs")
                for i, log in enumerate(tx_receipt['logs']):
                    self.log(f"  Log {i}: {log['address']} - {len(log['data'])} bytes")
            else:
                self.log("❌ No logs - transaction failed before any events")
            
            return tx_receipt['status'] == 1
            
        except Exception as e:
            self.log(f"❌ Error analyzing transaction: {e}", "ERROR")
            return False
    
    def analyze_mint_call(self, input_data):
        """Analyze the mint function call"""
        self.log("🔍 Analyzing mint function call...")
        
        # mint function selector: 0x88316456
        if input_data.startswith('0x88316456'):
            self.log("✅ mint() function was called")
            
            # Extract parameters (simplified - would need full ABI for complete decoding)
            self.log(f"📊 Input data length: {len(input_data)} characters")
            self.log(f"📊 Function selector: {input_data[:10]}")
            
            # Try to extract some basic info
            if len(input_data) > 10:
                params_data = input_data[10:]
                self.log(f"📊 Parameters data: {params_data[:100]}...")
                
                # Extract token addresses (first two addresses in the call)
                if len(params_data) >= 128:  # 2 addresses = 64 chars each
                    token0 = "0x" + params_data[24:64]  # Skip first 24 chars (padding)
                    token1 = "0x" + params_data[88:128]  # Skip first 88 chars
                    
                    self.log(f"🎯 Token0: {token0}")
                    self.log(f"🎯 Token1: {token1}")
                    
                    # Check if these are the expected tokens
                    expected_weth = "0x4200000000000000000000000000000000000006"
                    expected_usdc = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
                    
                    if token0.lower() == expected_weth.lower():
                        self.log("✅ Token0 is WETH (correct)")
                    elif token0.lower() == expected_usdc.lower():
                        self.log("✅ Token0 is USDC (correct)")
                    else:
                        self.log(f"❌ Token0 is unexpected: {token0}", "ERROR")
                    
                    if token1.lower() == expected_weth.lower():
                        self.log("✅ Token1 is WETH (correct)")
                    elif token1.lower() == expected_usdc.lower():
                        self.log("✅ Token1 is USDC (correct)")
                    else:
                        self.log(f"❌ Token1 is unexpected: {token1}", "ERROR")
        else:
            self.log(f"❌ Unknown function called: {input_data[:10]}")
    
    def check_pool_exists(self, pool_address):
        """Check if a pool contract exists"""
        try:
            code = self.w3.eth.get_code(pool_address)
            return len(code) > 2
        except Exception as e:
            self.log(f"❌ Error checking pool: {e}", "ERROR")
            return False
    
    def run_analysis(self):
        """Run complete transaction analysis"""
        self.log("🚀 Starting Transaction Analysis")
        self.log("=" * 60)
        
        success = self.analyze_transaction()
        
        self.log("=" * 60)
        self.log("📊 ANALYSIS SUMMARY")
        self.log("=" * 60)
        
        if success:
            self.log("✅ Transaction succeeded")
        else:
            self.log("❌ Transaction failed")
            self.log("")
            self.log("🔧 LIKELY ISSUES:")
            self.log("1. Wrong pool address")
            self.log("2. Insufficient token balance")
            self.log("3. Incorrect token ordering")
            self.log("4. Gas estimation issues")
            self.log("5. Contract interaction errors")
        
        return success

def main():
    print("🔍 TRANSACTION ANALYZER")
    print("=" * 60)
    print("Analyzing failed transaction to identify root cause")
    print("=" * 60)
    
    analyzer = TransactionAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
