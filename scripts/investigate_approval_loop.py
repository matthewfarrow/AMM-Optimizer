#!/usr/bin/env python3
"""
INVESTIGATE APPROVAL LOOP - CRITICAL DEBUG
Investigates why the app is stuck in an endless WETH approval loop
"""

import requests
import json
from web3 import Web3

class ApprovalLoopInvestigator:
    def __init__(self):
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
    
    def get_current_price(self):
        """Get current WETH price"""
        try:
            response = requests.get("http://localhost:8000/api/analytics/0xd0b53D9277642d899DF5C87A3966A349A798F224/price-data?timeframe=1d", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    price = data['data'][-1]['price']
                    self.log(f"📊 Current WETH price: ${price:,.2f}")
                    return price
            return None
        except Exception as e:
            self.log(f"❌ Error getting price: {e}", "ERROR")
            return None
    
    def calculate_required_amounts(self, price):
        """Calculate amounts needed for a small position"""
        if not price:
            return None, None
        
        # For a $0.01 position
        target_usd = 0.01
        weth_amount = target_usd / price
        usdc_amount = target_usd
        
        weth_amount_wei = int(weth_amount * 1e18)
        usdc_amount_wei = int(usdc_amount * 1e6)
        
        self.log(f"🎯 For ${target_usd} position:")
        self.log(f"   WETH needed: {weth_amount:.8f} WETH ({weth_amount_wei} wei)")
        self.log(f"   USDC needed: {usdc_amount:.6f} USDC ({usdc_amount_wei} wei)")
        
        return weth_amount_wei, usdc_amount_wei
    
    def analyze_approval_loop_issue(self, weth_allowance, usdc_allowance, weth_needed, usdc_needed):
        """Analyze why the approval loop is happening"""
        self.log("🔍 Analyzing approval loop issue...")
        
        # Check if allowances are sufficient
        weth_sufficient = weth_allowance >= weth_needed
        usdc_sufficient = usdc_allowance >= usdc_needed
        
        self.log(f"📋 Allowance analysis:")
        self.log(f"   WETH sufficient: {weth_sufficient} ({weth_allowance} >= {weth_needed})")
        self.log(f"   USDC sufficient: {usdc_sufficient} ({usdc_allowance} >= {usdc_needed})")
        
        if weth_sufficient and usdc_sufficient:
            self.log("✅ Both allowances are sufficient!")
            self.log("💡 The app should NOT be trying to approve anything")
            self.log("🚨 ROOT CAUSE: Frontend logic is broken - it's not checking allowances correctly")
            return "frontend_logic_broken"
        else:
            self.log("❌ Allowances are insufficient")
            if not weth_sufficient:
                self.log(f"   Need more WETH allowance: {weth_needed - weth_allowance} wei")
            if not usdc_sufficient:
                self.log(f"   Need more USDC allowance: {usdc_needed - usdc_allowance} wei")
            return "insufficient_allowances"
    
    def check_frontend_logic_issue(self):
        """Check if there's a frontend logic issue"""
        self.log("🔍 Checking frontend logic issue...")
        
        # The issue might be:
        # 1. Wrong decimal parsing in frontend
        # 2. Wrong token ordering
        # 3. Wrong allowance comparison
        # 4. Frontend not reading allowances correctly
        
        self.log("🚨 POTENTIAL ISSUES:")
        self.log("1. Frontend might be using wrong decimals (18 vs 6)")
        self.log("2. Frontend might be comparing wrong token allowances")
        self.log("3. Frontend might not be reading allowances from blockchain")
        self.log("4. Frontend might be stuck in a retry loop")
        
        return True
    
    def create_immediate_fix(self):
        """Create an immediate fix for the approval loop"""
        self.log("🔧 Creating immediate fix...")
        
        fix_content = '''// IMMEDIATE FIX FOR APPROVAL LOOP
// Add this to StrategyConfig.tsx to break the approval loop

const handleSubmit = async () => {
  console.log('🚀 Starting position creation process...');
  
  if (!address || !volatilityData?.current_price) {
    console.error('❌ Missing required data');
    toast.error('Missing required data');
    return;
  }

  try {
    setLoading(true);
    
    // Calculate amounts with correct decimals
    const amount0BigInt = parseUnits(amount0, token0Symbol === 'USDC' ? 6 : 18);
    const amount1BigInt = parseUnits(amount1, token1Symbol === 'USDC' ? 6 : 18);
    
    console.log('🔍 Approval check:', {
      token0Symbol,
      token1Symbol,
      token0Allowance: token0Allowance?.toString(),
      token1Allowance: token1Allowance?.toString(),
      amount0BigInt: amount0BigInt.toString(),
      amount1BigInt: amount1BigInt.toString()
    });
    
    // CRITICAL FIX: Check if allowances are sufficient
    const needsToken0Approval = !token0Allowance || token0Allowance < amount0BigInt;
    const needsToken1Approval = !token1Allowance || token1Allowance < amount1BigInt;
    
    console.log('📋 Approval needed:', {
      needsToken0Approval,
      needsToken1Approval
    });
    
    // BREAK THE LOOP: If no approval needed, go directly to position creation
    if (!needsToken0Approval && !needsToken1Approval) {
      console.log('✅ No approval needed - proceeding directly to position creation');
      setCurrentStep('Creating Position');
      toast.info('Creating position...');
      await createPosition();
      return;
    }
    
    // Only approve if actually needed
    if (needsToken0Approval) {
      console.log('⚠️  Token0 approval needed');
      setCurrentStep(`Approving ${token0Symbol}`);
      toast.info(`Approving ${token0Symbol}...`);
      await approveToken(finalToken0Address, amount0BigInt);
      return; // Wait for approval
    }
    
    if (needsToken1Approval) {
      console.log('⚠️  Token1 approval needed');
      setCurrentStep(`Approving ${token1Symbol}`);
      toast.info(`Approving ${token1Symbol}...`);
      await approveToken(finalToken1Address, amount1BigInt);
      return; // Wait for approval
    }
    
  } catch (error) {
    console.error('Error in handleSubmit:', error);
    toast.error('Failed to create position');
  } finally {
    setLoading(false);
  }
};
'''
        
        with open("IMMEDIATE_APPROVAL_LOOP_FIX.js", "w") as f:
            f.write(fix_content)
        
        self.log("✅ Immediate fix created: IMMEDIATE_APPROVAL_LOOP_FIX.js")
    
    def run_investigation(self):
        """Run complete investigation"""
        self.log("🚀 APPROVAL LOOP INVESTIGATION")
        self.log("=" * 60)
        
        # Check current state
        weth_balance, usdc_balance = self.check_token_balances()
        weth_allowance, usdc_allowance = self.check_current_allowances()
        
        # Get current price and calculate required amounts
        price = self.get_current_price()
        weth_needed, usdc_needed = self.calculate_required_amounts(price)
        
        # Analyze the issue
        if weth_needed and usdc_needed:
            issue_type = self.analyze_approval_loop_issue(
                weth_allowance, usdc_allowance, weth_needed, usdc_needed
            )
            
            if issue_type == "frontend_logic_broken":
                self.check_frontend_logic_issue()
        
        # Create immediate fix
        self.create_immediate_fix()
        
        self.log("=" * 60)
        self.log("📊 INVESTIGATION RESULTS")
        self.log("=" * 60)
        
        if weth_allowance >= weth_needed and usdc_allowance >= usdc_needed:
            self.log("🎯 ROOT CAUSE IDENTIFIED:")
            self.log("   Your allowances are sufficient, but the frontend is broken!")
            self.log("   The app keeps trying to approve tokens that are already approved.")
            self.log("")
            self.log("🔧 IMMEDIATE SOLUTION:")
            self.log("   1. Apply the fix in IMMEDIATE_APPROVAL_LOOP_FIX.js")
            self.log("   2. Update your StrategyConfig.tsx file")
            self.log("   3. The app will skip approval and create position directly")
            return True
        else:
            self.log("⚠️  APPROVAL STILL NEEDED")
            self.log("   Your allowances are insufficient")
            self.log("   You need to approve more tokens first")
            return False

def main():
    print("🔍 APPROVAL LOOP INVESTIGATOR")
    print("=" * 60)
    print("Investigating why the app is stuck in an endless approval loop")
    print("=" * 60)
    
    investigator = ApprovalLoopInvestigator()
    success = investigator.run_investigation()
    
    if success:
        print("\n🎉 ISSUE IDENTIFIED!")
        print("The frontend logic is broken - apply the fix to break the loop.")
    else:
        print("\n⚠️  APPROVAL NEEDED!")
        print("You need to approve more tokens first.")

if __name__ == "__main__":
    main()
