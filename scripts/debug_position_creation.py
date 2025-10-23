#!/usr/bin/env python3
"""
Debug Position Creation - Simple test to identify the issue
"""

import sys
from pathlib import Path
from web3 import Web3
from eth_account import Account

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration
PRIVATE_KEY = "9c31f983fb60e4a23e15b44d9dbe736dc5d5e133a866ea79881b664c2ed773fe"
WALLET_ADDRESS = "0x8a679aCf39c06682072C4a2A833eb437A0CC0bdb"
RPC_URL = "https://mainnet.base.org"

# Pool configuration
POOL_ADDRESS = "0x6c561B446416E1A00E8E93E221854d6eA4171372"
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
POSITION_MANAGER = "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1"

    # Very small test amounts - we'll calculate the correct ratio
TOTAL_VALUE_USD = 0.01  # $0.01 total

# ABIs (minimal)
POOL_ABI = [
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"},
            {"internalType": "int24", "name": "tick", "type": "int24"},
            {"internalType": "uint16", "name": "observationIndex", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinality", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinalityNext", "type": "uint16"},
            {"internalType": "uint8", "name": "feeProtocol", "type": "uint8"},
            {"internalType": "bool", "name": "unlocked", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

ERC20_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

POSITION_MANAGER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "token0", "type": "address"},
                    {"internalType": "address", "name": "token1", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "int24", "name": "tickLower", "type": "int24"},
                    {"internalType": "int24", "name": "tickUpper", "type": "int24"},
                    {"internalType": "uint256", "name": "amount0Desired", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount1Desired", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount0Min", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount1Min", "type": "uint256"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "internalType": "struct INonfungiblePositionManager.MintParams",
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "mint",
        "outputs": [
            {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
            {"internalType": "uint128", "name": "liquidity", "type": "uint128"},
            {"internalType": "uint256", "name": "amount0", "type": "uint256"},
            {"internalType": "uint256", "name": "amount1", "type": "uint256"}
        ],
        "stateMutability": "payable",
        "type": "function"
    }
]

def main():
    print("🔍 Debug Position Creation")
    print("=" * 40)
    
    # Setup
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("❌ Failed to connect to Base network")
        return
    
    account = Account.from_key(PRIVATE_KEY)
    print(f"✅ Connected to Base (chain ID: {w3.eth.chain_id})")
    print(f"✅ Account: {account.address}")
    
    # Get current tick first
    print("\n🎯 Getting current tick...")
    pool_contract = w3.eth.contract(address=POOL_ADDRESS, abi=POOL_ABI)
    slot0 = pool_contract.functions.slot0().call()
    current_tick = slot0[1]
    print(f"Current tick: {current_tick}")
    
    # Use estimated price based on user's information
    # User mentioned WETH is around $3,850
    weth_usdc_price = 3850.0  # Estimated WETH price in USDC
    
    print(f"Using estimated price (WETH/USDC): {weth_usdc_price:.2f}")
    print(f"Note: Actual tick-based calculation has precision issues with negative ticks")
    
    # For concentrated liquidity, we need to provide the correct ratio
    # Let's try a different approach - provide only WETH and let the contract calculate USDC
    # Or provide only USDC and let the contract calculate WETH
    
    # Let's try with only USDC first (simpler)
    usdc_amount = 0.01  # $0.01 USDC
    weth_amount = 0.0   # Let the contract calculate this
    
    print(f"Using single-token approach:")
    print(f"  WETH: {weth_amount:.8f} WETH (contract will calculate)")
    print(f"  USDC: {usdc_amount:.6f} USDC")
    
    # Convert to wei
    weth_amount_wei = w3.to_wei(weth_amount, 'ether')
    usdc_amount_wei = int(usdc_amount * 10**6)
    
    # Check balances
    print("\n💰 Checking balances...")
    eth_balance = w3.eth.get_balance(account.address)
    print(f"ETH: {w3.from_wei(eth_balance, 'ether'):.6f} ETH")
    
    weth_contract = w3.eth.contract(address=WETH_ADDRESS, abi=ERC20_ABI)
    weth_balance = weth_contract.functions.balanceOf(account.address).call()
    print(f"WETH: {w3.from_wei(weth_balance, 'ether'):.6f} WETH")
    
    usdc_contract = w3.eth.contract(address=USDC_ADDRESS, abi=ERC20_ABI)
    usdc_balance = usdc_contract.functions.balanceOf(account.address).call()
    print(f"USDC: {usdc_balance / 10**6:.6f} USDC")
    
    # Check if we have enough balance
    if weth_balance < weth_amount_wei:
        print(f"❌ Insufficient WETH: {w3.from_wei(weth_balance, 'ether'):.6f} < {weth_amount:.6f}")
        return
    
    if usdc_balance < usdc_amount_wei:
        print(f"❌ Insufficient USDC: {usdc_balance / 10**6:.6f} < {usdc_amount:.6f}")
        return
    
    print("✅ Sufficient balances")
    
    # Calculate tick bounds (smaller range for testing)
    tick_range = 100  # 1% range
    tick_spacing = 60  # 0.3% fee tier
    
    tick_lower = current_tick - tick_range
    tick_upper = current_tick + tick_range
    
    # Align with tick spacing
    aligned_tick_lower = (tick_lower // tick_spacing) * tick_spacing
    aligned_tick_upper = (tick_upper // tick_spacing) * tick_spacing
    
    final_tick_lower = min(aligned_tick_lower, aligned_tick_upper)
    final_tick_upper = max(aligned_tick_lower, aligned_tick_upper)
    
    print(f"Tick range: {final_tick_lower} to {final_tick_upper}")
    
    # Check if current tick is within range
    if current_tick < final_tick_lower or current_tick > final_tick_upper:
        print(f"❌ Current tick {current_tick} is outside range [{final_tick_lower}, {final_tick_upper}]")
        print("This would result in a position that's immediately out of range!")
        return
    
    print("✅ Current tick is within range")
    
    # Try to estimate gas for mint
    print("\n⛽ Estimating gas...")
    try:
        position_manager_contract = w3.eth.contract(address=POSITION_MANAGER, abi=POSITION_MANAGER_ABI)
        
        # Build mint parameters
        import time
        deadline = int(time.time()) + 20 * 60  # 20 minutes from now
        mint_params = (
            WETH_ADDRESS,      # token0
            USDC_ADDRESS,      # token1
            3000,              # fee
            final_tick_lower,  # tickLower
            final_tick_upper,  # tickUpper
            weth_amount_wei,   # amount0Desired
            usdc_amount_wei,   # amount1Desired
            weth_amount_wei,   # amount0Min (no slippage for testing)
            usdc_amount_wei,   # amount1Min (no slippage for testing)
            account.address,   # recipient
            deadline           # deadline
        )
        
        # Estimate gas
        gas_estimate = position_manager_contract.functions.mint(mint_params).estimate_gas({
            'from': account.address,
            'value': 0
        })
        
        print(f"✅ Gas estimate: {gas_estimate}")
        
        # Check if we have enough ETH for gas
        gas_price = w3.eth.gas_price
        gas_cost = gas_estimate * gas_price
        gas_cost_eth = w3.from_wei(gas_cost, 'ether')
        
        print(f"Gas price: {gas_price / 10**9:.2f} Gwei")
        print(f"Gas cost: {gas_cost_eth:.6f} ETH")
        
        if eth_balance < gas_cost:
            print(f"❌ Insufficient ETH for gas: {w3.from_wei(eth_balance, 'ether'):.6f} < {gas_cost_eth:.6f}")
            return
        
        print("✅ Sufficient ETH for gas")
        
    except Exception as e:
        print(f"❌ Gas estimation failed: {e}")
        return
    
    print("\n🎉 All checks passed! Position creation should work.")
    print("The issue might be with the actual transaction execution.")

if __name__ == "__main__":
    main()
