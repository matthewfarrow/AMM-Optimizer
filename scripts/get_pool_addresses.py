#!/usr/bin/env python3
"""
Script to get real Uniswap V3 pool addresses from the factory on Base network
"""

import requests
import json

# Base network RPC URL
BASE_RPC_URL = "https://mainnet.base.org"

# Uniswap V3 Factory address on Base
FACTORY_ADDRESS = "0x33128a8fC17869897dcE68Ed026d694621f6FDfD"

# Token addresses on Base
WETH = "0x4200000000000000000000000000000000000006"
USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
DAI = "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb"

# Fee tiers in bips
FEE_500 = 500    # 0.05%
FEE_3000 = 3000  # 0.3%

def get_pool_address(token0, token1, fee):
    """Get pool address from Uniswap V3 Factory"""
    
    # Factory getPool function signature
    method_id = "0x1698ee82"  # getPool(address,address,uint24)
    
    # Encode parameters
    token0_encoded = token0[2:].lower().zfill(64)
    token1_encoded = token1[2:].lower().zfill(64)
    fee_encoded = hex(fee)[2:].zfill(8)
    
    data = method_id + token0_encoded + token1_encoded + fee_encoded
    
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [
            {
                "to": FACTORY_ADDRESS,
                "data": data
            },
            "latest"
        ],
        "id": 1
    }
    
    try:
        response = requests.post(BASE_RPC_URL, json=payload)
        result = response.json()
        
        if "result" in result:
            pool_address = "0x" + result["result"][-40:]  # Last 40 chars (20 bytes)
            return pool_address
        else:
            print(f"Error: {result}")
            return None
            
    except Exception as e:
        print(f"Error calling RPC: {e}")
        return None

def main():
    print("Getting Uniswap V3 pool addresses on Base network...")
    print()
    
    pools = [
        ("WETH-USDC", WETH, USDC, FEE_500),
        ("WETH-USDC", WETH, USDC, FEE_3000),
        ("WETH-DAI", WETH, DAI, FEE_500),
        ("WETH-DAI", WETH, DAI, FEE_3000),
    ]
    
    for name, token0, token1, fee in pools:
        pool_address = get_pool_address(token0, token1, fee)
        fee_percent = fee / 10000
        print(f"{name} ({fee_percent}%): {pool_address}")
    
    print()
    print("Note: If pool address is 0x0000000000000000000000000000000000000000, the pool doesn't exist yet.")

if __name__ == "__main__":
    main()
