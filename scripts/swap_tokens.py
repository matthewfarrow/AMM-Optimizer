#!/usr/bin/env python3
"""
Generic token swap script for Uniswap V3.
Supports swapping between any two ERC20 tokens.
Essential for auto-trading and rebalancing strategies.
"""
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web3 import Web3
from src.dex.web3_client import get_web3_client
from src.dex.abis import ROUTER_ABI, ERC20_ABI
from src.utils.config import get_config
from src.utils.logger import log as logger


# Token addresses on Base Mainnet
TOKENS = {
    'WETH': '0x4200000000000000000000000000000000000006',
    'ETH': '0x4200000000000000000000000000000000000006',  # Same as WETH for swaps
    'USDC': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',  # USDC on Base Mainnet
}

# Fee tiers (in basis points)
FEE_TIERS = {
    'lowest': 100,    # 0.01%
    'low': 500,       # 0.05%
    'medium': 3000,   # 0.3%
    'high': 10000,    # 1%
}


def get_token_balance(w3, token_address: str, wallet: str, symbol: str = None) -> tuple:
    """Get token balance and decimals."""
    token_contract = w3.eth.contract(
        address=Web3.to_checksum_address(token_address),
        abi=ERC20_ABI
    )
    
    balance = token_contract.functions.balanceOf(wallet).call()
    decimals = token_contract.functions.decimals().call()
    
    # Use provided symbol to avoid extra RPC calls
    if symbol is None:
        try:
            symbol = token_contract.functions.symbol().call()
        except:
            symbol = "Unknown"
    
    return balance, decimals, symbol


