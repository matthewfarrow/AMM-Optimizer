#!/usr/bin/env python3
"""
Debug script to identify transaction issues
"""

import requests
import json
import time

def test_rpc_connection():
    """Test RPC connection and rate limiting"""
    print("🔍 Testing RPC Connection...")
    
    rpc_url = "https://mainnet.base.org"
    
    # Test basic RPC call
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 1
    }
    
    try:
        response = requests.post(rpc_url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            block_number = int(data['result'], 16)
            print(f"✅ RPC connection successful - Block: {block_number}")
            return True
        else:
            print(f"❌ RPC error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ RPC connection failed: {e}")
        return False

def test_rate_limiting():
    """Test rate limiting by making multiple requests"""
    print("\n🚦 Testing Rate Limiting...")
    
    rpc_url = "https://mainnet.base.org"
    
    for i in range(5):
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": i + 1
        }
        
        try:
            response = requests.post(rpc_url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"✅ Request {i+1}: Success")
            else:
                print(f"❌ Request {i+1}: Failed - {response.status_code}")
                if "rate limit" in response.text.lower():
                    print("🚨 RATE LIMITING DETECTED!")
                    return True
        except Exception as e:
            print(f"❌ Request {i+1}: Error - {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    return False

def check_pool_addresses():
    """Check if pool addresses are valid"""
    print("\n🏊 Checking Pool Addresses...")
    
    pools = [
        {
            "name": "WETH-USDC 0.05%",
            "address": "0x72ab388e2e2f6facef59e3c3fa2c4e29011c2d38",
            "expected_tokens": ["WETH", "USDC"]
        },
        {
            "name": "WETH-USDC 0.3%", 
            "address": "0xd0b53D9277642d899DF5C87A3966A349A798F224",
            "expected_tokens": ["WETH", "USDC"]
        }
    ]
    
    rpc_url = "https://mainnet.base.org"
    
    for pool in pools:
        print(f"\nChecking {pool['name']}...")
        
        # Check if contract exists
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getCode",
            "params": [pool["address"], "latest"],
            "id": 1
        }
        
        try:
            response = requests.post(rpc_url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['result'] == '0x':
                    print(f"❌ Pool {pool['address']} does not exist (no code)")
                else:
                    print(f"✅ Pool {pool['address']} exists")
            else:
                print(f"❌ Failed to check pool: {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking pool: {e}")

def check_contract_addresses():
    """Check Uniswap V3 contract addresses"""
    print("\n📋 Checking Uniswap V3 Contract Addresses...")
    
    contracts = {
        "NonfungiblePositionManager": "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1",
        "Factory": "0x33128a8fC17869897dcE68Ed026d694621f6FDfD",
        "Router": "0x2626664c2603336E57B271c5C0b26F421741e481"
    }
    
    rpc_url = "https://mainnet.base.org"
    
    for name, address in contracts.items():
        print(f"\nChecking {name}...")
        
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getCode",
            "params": [address, "latest"],
            "id": 1
        }
        
        try:
            response = requests.post(rpc_url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['result'] == '0x':
                    print(f"❌ {name} {address} does not exist")
                else:
                    print(f"✅ {name} {address} exists")
            else:
                print(f"❌ Failed to check {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")

def main():
    print("🔧 AMM Optimizer Transaction Debug Tool")
    print("=" * 50)
    
    # Test RPC connection
    if not test_rpc_connection():
        print("\n❌ Cannot proceed - RPC connection failed")
        return
    
    # Test rate limiting
    if test_rate_limiting():
        print("\n🚨 RATE LIMITING DETECTED!")
        print("💡 Solutions:")
        print("   - Wait 1-2 minutes before trying again")
        print("   - Use a different RPC provider")
        print("   - Add delays between requests")
    
    # Check pool addresses
    check_pool_addresses()
    
    # Check contract addresses
    check_contract_addresses()
    
    print("\n" + "=" * 50)
    print("🎯 Debug Summary:")
    print("1. If rate limiting detected, wait before retrying")
    print("2. If pools don't exist, check addresses")
    print("3. If contracts don't exist, update addresses")
    print("4. Try with smaller amounts first")

if __name__ == "__main__":
    main()
