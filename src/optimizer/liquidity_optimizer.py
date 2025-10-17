"""
Liquidity optimization engine.
"""
from typing import Tuple, Dict, Any
import numpy as np
from ..utils.logger import log
from ..utils.config import get_config
from ..utils.math import (
    price_to_tick,
    tick_to_price,
    get_tick_range,
    calculate_concentration_factor
)
from ..data.price_data import get_price_collector


class LiquidityOptimizer:
    """Optimize liquidity provision parameters."""
    
    def __init__(self):
        """Initialize optimizer."""
        self.config = get_config()
        self.price_collector = get_price_collector()
        
        log.info("Liquidity optimizer initialized")
    
    def calculate_optimal_range(
        self,
        pool_name: str,
        current_price: float,
        capital_usd: float,
        strategy_type: str = "concentrated_follower"
    ) -> Tuple[int, int, Dict[str, Any]]:
        """
        Calculate optimal tick range for liquidity position.
        
        Args:
            pool_name: Pool name
            current_price: Current price
            capital_usd: Capital in USD
            strategy_type: Strategy type
        
        Returns:
            (lower_tick, upper_tick, metadata)
        """
        log.info(f"Calculating optimal range for {pool_name}")
        log.info(f"Current price: {current_price}, Capital: ${capital_usd}")
        
        # Get pool config
        pool_config = self.config.get_pool_by_name(pool_name)
        if not pool_config:
            raise ValueError(f"Pool {pool_name} not found in config")
        
        tick_spacing = self._get_tick_spacing(pool_config['fee_tier'])
        
        # Calculate volatility
        volatility_window = self.config.get('data.volatility_window_hours', 24)
        volatility = self.price_collector.calculate_volatility(
            pool_name,
            window_hours=volatility_window
        )
        
        log.info(f"Volatility: {volatility:.6f}")
        
        # Estimate gas costs
        gas_cost_usd = self._estimate_rebalance_cost_usd()
        gas_cost_ratio = gas_cost_usd / capital_usd
        
        log.info(f"Estimated gas cost: ${gas_cost_usd:.2f} ({gas_cost_ratio:.2%})")
        
        # Calculate target duration before rebalancing
        target_duration = self._calculate_target_duration(
            volatility=volatility,
            gas_cost_ratio=gas_cost_ratio,
            strategy_type=strategy_type
        )
        
        log.info(f"Target duration: {target_duration:.1f} hours")
        
        # Calculate concentration factor
        max_gas_ratio = self.config.get('strategy.max_gas_cost_ratio', 0.02)
        concentration = calculate_concentration_factor(
            volatility=volatility,
            target_duration_hours=target_duration,
            max_gas_ratio=max_gas_ratio
        )
        
        # Adjust concentration based on strategy
        if strategy_type == "concentrated_follower":
            concentration *= 1.0  # Full concentration
        elif strategy_type == "multi_position":
            concentration *= 0.7  # Less concentrated
        
        log.info(f"Concentration factor: {concentration:.3f}")
        
        # Calculate price range
        price_range_percent = self._calculate_price_range(
            volatility=volatility,
            concentration=concentration,
            target_duration=target_duration
        )
        
        log.info(f"Price range: ±{price_range_percent:.2%}")
        
        # Convert to ticks
        lower_tick, upper_tick = get_tick_range(
            current_price=current_price,
            price_range_percent=price_range_percent,
            tick_spacing=tick_spacing
        )
        
        # Apply min/max constraints
        min_tick_range = self.config.get('strategy.min_tick_range', 50)
        max_tick_range = self.config.get('strategy.max_tick_range', 1000)
        
        tick_range = upper_tick - lower_tick
        if tick_range < min_tick_range * tick_spacing:
            # Expand range
            expansion = (min_tick_range * tick_spacing - tick_range) // 2
            lower_tick -= expansion
            upper_tick += expansion
        elif tick_range > max_tick_range * tick_spacing:
            # Contract range
            contraction = (tick_range - max_tick_range * tick_spacing) // 2
            lower_tick += contraction
            upper_tick -= contraction
        
        # Ensure ticks are aligned
        lower_tick = (lower_tick // tick_spacing) * tick_spacing
        upper_tick = (upper_tick // tick_spacing) * tick_spacing
        
        lower_price = tick_to_price(lower_tick)
        upper_price = tick_to_price(upper_tick)
        
        log.info(f"Optimal range: [{lower_tick}, {upper_tick}]")
        log.info(f"Price range: [{lower_price:.6f}, {upper_price:.6f}]")
        
        # Calculate metadata
        metadata = {
            'volatility': volatility,
            'concentration': concentration,
            'price_range_percent': price_range_percent,
            'target_duration_hours': target_duration,
            'estimated_gas_cost_usd': gas_cost_usd,
            'gas_cost_ratio': gas_cost_ratio,
            'lower_price': lower_price,
            'upper_price': upper_price
        }
        
        return lower_tick, upper_tick, metadata
    
    def should_rebalance(
        self,
        current_price: float,
        position_lower_tick: int,
        position_upper_tick: int,
        last_rebalance_time: float
    ) -> Tuple[bool, str]:
        """
        Determine if position should be rebalanced.
        
        Args:
            current_price: Current price
            position_lower_tick: Current position lower tick
            position_upper_tick: Current position upper tick
            last_rebalance_time: Timestamp of last rebalance
        
        Returns:
            (should_rebalance, reason)
        """
        import time
        
        current_tick = price_to_tick(current_price)
        position_center_tick = (position_lower_tick + position_upper_tick) / 2
        tick_range = position_upper_tick - position_lower_tick
        
        # Check if out of range
        if current_tick <= position_lower_tick or current_tick >= position_upper_tick:
            return True, "Price out of range"
        
        # Check threshold
        threshold = self.config.get('strategy.rebalance_threshold', 0.05)
        deviation = abs(current_tick - position_center_tick) / tick_range
        
        if deviation > threshold:
            return True, f"Price deviated {deviation:.1%} from center"
        
        # Check minimum interval
        min_interval = self.config.get('strategy.min_rebalance_interval_hours', 1) * 3600
        time_since_last = time.time() - last_rebalance_time
        
        if time_since_last < min_interval:
            return False, f"Too soon since last rebalance ({time_since_last/3600:.1f}h)"
        
        return False, "No rebalance needed"
    
    def _get_tick_spacing(self, fee_tier: int) -> int:
        """Get tick spacing for fee tier."""
        # Standard Uniswap V3 tick spacings
        tick_spacings = {
            500: 10,    # 0.05%
            3000: 60,   # 0.3%
            10000: 200  # 1%
        }
        return tick_spacings.get(fee_tier, 60)
    
    def _estimate_rebalance_cost_usd(self) -> float:
        """
        Estimate cost of rebalancing in USD.
        
        Rebalancing involves:
        1. Unstake (if staked)
        2. Remove liquidity
        3. Collect fees
        4. Add liquidity
        5. Stake (if staking)
        
        Returns:
            Estimated cost in USD
        """
        # Rough estimate: 5 transactions @ 25 gwei, 500k gas each
        # TODO: Use actual gas prices and estimates
        
        gas_price_gwei = self.config.get('network.gas_price_gwei', 25)
        num_transactions = 5
        gas_per_tx = 500_000
        
        total_gas = num_transactions * gas_per_tx
        total_cost_avax = (total_gas * gas_price_gwei) / 1e9
        
        # TODO: Get actual AVAX price
        avax_price_usd = 30.0  # Placeholder
        
        return total_cost_avax * avax_price_usd
    
    def _calculate_target_duration(
        self,
        volatility: float,
        gas_cost_ratio: float,
        strategy_type: str
    ) -> float:
        """
        Calculate target duration before rebalancing.
        
        Args:
            volatility: Price volatility
            gas_cost_ratio: Gas cost as ratio of position
            strategy_type: Strategy type
        
        Returns:
            Target duration in hours
        """
        # Base duration on strategy
        if strategy_type == "concentrated_follower":
            base_duration = 6  # 6 hours
        else:
            base_duration = 24  # 24 hours
        
        # Adjust for volatility and gas costs
        # Higher volatility -> longer duration (wider range)
        # Higher gas cost -> longer duration (rebalance less often)
        
        volatility_factor = 1 + (volatility * 10)  # Scale volatility
        gas_factor = 1 + (gas_cost_ratio * 20)
        
        target_duration = base_duration * volatility_factor * gas_factor
        
        # Clamp to reasonable range
        return max(1, min(72, target_duration))
    
    def _calculate_price_range(
        self,
        volatility: float,
        concentration: float,
        target_duration: float
    ) -> float:
        """
        Calculate price range percentage.
        
        Args:
            volatility: Price volatility
            concentration: Concentration factor (0-1)
            target_duration: Target duration in hours
        
        Returns:
            Price range as percentage (e.g., 0.05 = ±5%)
        """
        # Expected price move in target duration
        expected_move = volatility * np.sqrt(target_duration / 24)
        
        # Apply concentration
        # Higher concentration = tighter range
        range_multiplier = 2.0 * (1 - concentration * 0.7)
        
        price_range = expected_move * range_multiplier
        
        # Clamp to reasonable range
        return max(0.01, min(0.5, price_range))


# Global instance
_optimizer = None


def get_optimizer() -> LiquidityOptimizer:
    """Get global optimizer instance."""
    global _optimizer
    if _optimizer is None:
        _optimizer = LiquidityOptimizer()
    return _optimizer
