#!/usr/bin/env python3
"""
Simple working swap using Uniswap V3 SwapRouter.
This version focuses on actually working rather than being fancy.
"""
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web3 import Web3
from src.dex.web3_client import get_web3_client
from src.dex.abis import ERC20_ABI
from src.utils.config import get_config
from src.utils.logger import log as logger


# Minimal SwapRouter ABI - just what we need
SWAP_ROUTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"}
                ],
                "internalType": "struct ISwapRouter.ExactInputSingleParams",
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    }
]


def simple_swap(amount_weth: float = 0.00005):
    """
    Dead simple WETH → USDC swap.
    No fancy features, just make it work.
    """
    logger.info("=" * 80)
    logger.info("SIMPLE WETH → USDC SWAP")
    logger.info("=" * 80)
    
    # Setup
    web3_client = get_web3_client()
    w3 = web3_client.w3
    config = get_config()
    wallet = web3_client.address
    
    # Addresses
    WETH = Web3.to_checksum_address("0x4200000000000000000000000000000000000006")
    USDC = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
    router_address = Web3.to_checksum_address(config.get('uniswap.router_address'))
    
    # Convert amount
    amount_in = int(amount_weth * 1e18)  # WETH has 18 decimals
    
    logger.info(f"\n📊 Swap Setup:")
    logger.info(f"  Amount: {amount_weth} WETH")
    logger.info(f"  Router: {router_address}")
    logger.info(f"  Wallet: {wallet}")
    
    # Check WETH balance
    weth = w3.eth.contract(address=WETH, abi=ERC20_ABI)
    weth_balance = weth.functions.balanceOf(wallet).call()
    
    logger.info(f"\n💰 WETH Balance: {weth_balance / 1e18}")
    
    if weth_balance < amount_in:
        logger.error(f"❌ Insufficient WETH! Have {weth_balance / 1e18}, need {amount_weth}")
        return False
    
    # Step 1: Approve
    logger.info(f"\n🔄 Step 1: Checking approval...")
    allowance = weth.functions.allowance(wallet, router_address).call()
    
    if allowance < amount_in:
        logger.info(f"  Approving WETH...")
        approve_tx = weth.functions.approve(router_address, amount_in * 10).build_transaction({
            'from': wallet,
            'nonce': w3.eth.get_transaction_count(wallet),
            'gas': 100000,
            'gasPrice': w3.eth.gas_price
        })
        
        signed = w3.eth.account.sign_transaction(approve_tx, web3_client.private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        logger.info(f"  Approval tx: {tx_hash.hex()}")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt['status'] != 1:
            logger.error(f"❌ Approval failed!")
            return False
        
        logger.info(f"  ✅ Approved!")
        time.sleep(2)  # Wait for it to settle
    else:
        logger.info(f"  ✅ Already approved (allowance: {allowance})")
    
    # Step 2: Swap
    logger.info(f"\n🔄 Step 2: Executing swap...")
    
    # Get router
    router = w3.eth.contract(address=router_address, abi=SWAP_ROUTER_ABI)
    
    # Swap params - AS A TUPLE, NOT DICT!
    deadline = int(time.time()) + 600  # 10 minutes
    params = (
        WETH,                 # tokenIn
        USDC,                 # tokenOut
        500,                  # fee (0.05%)
        wallet,               # recipient
        amount_in,            # amountIn
        0,                    # amountOutMinimum (accept any amount for now)
        0                     # sqrtPriceLimitX96 (no price limit)
    )
    
    try:
        # Build transaction
        nonce = w3.eth.get_transaction_count(wallet, 'pending')
        
        swap_tx = router.functions.exactInputSingle(params).build_transaction({
            'from': wallet,
            'nonce': nonce,
            'gas': 300000,
            'gasPrice': w3.eth.gas_price,
            'value': 0  # Not sending ETH, using WETH
        })
        
        logger.info(f"  Gas: {swap_tx['gas']}")
        logger.info(f"  Gas Price: {w3.from_wei(swap_tx['gasPrice'], 'gwei')} gwei")
        
        # Sign and send
        signed = w3.eth.account.sign_transaction(swap_tx, web3_client.private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        
        logger.info(f"\n📝 Transaction sent!")
        logger.info(f"  Hash: {tx_hash.hex()}")
        logger.info(f"  Explorer: https://basescan.org/tx/{tx_hash.hex()}")
        
        # Wait
        logger.info(f"\n⏳ Waiting...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt['status'] == 1:
            logger.info(f"\n✅ SWAP SUCCESS!")
            
            # Check new balances
            usdc = w3.eth.contract(address=USDC, abi=ERC20_ABI)
            usdc_balance = usdc.functions.balanceOf(wallet).call()
            weth_balance_new = weth.functions.balanceOf(wallet).call()
            
            logger.info(f"\n💰 New Balances:")
            logger.info(f"  WETH: {weth_balance_new / 1e18}")
            logger.info(f"  USDC: {usdc_balance / 1e6}")  # USDC has 6 decimals
            
            return True
        else:
            logger.error(f"\n❌ SWAP FAILED - Transaction reverted")
            logger.error(f"  Check: https://basescan.org/tx/{tx_hash.hex()}")
            return False
            
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple WETH to USDC swap')
    parser.add_argument('--amount', type=float, default=0.00005,
                       help='Amount of WETH to swap (default: 0.00005)')
    
    args = parser.parse_args()
    
    success = simple_swap(args.amount)
    sys.exit(0 if success else 1)
