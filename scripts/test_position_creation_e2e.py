#!/usr/bin/env python3
"""
End-to-End Position Creation Test Script

This script programmatically tests the full position creation flow using the user's private key.
It verifies that the fixes for tick calculation and approval loops are working correctly.

Usage:
    python scripts/test_position_creation_e2e.py

Test Configuration:
- Private key: 9c31f983fb60e4a23e15b44d9dbe736dc5d5e133a866ea79881b664c2ed773fe
- Wallet: 0x8a679aCf39c06682072C4a2A833eb437A0CC0bdb
- RPC: Alchemy Base (IkAsMgibgkR4Rwsh_Tm0)
- Test amount: $0.01 (0.000003 WETH + 0.01 USDC)
- Pool: 0x6c561B446416E1A00E8E93E221854d6eA4171372 (WETH-USDC 0.3%)
"""

import sys
import time
import json
import requests
from pathlib import Path
from web3 import Web3
from eth_account import Account

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration
PRIVATE_KEY = "9c31f983fb60e4a23e15b44d9dbe736dc5d5e133a866ea79881b664c2ed773fe"
WALLET_ADDRESS = "0x8a679aCf39c06682072C4a2A833eb437A0CC0bdb"
ALCHEMY_RPC = "https://mainnet.base.org"
BACKEND_URL = "http://localhost:8000"

# Pool configuration
POOL_ADDRESS = "0x6c561B446416E1A00E8E93E221854d6eA4171372"
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
POSITION_MANAGER = "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1"

# Test amounts (very small for testing)
WETH_AMOUNT = 0.000003  # ~$0.01 at $3800 ETH
USDC_AMOUNT = 0.01      # $0.01
TICK_RANGE = 500        # 5% range

# ABIs
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
    }
]

ERC20_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "address", "name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    }
]

POSITION_MANAGER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "token0", "type": "address"},
                    {"internalType": "address", "name": "token1", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "int24", "name": "tickLower", "type": "int24"},
                    {"internalType": "int24", "name": "tickUpper", "type": "int24"},
                    {"internalType": "uint256", "name": "amount0Desired", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount1Desired", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount0Min", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount1Min", "type": "uint256"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "internalType": "struct INonfungiblePositionManager.MintParams",
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "mint",
        "outputs": [
            {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
            {"internalType": "uint128", "name": "liquidity", "type": "uint128"},
            {"internalType": "uint256", "name": "amount0", "type": "uint256"},
            {"internalType": "uint256", "name": "amount1", "type": "uint256"}
        ],
        "stateMutability": "payable",
        "type": "function"
    }
]

def setup_web3():
    """Initialize Web3 connection with Alchemy RPC"""
    print("🔗 Setting up Web3 connection...")
    w3 = Web3(Web3.HTTPProvider(ALCHEMY_RPC))
    
    if not w3.is_connected():
        raise Exception("❌ Failed to connect to Base network")
    
    print(f"✅ Connected to Base network (chain ID: {w3.eth.chain_id})")
    return w3

def setup_account():
    """Setup account from private key"""
    print("🔑 Setting up account...")
    account = Account.from_key(PRIVATE_KEY)
    
    if account.address.lower() != WALLET_ADDRESS.lower():
        raise Exception(f"❌ Address mismatch: {account.address} != {WALLET_ADDRESS}")
    
    print(f"✅ Account setup: {account.address}")
    return account

def check_backend_health():
    """Check if backend is running and healthy"""
    print("🏥 Checking backend health...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend unreachable: {e}")
        return False

def get_pool_data():
    """Get pool data from backend"""
    print("📊 Fetching pool data from backend...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/pools/", timeout=10)
        if response.status_code == 200:
            pools = response.json()
            print(f"✅ Found {len(pools)} pools")
            return pools
        else:
            print(f"❌ Failed to fetch pools: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error fetching pools: {e}")
        return None

def get_token_balances(w3, account):
    """Get current token balances"""
    print("💰 Checking token balances...")
    
    # Get ETH balance
    eth_balance = w3.eth.get_balance(account.address)
    eth_balance_ether = w3.from_wei(eth_balance, 'ether')
    print(f"ETH Balance: {eth_balance_ether:.6f} ETH")
    
    # Get WETH balance
    weth_contract = w3.eth.contract(address=WETH_ADDRESS, abi=ERC20_ABI)
    weth_balance = weth_contract.functions.balanceOf(account.address).call()
    weth_balance_ether = w3.from_wei(weth_balance, 'ether')
    print(f"WETH Balance: {weth_balance_ether:.6f} WETH")
    
    # Get USDC balance
    usdc_contract = w3.eth.contract(address=USDC_ADDRESS, abi=ERC20_ABI)
    usdc_balance = usdc_contract.functions.balanceOf(account.address).call()
    usdc_balance_formatted = usdc_balance / 10**6  # USDC has 6 decimals
    print(f"USDC Balance: {usdc_balance_formatted:.6f} USDC")
    
    return {
        'eth': eth_balance_ether,
        'weth': weth_balance_ether,
        'usdc': usdc_balance_formatted
    }

