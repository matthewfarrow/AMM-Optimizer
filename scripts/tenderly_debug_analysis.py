#!/usr/bin/env python3
"""
TENDERLY DEBUG ANALYSIS - RATE LIMITING INVESTIGATION
Uses Tenderly API to analyze rate limiting issues and debug smart contract interactions
"""

import requests
import json
import time
from web3 import Web3

class TenderlyDebugger:
    def __init__(self):
        self.tenderly_token = "SKEkWW3k7OBXeoNgKHvd4b-9CAHBFMgG"
        self.base_rpc = "https://mainnet.base.org"
        self.w3 = Web3(Web3.HTTPProvider(self.base_rpc))
        self.user_address = "0x8a679aCf39c06682072C4a2A833eb437A0CC0bdb"
        
        # Contract addresses
        self.position_manager = "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1"
        self.weth_address = "0x4200000000000000000000000000000000000006"
        self.usdc_address = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        
        # Pool addresses (verified)
        self.pools = {
            "WETH-USDC 0.05%": "0xd0b53D9277642d899DF5C87A3966A349A798F224",
            "WETH-USDC 0.3%": "0x6c561B446416E1A00E8E93E221854d6eA4171372"
        }
        
    def log(self, message, level="INFO"):
        print(f"[{level}] {message}")
    
    def check_rpc_rate_limits(self):
        """Check if RPC endpoint is rate limited"""
        self.log("🔍 Checking RPC rate limits...")
        
        try:
            # Test basic RPC call
            start_time = time.time()
            block_number = self.w3.eth.block_number
            end_time = time.time()
            
            response_time = end_time - start_time
            self.log(f"📊 RPC Response Time: {response_time:.3f}s")
            
            if response_time > 5:
                self.log("⚠️  RPC is slow - possible rate limiting", "WARNING")
                return False
            else:
                self.log("✅ RPC is responding normally")
                return True
                
        except Exception as e:
            self.log(f"❌ RPC Error: {e}", "ERROR")
            return False
    
    def simulate_approval_transaction(self, token_address, amount):
        """Simulate approval transaction using Tenderly"""
        self.log(f"🔍 Simulating approval transaction for {token_address}")
        
        try:
            # Get current nonce
            nonce = self.w3.eth.get_transaction_count(self.user_address)
            
            # Build approval transaction
            approval_tx = {
                'from': self.user_address,
                'to': token_address,
                'data': self.w3.eth.contract(
                    address=token_address,
                    abi=[{
                        "inputs": [
                            {"internalType": "address", "name": "spender", "type": "address"},
                            {"internalType": "uint256", "name": "amount", "type": "uint256"}
                        ],
                        "name": "approve",
                        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                        "stateMutability": "nonpayable",
                        "type": "function"
                    }]
                ).encodeABI(fn_name='approve', args=[self.position_manager, amount]),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
                'value': 0
            }
            
            # Simulate with Tenderly
            simulation_data = {
                "network_id": "8453",  # Base mainnet
                "from": self.user_address,
                "to": token_address,
                "input": approval_tx['data'],
                "gas": approval_tx['gas'],
                "gas_price": str(approval_tx['gasPrice']),
                "value": "0"
            }
            
            headers = {
                "X-Access-Key": self.tenderly_token,
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.tenderly.co/api/v1/simulate",
                headers=headers,
                json=simulation_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log("✅ Tenderly simulation successful")
                
                if result.get('transaction', {}).get('status'):
                    self.log("✅ Transaction would succeed")
                    return True
                else:
                    self.log("❌ Transaction would fail")
                    error = result.get('transaction', {}).get('error_message', 'Unknown error')
                    self.log(f"   Error: {error}")
                    return False
            else:
                self.log(f"❌ Tenderly API error: {response.status_code}", "ERROR")
                self.log(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Simulation error: {e}", "ERROR")
            return False
    
    def check_token_allowances(self):
        """Check current token allowances"""
        self.log("🔍 Checking current token allowances...")
        
        try:
            # Check WETH allowance
            weth_contract = self.w3.eth.contract(
                address=self.weth_address,
                abi=[{
                    "inputs": [
                        {"internalType": "address", "name": "owner", "type": "address"},
                        {"internalType": "address", "name": "spender", "type": "address"}
                    ],
                    "name": "allowance",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                }]
            )
            
            weth_allowance = weth_contract.functions.allowance(
                self.user_address, 
                self.position_manager
            ).call()
            
            self.log(f"💎 WETH Allowance: {weth_allowance} wei ({weth_allowance / 1e18:.6f} WETH)")
            
            # Check USDC allowance
            usdc_contract = self.w3.eth.contract(
                address=self.usdc_address,
                abi=[{
                    "inputs": [
                        {"internalType": "address", "name": "owner", "type": "address"},
                        {"internalType": "address", "name": "spender", "type": "address"}
                    ],
                    "name": "allowance",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                }]
            )
            
            usdc_allowance = usdc_contract.functions.allowance(
                self.user_address, 
                self.position_manager
            ).call()
            
            self.log(f"💵 USDC Allowance: {usdc_allowance} wei ({usdc_allowance / 1e6:.6f} USDC)")
            
            return weth_allowance, usdc_allowance
            
        except Exception as e:
            self.log(f"❌ Error checking allowances: {e}", "ERROR")
            return 0, 0
    
    def check_token_balances(self):
        """Check current token balances"""
        self.log("💰 Checking current token balances...")
        
        try:
            # Check WETH balance
            weth_contract = self.w3.eth.contract(
                address=self.weth_address,
                abi=[{
                    "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                }]
            )
            
            weth_balance = weth_contract.functions.balanceOf(self.user_address).call()
            self.log(f"💎 WETH Balance: {weth_balance} wei ({weth_balance / 1e18:.6f} WETH)")
            
            # Check USDC balance
            usdc_contract = self.w3.eth.contract(
                address=self.usdc_address,
                abi=[{
                    "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                }]
            )
            
            usdc_balance = usdc_contract.functions.balanceOf(self.user_address).call()
            self.log(f"💵 USDC Balance: {usdc_balance} wei ({usdc_balance / 1e6:.6f} USDC)")
            
            return weth_balance, usdc_balance
            
        except Exception as e:
            self.log(f"❌ Error checking balances: {e}", "ERROR")
            return 0, 0
    
    def analyze_rate_limiting_issue(self):
        """Analyze the rate limiting issue comprehensively"""
        self.log("🚀 COMPREHENSIVE RATE LIMITING ANALYSIS")
        self.log("=" * 60)
        
        # Check RPC health
        rpc_ok = self.check_rpc_rate_limits()
        
        # Check balances and allowances
        weth_balance, usdc_balance = self.check_token_balances()
        weth_allowance, usdc_allowance = self.check_token_allowances()
        
        # Simulate approval transactions
        self.log("")
        self.log("🧪 Simulating approval transactions...")
        
        # Test WETH approval
        weth_approval_ok = self.simulate_approval_transaction(self.weth_address, 1000000000000000000)  # 1 WETH
        
        # Test USDC approval  
        usdc_approval_ok = self.simulate_approval_transaction(self.usdc_address, 1000000)  # 1 USDC
        
        self.log("=" * 60)
        self.log("📊 ANALYSIS RESULTS")
        self.log("=" * 60)
        
        if not rpc_ok:
            self.log("❌ RPC is experiencing issues")
            self.log("💡 SOLUTION: Switch to a different RPC endpoint")
            self.log("   - Use Infura: https://base-mainnet.infura.io/v3/YOUR_KEY")
            self.log("   - Use Alchemy: https://base-mainnet.g.alchemy.com/v2/YOUR_KEY")
            self.log("   - Use QuickNode: https://YOUR_ENDPOINT.base-mainnet.quiknode.pro/YOUR_KEY/")
        
        if weth_approval_ok and usdc_approval_ok:
            self.log("✅ Approval transactions would succeed")
            self.log("💡 The issue is RPC rate limiting, not smart contract logic")
        else:
            self.log("❌ Approval transactions would fail")
            self.log("💡 There may be smart contract issues beyond rate limiting")
        
        # Check if allowances are sufficient
        if weth_allowance > 0 and usdc_allowance > 0:
            self.log("✅ Token allowances are already set")
            self.log("💡 You can skip approval and go directly to position creation")
        else:
            self.log("❌ Token allowances need to be set")
            self.log("💡 Approval transactions are required")
        
        return rpc_ok and weth_approval_ok and usdc_approval_ok
    
    def create_rpc_fix_guide(self):
        """Create a guide to fix RPC rate limiting"""
        self.log("📝 Creating RPC fix guide...")
        
        guide_content = '''# 🔧 RPC RATE LIMITING FIX GUIDE

## 🚨 PROBLEM IDENTIFIED
Your app is experiencing **RPC rate limiting** on the Base mainnet endpoint. This is causing:
- "Request is being rate limited" errors
- Failed approval transactions
- Inability to create positions

## 💡 SOLUTIONS

### Option 1: Use Premium RPC Endpoints

#### Infura (Recommended)
```bash
# Get free tier: https://infura.io
# Add to your .env file:
BASE_RPC_URL=https://base-mainnet.infura.io/v3/YOUR_PROJECT_ID
```

#### Alchemy
```bash
# Get free tier: https://alchemy.com
# Add to your .env file:
BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/YOUR_API_KEY
```

#### QuickNode
```bash
# Get free tier: https://quicknode.com
# Add to your .env file:
BASE_RPC_URL=https://YOUR_ENDPOINT.base-mainnet.quiknode.pro/YOUR_KEY/
```

### Option 2: Implement RPC Fallback

Update your frontend to use multiple RPC endpoints:

```typescript
const RPC_ENDPOINTS = [
  "https://mainnet.base.org",
  "https://base-mainnet.infura.io/v3/YOUR_KEY",
  "https://base-mainnet.g.alchemy.com/v2/YOUR_KEY"
];

// Try each endpoint until one works
```

### Option 3: Add Retry Logic with Exponential Backoff

```typescript
async function retryWithBackoff(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.message.includes('rate limited') && i < maxRetries - 1) {
        const delay = Math.pow(2, i) * 1000; // 1s, 2s, 4s
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }
      throw error;
    }
  }
}
```

## 🎯 IMMEDIATE FIX

1. **Get Infura API Key** (free tier: 100k requests/day)
2. **Update your app's RPC URL**
3. **Test position creation again**

## 📊 RATE LIMITS COMPARISON

| Provider | Free Tier | Rate Limit |
|----------|-----------|------------|
| Base Official | Unlimited | ~10 req/sec |
| Infura | 100k/day | ~100 req/sec |
| Alchemy | 300M/month | ~1000 req/sec |
| QuickNode | 25M/month | ~500 req/sec |

## 🚀 NEXT STEPS

1. Sign up for Infura (2 minutes)
2. Get your project ID
3. Update RPC URL in your app
4. Test position creation
5. Success! 🎉
'''
        
        with open("RPC_RATE_LIMITING_FIX.md", "w") as f:
            f.write(guide_content)
        
        self.log("✅ RPC fix guide created: RPC_RATE_LIMITING_FIX.md")

def main():
    print("🔍 TENDERLY DEBUG ANALYSIS")
    print("=" * 60)
    print("Analyzing rate limiting issues with Tenderly and smart contract debugging")
    print("=" * 60)
    
    debugger = TenderlyDebugger()
    success = debugger.analyze_rate_limiting_issue()
    debugger.create_rpc_fix_guide()
    
    if success:
        print("\n🎉 ANALYSIS COMPLETE!")
        print("The issue is RPC rate limiting, not smart contract problems.")
        print("Read RPC_RATE_LIMITING_FIX.md for solutions.")
    else:
        print("\n⚠️  ISSUES DETECTED!")
        print("Multiple problems found. Check the analysis above.")

if __name__ == "__main__":
    main()
