"""
Concentrated follower strategy - single position that closely tracks price.
"""
import time
from typing import Dict, Any, List
from .base_strategy import BaseStrategy
from ..utils.logger import log
from ..utils.config import get_config
from ..data.price_data import get_price_collector
from ..optimizer.liquidity_optimizer import get_optimizer
from ..dex.uniswap import get_uniswap_v3


class ConcentratedFollowerStrategy(BaseStrategy):
    """
    Single hyper-concentrated position that follows price closely.
    
    This strategy maintains one position with tight bounds around current price
    and rebalances frequently to follow price movements.
    """
    
    def __init__(self):
        """Initialize concentrated follower strategy."""
        super().__init__("Concentrated Follower")
        
        self.config = get_config()
        self.price_collector = get_price_collector()
        self.optimizer = get_optimizer()
        self.dex = get_uniswap_v3()
        
        self.current_position = None
        self.last_rebalance_time = 0
    
    def analyze(self, pool_name: str, capital_usd: float) -> Dict[str, Any]:
        """
        Analyze pool and determine if action is needed.
        
        Args:
            pool_name: Pool name
            capital_usd: Available capital
        
        Returns:
            Analysis with recommended actions
        """
        log.info(f"[{self.name}] Analyzing {pool_name}")
        
        # Get current price
        current_price = self.price_collector.fetch_current_price(pool_name)
        
        # Check if we have an existing position
        if self.current_position is None:
            log.info("No existing position - recommending new position")
            
            # Calculate optimal range
            lower_tick, upper_tick, metadata = self.optimizer.calculate_optimal_range(
                pool_name=pool_name,
                current_price=current_price,
                capital_usd=capital_usd,
                strategy_type="concentrated_follower"
            )
            
            return {
                'action': 'open_position',
                'pool_name': pool_name,
                'current_price': current_price,
                'lower_tick': lower_tick,
                'upper_tick': upper_tick,
                'capital_usd': capital_usd,
                'metadata': metadata
            }
        
        # Check if rebalance is needed
        should_rebalance, reason = self.optimizer.should_rebalance(
            current_price=current_price,
            position_lower_tick=self.current_position['lower_tick'],
            position_upper_tick=self.current_position['upper_tick'],
            last_rebalance_time=self.last_rebalance_time
        )
        
        if should_rebalance:
            log.info(f"Rebalance needed: {reason}")
            
            # Calculate new optimal range
            lower_tick, upper_tick, metadata = self.optimizer.calculate_optimal_range(
                pool_name=pool_name,
                current_price=current_price,
                capital_usd=capital_usd,
                strategy_type="concentrated_follower"
            )
            
            return {
                'action': 'rebalance',
                'pool_name': pool_name,
                'current_price': current_price,
                'old_position': self.current_position,
                'new_lower_tick': lower_tick,
                'new_upper_tick': upper_tick,
                'reason': reason,
                'metadata': metadata
            }
        
        log.info(f"No action needed: {reason}")
        return {
            'action': 'hold',
            'reason': reason,
            'current_price': current_price,
            'position': self.current_position
        }
    
    def execute(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Execute strategy based on analysis.
        
        Args:
            analysis: Analysis results
        
        Returns:
            List of transaction hashes
        """
        action = analysis['action']
        
        if action == 'hold':
            log.info("Holding current position")
            return []
        
        elif action == 'open_position':
            return self._open_position(analysis)
        
        elif action == 'rebalance':
            return self._rebalance_position(analysis)
        
        else:
            log.warning(f"Unknown action: {action}")
            return []
    
    def should_rebalance(self, position: Dict[str, Any]) -> bool:
        """
        Check if position should be rebalanced.
        
        Args:
            position: Position details
        
        Returns:
            True if should rebalance
        """
        if position is None:
            return False
        
        pool_name = position['pool_name']
        current_price = self.price_collector.get_cached_price(pool_name)
        
        if current_price is None:
            current_price = self.price_collector.fetch_current_price(pool_name)
        
        should_rebalance, _ = self.optimizer.should_rebalance(
            current_price=current_price,
            position_lower_tick=position['lower_tick'],
            position_upper_tick=position['upper_tick'],
            last_rebalance_time=self.last_rebalance_time
        )
        
        return should_rebalance
    
    def _open_position(self, analysis: Dict[str, Any]) -> List[str]:
        """Open new position."""
        log.info(f"[{self.name}] Opening new position")
        
        pool_name = analysis['pool_name']
        pool_config = self.config.get_pool_by_name(pool_name)
        
        # TODO: Calculate token amounts based on capital and price
        # For now, this is a placeholder
        
        try:
            tx_hash = self.dex.add_liquidity(
                pool_address=pool_config['address'],
                token0_amount=0,  # TODO: Calculate
                token1_amount=0,  # TODO: Calculate
                tick_lower=analysis['lower_tick'],
                tick_upper=analysis['upper_tick']
            )
            
            # Wait for confirmation
            receipt = self.dex.web3_client.wait_for_transaction(tx_hash)
            
            if receipt['status'] == 1:
                # Update current position
                self.current_position = {
                    'pool_name': pool_name,
                    'token_id': None,  # TODO: Extract from receipt
                    'lower_tick': analysis['lower_tick'],
                    'upper_tick': analysis['upper_tick'],
                    'opened_at': time.time()
                }
                
                self.last_rebalance_time = time.time()
                
                # Log performance
                self.log_performance('open_position', analysis)
                
                log.info(f"Position opened successfully: {tx_hash}")
                return [tx_hash]
            else:
                log.error("Position opening failed")
                return []
        
        except NotImplementedError:
            log.warning("Uniswap V3 interface not fully implemented yet - simulating success")
            return ['0xsimulated']
    
    def _rebalance_position(self, analysis: Dict[str, Any]) -> List[str]:
        """Rebalance existing position."""
        log.info(f"[{self.name}] Rebalancing position")
        
        old_position = analysis['old_position']
        
        try:
            close_tx, open_tx = self.dex.rebalance_position(
                token_id=old_position['token_id'],
                new_tick_lower=analysis['new_lower_tick'],
                new_tick_upper=analysis['new_upper_tick']
            )
            
            # Update position
            self.current_position.update({
                'lower_tick': analysis['new_lower_tick'],
                'upper_tick': analysis['new_upper_tick'],
                'rebalanced_at': time.time()
            })
            
            self.last_rebalance_time = time.time()
            
            # Log performance
            self.log_performance('rebalance', analysis)
            
            log.info(f"Position rebalanced: {close_tx}, {open_tx}")
            return [close_tx, open_tx]
        
        except NotImplementedError:
            log.warning("Uniswap V3 interface not fully implemented yet - simulating success")
            return ['0xsimulated_close', '0xsimulated_open']
