"""
Find available Uniswap V3 pools on Base Sepolia testnet.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dex.web3_client import get_web3_client
from src.utils.config import get_config
from src.utils.logger import log
from web3 import Web3

# Common testnet tokens on Base Sepolia
TESTNET_TOKENS = {
    'WETH': '0x4200000000000000000000000000000000000006',  # Wrapped ETH
    'USDC': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',  # Test USDC
    'DAI': '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',   # Test DAI (if exists)
    'USDT': '0xf08A50178dfcDe18524640EA6618a1f965821715',  # Test USDT (if exists)
}

# Fee tiers
FEE_TIERS = [500, 3000, 10000]  # 0.05%, 0.3%, 1%

FACTORY_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "tokenA", "type": "address"},
            {"internalType": "address", "name": "tokenB", "type": "address"},
            {"internalType": "uint24", "name": "fee", "type": "uint24"}
        ],
        "name": "getPool",
        "outputs": [{"internalType": "address", "name": "pool", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]


def find_pools():
    """Find available Uniswap V3 pools on testnet."""
    log.info("Finding Uniswap V3 pools on Base Sepolia testnet...")
    
    config = get_config()
    client = get_web3_client()
    w3 = client.w3
    
    factory_address = config.get('uniswap.factory_address')
    log.info(f"Factory address: {factory_address}")
    
    factory = w3.eth.contract(
        address=Web3.to_checksum_address(factory_address),
        abi=FACTORY_ABI
    )
    
    found_pools = []
    
    # Try all token pairs
    token_pairs = [
        ('WETH', 'USDC'),
        ('WETH', 'DAI'),
        ('WETH', 'USDT'),
        ('USDC', 'DAI'),
        ('USDC', 'USDT'),
    ]
    
    for token0_name, token1_name in token_pairs:
        if token0_name not in TESTNET_TOKENS or token1_name not in TESTNET_TOKENS:
            continue
            
        token0 = TESTNET_TOKENS[token0_name]
        token1 = TESTNET_TOKENS[token1_name]
        
        for fee in FEE_TIERS:
            try:
                pool_address = factory.functions.getPool(
                    Web3.to_checksum_address(token0),
                    Web3.to_checksum_address(token1),
                    fee
                ).call()
                
                if pool_address != '0x0000000000000000000000000000000000000000':
                    pool_name = f"{token0_name}-{token1_name}"
                    fee_percent = fee / 10000
                    
                    found_pools.append({
                        'name': pool_name,
                        'address': pool_address,
                        'token0': token0_name,
                        'token1': token1_name,
                        'fee': fee,
                        'fee_percent': fee_percent
                    })
                    
                    log.info(f"✓ Found: {pool_name} (fee: {fee_percent}%)")
                    log.info(f"  Address: {pool_address}")
                    
            except Exception as e:
                log.debug(f"No pool for {token0_name}-{token1_name} @ {fee/10000}%: {e}")
    
    # Print summary
    log.info("=" * 80)
    log.info(f"Found {len(found_pools)} pools on Base Sepolia")
    log.info("=" * 80)
    
    if found_pools:
        print("\n# Add these to config/pools.yaml:")
        print("\npools:")
        for pool in found_pools:
            print(f"  - name: {pool['name']}")
            print(f"    address: '{pool['address']}'")
            print(f"    token0: {pool['token0']}")
            print(f"    token1: {pool['token1']}")
            print(f"    fee: {pool['fee']}")
            print(f"    enabled: true")
            print()
    else:
        log.warning("No pools found! You may need to create pools on testnet first.")
        log.info("\nTo create a test pool, you can:")
        log.info("1. Go to https://app.uniswap.org/")
        log.info("2. Switch to Base Sepolia network")
        log.info("3. Create a new pool with test tokens")
    
    return found_pools


if __name__ == '__main__':
    try:
        pools = find_pools()
        
        if pools:
            log.info("\n✅ Testnet pools are available for testing!")
        else:
            log.warning("\n⚠️  No testnet pools found")
            
    except Exception as e:
        log.error(f"Error: {e}", exc_info=True)