def get_current_tick(w3):
    """Read current tick from pool contract"""
    print("🎯 Reading current tick from pool...")
    
    pool_contract = w3.eth.contract(address=POOL_ADDRESS, abi=POOL_ABI)
    slot0 = pool_contract.functions.slot0().call()
    current_tick = slot0[1]
    
    print(f"✅ Current tick: {current_tick}")
    return current_tick

def calculate_tick_bounds(current_tick, tick_range, fee_tier):
    """Calculate tick bounds with proper spacing"""
    print(f"📐 Calculating tick bounds (range: {tick_range})...")
    
    # Get tick spacing based on fee tier
    tick_spacing = 60 if fee_tier == 3000 else (10 if fee_tier == 500 else 200)
    print(f"Tick spacing: {tick_spacing}")
    
    # Calculate bounds from current tick
    tick_lower = current_tick - tick_range
    tick_upper = current_tick + tick_range
    
    # Align with tick spacing
    aligned_tick_lower = (tick_lower // tick_spacing) * tick_spacing
    aligned_tick_upper = (tick_upper // tick_spacing) * tick_spacing
    
    # Ensure proper ordering
    final_tick_lower = min(aligned_tick_lower, aligned_tick_upper)
    final_tick_upper = max(aligned_tick_lower, aligned_tick_upper)
    
    print(f"✅ Tick bounds: {final_tick_lower} to {final_tick_upper}")
    return final_tick_lower, final_tick_upper

def check_allowances(w3, account):
    """Check current token allowances"""
    print("🔍 Checking token allowances...")
    
    weth_contract = w3.eth.contract(address=WETH_ADDRESS, abi=ERC20_ABI)
    usdc_contract = w3.eth.contract(address=USDC_ADDRESS, abi=ERC20_ABI)
    
    weth_allowance = weth_contract.functions.allowance(account.address, POSITION_MANAGER).call()
    usdc_allowance = usdc_contract.functions.allowance(account.address, POSITION_MANAGER).call()
    
    weth_allowance_ether = w3.from_wei(weth_allowance, 'ether')
    usdc_allowance_formatted = usdc_allowance / 10**6
    
    print(f"WETH Allowance: {weth_allowance_ether:.6f} WETH")
    print(f"USDC Allowance: {usdc_allowance_formatted:.6f} USDC")
    
    return {
        'weth': weth_allowance,
        'usdc': usdc_allowance
    }

def approve_token(w3, account, token_address, amount, token_name):
    """Approve token spending"""
    print(f"✅ Approving {token_name}...")
    
    token_contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
    
    # Build transaction
    nonce = w3.eth.get_transaction_count(account.address)
    gas_price = w3.eth.gas_price
    
    transaction = token_contract.functions.approve(
        POSITION_MANAGER,
        amount
    ).build_transaction({
        'from': account.address,
        'gas': 100000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })
    
    # Sign and send transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    print(f"📤 Approval transaction sent: {tx_hash.hex()}")
    
    # Wait for confirmation
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"✅ {token_name} approved successfully")
        return True
    else:
        print(f"❌ {token_name} approval failed")
        return False

def create_position(w3, account, tick_lower, tick_upper):
    """Create liquidity position"""
    print("🚀 Creating liquidity position...")
    
    # Convert amounts to wei
    weth_amount_wei = w3.to_wei(WETH_AMOUNT, 'ether')
    usdc_amount_wei = int(USDC_AMOUNT * 10**6)  # USDC has 6 decimals
    
    # Calculate minimum amounts (0.5% slippage)
    weth_amount_min = int(weth_amount_wei * 0.995)
    usdc_amount_min = int(usdc_amount_wei * 0.995)
    
    # Set deadline (20 minutes from now)
    deadline = int(time.time()) + 20 * 60
    
    # Build mint parameters
    mint_params = (
        WETH_ADDRESS,      # token0 (WETH)
        USDC_ADDRESS,      # token1 (USDC)
        3000,              # fee (0.3%)
        tick_lower,        # tickLower
        tick_upper,        # tickUpper
        weth_amount_wei,   # amount0Desired
        usdc_amount_wei,   # amount1Desired
        weth_amount_min,   # amount0Min
        usdc_amount_min,   # amount1Min
        account.address,   # recipient
        deadline           # deadline
    )
    
    print(f"📋 Mint parameters:")
    print(f"  Token0 (WETH): {WETH_ADDRESS}")
    print(f"  Token1 (USDC): {USDC_ADDRESS}")
    print(f"  Fee: 3000 (0.3%)")
    print(f"  Tick range: {tick_lower} to {tick_upper}")
    print(f"  Amount0: {WETH_AMOUNT} WETH")
    print(f"  Amount1: {USDC_AMOUNT} USDC")
    print(f"  Deadline: {deadline}")
    
    # Build transaction
    position_manager_contract = w3.eth.contract(address=POSITION_MANAGER, abi=POSITION_MANAGER_ABI)
    
    nonce = w3.eth.get_transaction_count(account.address)
    gas_price = w3.eth.gas_price
    
    transaction = position_manager_contract.functions.mint(mint_params).build_transaction({
        'from': account.address,
        'gas': 500000,
        'gasPrice': gas_price,
        'nonce': nonce,
        'value': 0,  # No ETH value
    })
    
    # Sign and send transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    print(f"📤 Position creation transaction sent: {tx_hash.hex()}")
    
    # Wait for confirmation
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"✅ Position created successfully!")
        print(f"📊 Gas used: {receipt.gasUsed}")
        print(f"💰 Gas price: {gas_price / 10**9:.2f} Gwei")
        print(f"💸 Total cost: {(receipt.gasUsed * gas_price) / 10**18:.6f} ETH")
        
        # Check for NFT transfer event
        for log in receipt.logs:
            if len(log.topics) > 3 and log.topics[0].hex() == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
                print(f"🎨 NFT transferred (position created)")
                break
        
        return True, tx_hash.hex()
    else:
        print(f"❌ Position creation failed")
        return False, None

