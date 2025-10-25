#!/usr/bin/env python3
"""
Debug Uniswap V3 Mint Parameters
Analyzes the mint parameters to identify potential issues
"""

import json

def analyze_mint_params():
    """
    Analyze the mint parameters from MetaMask
    """
    print("🔍 Analyzing Uniswap V3 Mint Parameters")
    print("=" * 50)
    
    # Parameters from MetaMask
    params = {
        "token0": "WETH",
        "token1": "USDC", 
        "fee": 500,
        "tickLower": 82290,
        "tickUpper": 83290,
        "amount0Desired": 63000000000000,  # 0.000063 WETH
        "amount1Desired": 334594,          # 0.334594 USDC
        "amount0Min": 62685000000000,      # 0.000062685 WETH
        "amount1Min": 332921,              # 0.332921 USDC
        "recipient": "0x55Ed466ea47249C1687d6aa7ab031CEA6c201F0A",
        "deadline": 1761341309
    }
    
    print("📋 Transaction Parameters:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    print("\n🔍 Analysis:")
    
    # Check tick range
    tick_range = params["tickUpper"] - params["tickLower"]
    print(f"  Tick Range: {tick_range} ticks")
    
    if tick_range < 100:
        print("  ⚠️  WARNING: Tick range is very small (< 100 ticks)")
    
    # Check amounts
    amount0_wei = params["amount0Desired"]
    amount1_wei = params["amount1Desired"]
    
    # Convert to human readable
    amount0_eth = amount0_wei / 1e18
    amount1_usdc = amount1_wei / 1e6
    
    print(f"  Amount 0 (WETH): {amount0_eth:.6f} WETH")
    print(f"  Amount 1 (USDC): {amount1_usdc:.6f} USDC")
    
    # Check if amounts are too small
    if amount0_eth < 0.001:
        print("  ⚠️  WARNING: WETH amount is very small (< 0.001)")
    
    if amount1_usdc < 1:
        print("  ⚠️  WARNING: USDC amount is very small (< 1)")
    
    # Check deadline
    import time
    current_time = int(time.time())
    deadline = params["deadline"]
    
    if deadline < current_time:
        print("  ❌ ERROR: Deadline has already passed!")
    else:
        time_left = deadline - current_time
        print(f"  ✅ Deadline: {time_left} seconds remaining")
    
    # Check slippage
    slippage0 = (params["amount0Desired"] - params["amount0Min"]) / params["amount0Desired"]
    slippage1 = (params["amount1Desired"] - params["amount1Min"]) / params["amount1Desired"]
    
    print(f"  Slippage 0: {slippage0:.4%}")
    print(f"  Slippage 1: {slippage1:.4%}")
    
    if slippage0 > 0.05 or slippage1 > 0.05:
        print("  ⚠️  WARNING: High slippage tolerance (> 5%)")
    
    print("\n🎯 Potential Issues:")
    print("  1. Very small amounts might cause precision issues")
    print("  2. Small tick range might not provide enough liquidity")
    print("  3. Check if the pool has sufficient liquidity")
    print("  4. Verify token addresses are correct for Base network")

if __name__ == "__main__":
    analyze_mint_params()

