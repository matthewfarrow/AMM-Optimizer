"""
Quick start guide and examples.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import get_config
from src.utils.logger import log
from src.strategies.concentrated_follower import ConcentratedFollowerStrategy


def example_concentrated_follower():
    """Example: Run concentrated follower strategy."""
    log.info("Example: Concentrated Follower Strategy")
    
    # Initialize strategy
    strategy = ConcentratedFollowerStrategy()
    
    # Analyze pool
    analysis = strategy.analyze(
        pool_name="WETH-USDC",
        capital_usd=5000
    )
    
    log.info(f"Analysis: {analysis}")
    
    # Execute (dry run - won't actually send transactions if not implemented)
    tx_hashes = strategy.execute(analysis)
    
    log.info(f"Transactions: {tx_hashes}")


def example_check_config():
    """Example: Check configuration."""
    log.info("Example: Check Configuration")
    
    config = get_config()
    
    log.info(f"RPC URL: {config.rpc_url}")
    log.info(f"Chain ID: {config.chain_id}")
    
    enabled_pools = config.get_enabled_pools()
    log.info(f"Enabled pools: {len(enabled_pools)}")
    
    for pool in enabled_pools:
        log.info(f"  - {pool['name']}: {pool['token0']}/{pool['token1']}")


def example_calculate_optimal_range():
    """Example: Calculate optimal liquidity range."""
    from src.optimizer.liquidity_optimizer import get_optimizer
    
    log.info("Example: Calculate Optimal Range")
    
    optimizer = get_optimizer()
    
    # This will fail without actual price data, but shows the interface
    try:
        lower_tick, upper_tick, metadata = optimizer.calculate_optimal_range(
            pool_name="WETH-USDC",
            current_price=2500.0,  # $2500 ETH
            capital_usd=10000,
            strategy_type="concentrated_follower"
        )
        
        log.info(f"Optimal range: [{lower_tick}, {upper_tick}]")
        log.info(f"Metadata: {metadata}")
    
    except NotImplementedError as e:
        log.warning(f"Not implemented yet: {e}")


if __name__ == '__main__':
    log.info("=" * 80)
    log.info("AMM Optimizer Examples")
    log.info("=" * 80)
    
    # Run examples
    example_check_config()
    print()
    
    # Uncomment to run other examples:
    # example_calculate_optimal_range()
    # example_concentrated_follower()