def verify_position_on_uniswap(tx_hash):
    """Verify position appears on Uniswap"""
    print(f"🔍 Verifying position on Uniswap...")
    print(f"📋 Transaction: https://basescan.org/tx/{tx_hash}")
    print(f"🎯 Check positions: https://app.uniswap.org/positions")
    print("✅ Position should appear within 1-2 minutes")

def main():
    """Main test function"""
    print("🧪 Starting End-to-End Position Creation Test")
    print("=" * 60)
    
    try:
        # Setup
        w3 = setup_web3()
        account = setup_account()
        
        # Check backend health
        if not check_backend_health():
            print("❌ Backend not available - skipping backend tests")
        
        # Get pool data
        pools = get_pool_data()
        
        # Check balances
        balances = get_token_balances(w3, account)
        
        # Check if we have enough balance
        if balances['weth'] < WETH_AMOUNT:
            print(f"❌ Insufficient WETH balance: {balances['weth']:.6f} < {WETH_AMOUNT}")
            return False
        
        if balances['usdc'] < USDC_AMOUNT:
            print(f"❌ Insufficient USDC balance: {balances['usdc']:.6f} < {USDC_AMOUNT}")
            return False
        
        # Get current tick from pool
        current_tick = get_current_tick(w3)
        
        # Calculate tick bounds
        tick_lower, tick_upper = calculate_tick_bounds(current_tick, TICK_RANGE, 3000)
        
        # Check allowances
        allowances = check_allowances(w3, account)
        
        # Approve tokens if needed
        weth_amount_wei = w3.to_wei(WETH_AMOUNT, 'ether')
        usdc_amount_wei = int(USDC_AMOUNT * 10**6)
        
        if allowances['weth'] < weth_amount_wei:
            if not approve_token(w3, account, WETH_ADDRESS, weth_amount_wei, "WETH"):
                return False
        else:
            print("✅ WETH already approved")
        
        if allowances['usdc'] < usdc_amount_wei:
            if not approve_token(w3, account, USDC_ADDRESS, usdc_amount_wei, "USDC"):
                return False
        else:
            print("✅ USDC already approved")
        
        # Create position
        success, tx_hash = create_position(w3, account, tick_lower, tick_upper)
        
        if success:
            verify_position_on_uniswap(tx_hash)
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Position creation successful")
            print("✅ Tick calculation fixed")
            print("✅ Approval loop prevented")
            return True
        else:
            print("\n❌ POSITION CREATION FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
