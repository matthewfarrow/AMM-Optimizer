"""
Monitor Uniswap V3 pools on Base Mainnet.

This script helps you:
1. View all available pools
2. Check if a position is in/out of range
3. Calculate APR for each pool
4. Monitor price updates
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import requests
from decimal import Decimal
from web3 import Web3
from src.dex.web3_client import get_web3_client
from src.utils.config import get_config
from src.utils.logger import log

# Base Mainnet tokens
TOKENS = {
    'WETH': '0x4200000000000000000000000000000000000006',
    'USDC': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    'DAI': '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
    'USDbC': '0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA',
    'cbETH': '0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22',
}

# Known pools from discovery
POOLS = {
    'WETH-USDC-0.05%': {
        'address': '0xd0b53D9277642d899DF5C87A3966A349A798F224',
        'token0': 'WETH',
        'token1': 'USDC',
        'fee': 500,
        'decimals0': 18,
        'decimals1': 6,
    },
    'WETH-USDC-0.3%': {
        'address': '0x6c561B446416E1A00E8E93E221854d6eA4171372',
        'token0': 'WETH',
        'token1': 'USDC',
        'fee': 3000,
        'decimals0': 18,
        'decimals1': 6,
    },
    'WETH-USDbC-0.05%': {
        'address': '0x4C36388bE6F416A29C8d8Eee81C771cE6bE14B18',
        'token0': 'WETH',
        'token1': 'USDbC',
        'fee': 500,
        'decimals0': 18,
        'decimals1': 6,
    },
    'WETH-cbETH-0.05%': {
        'address': '0x10648BA41B8565907Cfa1496765fA4D95390aa0d',
        'token0': 'WETH',
        'token1': 'cbETH',
        'fee': 500,
        'decimals0': 18,
        'decimals1': 18,
    },
}

POOL_ABI = [
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"},
            {"internalType": "int24", "name": "tick", "type": "int24"},
            {"internalType": "uint16", "name": "observationIndex", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinality", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinalityNext", "type": "uint16"},
            {"internalType": "uint8", "name": "feeProtocol", "type": "uint8"},
            {"internalType": "bool", "name": "unlocked", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "liquidity",
        "outputs": [{"internalType": "uint128", "name": "", "type": "uint128"}],
        "stateMutability": "view",
        "type": "function"
    },
]


def get_pool_price(pool_address: str, decimals0: int, decimals1: int) -> tuple:
    """Get current pool price from on-chain data."""
    client = get_web3_client()
    w3 = client.w3
    
    pool = w3.eth.contract(
        address=Web3.to_checksum_address(pool_address),
        abi=POOL_ABI
    )
    
    slot0 = pool.functions.slot0().call()
    sqrt_price_x96 = slot0[0]
    current_tick = slot0[1]
    
    # Convert sqrtPriceX96 to actual price
    # price = (sqrtPriceX96 / 2^96)^2
    price = (sqrt_price_x96 / (2**96)) ** 2
    
    # Adjust for decimals
    price = price * (10 ** decimals0) / (10 ** decimals1)
    
    return price, current_tick


def get_dexscreener_price(token0: str, token1: str) -> dict:
    """Get price and APR data from DexScreener API."""
    # Map token symbols to addresses for API
    token0_addr = TOKENS.get(token0)
    token1_addr = TOKENS.get(token1)
    
    if not token0_addr or not token1_addr:
        return None
    
    try:
        # DexScreener API - search for pool
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token0_addr}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Find the pool on Base network
            for pair in data.get('pairs', []):
                if pair.get('chainId') == 'base':
                    # Check if it's the right pair
                    base_token = pair.get('baseToken', {}).get('symbol', '')
                    quote_token = pair.get('quoteToken', {}).get('symbol', '')
                    
                    if (base_token == token0 and quote_token == token1) or \
                       (base_token == token1 and quote_token == token0):
                        return {
                            'price': float(pair.get('priceUsd', 0)),
                            'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                            'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                            'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
                            'txns_24h': pair.get('txns', {}).get('h24', {}).get('buys', 0) + 
                                       pair.get('txns', {}).get('h24', {}).get('sells', 0),
                        }
        
        return None
    except Exception as e:
        log.warning(f"Could not fetch DexScreener data: {e}")
        return None


def tick_to_price(tick: int, decimals0: int, decimals1: int) -> float:
    """Convert tick to human-readable price."""
    price = 1.0001 ** tick
    price = price * (10 ** decimals0) / (10 ** decimals1)
    return price


def is_position_in_range(current_tick: int, tick_lower: int, tick_upper: int) -> bool:
    """Check if current price is within position range."""
    return tick_lower <= current_tick <= tick_upper


def estimate_apr(pool_info: dict, dex_data: dict) -> float:
    """
    Estimate APR based on pool volume and liquidity.
    
    Formula: APR = (24h_volume * fee_rate * 365) / liquidity
    """
    if not dex_data or dex_data.get('liquidity', 0) == 0:
        return 0.0
    
    volume_24h = dex_data.get('volume_24h', 0)
    liquidity = dex_data.get('liquidity', 1)  # Avoid division by zero
    fee_rate = pool_info['fee'] / 1_000_000  # Convert to decimal (e.g., 500 -> 0.0005)
    
    # APR = daily fees * 365 / liquidity
    daily_fees = volume_24h * fee_rate
    apr = (daily_fees * 365) / liquidity * 100
    
    return apr


def monitor_pools():
    """Monitor all available pools."""
    log.info("=" * 80)
    log.info("UNISWAP V3 POOL MONITOR - BASE MAINNET")
    log.info("=" * 80)
    log.info("")
    
    for pool_name, pool_info in POOLS.items():
        log.info(f"📊 {pool_name}")
        log.info(f"   Address: {pool_info['address']}")
        log.info(f"   Fee Tier: {pool_info['fee'] / 10000}%")
        
        try:
            # Get on-chain price
            time.sleep(0.5)  # Rate limit protection
            price, current_tick = get_pool_price(
                pool_info['address'],
                pool_info['decimals0'],
                pool_info['decimals1']
            )
            
            log.info(f"   Current Price: ${price:,.2f} (tick: {current_tick})")
            
            # Get market data from DexScreener
            time.sleep(1)  # API rate limit
            dex_data = get_dexscreener_price(pool_info['token0'], pool_info['token1'])
            
            if dex_data:
                log.info(f"   24h Volume: ${dex_data['volume_24h']:,.0f}")
                log.info(f"   Liquidity: ${dex_data['liquidity']:,.0f}")
                log.info(f"   24h Change: {dex_data['price_change_24h']:+.2f}%")
                log.info(f"   Transactions: {dex_data['txns_24h']:,}")
                
                # Calculate estimated APR
                apr = estimate_apr(pool_info, dex_data)
                log.info(f"   Estimated APR: {apr:.2f}%")
            
            log.info("")
            
        except Exception as e:
            log.error(f"   Error: {e}")
            log.info("")
    
    log.info("=" * 80)
    log.info("PRICE DATA SOURCE")
    log.info("=" * 80)
    log.info("• On-chain: Real-time from pool's slot0() function")
    log.info("• Market data: DexScreener API (updates every ~60 seconds)")
    log.info("• Your optimizer: Fetches price before each operation")
    log.info("")
    log.info("💡 Tips:")
    log.info("• Higher volume pools = more fees = higher APR")
    log.info("• Lower fee tiers = more competitive = more volume")
    log.info("• Monitor your position tick range vs current tick")
    log.info("• Position out of range = no fees earned")
    log.info("")


def check_position_range(pool_name: str, tick_lower: int, tick_upper: int):
    """Check if your position is in range."""
    if pool_name not in POOLS:
        log.error(f"Pool {pool_name} not found!")
        return
    
    pool_info = POOLS[pool_name]
    
    log.info(f"Checking position range for {pool_name}...")
    
    try:
        price, current_tick = get_pool_price(
            pool_info['address'],
            pool_info['decimals0'],
            pool_info['decimals1']
        )
        
        in_range = is_position_in_range(current_tick, tick_lower, tick_upper)
        
        lower_price = tick_to_price(tick_lower, pool_info['decimals0'], pool_info['decimals1'])
        upper_price = tick_to_price(tick_upper, pool_info['decimals0'], pool_info['decimals1'])
        
        log.info(f"  Current Tick: {current_tick}")
        log.info(f"  Current Price: ${price:,.2f}")
        log.info(f"  Your Range: {tick_lower} to {tick_upper}")
        log.info(f"  Price Range: ${lower_price:,.2f} to ${upper_price:,.2f}")
        log.info(f"  Status: {'✅ IN RANGE' if in_range else '❌ OUT OF RANGE'}")
        
        if not in_range:
            if current_tick < tick_lower:
                log.info(f"  ⬇️  Price is BELOW your range (rebalance needed)")
            else:
                log.info(f"  ⬆️  Price is ABOVE your range (rebalance needed)")
        
    except Exception as e:
        log.error(f"Error checking position: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor Uniswap V3 pools")
    parser.add_argument('--check-range', action='store_true', help='Check if position is in range')
    parser.add_argument('--pool', type=str, help='Pool name (e.g., WETH-USDC-0.05%)')
    parser.add_argument('--tick-lower', type=int, help='Lower tick of your position')
    parser.add_argument('--tick-upper', type=int, help='Upper tick of your position')
    
    args = parser.parse_args()
    
    if args.check_range:
        if not all([args.pool, args.tick_lower, args.tick_upper]):
            log.error("Must provide --pool, --tick-lower, and --tick-upper")
            sys.exit(1)
        check_position_range(args.pool, args.tick_lower, args.tick_upper)
    else:
        monitor_pools()
