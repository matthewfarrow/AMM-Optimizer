#!/usr/bin/env python3
"""
Test script to verify transaction parameters for position creation
"""

import math

def test_tick_calculation():
    """Test tick calculation logic"""
    
    # Test parameters (similar to what we'd use for a small position)
    current_price = 3800  # WETH price in USDC
    tick_range = 100  # 1% range
    fee_tier = 500  # 0.05% fee
    
    # Calculate tick spacing
    tick_spacing = 10 if fee_tier == 500 else 60 if fee_tier == 3000 else 200
    
    # Calculate tick bounds
    tick_lower = math.floor(math.log(current_price * (1 - tick_range / 10000)) / math.log(1.0001))
    tick_upper = math.floor(math.log(current_price * (1 + tick_range / 10000)) / math.log(1.0001))
    
    # Align with tick spacing
    aligned_tick_lower = math.floor(tick_lower / tick_spacing) * tick_spacing
    aligned_tick_upper = math.floor(tick_upper / tick_spacing) * tick_spacing
    
    # Ensure proper ordering
    final_tick_lower = min(aligned_tick_lower, aligned_tick_upper)
    final_tick_upper = max(aligned_tick_lower, aligned_tick_upper)
    
    print("Tick Calculation Test:")
    print(f"Current Price: {current_price}")
    print(f"Tick Range: {tick_range} bips")
    print(f"Fee Tier: {fee_tier} bips")
    print(f"Tick Spacing: {tick_spacing}")
    print(f"Raw Tick Lower: {tick_lower}")
    print(f"Raw Tick Upper: {tick_upper}")
    print(f"Aligned Tick Lower: {aligned_tick_lower}")
    print(f"Aligned Tick Upper: {aligned_tick_upper}")
    print(f"Final Tick Lower: {final_tick_lower}")
    print(f"Final Tick Upper: {final_tick_upper}")
    print()
    
    # Test small amounts
    amount0_usdc = 0.05  # 5 cents in USDC
    amount1_weth = amount0_usdc / current_price  # Equivalent WETH
    
    print("Amount Calculation Test:")
    print(f"Amount0 (USDC): {amount0_usdc}")
    print(f"Amount1 (WETH): {amount1_weth}")
    print(f"Amount0 in wei: {int(amount0_usdc * 10**6)}")
    print(f"Amount1 in wei: {int(amount1_weth * 10**18)}")
    print()
    
    # Verify token ordering
    usdc_address = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    weth_address = "0x4200000000000000000000000000000000000006"
    
    print("Token Ordering Test:")
    print(f"USDC Address: {usdc_address}")
    print(f"WETH Address: {weth_address}")
    print(f"USDC < WETH: {usdc_address.lower() < weth_address.lower()}")
    print("Token0 should be USDC, Token1 should be WETH")
    print()
    
    # Test pool addresses
    pool_addresses = [
        "0x72ab388e2e2f6facef59e3c3fa2c4e29011c2d38",  # WETH-USDC 0.05%
        "0xd0b53D9277642d899DF5C87A3966A349A798F224",  # WETH-USDC 0.3%
        "0xdbc6998296caa1652a810dc8d3baf4a8294330f1",  # WETH-USDC 0.05%
        "0xb2cc224c1c9fee385f8ad6a55b4d94e92359dc59",  # WETH-USDC 0.3%
    ]
    
    print("Pool Addresses:")
    for i, addr in enumerate(pool_addresses, 1):
        print(f"{i}. {addr}")
    print()
    
    print("Expected Transaction Parameters:")
    print(f"Token0: {usdc_address} (USDC)")
    print(f"Token1: {weth_address} (WETH)")
    print(f"Fee: {fee_tier}")
    print(f"TickLower: {final_tick_lower}")
    print(f"TickUpper: {final_tick_upper}")
    print(f"Amount0Desired: {int(amount0_usdc * 10**6)}")
    print(f"Amount1Desired: {int(amount1_weth * 10**18)}")
    print(f"Gas Limit: 500000 (reasonable for Base)")

if __name__ == "__main__":
    test_tick_calculation()
