"""
Multi-position strategy - spread positions across price ranges.
"""
import time
from typing import Dict, Any, List
from .base_strategy import BaseStrategy
from ..utils.logger import log
from ..utils.config import get_config
from ..utils.math import get_tick_range, tick_to_price
from ..data.price_data import get_price_collector
from ..optimizer.liquidity_optimizer import get_optimizer
from ..dex.uniswap import get_uniswap_v3


class MultiPositionStrategy(BaseStrategy):
    """
    Multiple positions spread across different price ranges.
    
    This strategy creates several positions at different ranges to:
    1. Capture fees across wider price movements
    2. Reduce rebalancing frequency
    3. Diversify risk
    """
    
    def __init__(self, num_positions: int = 3):
        """
        Initialize multi-position strategy.
        
        Args:
            num_positions: Number of positions to maintain
        """
        super().__init__(f"Multi-Position ({num_positions})")
        
        self.num_positions = num_positions
        self.config = get_config()
        self.price_collector = get_price_collector()
        self.optimizer = get_optimizer()
        self.dex = get_uniswap_v3()
        
        self.positions = []
        self.last_rebalance_times = {}
    
    def analyze(self, pool_name: str, capital_usd: float) -> Dict[str, Any]:
        """
        Analyze and determine position setup.
        
        Strategy:
        - Split capital across multiple positions
        - Center position: tight around current price
        - Outer positions: wider ranges above and below
        
        Args:
            pool_name: Pool name
            capital_usd: Available capital
        
        Returns:
            Analysis with recommended actions
        """
        log.info(f"[{self.name}] Analyzing {pool_name}")
        
        current_price = self.price_collector.fetch_current_price(pool_name)
        pool_config = self.config.get_pool_by_name(pool_name)
        tick_spacing = self.optimizer._get_tick_spacing(pool_config['fee_tier'])
        
        # Calculate capital allocation
        capital_per_position = capital_usd / self.num_positions
        
        # Define positions with varying concentrations
        # Position 0: Very concentrated at current price (40% capital)
        # Position 1: Medium range (30% capital)
        # Position 2: Wide range (30% capital)
        
        capital_allocations = self._calculate_capital_allocation()
        concentrations = [0.8, 0.5, 0.3][:self.num_positions]
        
        recommended_positions = []
        
        for i in range(self.num_positions):
            concentration = concentrations[i]
            capital = capital_usd * capital_allocations[i]
            
            # Calculate range based on concentration
            volatility = self.price_collector.calculate_volatility(pool_name, 24)
            price_range = volatility * (2.0 - concentration)
            
            lower_tick, upper_tick = get_tick_range(
                current_price=current_price,
                price_range_percent=price_range,
                tick_spacing=tick_spacing
            )
            
            recommended_positions.append({
                'index': i,
                'lower_tick': lower_tick,
                'upper_tick': upper_tick,
                'capital': capital,
                'concentration': concentration,
                'lower_price': tick_to_price(lower_tick),
                'upper_price': tick_to_price(upper_tick)
            })
        
        # Check if we need to create or rebalance positions
        if len(self.positions) == 0:
            return {
                'action': 'create_positions',
                'pool_name': pool_name,
                'current_price': current_price,
                'positions': recommended_positions,
                'total_capital': capital_usd
            }
        
        # Check if any positions need rebalancing
        positions_to_rebalance = []
        for pos in self.positions:
            if self.should_rebalance(pos):
                positions_to_rebalance.append(pos)
        
        if positions_to_rebalance:
            return {
                'action': 'rebalance_positions',
                'pool_name': pool_name,
                'current_price': current_price,
                'positions_to_rebalance': positions_to_rebalance,
                'recommended_positions': recommended_positions
            }
        
        return {
            'action': 'hold',
            'reason': 'All positions within acceptable ranges',
            'current_price': current_price,
            'positions': self.positions
        }
    
    def execute(self, analysis: Dict[str, Any]) -> List[str]:
        """Execute strategy."""
        action = analysis['action']
        
        if action == 'hold':
            return []
        
        elif action == 'create_positions':
            return self._create_positions(analysis)
        
        elif action == 'rebalance_positions':
            return self._rebalance_positions(analysis)
        
        return []
    
    def should_rebalance(self, position: Dict[str, Any]) -> bool:
        """Check if specific position needs rebalancing."""
        if position is None:
            return False
        
        pool_name = position['pool_name']
        current_price = self.price_collector.get_cached_price(pool_name)
        
        if current_price is None:
            current_price = self.price_collector.fetch_current_price(pool_name)
        
        last_rebalance = self.last_rebalance_times.get(position['token_id'], 0)
        
        should_rebalance, _ = self.optimizer.should_rebalance(
            current_price=current_price,
            position_lower_tick=position['lower_tick'],
            position_upper_tick=position['upper_tick'],
            last_rebalance_time=last_rebalance
        )
        
        return should_rebalance
    
    def _calculate_capital_allocation(self) -> List[float]:
        """Calculate capital allocation across positions."""
        if self.num_positions == 1:
            return [1.0]
        elif self.num_positions == 2:
            return [0.6, 0.4]  # More in concentrated
        elif self.num_positions == 3:
            return [0.4, 0.3, 0.3]
        else:
            # Equal allocation for more positions
            alloc = 1.0 / self.num_positions
            return [alloc] * self.num_positions
    
    def _create_positions(self, analysis: Dict[str, Any]) -> List[str]:
        """Create multiple positions."""
        log.info(f"[{self.name}] Creating {self.num_positions} positions")
        
        tx_hashes = []
        
        for pos_config in analysis['positions']:
            log.info(f"Creating position {pos_config['index']}: "
                    f"[{pos_config['lower_tick']}, {pos_config['upper_tick']}]")
            
            # Simulate for now
            tx_hash = f"0xsimulated_create_{pos_config['index']}"
            tx_hashes.append(tx_hash)
            
            # Track position
            position = {
                'pool_name': analysis['pool_name'],
                'token_id': f"sim_{pos_config['index']}",
                'lower_tick': pos_config['lower_tick'],
                'upper_tick': pos_config['upper_tick'],
                'capital': pos_config['capital'],
                'created_at': time.time()
            }
            
            self.positions.append(position)
            self.last_rebalance_times[position['token_id']] = time.time()
        
        self.log_performance('create_positions', analysis)
        
        return tx_hashes
    
    def _rebalance_positions(self, analysis: Dict[str, Any]) -> List[str]:
        """Rebalance selected positions."""
        log.info(f"[{self.name}] Rebalancing {len(analysis['positions_to_rebalance'])} positions")
        
        tx_hashes = []
        
        for old_pos in analysis['positions_to_rebalance']:
            # Find matching new configuration
            index = next(
                (i for i, p in enumerate(self.positions) if p['token_id'] == old_pos['token_id']),
                0
            )
            
            new_config = analysis['recommended_positions'][index]
            
            log.info(f"Rebalancing position {old_pos['token_id']}")
            
            # Simulate
            close_tx = f"0xsim_close_{old_pos['token_id']}"
            open_tx = f"0xsim_open_{old_pos['token_id']}"
            tx_hashes.extend([close_tx, open_tx])
            
            # Update position
            old_pos.update({
                'lower_tick': new_config['lower_tick'],
                'upper_tick': new_config['upper_tick'],
                'rebalanced_at': time.time()
            })
            
            self.last_rebalance_times[old_pos['token_id']] = time.time()
        
        self.log_performance('rebalance_positions', analysis)
        
        return tx_hashes
