#!/usr/bin/env python3
"""
Wrap ETH to WETH on Base Sepolia.
WETH is required for Uniswap V3 pools.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web3 import Web3
from src.dex.web3_client import get_web3_client
from src.utils.config import get_config
from src.utils.logger import log as logger


# WETH contract on Base Sepolia
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"

# Minimal WETH ABI (just deposit and balanceOf)
WETH_ABI = [
    {
        "constant": False,
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "payable": True,
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]


def wrap_eth(eth_amount: float = 0.0005):
    """
    Wrap ETH to WETH.
    
    Args:
        eth_amount: Amount of ETH to wrap (default: 0.0005 = ~$2 worth)
    """
    logger.info("=" * 60)
    logger.info("WRAP ETH TO WETH ON BASE SEPOLIA")
    logger.info("=" * 60)
    
    # Get client
    web3_client = get_web3_client()
    w3 = web3_client.w3
    wallet = web3_client.address
    
    # Convert to wei
    eth_wei = w3.to_wei(eth_amount, 'ether')
    
    logger.info(f"\n📊 Wrap Details:")
    logger.info(f"  Amount: {eth_amount} ETH")
    logger.info(f"  Wallet: {wallet}")
    logger.info(f"  WETH Contract: {WETH_ADDRESS}")
    
    # Check current balances
    eth_balance = w3.eth.get_balance(wallet)
    weth_contract = w3.eth.contract(
        address=Web3.to_checksum_address(WETH_ADDRESS),
        abi=WETH_ABI
    )
    weth_balance_before = weth_contract.functions.balanceOf(wallet).call()
    
    logger.info(f"\n💰 Current Balances:")
    logger.info(f"  ETH: {w3.from_wei(eth_balance, 'ether'):.6f} ETH")
    logger.info(f"  WETH: {w3.from_wei(weth_balance_before, 'ether'):.6f} WETH")
    
    if eth_balance < eth_wei:
        logger.error(f"\n❌ Insufficient ETH!")
        logger.error(f"  Need: {eth_amount} ETH")
        logger.error(f"  Have: {w3.from_wei(eth_balance, 'ether')} ETH")
        return
    
    logger.info(f"\n🔄 Wrapping ETH...")
    
    try:
        # Build deposit transaction
        tx = weth_contract.functions.deposit().build_transaction({
            'from': wallet,
            'value': eth_wei,
            'nonce': w3.eth.get_transaction_count(wallet),
            'gas': 50000,
            'gasPrice': w3.eth.gas_price
        })
        
        logger.info(f"  Gas Price: {w3.from_wei(tx['gasPrice'], 'gwei')} gwei")
        logger.info(f"  Gas Limit: {tx['gas']}")
        
        # Sign and send
        signed_tx = w3.eth.account.sign_transaction(tx, web3_client.private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"\n📝 Transaction Sent!")
        logger.info(f"  Hash: {tx_hash.hex()}")
        logger.info(f"  Explorer: https://sepolia.basescan.org/tx/{tx_hash.hex()}")
        
        # Wait for confirmation
        logger.info(f"\n⏳ Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt['status'] == 1:
            logger.info(f"\n✅ WRAPPING SUCCESSFUL!")
            
            # Check new balances
            eth_balance_after = w3.eth.get_balance(wallet)
            weth_balance_after = weth_contract.functions.balanceOf(wallet).call()
            
            logger.info(f"\n💵 New Balances:")
            logger.info(f"  ETH: {w3.from_wei(eth_balance_after, 'ether'):.6f} ETH")
            logger.info(f"  WETH: {w3.from_wei(weth_balance_after, 'ether'):.6f} WETH")
            logger.info(f"  WETH Gained: +{w3.from_wei(weth_balance_after - weth_balance_before, 'ether'):.6f} WETH")
            
            logger.info(f"\n🎉 You now have WETH for LP positions!")
            logger.info(f"\nNext steps:")
            logger.info(f"  1. Get USDC: python scripts/get_testnet_tokens.py --amount 0.01")
            logger.info(f"  2. Create LP: python scripts/test_create_position.py --capital 10")
            
        else:
            logger.error(f"\n❌ WRAPPING FAILED!")
            logger.error(f"  Transaction reverted")
            
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Wrap ETH to WETH on Base Sepolia')
    parser.add_argument('--amount', type=float, default=0.0001,
                      help='Amount of ETH to wrap (default: 0.0001 = ~$0.40)')
    
    args = parser.parse_args()
    
    wrap_eth(args.amount)
