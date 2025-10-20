#!/usr/bin/env python3
"""
Create Initial LP Position for Monitoring

Creates a concentrated liquidity position with ±50 ticks (±0.5%) range
around the current price.

Usage:
    python scripts/create_initial_position.py --pool WETH-USDC --amount0 0.0001 --amount1 0.2
"""

import argparse
import sys
import math
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dex.uniswap import get_uniswap
from src.data.price_data import get_price_collector
from src.utils.config import get_config
from src.utils.logger import log as logger


def create_position(pool_name: str, amount0: float, amount1: float, 
                   tick_range: int = 50) -> int:
    """
    Create a new LP position centered around current price
    
    Args:
        pool_name: Pool identifier (e.g., "WETH-USDC")
        amount0: Amount of token0 to deposit
        amount1: Amount of token1 to deposit
        tick_range: Number of ticks for position range (default: 50 = ±0.5%)
        
    Returns:
        Position NFT token ID
    """
    config = get_config()
    uniswap = get_uniswap()
    price_collector = get_price_collector()
    
    logger.info(f"Creating position for {pool_name}")
    logger.info(f"Amounts: {amount0} token0, {amount1} token1")
    logger.info(f"Tick range: ±{tick_range} ticks (~±{tick_range/100}%)")
    
    # Get pool from config
    pool_config = config.get_pool_by_name(pool_name)
    if not pool_config:
        raise ValueError(f"Pool {pool_name} not found in config. Available pools: {[p.get('name') for p in config.get_enabled_pools()]}")
    
    pool_address = pool_config['address']
    token0 = pool_config['token0_address']
    token1 = pool_config['token1_address']
    fee = pool_config.get('fee_tier', 500)
    
    logger.info(f"Pool address: {pool_address}")
    logger.info(f"Fee tier: {fee/10000}%")
    
    # Get current tick from pool
    from src.dex.abis import POOL_ABI
    pool_contract = uniswap.w3.eth.contract(
        address=pool_address,
        abi=POOL_ABI
    )
    slot0 = pool_contract.functions.slot0().call()
    current_tick = slot0[1]
    
    logger.info(f"Current tick: {current_tick}")
    
    # Calculate tick range: CURRENT TICK ± tick_range
    # This ensures the position is centered on current price
    tick_spacing = 60 if fee == 3000 else (10 if fee == 500 else 200)
    
    # Round current tick to nearest tick spacing
    current_tick_aligned = (current_tick // tick_spacing) * tick_spacing
    
    # Add/subtract tick_range from current tick
    tick_lower = current_tick_aligned - tick_range
    tick_upper = current_tick_aligned + tick_range
    
    # Align to tick spacing
    tick_lower = (tick_lower // tick_spacing) * tick_spacing
    tick_upper = (tick_upper // tick_spacing) * tick_spacing
    
    logger.info(f"Tick range: [{tick_lower}, {tick_upper}]")
    logger.info(f"Tick spacing: {tick_spacing}")
    
    # Calculate price range from ticks for display
    price_lower = 1.0001 ** tick_lower
    price_upper = 1.0001 ** tick_upper
    logger.info(f"Price range: ${price_lower:,.2f} - ${price_upper:,.2f}")
    
    # Get current price for display
    try:
        current_price = price_collector.fetch_current_price(pool_name)
        logger.info(f"Current price: ${current_price:,.2f}")
    except Exception as e:
        logger.warning(f"Could not fetch current price for display: {e}")
    
    # Convert amounts to wei/base units
    amount0_wei = int(amount0 * 1e18)  # WETH has 18 decimals
    amount1_wei = int(amount1 * 1e6)   # USDC has 6 decimals
    
    # Create the position
    logger.info("Creating position...")
    result = uniswap.add_liquidity(
        pool_address=pool_address,
        token0_amount=amount0_wei,
        token1_amount=amount1_wei,
        tick_lower=tick_lower,
        tick_upper=tick_upper,
        token0_address=token0,
        token1_address=token1,
        fee=fee
    )
    
    if not result['success']:
        raise Exception(f"Failed to create position: {result.get('error', 'Unknown error')}")
    
    tx_hash = result['tx_hash']
    token_id = result.get('token_id', 'Unknown')
    
    logger.info("=" * 60)
    logger.info("✅ POSITION CREATED SUCCESSFULLY!")
    logger.info("=" * 60)
    logger.info(f"Position Token ID: {token_id}")
    logger.info(f"Transaction: https://basescan.org/tx/{tx_hash}")
    logger.info(f"Pool: {pool_name}")
    logger.info(f"Fee Tier: {fee/10000}%")
    logger.info(f"Tick Range: [{tick_lower}, {tick_upper}]")
    logger.info("=" * 60)
    logger.info("\nTo monitor this position, run:")
    logger.info(f"python scripts/monitor_and_rebalance.py --pool {pool_name} "
               f"--amount0 {amount0} --amount1 {amount1} --position-id {token_id}")
    logger.info("=" * 60)
    
    return token_id


def main():
    parser = argparse.ArgumentParser(description='Create initial LP position')
    parser.add_argument('--pool', type=str, required=True,
                       help='Pool name (e.g., WETH-USDC)')
    parser.add_argument('--amount0', type=float, required=True,
                       help='Amount of token0 to deposit')
    parser.add_argument('--amount1', type=float, required=True,
                       help='Amount of token1 to deposit')
    parser.add_argument('--tick-range', type=int, default=50,
                       help='Tick range for position (default: 50 = ±0.5%%)')
    
    args = parser.parse_args()
    
    try:
        token_id = create_position(
            pool_name=args.pool,
            amount0=args.amount0,
            amount1=args.amount1,
            tick_range=args.tick_range
        )
    except Exception as e:
        logger.error(f"❌ Failed to create position: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
