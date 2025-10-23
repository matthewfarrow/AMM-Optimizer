#!/usr/bin/env python3
"""
SIMPLE TRANSACTION ANALYSIS
"""

import requests
from web3 import Web3

def analyze_tx():
    w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
    tx_hash = "0x501119459e5d68de6ef3d89ea1ebe2666397cedad4354e16a60184a063bdc026"
    
    try:
        tx = w3.eth.get_transaction(tx_hash)
        tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        print(f"Transaction: {tx_hash}")
        print(f"From: {tx['from']}")
        print(f"To: {tx['to']}")
        print(f"Gas Limit: {tx['gas']}")
        print(f"Gas Used: {tx_receipt['gasUsed']}")
        print(f"Status: {'Success' if tx_receipt['status'] == 1 else 'Failed'}")
        print(f"Input Data: {tx['input'][:100]}...")
        
        # Check if it's the right contract
        position_manager = "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1"
        if tx['to'].lower() == position_manager.lower():
            print("✅ Correct NonfungiblePositionManager address")
        else:
            print(f"❌ Wrong contract address. Expected: {position_manager}")
        
        # Check gas price
        gas_price_gwei = w3.from_wei(tx['gasPrice'], 'gwei')
        print(f"Gas Price: {gas_price_gwei} gwei")
        
        if gas_price_gwei < 0.01:
            print("✅ Gas price is reasonable")
        else:
            print("❌ Gas price might be too high")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_tx()
