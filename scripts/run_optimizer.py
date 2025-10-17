"""
Main execution script for the optimizer.
"""
import sys
import time
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import get_config
from src.utils.logger import log
from src.strategies.concentrated_follower import ConcentratedFollowerStrategy
from src.strategies.multi_position import MultiPositionStrategy


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='AMM Liquidity Optimizer')
    
    parser.add_argument(
        '--strategy',
        type=str,
        default='concentrated_follower',
        choices=['concentrated_follower', 'multi_position'],
        help='Strategy to use'
    )
    
    parser.add_argument(
        '--pool',
        type=str,
        required=True,
        help='Pool name (e.g., AVAX-USDC)'
    )
    
    parser.add_argument(
        '--capital',
        type=float,
        required=True,
        help='Capital in USD'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Check interval in seconds (default: 300)'
    )
    
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (no loop)'
    )
    
    return parser.parse_args()


def create_strategy(strategy_type: str):
    """Create strategy instance."""
    if strategy_type == 'concentrated_follower':
        return ConcentratedFollowerStrategy()
    elif strategy_type == 'multi_position':
        return MultiPositionStrategy(num_positions=3)
    else:
        raise ValueError(f"Unknown strategy: {strategy_type}")


def run_iteration(strategy, pool_name: str, capital_usd: float):
    """Run one iteration of the strategy."""
    try:
        log.info("=" * 80)
        log.info(f"Running strategy: {strategy.name}")
        log.info(f"Pool: {pool_name}, Capital: ${capital_usd:,.2f}")
        log.info("=" * 80)
        
        # Analyze
        analysis = strategy.analyze(pool_name, capital_usd)
        
        log.info(f"Analysis result: {analysis['action']}")
        
        # Execute
        tx_hashes = strategy.execute(analysis)
        
        if tx_hashes:
            log.info(f"Executed {len(tx_hashes)} transactions")
            for tx in tx_hashes:
                log.info(f"  TX: {tx}")
        
        # Show performance
        metrics = strategy.get_performance_metrics()
        log.info("Performance metrics:")
        for key, value in metrics.items():
            log.info(f"  {key}: {value}")
        
        return True
    
    except Exception as e:
        log.error(f"Error in iteration: {e}", exc_info=True)
        return False


def main():
    """Main entry point."""
    args = parse_args()
    
    log.info("AMM Liquidity Optimizer Starting")
    log.info(f"Strategy: {args.strategy}")
    log.info(f"Pool: {args.pool}")
    log.info(f"Capital: ${args.capital:,.2f}")
    
    # Load config
    config = get_config()
    
    # Verify pool is configured
    pool_config = config.get_pool_by_name(args.pool)
    if not pool_config:
        log.error(f"Pool {args.pool} not found in config")
        sys.exit(1)
    
    if not pool_config.get('enabled', False):
        log.warning(f"Pool {args.pool} is disabled in config")
    
    # Create strategy
    strategy = create_strategy(args.strategy)
    
    if args.once:
        # Run once
        log.info("Running once and exiting")
        success = run_iteration(strategy, args.pool, args.capital)
        sys.exit(0 if success else 1)
    
    # Run loop
    log.info(f"Running in loop mode (interval: {args.interval}s)")
    log.info("Press Ctrl+C to stop")
    
    try:
        while True:
            run_iteration(strategy, args.pool, args.capital)
            
            log.info(f"Sleeping for {args.interval} seconds...")
            time.sleep(args.interval)
    
    except KeyboardInterrupt:
        log.info("Interrupted by user")
        log.info("Shutting down gracefully...")
    
    except Exception as e:
        log.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    
    log.info("Optimizer stopped")


if __name__ == '__main__':
    main()
