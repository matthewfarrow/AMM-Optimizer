"""
Base strategy interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from ..utils.logger import log


class BaseStrategy(ABC):
    """Base class for LP strategies."""
    
    def __init__(self, name: str):
        """
        Initialize strategy.
        
        Args:
            name: Strategy name
        """
        self.name = name
        self.positions = []  # Active positions
        self.performance_history = []
        
        log.info(f"Strategy initialized: {name}")
    
    @abstractmethod
    def analyze(self, pool_name: str, capital_usd: float) -> Dict[str, Any]:
        """
        Analyze current situation and determine actions.
        
        Args:
            pool_name: Pool name
            capital_usd: Available capital
        
        Returns:
            Analysis results and recommended actions
        """
        pass
    
    @abstractmethod
    def execute(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Execute strategy based on analysis.
        
        Args:
            analysis: Analysis results from analyze()
        
        Returns:
            List of transaction hashes
        """
        pass
    
    @abstractmethod
    def should_rebalance(self, position: Dict[str, Any]) -> bool:
        """
        Determine if position should be rebalanced.
        
        Args:
            position: Position details
        
        Returns:
            True if should rebalance
        """
        pass
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Calculate performance metrics.
        
        Returns:
            Performance metrics
        """
        if not self.performance_history:
            return {
                'total_return': 0.0,
                'fees_earned': 0.0,
                'gas_costs': 0.0,
                'net_profit': 0.0,
                'roi': 0.0
            }
        
        # Calculate metrics from history
        # TODO: Implement actual calculation
        
        return {
            'total_return': 0.0,
            'fees_earned': 0.0,
            'gas_costs': 0.0,
            'net_profit': 0.0,
            'roi': 0.0
        }
    
    def log_performance(self, event: str, data: Dict[str, Any]):
        """
        Log performance event.
        
        Args:
            event: Event type
            data: Event data
        """
        import time
        
        entry = {
            'timestamp': time.time(),
            'event': event,
            'data': data
        }
        
        self.performance_history.append(entry)
        log.info(f"Performance logged: {event}")
