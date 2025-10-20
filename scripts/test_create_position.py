#!/usr/bin/env python3
"""
Test LP position creation on Base Sepolia testnet.
This is your dry run before using real money!
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web3 import Web3
from src.dex.web3_client import get_web3_client
from src.dex.uniswap import get_uniswap
from src.data.price_data import get_price_collector
from src.optimizer.liquidity_optimizer import LiquidityOptimizer
from src.utils.config import get_config
from src.utils.logger import log as logger


def test_create_lp_position(capital_usd: float = 0.40):
    """
    Test creating a real LP position on Base Mainnet.
    MICRO-TESTING MODE: Uses tiny amounts ($0.40 default) for safe testing with $4 wallet.
    
    Args:
        capital_usd: Capital to deploy (in USD value, default: 0.40 for micro-testing)
    """
    logger.info("=" * 60)
    logger.info("MICRO LP POSITION TEST ON BASE MAINNET")
    logger.info("=" * 60)
    
    # Get components
    config = get_config()
    web3_client = get_web3_client()
    uniswap = get_uniswap()
    price_collector = get_price_collector()
    
    # Pool configuration
    pool_name = "WETH-USDC"
    pool_config = config.get_pool_by_name(pool_name)
    
    if not pool_config:
        logger.error(f"Pool {pool_name} not found in config!")
        enabled_pools = config.get_enabled_pools()
        logger.info(f"Available pools: {[p.get('name') for p in enabled_pools]}")
        return
    
    pool_address = pool_config['address']
    logger.info(f"\n📍 Pool: {pool_name}")
    logger.info(f"  Address: {pool_address}")
    logger.info(f"  Capital: ${capital_usd}")
    
    # Get current price
    logger.info(f"\n💰 Fetching current price...")
    try:
        current_price = price_collector.fetch_current_price(pool_name)
        logger.info(f"  Current Price: ${current_price:,.2f}")
    except Exception as e:
        logger.error(f"Failed to fetch price: {e}")
        # Use a fallback price for testing
        current_price = 4000.0
        logger.warning(f"  Using fallback price: ${current_price:,.2f}")
    
    # Calculate optimal range using optimizer
    logger.info(f"\n📊 Calculating optimal range...")
    optimizer = LiquidityOptimizer()
    
    # Simple ±1% range for testing
    lower_price = current_price * 0.99
    upper_price = current_price * 1.01
    
    logger.info(f"  Range: ${lower_price:,.2f} - ${upper_price:,.2f}")
    logger.info(f"  Width: ±1%")
    
    # Convert prices to ticks
    # tick = floor(log(price) / log(1.0001))
    import math
    tick_lower = int(math.floor(math.log(lower_price) / math.log(1.0001)))
    tick_upper = int(math.floor(math.log(upper_price) / math.log(1.0001)))
    
    # Align ticks to tick spacing (60 for 0.3% fee tier, 10 for 0.05%)
    fee = pool_config.get('fee_tier', 3000)
    tick_spacing = 60 if fee == 3000 else (10 if fee == 500 else 200)
    
    tick_lower = (tick_lower // tick_spacing) * tick_spacing
    tick_upper = (tick_upper // tick_spacing) * tick_spacing
    
    logger.info(f"  Tick Range: [{tick_lower}, {tick_upper}]")
    logger.info(f"  Tick Spacing: {tick_spacing}")
    
    # Calculate token amounts
    # For simplicity, split 50/50 in USD value
    eth_value = capital_usd / 2  # $5 of ETH
    usdc_value = capital_usd / 2  # $5 of USDC
    
    eth_amount = eth_value / current_price  # Convert to ETH
    usdc_amount = usdc_value  # Already in USDC
    
    # Convert to wei/base units
    eth_wei = int(eth_amount * 1e18)  # ETH has 18 decimals
    usdc_base = int(usdc_amount * 1e6)  # USDC has 6 decimals
    
    logger.info(f"\n💎 Token Amounts:")
    logger.info(f"  ETH: {eth_amount:.6f} ({eth_wei} wei)")
    logger.info(f"  USDC: {usdc_amount:.2f} ({usdc_base} base units)")
    
    # Check balances
    logger.info(f"\n🔍 Checking wallet balances...")
    w3 = web3_client.w3
    wallet = web3_client.address
    
    # Get token addresses from pool
    from src.dex.abis import POOL_ABI, ERC20_ABI
    pool_contract = w3.eth.contract(
        address=Web3.to_checksum_address(pool_address),
        abi=POOL_ABI
    )
    token0_address = pool_contract.functions.token0().call()
    token1_address = pool_contract.functions.token1().call()
    
    # Get balances
    token0_contract = w3.eth.contract(address=token0_address, abi=ERC20_ABI)
    token1_contract = w3.eth.contract(address=token1_address, abi=ERC20_ABI)
    
    import time
    time.sleep(0.5)  # Avoid rate limits
    
    token0_balance = token0_contract.functions.balanceOf(wallet).call()
    time.sleep(0.5)
    token1_balance = token1_contract.functions.balanceOf(wallet).call()
    
    # Hardcode decimals to avoid extra RPC calls (WETH=18, USDC=6)
    token0_decimals = 18 if "4200000000000000000000000000000000000006" in token0_address.lower() else 6
    token1_decimals = 6 if token0_decimals == 18 else 18
    
    logger.info(f"  Token0 Balance: {token0_balance / (10**token0_decimals):.6f}")
    logger.info(f"  Token1 Balance: {token1_balance / (10**token1_decimals):.6f}")
    
    # Determine which is which (token0 < token1 by address)
    if token0_address.lower() < token1_address.lower():
        # token0 is first alphabetically
        if "4200000000000000000000000000000000000006" in token0_address.lower():  # WETH
            weth_balance = token0_balance / (10**token0_decimals)
            usdc_balance = token1_balance / (10**token1_decimals)
        else:
            usdc_balance = token0_balance / (10**token0_decimals)
            weth_balance = token1_balance / (10**token1_decimals)
    else:
        if "4200000000000000000000000000000000000006" in token1_address.lower():  # WETH
            weth_balance = token1_balance / (10**token1_decimals)
            usdc_balance = token0_balance / (10**token0_decimals)
        else:
            usdc_balance = token1_balance / (10**token1_decimals)
            weth_balance = token0_balance / (10**token0_decimals)
    
    logger.info(f"\n💰 Interpreted Balances:")
    logger.info(f"  WETH: {weth_balance:.6f}")
    logger.info(f"  USDC: {usdc_balance:.2f}")
    
    # Check if we have enough
    if weth_balance < eth_amount:
        logger.warning(f"⚠️  Insufficient WETH! Need {eth_amount:.6f}, have {weth_balance:.6f}")
        logger.warning(f"  You may need to wrap some ETH first")
    
    if usdc_balance < usdc_amount:
        logger.warning(f"⚠️  Insufficient USDC! Need {usdc_amount:.2f}, have {usdc_balance:.2f}")
        logger.warning(f"  Run: python scripts/get_testnet_tokens.py --amount 0.01")
        logger.warning(f"  This will swap 0.01 ETH for ~$40 USDC")
        return
    
    # Confirm before proceeding
    logger.info(f"\n⚠️  READY TO CREATE POSITION!")
    logger.info(f"\n  This will:")
    logger.info(f"  1. Approve WETH and USDC for Position Manager")
    logger.info(f"  2. Create LP position with ${capital_usd} capital")
    logger.info(f"  3. Mint NFT representing your position")
    logger.info(f"  4. Start earning fees from swaps!")
    
    response = input(f"\n  Proceed? (yes/no): ")
    
    if response.lower() != 'yes':
        logger.info("  Cancelled by user")
        return
    
    # CREATE THE POSITION!
    logger.info(f"\n🚀 Creating LP position...")
    
    try:
        result = uniswap.add_liquidity(
            pool_address=pool_address,
            token0_amount=token0_balance if token0_address < token1_address else token1_balance,
            token1_amount=token1_balance if token0_address < token1_address else token0_balance,
            tick_lower=tick_lower,
            tick_upper=tick_upper,
            token0_address=token0_address,
            token1_address=token1_address,
            fee=500  # 0.05% fee tier
        )
        
        if result['success']:
            logger.info(f"\n✅ SUCCESS! LP POSITION CREATED!")
            logger.info(f"\n📝 Transaction Details:")
            logger.info(f"  Hash: {result['tx_hash']}")
            logger.info(f"  Explorer: https://basescan.org/tx/{result['tx_hash']}")
            logger.info(f"  Gas Used: {result['receipt']['gasUsed']}")
            
            logger.info(f"\n🎉 Your position is now live on testnet!")
            logger.info(f"  It will earn fees whenever someone swaps WETH/USDC")
            logger.info(f"  Current range: ${lower_price:,.2f} - ${upper_price:,.2f}")
            
            logger.info(f"\n📊 Next Steps:")
            logger.info(f"  1. Monitor your position")
            logger.info(f"  2. Test rebalancing when price moves")
            logger.info(f"  3. Collect fees after some time")
            logger.info(f"  4. Try different strategies")
            logger.info(f"  5. Once confident, deploy on mainnet with real $!")
            
        else:
            logger.error(f"\n❌ POSITION CREATION FAILED")
            logger.error(f"  Check transaction: https://basescan.org/tx/{result['tx_hash']}")
            
    except Exception as e:
        logger.error(f"\n❌ Error creating position: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test LP position creation')
    parser.add_argument('--capital', type=float, default=0.40,
                      help='Capital to deploy in USD (default: 0.40 for micro-testing with $4 wallet)')
    
    args = parser.parse_args()
    
    test_create_lp_position(args.capital)
