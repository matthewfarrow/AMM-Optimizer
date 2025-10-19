"""
Check wallet balance and connection to Base Sepolia testnet.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dex.web3_client import get_web3_client
from src.utils.logger import log
from src.utils.config import get_config


def check_testnet_setup():
    """Check if testnet is properly configured."""
    log.info("Checking Base Sepolia Testnet Setup...")
    log.info("=" * 80)
    
    try:
        # Get config
        config = get_config()
        chain_id = config.get('base.chain_id')
        rpc_url = config.get('base.rpc_url')
        
        log.info(f"Network: {'Base Sepolia' if chain_id == 84532 else 'Base Mainnet'}")
        log.info(f"Chain ID: {chain_id}")
        log.info(f"RPC URL: {rpc_url}")
        
        if chain_id != 84532:
            log.warning("⚠️  Not configured for Base Sepolia testnet!")
            log.info("To use testnet: cp .env.testnet .env")
            return False
        
        # Get client
        client = get_web3_client()
        w3 = client.w3
        
        log.info(f"Wallet Address: {client.address}")
        
        # Check connection
        if not w3.is_connected():
            log.error("❌ Not connected to network!")
            return False
        
        log.info("✅ Connected to Base Sepolia")
        
        # Check balance
        balance_wei = w3.eth.get_balance(client.address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        
        log.info(f"Balance: {balance_eth:.6f} ETH")
        
        if balance_eth == 0:
            log.warning("⚠️  No ETH in wallet!")
            log.info("\nGet test ETH from:")
            log.info("  → https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet")
            return False
        
        if balance_eth < 0.01:
            log.warning(f"⚠️  Low balance: {balance_eth:.6f} ETH")
            log.info("Recommend at least 0.01 ETH for testing")
        else:
            log.info(f"✅ Sufficient balance: {balance_eth:.6f} ETH")
        
        # Check gas price
        gas_price = w3.eth.gas_price
        gas_price_gwei = w3.from_wei(gas_price, 'gwei')
        log.info(f"Current gas price: {gas_price_gwei:.2f} gwei")
        
        # Estimate transaction cost
        estimated_gas = 200000  # Typical for LP operations
        tx_cost_wei = gas_price * estimated_gas
        tx_cost_eth = w3.from_wei(tx_cost_wei, 'ether')
        log.info(f"Estimated tx cost: {tx_cost_eth:.6f} ETH")
        
        # Calculate how many txs possible
        possible_txs = int(balance_eth / tx_cost_eth) if tx_cost_eth > 0 else 0
        log.info(f"Possible transactions: ~{possible_txs}")
        
        log.info("=" * 80)
        log.info("✅ Testnet setup complete!")
        log.info("\nNext steps:")
        log.info("1. Find available pools: python scripts/find_pools.py")
        log.info("2. Run optimizer: python scripts/run_optimizer.py --pool WETH-USDC --capital 100 --once")
        
        return True
        
    except Exception as e:
        log.error(f"❌ Error checking setup: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    success = check_testnet_setup()
    sys.exit(0 if success else 1)
