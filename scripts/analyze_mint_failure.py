#!/usr/bin/env python3
"""
Analyze Uniswap V3 Mint Transaction Failure
Investigates why the mint transaction is failing
"""

def analyze_mint_failure():
    """
    Analyze the mint parameters that are failing
    """
    print("🔍 Analyzing Uniswap V3 Mint Transaction Failure")
    print("=" * 60)
    
    # Parameters from MetaMask that are failing
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
    
    print("📋 Failing Transaction Parameters:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    print("\n🔍 Potential Issues Analysis:")
    
    # 1. Check tick range
    tick_range = params["tickUpper"] - params["tickLower"]
    print(f"1. Tick Range: {tick_range} ticks")
    
    if tick_range < 100:
        print("   ⚠️  WARNING: Tick range is very small (< 100 ticks)")
    elif tick_range > 10000:
        print("   ⚠️  WARNING: Tick range is very large (> 10000 ticks)")
    else:
        print("   ✅ Tick range looks reasonable")
    
    # 2. Check amounts
    amount0_wei = params["amount0Desired"]
    amount1_wei = params["amount1Desired"]
    
    # Convert to human readable
    amount0_eth = amount0_wei / 1e18
    amount1_usdc = amount1_wei / 1e6
    
    print(f"2. Amounts:")
    print(f"   WETH: {amount0_eth:.6f} WETH")
    print(f"   USDC: {amount1_usdc:.6f} USDC")
    
    # 3. Check if amounts are too small for precision
    if amount0_wei < 1000:  # Less than 1000 wei
        print("   ⚠️  WARNING: WETH amount might be too small for precision")
    if amount1_wei < 1000:  # Less than 1000 units
        print("   ⚠️  WARNING: USDC amount might be too small for precision")
    
    # 4. Check slippage
    slippage0 = (params["amount0Desired"] - params["amount0Min"]) / params["amount0Desired"]
    slippage1 = (params["amount1Desired"] - params["amount1Min"]) / params["amount1Desired"]
    
    print(f"3. Slippage:")
    print(f"   WETH: {slippage0:.4%}")
    print(f"   USDC: {slippage1:.4%}")
    
    if slippage0 > 0.1 or slippage1 > 0.1:
        print("   ⚠️  WARNING: High slippage tolerance (> 10%)")
    
    # 5. Check deadline
    import time
    current_time = int(time.time())
    deadline = params["deadline"]
    
    if deadline < current_time:
        print("4. Deadline: ❌ ERROR: Deadline has already passed!")
    else:
        time_left = deadline - current_time
        print(f"4. Deadline: ✅ {time_left} seconds remaining")
    
    # 6. Check if the position is in range
    # For WETH/USDC, current price is around 3940
    # Tick 82290 corresponds to price: 1.0001^82290 ≈ 3940
    current_tick = 82795  # From console logs
    tick_lower = params["tickLower"]
    tick_upper = params["tickUpper"]
    
    print(f"5. Position Range:")
    print(f"   Current Tick: {current_tick}")
    print(f"   Position Range: {tick_lower} to {tick_upper}")
    
    if current_tick < tick_lower or current_tick > tick_upper:
        print("   ❌ ERROR: Current price is OUTSIDE the position range!")
        print("   This means the position would be inactive (no liquidity)")
    else:
        print("   ✅ Current price is within the position range")
    
    # 7. Check if amounts are proportional to the range
    # In Uniswap V3, you need to provide both tokens if the current price is in range
    print(f"6. Token Proportions:")
    if current_tick >= tick_lower and current_tick <= tick_upper:
        print("   ✅ Position is in range - both tokens needed")
        print("   This is correct for the current price")
    else:
        print("   ⚠️  Position is out of range - only one token needed")
    
    print("\n🎯 Most Likely Issues:")
    print("1. Position might be out of range (current price outside tick bounds)")
    print("2. Amounts might be too small for the pool's precision")
    print("3. Pool might not have sufficient liquidity")
    print("4. Token addresses might be incorrect for Base network")
    
    print("\n🔧 Suggested Fixes:")
    print("1. Try a wider tick range (e.g., ±1000 ticks instead of ±500)")
    print("2. Increase amounts slightly (e.g., 0.001 WETH, 1 USDC)")
    print("3. Verify token addresses are correct for Base network")
    print("4. Check if the pool has sufficient liquidity")

if __name__ == "__main__":
    analyze_mint_failure()

