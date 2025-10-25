#!/usr/bin/env python3
"""
Tenderly Transaction Analysis Script
Analyzes failed transactions using Tenderly API
"""

import requests
import json
import sys
from typing import Dict, Any

# Tenderly API configuration
TENDERLY_ACCESS_KEY = "dY0KFj31QTgc0RNlXvg9sw8FWUvd09VB"
TENDERLY_BASE_URL = "https://api.tenderly.co/api/v1"

def analyze_transaction(tx_hash: str, network_id: str = "8453") -> Dict[str, Any]:
    """
    Analyze a transaction using Tenderly API
    """
    headers = {
        "X-Access-Key": TENDERLY_ACCESS_KEY,
        "Content-Type": "application/json"
    }
    
    # Get transaction details
    tx_url = f"{TENDERLY_BASE_URL}/account/me/project/amm-optimizer/transaction/{tx_hash}"
    
    try:
        response = requests.get(tx_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching transaction: {response.status_code}")
            print(f"Response: {response.text}")
            return {}
    except Exception as e:
        print(f"Error: {e}")
        return {}

def simulate_transaction(tx_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate a transaction using Tenderly
    """
    headers = {
        "X-Access-Key": TENDERLY_ACCESS_KEY,
        "Content-Type": "application/json"
    }
    
    simulation_url = f"{TENDERLY_BASE_URL}/account/me/project/amm-optimizer/simulate"
    
    try:
        response = requests.post(simulation_url, headers=headers, json=tx_data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error simulating transaction: {response.status_code}")
            print(f"Response: {response.text}")
            return {}
    except Exception as e:
        print(f"Error: {e}")
        return {}

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_tenderly.py <transaction_hash>")
        print("Example: python analyze_tenderly.py 0x49924b0c23b5f75e6f91eb25dfe18b18654133f20cf7e34ed837ac8eaf2c75fd")
        sys.exit(1)
    
    tx_hash = sys.argv[1]
    print(f"🔍 Analyzing transaction: {tx_hash}")
    
    # Analyze the transaction
    result = analyze_transaction(tx_hash)
    
    if result:
        print("✅ Transaction analysis complete!")
        print(json.dumps(result, indent=2))
    else:
        print("❌ Failed to analyze transaction")

if __name__ == "__main__":
    main()

