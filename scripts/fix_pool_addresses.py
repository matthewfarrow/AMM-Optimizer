#!/usr/bin/env python3
"""
FIX POOL ADDRESSES - CRITICAL HACKATHON FIX
Identifies and fixes the pool address issues
"""

import requests
import json
import time
from web3 import Web3

class PoolAddressFixer:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.rpc_url = "https://mainnet.base.org"
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Uniswap V3 Factory on Base
        self.factory_address = "0x33128a8fC17869897dcE68Ed026d694621f6FDfD"
        
        # Token addresses (checksummed)
        self.weth_address = self.w3.to_checksum_address("0x4200000000000000000000000000000000000006")
        self.usdc_address = self.w3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
        self.dai_address = self.w3.to_checksum_address("0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb")
        
        # Position Manager
        self.position_manager = self.w3.to_checksum_address("0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1")
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def get_pool_address(self, token0, token1, fee):
        """Get pool address from Uniswap V3 Factory"""
        try:
            # getPool function selector: 0x1698ee82
            # Parameters: address tokenA, address tokenB, uint24 fee
            function_selector = "0x1698ee82"
            
            # Encode parameters
            token0_padded = token0[2:].zfill(64)
            token1_padded = token1[2:].zfill(64)
            fee_padded = hex(fee)[2:].zfill(64)
            
            data = function_selector + token0_padded + token1_padded + fee_padded
            
            # Call the contract
            result = self.w3.eth.call({
                'to': self.factory_address,
                'data': data
            })
            
            # Decode result (returns address)
            pool_address = "0x" + result.hex()[-40:]
            return self.w3.to_checksum_address(pool_address)
            
        except Exception as e:
            self.log(f"❌ Error getting pool address: {e}", "ERROR")
            return None
    
    def check_pool_exists(self, pool_address):
        """Check if pool contract exists"""
        try:
            code = self.w3.eth.get_code(pool_address)
            return len(code) > 2
        except Exception as e:
            self.log(f"❌ Error checking pool existence: {e}", "ERROR")
            return False
    
    def get_real_pool_addresses(self):
        """Get real pool addresses from Uniswap V3 Factory"""
        self.log("🔍 Getting real pool addresses from Uniswap V3 Factory...")
        
        pools = []
        
        # WETH-USDC pools
        weth_usdc_005 = self.get_pool_address(self.weth_address, self.usdc_address, 500)
        weth_usdc_03 = self.get_pool_address(self.weth_address, self.usdc_address, 3000)
        
        # WETH-DAI pools  
        weth_dai_005 = self.get_pool_address(self.weth_address, self.dai_address, 500)
        weth_dai_03 = self.get_pool_address(self.weth_address, self.dai_address, 3000)
        
        # Check which pools exist
        pool_configs = [
            ("WETH-USDC 0.05%", weth_usdc_005, 500),
            ("WETH-USDC 0.3%", weth_usdc_03, 3000),
            ("WETH-DAI 0.05%", weth_dai_005, 500),
            ("WETH-DAI 0.3%", weth_dai_03, 3000)
        ]
        
        for name, address, fee in pool_configs:
            if address and address != "0x0000000000000000000000000000000000000000":
                exists = self.check_pool_exists(address)
                if exists:
                    self.log(f"✅ {name}: {address} (EXISTS)")
                    pools.append({
                        'name': name,
                        'address': address,
                        'fee_tier': fee,
                        'token0': 'WETH',
                        'token1': 'USDC' if 'USDC' in name else 'DAI',
                        'token0_address': self.weth_address,
                        'token1_address': self.usdc_address if 'USDC' in name else self.dai_address
                    })
                else:
                    self.log(f"❌ {name}: {address} (DOES NOT EXIST)", "ERROR")
            else:
                self.log(f"❌ {name}: Pool not found in factory", "ERROR")
        
        return pools
    
    def check_position_manager(self):
        """Check if PositionManager exists"""
        self.log("🔧 Checking NonfungiblePositionManager...")
        
        try:
            code = self.w3.eth.get_code(self.position_manager)
            if len(code) > 2:
                self.log(f"✅ PositionManager exists at {self.position_manager}")
                return True
            else:
                self.log(f"❌ PositionManager does not exist at {self.position_manager}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error checking PositionManager: {e}", "ERROR")
            return False
    
    def update_backend_pools(self, real_pools):
        """Update backend with real pool addresses"""
        self.log("🔄 Updating backend with real pool addresses...")
        
        # This would update the backend pools.py file
        # For now, just log what needs to be updated
        self.log("📋 Backend update needed:")
        for pool in real_pools:
            self.log(f"  - {pool['name']}: {pool['address']}")
    
    def run_fix(self):
        """Run the complete fix process"""
        self.log("🚀 Starting Pool Address Fix Process")
        self.log("=" * 60)
        
        # Step 1: Check PositionManager
        if not self.check_position_manager():
            self.log("❌ PositionManager issue - this needs to be fixed first!", "ERROR")
            return False
        
        # Step 2: Get real pool addresses
        real_pools = self.get_real_pool_addresses()
        
        if not real_pools:
            self.log("❌ No valid pools found - this is the main issue!", "ERROR")
            return False
        
        # Step 3: Update backend
        self.update_backend_pools(real_pools)
        
        self.log("=" * 60)
        self.log("📊 FIX SUMMARY")
        self.log("=" * 60)
        self.log(f"✅ Found {len(real_pools)} valid pools")
        self.log("🎯 Next steps:")
        self.log("1. Update backend pools.py with real addresses")
        self.log("2. Update frontend contracts.ts with correct addresses")
        self.log("3. Test position creation with real pools")
        
        return True

def main():
    print("🔧 POOL ADDRESS FIXER")
    print("=" * 60)
    print("Fixing pool addresses to resolve transaction failures")
    print("=" * 60)
    
    fixer = PoolAddressFixer()
    fixer.run_fix()

if __name__ == "__main__":
    main()
