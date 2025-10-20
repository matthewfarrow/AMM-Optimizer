#!/usr/bin/env python3
"""
Get test USDC by swapping test ETH on Base Sepolia.
This prepares you for LP testing by getting both tokens.
"""
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web3 import Web3
from src.dex.web3_client import get_web3_client
from src.dex.uniswap import get_uniswap
from src.dex.abis import ROUTER_ABI, ERC20_ABI
from src.utils.config import get_config
from src.utils.logger import log as logger


def swap_eth_for_usdc(eth_amount: float = 0.005):
    """
    Swap test ETH for test USDC on Base Sepolia.
    
    Args:
        eth_amount: Amount of ETH to swap (default: 0.005 = ~$20 worth)
    """
    logger.info("=" * 60)
    logger.info("SWAP TEST ETH FOR TEST USDC")
    logger.info("=" * 60)
    
    # Get clients
    web3_client = get_web3_client()
    w3 = web3_client.w3
    config = get_config()
    
    # Contract addresses on Base Sepolia
    WETH = "0x4200000000000000000000000000000000000006"  # Wrapped ETH on Base
    USDC = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"  # USDC on Base Sepolia
    router_address = config.get('uniswap.router_address')
    
    wallet = web3_client.address
    
    # Convert ETH amount to wei
    eth_wei = w3.to_wei(eth_amount, 'ether')
    
    logger.info(f"\n📊 Swap Details:")
    logger.info(f"  From: {eth_amount} ETH")
    logger.info(f"  To: USDC (amount will vary by price)")
    logger.info(f"  Wallet: {wallet}")
    logger.info(f"  Router: {router_address}")
    
    # Get current balance
    eth_balance = w3.eth.get_balance(wallet)
    logger.info(f"\n💰 Current Balance:")
    logger.info(f"  ETH: {w3.from_wei(eth_balance, 'ether'):.4f} ETH")
    
    if eth_balance < eth_wei:
        logger.error(f"❌ Insufficient ETH! Need {eth_amount}, have {w3.from_wei(eth_balance, 'ether')}")
        return
    
    # Build swap parameters
    deadline = int(time.time()) + 1200  # 20 minutes
    
    swap_params = {
        'tokenIn': WETH,
        'tokenOut': USDC,
        'fee': 3000,  # 0.3% fee tier
        'recipient': wallet,
        'deadline': deadline,
        'amountIn': eth_wei,
        'amountOutMinimum': 0,  # Accept any amount (testnet, don't care about slippage)
        'sqrtPriceLimitX96': 0  # No price limit
    }
    
    # Get router contract
    router = w3.eth.contract(
        address=Web3.to_checksum_address(router_address),
        abi=ROUTER_ABI
    )
    
    logger.info(f"\n🔄 Step 1: Wrapping ETH to WETH first...")
    
    # First, wrap ETH to WETH (Uniswap V3 router needs WETH, not ETH)
    weth_contract = w3.eth.contract(
        address=Web3.to_checksum_address(WETH),
        abi=[{
            "constant": False,
            "inputs": [],
            "name": "deposit",
            "outputs": [],
            "payable": True,
            "stateMutability": "payable",
            "type": "function"
        }]
    )
    
    try:
        # Wrap ETH to WETH
        wrap_tx = weth_contract.functions.deposit().build_transaction({
            'from': wallet,
            'value': eth_wei,
            'nonce': w3.eth.get_transaction_count(wallet),
            'gas': 50000,
            'gasPrice': w3.eth.gas_price
        })
        
        signed_wrap = w3.eth.account.sign_transaction(wrap_tx, web3_client.private_key)
        wrap_hash = w3.eth.send_raw_transaction(signed_wrap.rawTransaction)
        logger.info(f"  Wrapping tx: {wrap_hash.hex()}")
        wrap_receipt = w3.eth.wait_for_transaction_receipt(wrap_hash)
        logger.info(f"  ✅ Wrapped {eth_amount} ETH to WETH")
        
    except Exception as e:
        logger.error(f"❌ Failed to wrap ETH: {e}")
        return
    
    # Small delay to ensure nonce updates
    time.sleep(1)
    
    logger.info(f"\n🔄 Step 2: Approving WETH for router...")
    
    # Approve WETH for router
    weth_contract_full = w3.eth.contract(
        address=Web3.to_checksum_address(WETH),
        abi=ERC20_ABI
    )
    
    # Get fresh nonce - wait for previous tx to be processed
    for _ in range(5):
        current_nonce = w3.eth.get_transaction_count(wallet, 'pending')
        if current_nonce >= w3.eth.get_transaction_count(wallet):
            break
        time.sleep(0.5)
    
    try:
        approve_tx = weth_contract_full.functions.approve(router_address, eth_wei).build_transaction({
            'from': wallet,
            'nonce': current_nonce,
            'gas': 100000,
            'gasPrice': w3.eth.gas_price
        })
        
        signed_approve = w3.eth.account.sign_transaction(approve_tx, web3_client.private_key)
        approve_hash = w3.eth.send_raw_transaction(signed_approve.rawTransaction)
        logger.info(f"  Approval tx: {approve_hash.hex()}")
        approve_receipt = w3.eth.wait_for_transaction_receipt(approve_hash)
        logger.info(f"  ✅ Approved WETH for router")
        
    except Exception as e:
        logger.error(f"❌ Failed to approve WETH: {e}")
        return
    
    # Small delay
    time.sleep(1)
    
    logger.info(f"\n🔄 Step 3: Swapping WETH for USDC...")
    
    # Get fresh nonce - wait for previous tx
    for _ in range(5):
        current_nonce = w3.eth.get_transaction_count(wallet, 'pending')
        if current_nonce >= w3.eth.get_transaction_count(wallet):
            break
        time.sleep(0.5)
    
    try:
        # Now swap WETH for USDC (no ETH value needed since we're using WETH)
        tx = router.functions.exactInputSingle(swap_params).build_transaction({
            'from': wallet,
            'nonce': current_nonce,
            'gas': 300000,
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
            logger.info(f"\n✅ SWAP SUCCESSFUL!")
            
            # Check new USDC balance
            usdc_contract = w3.eth.contract(
                address=Web3.to_checksum_address(USDC),
                abi=ERC20_ABI
            )
            usdc_balance = usdc_contract.functions.balanceOf(wallet).call()
            usdc_decimals = usdc_contract.functions.decimals().call()
            usdc_amount = usdc_balance / (10 ** usdc_decimals)
            
            logger.info(f"\n💵 New Balances:")
            new_eth_balance = w3.eth.get_balance(wallet)
            logger.info(f"  ETH: {w3.from_wei(new_eth_balance, 'ether'):.4f} ETH")
            logger.info(f"  USDC: {usdc_amount:.2f} USDC")
            
            logger.info(f"\n🎉 You now have both tokens for LP testing!")
            logger.info(f"\nNext step: Create LP position with:")
            logger.info(f"  python scripts/run_optimizer.py --pool WETH-USDC --capital 10 --once")
            
        else:
            logger.error(f"\n❌ SWAP FAILED!")
            logger.error(f"  Transaction was reverted")
            
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Get test USDC by swapping test ETH')
    parser.add_argument('--amount', type=float, default=0.005,
                      help='Amount of ETH to swap (default: 0.005 = ~$20)')
    
    args = parser.parse_args()
    
    swap_eth_for_usdc(args.amount)
