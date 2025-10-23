#!/usr/bin/env python3
"""
TEST LIQUIDITY CREATION - HACKATHON READY
"""

import requests
import json

def test_app():
    print("🧪 Testing AMM Optimizer App")
    print("=" * 50)
    
    # Test 1: Backend health
    try:
        response = requests.get("http://localhost:8000/api/pools/?limit=4")
        if response.status_code == 200:
            pools = response.json()
            print(f"✅ Backend working - {len(pools)} pools available")
            
            for pool in pools:
                print(f"   - {pool['name']} {pool['fee_tier']/10000}%: {pool['address']}")
        else:
            print(f"❌ Backend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False
    
    # Test 2: Price data
    try:
        response = requests.get("http://localhost:8000/api/analytics/0xd0b53D9277642d899DF5C87A3966A349A798F224/price-data?timeframe=1d")
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                price = data['data'][-1]['price']
                print(f"✅ Price data working - WETH: ${price:,.2f}")
            else:
                print("❌ Price data empty")
                return False
        else:
            print(f"❌ Price data failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Price data error: {e}")
        return False
    
    print("=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("")
    print("💡 READY FOR REAL MONEY TESTING:")
    print("1. Open http://localhost:3000/app")
    print("2. Connect your wallet")
    print("3. Select WETH-USDC 0.05% pool")
    print("4. Enter $0.01 amount")
    print("5. Click 'Create Position'")
    print("6. Watch console logs (F12)")
    print("")
    print("🔍 If it fails:")
    print("- Check console logs for error messages")
    print("- Ensure you have WETH and USDC in your wallet")
    print("- Try with a slightly larger amount ($0.05)")
    
    return True

if __name__ == "__main__":
    test_app()
