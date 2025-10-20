#!/usr/bin/env python3
"""
Position Manager - Manages existing positions before creating new ones

This script checks for existing positions in the wallet and:
1. If position exists and is out of range → liquidates it
2. Swaps tokens to get proper ratio for new position
3. Creates new position centered on current price with ±50 ticks (±0.5%)

Usage:
    python scripts/position_manager.py --pool WETH-USDC --check-wallet
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dex.uniswap import get_uniswap
from src.dex.abis import POSITION_MANAGER_ABI, POOL_ABI
from src.utils.config import get_config
from src.utils.logger import log as logger


class PositionManager:
    """Manages LP positions - checks, liquidates, and rebalances"""
    
    def __init__(self, pool_name: str):
        self.pool_name = pool_name
        self.config = get_config()
        self.uniswap = get_uniswap()
        
        # Get pool config
        pool_config = self.config.get_pool_by_name(pool_name)
        if not pool_config:
            raise ValueError(f"Pool {pool_name} not found in config")
        
        self.pool_address = pool_config['address']
        self.token0 = pool_config['token0_address']
        self.token1 = pool_config['token1_address']
        self.fee = pool_config.get('fee_tier', 500)
        self.tick_spacing = 60 if self.fee == 3000 else (10 if self.fee == 500 else 200)
        
        # Create position manager contract
        self.position_manager = self.uniswap.w3.eth.contract(
            address=self.uniswap.position_manager_address,
            abi=POSITION_MANAGER_ABI
        )
        
        self.wallet_address = self.uniswap.web3_client.address
        
        logger.info(f"Position Manager initialized for {pool_name}")
        logger.info(f"Wallet: {self.wallet_address}")
    
    def get_current_tick(self) -> int:
        """Get current tick from the pool"""
        pool_contract = self.uniswap.w3.eth.contract(
            address=self.pool_address,
            abi=POOL_ABI
        )
        slot0 = pool_contract.functions.slot0().call()
        return slot0[1]
    
    def get_all_positions(self) -> list:
        """Get all positions owned by wallet for this pool"""
        positions = []
        
        # Get balance of position NFTs
        balance = self.position_manager.functions.balanceOf(self.wallet_address).call()
        
        logger.info(f"Found {balance} position NFTs in wallet")
        
        for i in range(balance):
            try:
                # Get token ID
                token_id = self.position_manager.functions.tokenOfOwnerByIndex(
                    self.wallet_address, i
                ).call()
                
                # Get position details
                position = self.position_manager.functions.positions(token_id).call()
                
                # Check if this position is for our pool
                pos_token0 = position[2]
                pos_token1 = position[3]
                pos_fee = position[4]
                
                if (pos_token0.lower() == self.token0.lower() and 
                    pos_token1.lower() == self.token1.lower() and
                    pos_fee == self.fee):
                    
                    positions.append({
                        'token_id': token_id,
                        'liquidity': position[7],
                        'tick_lower': position[5],
                        'tick_upper': position[6],
                        'token0': pos_token0,
                        'token1': pos_token1,
                        'fee': pos_fee
                    })
                    
            except Exception as e:
                logger.warning(f"Error checking position {i}: {e}")
                continue
        
        return positions
    
    def is_position_in_range(self, position: dict) -> bool:
        """Check if a position is in range"""
        current_tick = self.get_current_tick()
        in_range = position['tick_lower'] <= current_tick <= position['tick_upper']
        
        logger.info(f"Position {position['token_id']}: "
                   f"Current tick {current_tick}, "
                   f"Range [{position['tick_lower']}, {position['tick_upper']}], "
                   f"{'IN RANGE' if in_range else 'OUT OF RANGE'}")
        
        return in_range
    
    def liquidate_position(self, token_id: int):
        """Remove all liquidity from a position"""
        logger.info(f"💧 Liquidating position {token_id}...")
        
        result = self.uniswap.remove_liquidity(
            token_id=token_id,
            liquidity_percent=1.0  # Remove 100%
        )
        
        if result['success']:
            logger.info(f"✅ Position liquidated: {result['tx_hash']}")
        else:
            raise Exception(f"Failed to liquidate: {result.get('error')}")
    
    def check_and_liquidate_out_of_range(self) -> bool:
        """Check wallet for positions and liquidate if out of range"""
        logger.info("=" * 80)
        logger.info("🔍 CHECKING WALLET FOR EXISTING POSITIONS")
        logger.info("=" * 80)
        
        positions = self.get_all_positions()
        
        if not positions:
            logger.info("✅ No existing positions found for this pool")
            return False
        
        logger.info(f"Found {len(positions)} position(s) for {self.pool_name}")
        
        liquidated = False
        for pos in positions:
            if pos['liquidity'] == 0:
                logger.info(f"⚠️  Position {pos['token_id']} has no liquidity, skipping")
                continue
            
            if not self.is_position_in_range(pos):
                logger.warning(f"⚠️  Position {pos['token_id']} is OUT OF RANGE!")
                logger.info("🔧 Liquidating out-of-range position...")
                self.liquidate_position(pos['token_id'])
                liquidated = True
            else:
                logger.info(f"✅ Position {pos['token_id']} is IN RANGE")
        
        return liquidated


def main():
    parser = argparse.ArgumentParser(description='Manage LP positions')
    parser.add_argument('--pool', type=str, required=True,
                       help='Pool name (e.g., WETH-USDC)')
    parser.add_argument('--check-wallet', action='store_true',
                       help='Check wallet for positions and liquidate if out of range')
    
    args = parser.parse_args()
    
    manager = PositionManager(pool_name=args.pool)
    
    if args.check_wallet:
        manager.check_and_liquidate_out_of_range()


if __name__ == '__main__':
    main()
