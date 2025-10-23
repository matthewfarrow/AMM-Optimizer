#!/usr/bin/env python3
"""
Test the app flow without private key
"""

import requests
import json
import time

def test_backend_health():
    """Test if backend is running"""
    print("🏥 Testing Backend Health...")
    
    try:
        response = requests.get("http://localhost:8000/api/pools/?limit=4", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is running - {len(data)} pools available")
            return data
        else:
            print(f"❌ Backend error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return None

def test_pool_data(pools):
    """Test pool data structure"""
    print("\n📊 Testing Pool Data...")
    
    if not pools:
        print("❌ No pools to test")
        return
    
    for pool in pools:
        print(f"\nPool: {pool['name']}")
        print(f"  Address: {pool['address']}")
        print(f"  Fee Tier: {pool['fee_tier']} ({pool['fee_tier']/10000}%)")
        print(f"  TVL: ${pool['tvl']:,.2f}")
        print(f"  APR: {pool['apr']:.2f}%")
        print(f"  Volume 1D: ${pool['volume_1d']:,.2f}")
        
        # Check if address is valid
        if len(pool['address']) == 42 and pool['address'].startswith('0x'):
            print("  ✅ Address format valid")
        else:
            print("  ❌ Address format invalid")

def test_analytics_endpoint():
    """Test analytics endpoint"""
    print("\n📈 Testing Analytics Endpoint...")
    
    # Use the first pool address
    pool_address = "0x72ab388e2e2f6facef59e3c3fa2c4e29011c2d38"
    
    try:
        response = requests.get(f"http://localhost:8000/api/analytics/{pool_address}/price-data?timeframe=1d", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics working - Current price: ${data.get('current_price', 'N/A')}")
        else:
            print(f"❌ Analytics error: {response.status_code}")
    except Exception as e:
        print(f"❌ Analytics failed: {e}")

def test_whitelist():
    """Test whitelist status"""
    print("\n🔐 Testing Whitelist...")
    
    test_address = "0x8a679aCf39c06682072C4a2A833eb437A0CC0bdb"
    
    try:
        response = requests.get(f"http://localhost:8000/api/whitelist/status/{test_address}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('whitelisted'):
                print(f"✅ Address {test_address} is whitelisted")
            else:
                print(f"❌ Address {test_address} is NOT whitelisted")
        else:
            print(f"❌ Whitelist check error: {response.status_code}")
    except Exception as e:
        print(f"❌ Whitelist check failed: {e}")

def main():
    print("🧪 AMM Optimizer App Flow Test")
    print("=" * 50)
    
    # Test backend health
    pools = test_backend_health()
    
    if pools:
        # Test pool data
        test_pool_data(pools)
        
        # Test analytics
        test_analytics_endpoint()
        
        # Test whitelist
        test_whitelist()
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("1. Backend should be running on port 8000")
    print("2. Frontend should be running on port 3000")
    print("3. All pools should have valid addresses")
    print("4. Analytics should return price data")
    print("5. Your address should be whitelisted")
    print("\n💡 Next Steps:")
    print("1. Open http://localhost:3000/app")
    print("2. Connect your wallet")
    print("3. Select a pool")
    print("4. Try creating a small position")
    print("5. If rate limited, wait 1-2 minutes and retry")

if __name__ == "__main__":
    main()
