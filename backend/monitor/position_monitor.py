"""
Extended position monitoring service
Integrates with the new smart contract and supports multi-user monitoring
"""

import asyncio
import time
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime, timedelta
import json

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.dex.uniswap import get_uniswap
from src.data.price_data import get_price_collector
from src.utils.config import get_config
from src.utils.logger import log as logger

class MultiUserPositionMonitor:
    """Monitors multiple user positions and handles rebalancing via smart contract"""
    
    def __init__(self, backend_url: str = "http://localhost:8000", contract_address: str = None):
        """
        Initialize the multi-user position monitor
        
        Args:
            backend_url: URL of the FastAPI backend
            contract_address: Address of the deployed LiquidityManager contract
        """
        self.backend_url = backend_url
        self.contract_address = contract_address
        self.running = False
        
        # Initialize existing components
        self.config = get_config()
        self.uniswap = get_uniswap()
        self.price_collector = get_price_collector()
        
        # Cache for position data
        self.position_cache = {}
        self.last_check_times = {}
        
        # Smart contract integration
        if contract_address:
            self.liquidity_manager = self.uniswap.w3.eth.contract(
                address=contract_address,
                abi=self._get_liquidity_manager_abi()
            )
        else:
            self.liquidity_manager = None
            logger.warning("No contract address provided - monitoring will be simulation only")
        
        logger.info("MultiUserPositionMonitor initialized")
        logger.info(f"Backend URL: {backend_url}")
        logger.info(f"Contract Address: {contract_address}")
    
    def _get_liquidity_manager_abi(self) -> list:
        """Get the LiquidityManager contract ABI"""
        # Simplified ABI for the key functions we need
        return [
            {
                "inputs": [{"internalType": "bytes[]", "name": "commands", "type": "bytes[]"}],
                "name": "executeCommands",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
                "name": "isWhitelisted",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
                "name": "getUserPositions",
                "outputs": [{"components": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}, {"internalType": "address", "name": "token0", "type": "address"}, {"internalType": "address", "name": "token1", "type": "address"}, {"internalType": "uint24", "name": "fee", "type": "uint24"}, {"internalType": "int24", "name": "tickLower", "type": "int24"}, {"internalType": "int24", "name": "tickUpper", "type": "int24"}, {"internalType": "uint256", "name": "depositedAmount0", "type": "uint256"}, {"internalType": "uint256", "name": "depositedAmount1", "type": "uint256"}, {"internalType": "uint256", "name": "createdAt", "type": "uint256"}, {"internalType": "bool", "name": "active", "type": "bool"}], "internalType": "struct LiquidityManager.UserPosition[]", "name": "", "type": "tuple[]"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    async def get_active_positions(self) -> List[Dict[str, Any]]:
        """Fetch active positions from backend API"""
        try:
            response = requests.get(f"{self.backend_url}/api/positions/active/all")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching active positions: {e}")
            return []
    
    async def check_position_range(self, position: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a position is in range"""
        try:
            # Get pool address and current tick
            pool_address = position["pool_address"]
            tick_lower = position["tick_lower"]
            tick_upper = position["tick_upper"]
            
            # Get current tick from pool
            pool_contract = self.uniswap.w3.eth.contract(
                address=pool_address,
                abi=self.uniswap.get_pool_abi()
            )
            slot0 = pool_contract.functions.slot0().call()
            current_tick = slot0[1]
            
            in_range = tick_lower <= current_tick <= tick_upper
            
            return {
                "position_id": position["id"],
                "in_range": in_range,
                "current_tick": current_tick,
                "tick_lower": tick_lower,
                "tick_upper": tick_upper,
                "distance_from_lower": current_tick - tick_lower,
                "distance_from_upper": tick_upper - current_tick
            }
            
        except Exception as e:
            logger.error(f"Error checking position range for {position['id']}: {e}")
            return {
                "position_id": position["id"],
                "in_range": True,  # Assume in range on error
                "error": str(e)
            }
    
    async def calculate_rebalance_commands(self, position: Dict[str, Any], status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate commands needed to rebalance a position"""
        commands = []
        
        if not status.get("in_range", True):
            logger.info(f"Position {position['id']} is out of range, calculating rebalance commands")
            
            # For now, return a simple rebalance command
            # In production, this would be more sophisticated
            commands.append({
                "type": "decrease_liquidity",
                "token_id": position.get("token_id"),
                "liquidity": "100%",  # Remove all liquidity
                "amount0_min": 0,
                "amount1_min": 0,
                "deadline": int(time.time()) + 300
            })
            
            # Add swap command if needed
            if status["current_tick"] < status["tick_lower"]:
                # Price below range - sell token0 for token1
                commands.append({
                    "type": "swap",
                    "token_in": position["pool_address"].split("-")[0],  # Simplified
                    "token_out": position["pool_address"].split("-")[1],
                    "amount_in": position["amount0"] / 2,  # Sell half
                    "amount_out_min": 0,
                    "deadline": int(time.time()) + 300
                })
            elif status["current_tick"] > status["tick_upper"]:
                # Price above range - sell token1 for token0
                commands.append({
                    "type": "swap",
                    "token_in": position["pool_address"].split("-")[1],
                    "token_out": position["pool_address"].split("-")[0],
                    "amount_in": position["amount1"] / 2,
                    "amount_out_min": 0,
                    "deadline": int(time.time()) + 300
                })
            
            # Add new position creation command
            commands.append({
                "type": "create_position",
                "pool_address": position["pool_address"],
                "tick_lower": status["current_tick"] - 50,  # New range around current price
                "tick_upper": status["current_tick"] + 50,
                "amount0": position["amount0"],
                "amount1": position["amount1"]
            })
        
        return commands
    
    async def execute_rebalance_commands(self, commands: List[Dict[str, Any]]) -> bool:
        """Execute rebalance commands via smart contract"""
        if not commands:
            return True
        
        try:
            if not self.liquidity_manager:
                logger.warning("No contract available - simulating command execution")
                for i, command in enumerate(commands):
                    logger.info(f"Simulated command {i+1}: {command['type']}")
                    await asyncio.sleep(0.1)
                return True
            
            # Encode commands for smart contract
            encoded_commands = []
            for command in commands:
                encoded_cmd = self._encode_command(command)
                if encoded_cmd:
                    encoded_commands.append(encoded_cmd)
            
            if not encoded_commands:
                logger.warning("No valid commands to execute")
                return True
            
            logger.info(f"Executing {len(encoded_commands)} rebalance commands on contract")
            
            # Execute multicall transaction
            tx_hash = self.liquidity_manager.functions.executeCommands(encoded_commands).transact({
                'from': self.uniswap.web3_client.address,
                'gas': 500000,  # Adjust based on command complexity
                'gasPrice': self.uniswap.w3.eth.gas_price
            })
            
            # Wait for transaction confirmation
            receipt = self.uniswap.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                logger.info(f"Rebalance commands executed successfully: {tx_hash.hex()}")
                return True
            else:
                logger.error(f"Rebalance transaction failed: {tx_hash.hex()}")
                return False
            
        except Exception as e:
            logger.error(f"Error executing rebalance commands: {e}")
            return False
    
    def _encode_command(self, command: Dict[str, Any]) -> bytes:
        """Encode a command for the smart contract"""
        try:
            command_type = command['type']
            
            if command_type == 'decrease_liquidity':
                # Encode decreaseLiquidity call
                return self._encode_decrease_liquidity(command)
            elif command_type == 'swap':
                # Encode swap call
                return self._encode_swap(command)
            elif command_type == 'create_position':
                # Encode createPosition call
                return self._encode_create_position(command)
            else:
                logger.warning(f"Unknown command type: {command_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error encoding command {command}: {e}")
            return None
    
    def _encode_decrease_liquidity(self, command: Dict[str, Any]) -> bytes:
        """Encode decreaseLiquidity command"""
        # This would encode the actual function call
        # For now, return a placeholder
        return b'\x00' * 32
    
    def _encode_swap(self, command: Dict[str, Any]) -> bytes:
        """Encode swap command"""
        # This would encode the actual swap function call
        # For now, return a placeholder
        return b'\x00' * 32
    
    def _encode_create_position(self, command: Dict[str, Any]) -> bytes:
        """Encode createPosition command"""
        # This would encode the actual position creation call
        # For now, return a placeholder
        return b'\x00' * 32
    
    async def update_position_status(self, position_id: int, status: Dict[str, Any]):
        """Update position status in backend"""
        try:
            # This would update the position in the database
            # For now, just log the status
            logger.info(f"Position {position_id} status: {status}")
            
        except Exception as e:
            logger.error(f"Error updating position status: {e}")
    
    async def monitor_position(self, position: Dict[str, Any]):
        """Monitor a single position"""
        position_id = position["id"]
        user_address = position["user_address"]
        check_interval = position["check_interval"]
        
        # Check if enough time has passed since last check
        last_check = self.last_check_times.get(position_id, 0)
        if time.time() - last_check < check_interval:
            return
        
        logger.info(f"Checking position {position_id} for user {user_address}")
        
        # Check if position is in range
        status = await self.check_position_range(position)
        
        # Update last check time
        self.last_check_times[position_id] = time.time()
        
        # If out of range, calculate and execute rebalance commands
        if not status.get("in_range", True):
            logger.warning(f"Position {position_id} is out of range!")
            
            # Calculate rebalance commands
            commands = await self.calculate_rebalance_commands(position, status)
            
            if commands:
                # Execute commands
                success = await self.execute_rebalance_commands(commands)
                
                if success:
                    logger.info(f"Position {position_id} rebalanced successfully")
                else:
                    logger.error(f"Failed to rebalance position {position_id}")
        
        # Update position status
        await self.update_position_status(position_id, status)
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting multi-user position monitoring...")
        self.running = True
        
        while self.running:
            try:
                # Get all active positions
                positions = await self.get_active_positions()
                
                if not positions:
                    logger.info("No active positions to monitor")
                    await asyncio.sleep(60)  # Wait 1 minute before checking again
                    continue
                
                logger.info(f"Monitoring {len(positions)} active positions")
                
                # Monitor each position
                tasks = []
                for position in positions:
                    task = asyncio.create_task(self.monitor_position(position))
                    tasks.append(task)
                
                # Wait for all position checks to complete
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Wait before next round
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def stop(self):
        """Stop the monitoring service"""
        logger.info("Stopping position monitoring...")
        self.running = False

async def main():
    """Main function to run the monitoring service"""
    # Get configuration from environment
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    contract_address = os.getenv("CONTRACT_ADDRESS")
    
    # Create monitor
    monitor = MultiUserPositionMonitor(
        backend_url=backend_url,
        contract_address=contract_address
    )
    
    try:
        # Start monitoring
        await monitor.monitor_loop()
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    finally:
        monitor.stop()

if __name__ == "__main__":
    asyncio.run(main())
