#!/usr/bin/env python3
"""
Test script to create a real position with 10 cents
"""

import requests
import json
import time

def test_real_transaction():
    """Test creating a real 10 cent position"""
    
    print("🧪 Testing Real Transaction with 10 cents")
    print("=" * 50)
    
    # Test parameters
    pool_address = "0x72ab388e2e2f6facef59e3c3fa2c4e29011c2d38"  # WETH-USDC 0.05%
    amount_usdc = 0.10  # 10 cents
    amount_weth = amount_usdc / 3800  # Approximate WETH amount
    
    print(f"Pool: {pool_address}")
    print(f"Amount USDC: ${amount_usdc}")
    print(f"Amount WETH: {amount_weth:.8f}")
    print(f"Total Value: ~${amount_usdc * 2}")
    print()
    
    # Test transaction parameters
    print("📋 Transaction Parameters:")
    print(f"Token0: WETH (0x4200000000000000000000000000000000000006)")
    print(f"Token1: USDC (0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913)")
    print(f"Fee Tier: 500 (0.05%)")
    print(f"Tick Range: 5% (500 bips)")
    print(f"Gas Limit: 500,000")
    print()
    
    # Expected amounts in wei
    amount0_wei = int(amount_weth * 10**18)
    amount1_wei = int(amount_usdc * 10**6)
    
    print("💰 Amounts in Wei:")
    print(f"Amount0 (WETH): {amount0_wei}")
    print(f"Amount1 (USDC): {amount1_wei}")
    print()
    
    # Test tick calculation
    current_price = 3800
    tick_range = 500  # 5%
    tick_spacing = 10  # For 0.05% fee
    
    tick_lower = int((current_price * (1 - tick_range / 10000)) ** 0.5 / 1.0001 ** 0.5)
    tick_upper = int((current_price * (1 + tick_range / 10000)) ** 0.5 / 1.0001 ** 0.5)
    
    # Align with tick spacing
    aligned_tick_lower = (tick_lower // tick_spacing) * tick_spacing
    aligned_tick_upper = (tick_upper // tick_spacing) * tick_spacing
    
    print("🎯 Tick Calculation:")
    print(f"Current Price: {current_price}")
    print(f"Tick Range: {tick_range} bips (5%)")
    print(f"Tick Spacing: {tick_spacing}")
    print(f"Tick Lower: {aligned_tick_lower}")
    print(f"Tick Upper: {aligned_tick_upper}")
    print()
    
    # Gas estimation
    gas_price_gwei = 0.001  # Base network gas price
    gas_limit = 500000
    gas_cost_eth = (gas_limit * gas_price_gwei) / 10**9
    gas_cost_usd = gas_cost_eth * 3800  # ETH price
    
    print("⛽ Gas Estimation:")
    print(f"Gas Limit: {gas_limit:,}")
    print(f"Gas Price: {gas_price_gwei} gwei")
    print(f"Gas Cost: {gas_cost_eth:.8f} ETH")
    print(f"Gas Cost: ${gas_cost_usd:.4f}")
    print()
    
    print("✅ Ready for testing!")
    print("Expected results:")
    print("- Gas cost should be under $0.10")
    print("- Transaction should succeed")
    print("- Position should appear on Uniswap")
    print()
    
    return {
        "pool_address": pool_address,
        "amount0_wei": amount0_wei,
        "amount1_wei": amount1_wei,
        "tick_lower": aligned_tick_lower,
        "tick_upper": aligned_tick_upper,
        "gas_limit": gas_limit,
        "gas_cost_usd": gas_cost_usd
    }

if __name__ == "__main__":
    test_real_transaction()
