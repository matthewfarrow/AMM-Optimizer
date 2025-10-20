#!/usr/bin/env python3
"""Check Base mainnet setup and balance."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dex.web3_client import get_web3_client
from src.dex.abis import ERC20_ABI
from web3 import Web3

def check_mainnet_setup():
    """Check mainnet connection and balances."""
    print("🔍 Checking Base Mainnet Setup...")
    print("=" * 80)
    
    # Get web3 client
    web3_client = get_web3_client()
    w3 = web3_client.w3
    wallet = web3_client.address
    
    # Check network
    chain_id = w3.eth.chain_id
    print(f"\n📡 Network Info:")
    print(f"  Chain ID: {chain_id}")
    print(f"  Network: {'Base Mainnet ✅' if chain_id == 8453 else 'Wrong Network ❌'}")
    print(f"  Wallet: {wallet}")
    
    if chain_id != 8453:
        print(f"\n❌ Not on Base Mainnet! Update your .env file:")
        print(f"  BASE_CHAIN_ID=8453")
        print(f"  BASE_RPC_URL=https://mainnet.base.org")
        return
    
    # Check ETH balance
    eth_balance = w3.eth.get_balance(wallet)
    eth_balance_float = w3.from_wei(eth_balance, 'ether')
    eth_usd = eth_balance_float * 4000  # Approximate ETH price
    
    print(f"\n💰 ETH Balance:")
    print(f"  {eth_balance_float:.6f} ETH (≈${eth_usd:.2f})")
    
    # Check WETH balance
    WETH = "0x4200000000000000000000000000000000000006"
    weth_contract = w3.eth.contract(
        address=Web3.to_checksum_address(WETH),
        abi=ERC20_ABI
    )
    weth_balance = weth_contract.functions.balanceOf(wallet).call()
    weth_balance_float = weth_balance / 1e18
    weth_usd = weth_balance_float * 4000
    
    print(f"\n💎 WETH Balance:")
    print(f"  {weth_balance_float:.6f} WETH (≈${weth_usd:.2f})")
    
    # Check USDC balance
    USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    usdc_contract = w3.eth.contract(
        address=Web3.to_checksum_address(USDC),
        abi=ERC20_ABI
    )
    usdc_balance = usdc_contract.functions.balanceOf(wallet).call()
    usdc_balance_float = usdc_balance / 1e6  # USDC has 6 decimals
    
    print(f"\n💵 USDC Balance:")
    print(f"  {usdc_balance_float:.2f} USDC")
    
    # Total value
    total_value = float(eth_usd) + float(weth_usd) + float(usdc_balance_float)
    print(f"\n💰 Total Portfolio Value: ≈${total_value:.2f}")
    
    # Recommendations based on balance
    print(f"\n📋 Testing Recommendations:")
    if total_value < 1:
        print(f"  ⚠️  Very low balance (${total_value:.2f})")
        print(f"  • Need at least $2-3 for micro-testing")
        print(f"  • Bridge more ETH from another network")
    elif total_value < 5:
        print(f"  ✅ Perfect for micro-testing! (${total_value:.2f})")
        print(f"  • Test positions: $0.20 - $0.50 each")
        print(f"  • Can do 3-5 test positions")
        print(f"  • Gas costs: ~$0.10 per transaction")
    elif total_value < 20:
        print(f"  ✅ Good for small testing! (${total_value:.2f})")
        print(f"  • Test positions: $1-2 each")
        print(f"  • Can do 5-10 test positions")
    else:
        print(f"  ✅ Great balance for testing! (${total_value:.2f})")
        print(f"  • Test positions: $5-10 each")
        print(f"  • Can do comprehensive testing")
    
    # Next steps
    print(f"\n🚀 Next Steps:")
    if eth_balance_float > 0 and weth_balance_float == 0 and usdc_balance_float == 0:
        print(f"  1. Wrap ETH to WETH: python3 scripts/wrap_eth.py --amount 0.0005")
        print(f"  2. Swap WETH to USDC: python3 scripts/swap_tokens.py --from WETH --to USDC --amount 0.0003")
        print(f"  3. Create LP: python3 scripts/test_create_position.py")
    elif weth_balance_float > 0 and usdc_balance_float == 0:
        print(f"  1. Swap WETH to USDC: python3 scripts/swap_tokens.py --from WETH --to USDC --amount 0.0003")
        print(f"  2. Create LP: python3 scripts/test_create_position.py")
    elif weth_balance_float > 0 and usdc_balance_float > 0:
        print(f"  ✅ You have both tokens! Ready to create LP position:")
        print(f"  python3 scripts/test_create_position.py")
    else:
        print(f"  1. Get some ETH on Base mainnet first")
        print(f"  2. Bridge from another network: https://bridge.base.org/")
    
    print(f"\n" + "=" * 80)
    print(f"✅ Mainnet setup complete!")

if __name__ == "__main__":
    check_mainnet_setup()
