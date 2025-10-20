#!/usr/bin/env python3
"""
Automated LP Position Monitor and Rebalancer

This script continuously monitors a Uniswap V3 LP position and automatically
rebalances when the price moves out of range.

MVP Specifications:
- Position range: ±50 ticks (±0.5% from current price)
- Check interval: Every 1 minute
- Auto-rebalance: When price exits the position's tick range

Usage:
    python scripts/monitor_and_rebalance.py --pool WETH-USDC --amount0 0.0001 --amount1 0.2 --position-id 4075626
"""

import argparse
import time
import sys
import math
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dex.uniswap import get_uniswap
from src.dex.abis import POOL_ABI, POSITION_MANAGER_ABI
from src.data.price_data import get_price_collector
from src.utils.config import get_config
from src.utils.logger import log as logger


class PositionMonitor:
    """Monitors and rebalances Uniswap V3 LP positions"""
    
    def __init__(self, pool_name: str, tick_range: int = 50, check_interval: int = 60, dry_run: bool = False):
        """
        Initialize the position monitor
        
        Args:
            pool_name: Pool identifier (e.g., "WETH-USDC")
            tick_range: Number of ticks for position range (default: 50 = ±0.5%)
            check_interval: Seconds between range checks (default: 60)
            dry_run: If True, simulate operations without executing transactions
        """
        self.pool_name = pool_name
        self.tick_range = tick_range
        self.check_interval = check_interval
        self.dry_run = dry_run
        self.pool_name = pool_name
        self.tick_range = tick_range
        self.check_interval = check_interval
        self.current_position_id = None
        
        # Initialize clients
        self.config = get_config()
        self.uniswap = get_uniswap()
        self.price_collector = get_price_collector()
        
        # Get pool config
        pool_config = self.config.get_pool_by_name(pool_name)
        if not pool_config:
            raise ValueError(f"Pool {pool_name} not found in config")
        
        self.pool_address = pool_config['address']
        self.token0 = pool_config['token0_address']
        self.token1 = pool_config['token1_address']
        self.fee = pool_config.get('fee_tier', 500)
        self.tick_spacing = 60 if self.fee == 3000 else (10 if self.fee == 500 else 200)
        
        # Create position manager contract object
        self.position_manager = self.uniswap.w3.eth.contract(
            address=self.uniswap.position_manager_address,
            abi=POSITION_MANAGER_ABI
        )
        
        logger.info(f"Initialized PositionMonitor for {pool_name} (fee: {self.fee/10000}%)")
        logger.info(f"Tick range: ±{tick_range} ticks (~±{tick_range/100}%)")
        logger.info(f"Check interval: {check_interval} seconds")
        logger.info(f"Dry run mode: {self.dry_run}")
    
    def get_existing_positions(self) -> list:
        """
        Get all existing LP positions for the connected wallet
        
        Returns:
            List of position dictionaries with token_id, pool_address, etc.
        """
        logger.info("Checking for existing LP positions...")
        
        try:
            positions = self.uniswap.get_positions()
            
            # Filter positions for this pool
            pool_positions = []
            for pos in positions:
                # Check if position is for our pool by comparing token addresses
                if (pos.get('token0') == self.token0 and pos.get('token1') == self.token1) or \
                   (pos.get('token0') == self.token1 and pos.get('token1') == self.token0):
                    pool_positions.append(pos)
            
            logger.info(f"Found {len(pool_positions)} positions for {self.pool_name}")
            
            for pos in pool_positions:
                token_id = pos.get('tokenId', pos.get('token_id'))
                logger.info(f"  Position {token_id}: liquidity={pos.get('liquidity', 0)}")
            
            return pool_positions
            
        except Exception as e:
            logger.error(f"Error getting existing positions: {e}")
            return []
    
    def get_current_tick(self) -> int:
        """Get current tick from the pool"""
        pool_contract = self.uniswap.w3.eth.contract(
            address=self.pool_address,
            abi=POOL_ABI
        )
        slot0 = pool_contract.functions.slot0().call()
        return slot0[1]
    
    def create_position(self, amount0: float, amount1: float) -> int:
        """
        Create a new LP position centered around current price
        
        Args:
            amount0: Amount of token0 to deposit
            amount1: Amount of token1 to deposit
            
        Returns:
            Position NFT token ID
        """
        logger.info(f"Creating new position with {amount0} token0 and {amount1} token1")
        
        # Get current tick from pool
        current_tick = self.get_current_tick()
        logger.info(f"Current tick: {current_tick}")
        
        # Calculate tick range: CURRENT TICK ± tick_range
        # This ensures the position is centered on current price
        current_tick_aligned = (current_tick // self.tick_spacing) * self.tick_spacing
        
        tick_lower = current_tick_aligned - self.tick_range
        tick_upper = current_tick_aligned + self.tick_range
        
        # Align to tick spacing
        tick_lower = (tick_lower // self.tick_spacing) * self.tick_spacing
        tick_upper = (tick_upper // self.tick_spacing) * self.tick_spacing
        
        logger.info(f"Position range: [{tick_lower}, {tick_upper}]")
        
        # Calculate price range from ticks for display
        price_lower = 1.0001 ** tick_lower
        price_upper = 1.0001 ** tick_upper
        logger.info(f"Price range: ${price_lower:,.2f} - ${price_upper:,.2f}")
        
        # Get current price for display
        try:
            current_price = self.price_collector.fetch_current_price(self.pool_name)
            logger.info(f"Current price: ${current_price:,.2f}")
        except Exception as e:
            logger.warning(f"Could not fetch current price for display: {e}")
        
        # Convert amounts to wei
        amount0_wei = int(amount0 * 1e18)  # WETH has 18 decimals
        amount1_wei = int(amount1 * 1e6)   # USDC has 6 decimals
        
        # Create the position
        logger.info("Creating position...")
        result = self.uniswap.add_liquidity(
            pool_address=self.pool_address,
            token0_amount=amount0_wei,
            token1_amount=amount1_wei,
            tick_lower=tick_lower,
            tick_upper=tick_upper,
            token0_address=self.token0,
            token1_address=self.token1,
            fee=self.fee,
            dry_run=self.dry_run
        )
        
        if not result['success']:
            raise Exception(f"Failed to create position: {result.get('error', 'Unknown error')}")
        
        # Handle dry run case
        if result.get('dry_run'):
            logger.info("✅ Position creation simulated (dry run)")
            return 999999  # Mock token ID for dry run
        
        tx_hash = result['tx_hash']
        
        # Extract token ID from transaction receipt
        receipt = self.uniswap.w3.eth.get_transaction_receipt(tx_hash)
        token_id = None
        
        for log in receipt['logs']:
            if log['address'].lower() == self.uniswap.position_manager_address.lower():
                if len(log['topics']) >= 4:
                    token_id = int(log['topics'][3].hex(), 16)
                    break
        
        if token_id is None:
            raise Exception("Could not extract token ID from transaction")
        
        logger.info(f"✅ Position created! Token ID: {token_id}")
        logger.info(f"Transaction: https://basescan.org/tx/{tx_hash}")
        
        return token_id
    
    def check_position_range(self, token_id: int) -> dict:
        """
        Check if position is in range
        
        Args:
            token_id: Position NFT token ID
            
        Returns:
            Dict with status info: {in_range: bool, current_tick: int, tick_lower: int, tick_upper: int}
        """
        # Get position details
        position = self.position_manager.functions.positions(token_id).call()
        tick_lower = position[5]
        tick_upper = position[6]
        
        # Get current tick
        current_tick = self.get_current_tick()
        
        in_range = tick_lower <= current_tick <= tick_upper
        
        result = {
            'in_range': in_range,
            'current_tick': current_tick,
            'tick_lower': tick_lower,
            'tick_upper': tick_upper,
            'distance_from_lower': current_tick - tick_lower,
            'distance_from_upper': tick_upper - current_tick
        }
        
        logger.debug(f"Position check: {result}")
        
        return result
    
    def remove_position(self, token_id: int) -> tuple:
        """
        Remove all liquidity from a position
        
        Args:
            token_id: Position NFT token ID
            
        Returns:
            Tuple of (amount0_collected, amount1_collected)
        """
        logger.info(f"Removing liquidity from position {token_id}")
        
        # Get position details
        position = self.position_manager.functions.positions(token_id).call()
        liquidity = position[7]
        
        if liquidity == 0:
            logger.warning(f"Position {token_id} has no liquidity")
            return (0, 0)
        
        # Use the existing remove_liquidity method
        try:
            result = self.uniswap.remove_liquidity(
                token_id=token_id,
                liquidity_percent=1.0,  # Remove 100% of liquidity
                dry_run=self.dry_run
            )
            
            if result['success']:
                if result.get('dry_run'):
                    logger.info("Liquidity removal simulated (dry run)")
                    # Return mock amounts for dry run (half of what was originally deposited)
                    return (int(0.00001 * 1e18), int(0.025 * 1e6))  # Mock collected amounts
                else:
                    logger.info(f"Liquidity removed: {result['tx_hash']}")
                    return (result.get('amount0', 0), result.get('amount1', 0))
            else:
                raise Exception(f"Failed to remove liquidity: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error removing liquidity: {e}")
            raise
    
    def rebalance_position(self, old_token_id: int, amount0: float, amount1: float, status: dict) -> int:
        """
        Rebalance position: remove old position, sell half into out-of-range asset, and create new one
        
        Args:
            old_token_id: Token ID of position to close
            amount0: Amount of token0 for new position
            amount1: Amount of token1 for new position
            status: Position status dict with in_range, current_tick, etc.
            
        Returns:
            New position token ID
        """
        logger.info("🔄 Starting rebalance...")
        
        # Remove old position
        collected_amounts = self.remove_position(old_token_id)
        amount0_collected, amount1_collected = collected_amounts
        
        logger.info(f"Collected: {amount0_collected} token0, {amount1_collected} token1")
        
        # Determine which asset is out of range and sell half of it
        if status['current_tick'] < status['tick_lower']:
            # Price is below range - we have too much token0 (WETH), sell half for token1 (USDC)
            sell_amount = amount0_collected / 2
            if sell_amount > 0:
                logger.info(f"Price below range - selling {sell_amount} token0 for token1")
                try:
                    swap_result = self.uniswap.swap_tokens(
                        token_in=self.pool_name.split('-')[0],  # token0 symbol
                        token_out=self.pool_name.split('-')[1],  # token1 symbol
                        amount_in=sell_amount / (10 ** 18),  # Convert from wei to ether
                        fee_tier='medium',
                        slippage=1.0,
                        dry_run=self.dry_run
                    )
                    if swap_result['success']:
                        logger.info("✅ Swap completed successfully")
                    else:
                        logger.error(f"❌ Swap failed: {swap_result.get('error', 'Unknown error')}")
                except Exception as e:
                    logger.error(f"Swap error: {e}")
        elif status['current_tick'] > status['tick_upper']:
            # Price is above range - we have too much token1 (USDC), sell half for token0 (WETH)
            sell_amount = amount1_collected / 2
            if sell_amount > 0:
                logger.info(f"Price above range - selling {sell_amount} token1 for token0")
                try:
                    swap_result = self.uniswap.swap_tokens(
                        token_in=self.pool_name.split('-')[1],  # token1 symbol
                        token_out=self.pool_name.split('-')[0],  # token0 symbol
                        amount_in=sell_amount / (10 ** 6),  # Convert from wei to USDC (6 decimals)
                        fee_tier='medium',
                        slippage=1.0,
                        dry_run=self.dry_run
                    )
                    if swap_result['success']:
                        logger.info("✅ Swap completed successfully")
                    else:
                        logger.error(f"❌ Swap failed: {swap_result.get('error', 'Unknown error')}")
                except Exception as e:
                    logger.error(f"Swap error: {e}")
        
        # Wait a bit for tokens to settle
        time.sleep(2)
        
        # Create new position with the amounts (modified or not)
        new_token_id = self.create_position(amount0, amount1)
        
        logger.info(f"✅ Rebalance complete! New position: {new_token_id}")
        
        return new_token_id
    
    def monitor_loop(self, initial_amount0: float, initial_amount1: float, 
                    initial_token_id: int = None):
        """
        Main monitoring loop
        
        Args:
            initial_amount0: Initial amount of token0
            initial_amount1: Initial amount of token1
            initial_token_id: Existing position ID (if None, checks for existing positions)
        """
        # Check for existing positions if no specific token_id provided
        if initial_token_id is None:
            existing_positions = self.get_existing_positions()
            if existing_positions:
                # Use the first existing position
                initial_token_id = existing_positions[0].get('tokenId', existing_positions[0].get('token_id'))
                logger.info(f"Found existing position: {initial_token_id}")
            else:
                logger.info("No existing positions found, will create new position")
        
        # Create initial position if needed
        if initial_token_id is None:
            logger.info("Creating initial position...")
            self.current_position_id = self.create_position(initial_amount0, initial_amount1)
        else:
            logger.info(f"Using existing position: {initial_token_id}")
            self.current_position_id = initial_token_id
        
        logger.info("🚀 Starting monitoring loop...")
        logger.info(f"Will check position every {self.check_interval} seconds")
        
        rebalance_count = 0
        check_count = 0
        
        try:
            while True:
                check_count += 1
                
                # Check if position is in range
                status = self.check_position_range(self.current_position_id)
                
                # Get current price
                try:
                    current_price = self.price_collector.fetch_current_price(self.pool_name)
                except Exception:
                    current_price = self.uniswap.get_pool_price(self.pool_address)
                
                # Calculate price bounds from ticks
                price_lower = 1.0001 ** status['tick_lower']
                price_upper = 1.0001 ** status['tick_upper']
                
                # Print detailed status header
                logger.info("=" * 80)
                logger.info(f"📊 CHECK #{check_count} - {self.pool_name} Position {self.current_position_id}")
                logger.info("=" * 80)
                logger.info(f"💰 Current Price: ${current_price:,.2f} {self.pool_name.split('-')[1]} per {self.pool_name.split('-')[0]}")
                logger.info(f"📏 Position Bounds:")
                logger.info(f"   Lower: ${price_lower:,.2f} (tick {status['tick_lower']})")
                logger.info(f"   Upper: ${price_upper:,.2f} (tick {status['tick_upper']})")
                logger.info(f"🎯 Current Tick: {status['current_tick']}")
                logger.info(f"📍 Distance from Lower Edge: {status['distance_from_lower']} ticks")
                logger.info(f"📍 Distance from Upper Edge: {status['distance_from_upper']} ticks")
                
                if status['in_range']:
                    # Calculate how centered the price is
                    total_range = status['tick_upper'] - status['tick_lower']
                    position_pct = ((status['current_tick'] - status['tick_lower']) / total_range * 100) if total_range > 0 else 50
                    
                    logger.info(f"✅ STATUS: IN RANGE ({position_pct:.1f}% through range)")
                    logger.info(f"📈 Total Rebalances: {rebalance_count}")
                else:
                    if status['current_tick'] < status['tick_lower']:
                        direction = "BELOW"
                        distance = status['tick_lower'] - status['current_tick']
                    else:
                        direction = "ABOVE"
                        distance = status['current_tick'] - status['tick_upper']
                    
                    logger.warning(f"⚠️  STATUS: OUT OF RANGE ({direction} by {distance} ticks)")
                    logger.warning(f"🔧 ACTION REQUIRED: Rebalancing position...")
                    
                    # Rebalance the position
                    logger.info("=" * 80)
                    self.current_position_id = self.rebalance_position(
                        self.current_position_id,
                        initial_amount0,
                        initial_amount1,
                        status
                    )
                    rebalance_count += 1
                    logger.info("=" * 80)
                    logger.info(f"✅ REBALANCE COMPLETE!")
                    logger.info(f"📈 Total Rebalances: {rebalance_count}")
                    logger.info(f"🆕 New Position ID: {self.current_position_id}")
                
                logger.info("=" * 80)
                logger.info(f"⏳ Next check in {self.check_interval} seconds...")
                logger.info("=" * 80)
                logger.info("")  # Blank line for readability
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("\n⛔ Monitoring stopped by user")
            logger.info(f"Final position ID: {self.current_position_id}")
            logger.info(f"Total rebalances performed: {rebalance_count}")
        except Exception as e:
            logger.error(f"❌ Error in monitoring loop: {e}", exc_info=True)
            raise


def main():
    parser = argparse.ArgumentParser(description='Monitor and rebalance Uniswap V3 LP position')
    parser.add_argument('--pool', type=str, required=True, 
                       help='Pool name (e.g., WETH-USDC)')
    parser.add_argument('--amount0', type=float, required=True,
                       help='Amount of token0 to deposit')
    parser.add_argument('--amount1', type=float, required=True,
                       help='Amount of token1 to deposit')
    parser.add_argument('--tick-range', type=int, default=50,
                       help='Tick range for position (default: 50 = ±0.5%%)')
    parser.add_argument('--interval', type=int, default=60,
                       help='Check interval in seconds (default: 60)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run mode - simulate swaps without executing transactions')
    parser.add_argument('--position-id', type=int, default=None,
                       help='Existing position token ID (if resuming monitoring)')
    
    args = parser.parse_args()
    
    # Create monitor
    monitor = PositionMonitor(
        pool_name=args.pool,
        tick_range=args.tick_range,
        check_interval=args.interval,
        dry_run=args.dry_run
    )
    
    # Start monitoring
    monitor.monitor_loop(
        initial_amount0=args.amount0,
        initial_amount1=args.amount1,
        initial_token_id=args.position_id
    )


if __name__ == '__main__':
    main()