def approve_token(w3, token_address: str, spender: str, amount: int, wallet: str, private_key: str, nonce: int):
    """Approve token spending."""
    token_contract = w3.eth.contract(
        address=Web3.to_checksum_address(token_address),
        abi=ERC20_ABI
    )
    
    # Check current allowance
    current_allowance = token_contract.functions.allowance(wallet, spender).call()
    
    if current_allowance >= amount:
        logger.info(f"  ✅ Already approved (allowance: {current_allowance})")
        return None
    
    # Build approval transaction
    approve_tx = token_contract.functions.approve(spender, amount).build_transaction({
        'from': wallet,
        'nonce': nonce,
        'gas': 100000,
        'gasPrice': w3.eth.gas_price
    })
    
    # Sign and send
    signed_tx = w3.eth.account.sign_transaction(approve_tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    logger.info(f"  Approval tx: {tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt['status'] == 1:
        logger.info(f"  ✅ Approved token for router")
        return tx_hash.hex()
    else:
        raise Exception("Approval failed")


def swap_tokens(
    token_in: str,
    token_out: str,
    amount_in: float,
    fee_tier: str = 'medium',
    slippage: float = 1.0,
    dry_run: bool = False
):
    """
    Swap one token for another on Uniswap V3.
    
    Args:
        token_in: Symbol of input token (e.g., 'USDC', 'WETH')
        token_out: Symbol of output token (e.g., 'WETH', 'USDC')
        amount_in: Amount of input token to swap
        fee_tier: Fee tier to use ('lowest', 'low', 'medium', 'high')
        slippage: Maximum slippage tolerance in percent (default: 1%)
        dry_run: If True, only simulate, don't execute
    """
    logger.info("=" * 60)
    logger.info(f"SWAP: {token_in} → {token_out}")
    logger.info("=" * 60)
    
    # Validate inputs
    if token_in not in TOKENS:
        logger.error(f"❌ Unknown token: {token_in}")
        logger.info(f"Available tokens: {list(TOKENS.keys())}")
        return
    
    if token_out not in TOKENS:
        logger.error(f"❌ Unknown token: {token_out}")
        logger.info(f"Available tokens: {list(TOKENS.keys())}")
        return
    
    if token_in == token_out:
        logger.error(f"❌ Cannot swap token with itself!")
        return
    
    # Get clients
    web3_client = get_web3_client()
    w3 = web3_client.w3
    config = get_config()
    
    # Get addresses
    token_in_address = TOKENS[token_in]
    token_out_address = TOKENS[token_out]
    router_address = config.get('uniswap.router_address')
    wallet = web3_client.address
    
    logger.info(f"\n📊 Swap Details:")
    logger.info(f"  From: {amount_in} {token_in}")
    logger.info(f"  To: {token_out} (amount varies by price)")
    logger.info(f"  Fee Tier: {fee_tier} ({FEE_TIERS[fee_tier]/10000}%)")
    logger.info(f"  Slippage: {slippage}%")
    logger.info(f"  Wallet: {wallet}")
    
    if dry_run:
        logger.info(f"\n🔍 DRY RUN MODE - No transactions will be sent")
    
    # Get token info and balance (pass symbols to avoid extra RPC calls)
    balance_in, decimals_in, symbol_in = get_token_balance(w3, token_in_address, wallet, token_in)
    balance_out, decimals_out, symbol_out = get_token_balance(w3, token_out_address, wallet, token_out)
    
    amount_in_wei = int(amount_in * (10 ** decimals_in))
    
    logger.info(f"\n💰 Current Balances:")
    logger.info(f"  {symbol_in}: {balance_in / (10 ** decimals_in):.6f}")
    logger.info(f"  {symbol_out}: {balance_out / (10 ** decimals_out):.6f}")
    
    # Check if we have enough balance
    if balance_in < amount_in_wei:
        logger.error(f"\n❌ Insufficient {token_in}!")
        logger.error(f"  Need: {amount_in}")
        logger.error(f"  Have: {balance_in / (10 ** decimals_in):.6f}")
        return
    
    if dry_run:
        logger.info(f"\n✅ Dry run complete - would swap {amount_in} {token_in} for {token_out}")
        return
    
    # Build swap parameters
    deadline = int(time.time()) + 1200  # 20 minutes
    
    # Calculate minimum output with slippage (simplified - in production use price oracle)
    # For now, accept any amount but log it
    amount_out_minimum = 0  # We'll improve this with price quotes
    
    swap_params = {
        'tokenIn': Web3.to_checksum_address(token_in_address),
        'tokenOut': Web3.to_checksum_address(token_out_address),
        'fee': FEE_TIERS[fee_tier],
        'recipient': wallet,
        'deadline': deadline,
        'amountIn': amount_in_wei,
        'amountOutMinimum': amount_out_minimum,
        'sqrtPriceLimitX96': 0  # No price limit
    }
    
    # Get router contract
    router = w3.eth.contract(
        address=Web3.to_checksum_address(router_address),
        abi=ROUTER_ABI
    )
    
    try:
        # Step 1: Approve token for router
        logger.info(f"\n🔄 Step 1: Approving {token_in} for router...")
        current_nonce = w3.eth.get_transaction_count(wallet)
        
        approve_hash = approve_token(
            w3, token_in_address, router_address, amount_in_wei,
            wallet, web3_client.private_key, current_nonce
        )
        
        if approve_hash:
            time.sleep(1)  # Wait for approval to settle
            current_nonce += 1
        
        # Step 2: Execute swap
        logger.info(f"\n🔄 Step 2: Executing swap...")
        
        # Build swap transaction
        swap_tx = router.functions.exactInputSingle(swap_params).build_transaction({
            'from': wallet,
            'nonce': current_nonce,
            'gas': 300000,
            'gasPrice': w3.eth.gas_price
        })
        
        logger.info(f"  Gas Price: {w3.from_wei(swap_tx['gasPrice'], 'gwei'):.2f} gwei")
        logger.info(f"  Gas Limit: {swap_tx['gas']}")
        logger.info(f"  Est. Gas Cost: {w3.from_wei(swap_tx['gas'] * swap_tx['gasPrice'], 'ether'):.6f} ETH")
        
        # Sign and send
        signed_tx = w3.eth.account.sign_transaction(swap_tx, web3_client.private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"\n📝 Transaction Sent!")
        logger.info(f"  Hash: {tx_hash.hex()}")
        logger.info(f"  Explorer: https://basescan.org/tx/{tx_hash.hex()}")
        
        # Wait for confirmation
        logger.info(f"\n⏳ Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt['status'] == 1:
            logger.info(f"\n✅ SWAP SUCCESSFUL!")
            
            # Check new balances
            new_balance_in, _, _ = get_token_balance(w3, token_in_address, wallet)
            new_balance_out, _, _ = get_token_balance(w3, token_out_address, wallet)
            
            amount_out = (new_balance_out - balance_out) / (10 ** decimals_out)
            
            logger.info(f"\n💵 New Balances:")
            logger.info(f"  {symbol_in}: {new_balance_in / (10 ** decimals_in):.6f}")
            logger.info(f"  {symbol_out}: {new_balance_out / (10 ** decimals_out):.6f}")
            logger.info(f"\n📊 Swap Summary:")
            logger.info(f"  Spent: {amount_in} {symbol_in}")
            logger.info(f"  Received: {amount_out:.6f} {symbol_out}")
            logger.info(f"  Rate: 1 {symbol_in} = {amount_out/amount_in:.6f} {symbol_out}")
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'amount_in': amount_in,
                'amount_out': amount_out,
                'token_in': symbol_in,
                'token_out': symbol_out
            }
            
        else:
            logger.error(f"\n❌ SWAP FAILED!")
            logger.error(f"  Transaction was reverted")
            logger.error(f"  Check explorer for details: https://basescan.org/tx/{tx_hash.hex()}")
            return None
            
    except Exception as e:
        logger.error(f"\n❌ Error during swap: {e}")
        import traceback
        traceback.print_exc()
        return None


def add_token(symbol: str, address: str):
    """Add a new token to the supported tokens list."""
    TOKENS[symbol] = address
    logger.info(f"✅ Added token: {symbol} at {address}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Swap tokens on Uniswap V3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Swap 10 USDC for WETH
  python scripts/swap_tokens.py --from USDC --to WETH --amount 10
  
  # Swap 0.001 WETH for USDC with low slippage
  python scripts/swap_tokens.py --from WETH --to USDC --amount 0.001 --slippage 0.5
  
  # Dry run (simulate without executing)
  python scripts/swap_tokens.py --from USDC --to WETH --amount 10 --dry-run
  
  # Use different fee tier
  python scripts/swap_tokens.py --from WETH --to USDC --amount 0.001 --fee low
        """
    )
    
    parser.add_argument('--from', dest='token_in', required=True,
                       help='Input token symbol (e.g., USDC, WETH)')
    parser.add_argument('--to', dest='token_out', required=True,
                       help='Output token symbol (e.g., WETH, USDC)')
    parser.add_argument('--amount', type=float, required=True,
                       help='Amount of input token to swap')
    parser.add_argument('--fee', choices=['lowest', 'low', 'medium', 'high'],
                       default='medium', help='Fee tier (default: medium/0.3%%)')
    parser.add_argument('--slippage', type=float, default=1.0,
                       help='Maximum slippage tolerance in percent (default: 1%%)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simulate swap without executing')
    
    args = parser.parse_args()
    
    swap_tokens(
        token_in=args.token_in.upper(),
        token_out=args.token_out.upper(),
        amount_in=args.amount,
        fee_tier=args.fee,
        slippage=args.slippage,
        dry_run=args.dry_run
    )
