#!/usr/bin/env python3
"""
Test script to verify transaction parameters with larger amounts
"""

import math

def test_larger_amounts():
    """Test with larger amounts to avoid dust amounts"""
    
    # Test parameters with larger amounts
    current_price = 3800  # WETH price in USDC
    tick_range = 100  # 1% range
    fee_tier = 500  # 0.05% fee
    
    # Use larger amounts to avoid dust
    amount0_usdc = 1.0  # $1 in USDC
    amount1_weth = amount0_usdc / current_price  # Equivalent WETH
    
    print("Larger Amount Test:")
    print(f"Amount0 (USDC): {amount0_usdc}")
    print(f"Amount1 (WETH): {amount1_weth}")
    print(f"Amount0 in wei: {int(amount0_usdc * 10**6)}")
    print(f"Amount1 in wei: {int(amount1_weth * 10**18)}")
    print()
    
    # Test with even larger amounts
    amount0_usdc_large = 10.0  # $10 in USDC
    amount1_weth_large = amount0_usdc_large / current_price  # Equivalent WETH
    
    print("Even Larger Amount Test:")
    print(f"Amount0 (USDC): {amount0_usdc_large}")
    print(f"Amount1 (WETH): {amount1_weth_large}")
    print(f"Amount0 in wei: {int(amount0_usdc_large * 10**6)}")
    print(f"Amount1 in wei: {int(amount1_weth_large * 10**18)}")
    print()
    
    # Test minimum amounts for Uniswap V3
    print("Minimum Amount Recommendations:")
    print("- Use at least $1-5 for testing to avoid dust amounts")
    print("- Ensure amounts are above minimum liquidity requirements")
    print("- Check that tick range is reasonable (not too narrow)")

if __name__ == "__main__":
    test_larger_amounts()
