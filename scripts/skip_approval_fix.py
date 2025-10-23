#!/usr/bin/env python3
"""
SKIP APPROVAL FIX - CRITICAL HACKATHON FIX
Fixes the app to skip approval when allowances are already sufficient
"""

import requests
import json
from web3 import Web3

class SkipApprovalFixer:
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
    
    def check_current_allowances(self):
        """Check current token allowances"""
        self.log("🔍 Checking current token allowances...")
        
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
    
    def check_token_balances(self):
        """Check current token balances"""
        self.log("💰 Checking current token balances...")
        
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
    
    def calculate_required_amounts(self):
        """Calculate amounts needed for a small position"""
        self.log("🎯 Calculating required amounts for position...")
        
        # For a $0.01 position
        target_usd = 0.01
        weth_price = 3849.86  # Current price from our data
        
        weth_amount = target_usd / weth_price
        usdc_amount = target_usd
        
        weth_amount_wei = int(weth_amount * 1e18)
        usdc_amount_wei = int(usdc_amount * 1e6)
        
        self.log(f"🎯 For ${target_usd} position:")
        self.log(f"   WETH needed: {weth_amount:.8f} WETH ({weth_amount_wei} wei)")
        self.log(f"   USDC needed: {usdc_amount:.6f} USDC ({usdc_amount_wei} wei)")
        
        return weth_amount_wei, usdc_amount_wei
    
    def check_sufficient_allowances(self, weth_allowance, usdc_allowance, weth_needed, usdc_needed):
        """Check if allowances are sufficient"""
        self.log("🔍 Checking if allowances are sufficient...")
        
        weth_sufficient = weth_allowance >= weth_needed
        usdc_sufficient = usdc_allowance >= usdc_needed
        
        self.log(f"💎 WETH sufficient: {weth_sufficient} ({weth_allowance} >= {weth_needed})")
        self.log(f"💵 USDC sufficient: {usdc_sufficient} ({usdc_allowance} >= {usdc_needed})")
        
        if weth_sufficient and usdc_sufficient:
            self.log("✅ Both allowances are sufficient!")
            self.log("💡 You can skip approval and go directly to position creation")
            return True
        else:
            self.log("❌ Allowances are insufficient")
            if not weth_sufficient:
                self.log(f"   Need more WETH allowance: {weth_needed - weth_allowance} wei")
            if not usdc_sufficient:
                self.log(f"   Need more USDC allowance: {usdc_needed - usdc_allowance} wei")
            return False
    
    def create_frontend_fix(self):
        """Create a fix for the frontend to skip approval when not needed"""
        self.log("📝 Creating frontend fix...")
        
        fix_content = '''// FRONTEND FIX: Skip approval when allowances are sufficient
// Add this to StrategyConfig.tsx in the handleSubmit function

const checkAndSkipApproval = async () => {
  console.log('🔍 Checking if approval is needed...');
  
  // Check current allowances
  const token0Allowance = await readContract({
    address: finalToken0Address as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'allowance',
    args: [address, UNISWAP_V3_ADDRESSES.NONFUNGIBLE_POSITION_MANAGER as `0x${string}`],
  });
  
  const token1Allowance = await readContract({
    address: finalToken1Address as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'allowance',
    args: [address, UNISWAP_V3_ADDRESSES.NONFUNGIBLE_POSITION_MANAGER as `0x${string}`],
  });
  
  // Calculate required amounts
  const amount0Desired = parseUnits(amount0, token0Symbol === 'USDC' ? 6 : 18);
  const amount1Desired = parseUnits(amount1, token1Symbol === 'USDC' ? 6 : 18);
  
  console.log('💰 Allowance check:', {
    token0Allowance: token0Allowance.toString(),
    token1Allowance: token1Allowance.toString(),
    amount0Desired: amount0Desired.toString(),
    amount1Desired: amount1Desired.toString()
  });
  
  // Check if approval is needed
  const needsToken0Approval = token0Allowance < amount0Desired;
  const needsToken1Approval = token1Allowance < amount1Desired;
  
  if (needsToken0Approval) {
    console.log('⚠️  Token0 approval needed');
    await approveToken(finalToken0Address, amount0Desired);
    return false; // Wait for approval
  }
  
  if (needsToken1Approval) {
    console.log('⚠️  Token1 approval needed');
    await approveToken(finalToken1Address, amount1Desired);
    return false; // Wait for approval
  }
  
  console.log('✅ No approval needed - proceeding to position creation');
  return true; // Can proceed directly
};

// Update handleSubmit function
const handleSubmit = async () => {
  console.log('🚀 Starting position creation process...');
  
  // Check if approval is needed
  const canProceed = await checkAndSkipApproval();
  
  if (canProceed) {
    // Skip approval, go directly to position creation
    console.log('🎯 Skipping approval - creating position directly');
    await createPosition();
  } else {
    // Approval is in progress, wait for it to complete
    console.log('⏳ Waiting for approval to complete...');
  }
};
'''
        
        with open("FRONTEND_SKIP_APPROVAL_FIX.js", "w") as f:
            f.write(fix_content)
        
        self.log("✅ Frontend fix created: FRONTEND_SKIP_APPROVAL_FIX.js")
    
    def run_analysis(self):
        """Run complete analysis"""
        self.log("🚀 SKIP APPROVAL ANALYSIS")
        self.log("=" * 50)
        
        # Check current state
        weth_balance, usdc_balance = self.check_token_balances()
        weth_allowance, usdc_allowance = self.check_current_allowances()
        
        # Calculate required amounts
        weth_needed, usdc_needed = self.calculate_required_amounts()
        
        # Check if allowances are sufficient
        sufficient = self.check_sufficient_allowances(
            weth_allowance, usdc_allowance, weth_needed, usdc_needed
        )
        
        # Create frontend fix
        self.create_frontend_fix()
        
        self.log("=" * 50)
        self.log("📊 ANALYSIS RESULTS")
        self.log("=" * 50)
        
        if sufficient:
            self.log("🎉 SOLUTION FOUND!")
            self.log("")
            self.log("💡 THE ISSUE:")
            self.log("   Your app is trying to approve tokens that are already approved!")
            self.log("   This causes rate limiting because it's unnecessary.")
            self.log("")
            self.log("🔧 THE FIX:")
            self.log("   1. Check current allowances before approving")
            self.log("   2. Skip approval if allowances are sufficient")
            self.log("   3. Go directly to position creation")
            self.log("")
            self.log("📝 IMPLEMENTATION:")
            self.log("   Apply the fix in FRONTEND_SKIP_APPROVAL_FIX.js")
            self.log("   Update your StrategyConfig.tsx file")
            return True
        else:
            self.log("⚠️  APPROVAL STILL NEEDED")
            self.log("   Your allowances are insufficient for the position size")
            self.log("   You need to approve more tokens first")
            return False

def main():
    print("🔧 SKIP APPROVAL FIX")
    print("=" * 50)
    print("Fixing the app to skip unnecessary approvals")
    print("=" * 50)
    
    fixer = SkipApprovalFixer()
    success = fixer.run_analysis()
    
    if success:
        print("\n🎉 FIX READY!")
        print("Apply the frontend fix to skip unnecessary approvals.")
    else:
        print("\n⚠️  APPROVAL NEEDED!")
        print("You need to approve more tokens first.")

if __name__ == "__main__":
    main()
