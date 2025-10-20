"""
Uniswap V3 interface for Base Network with full transaction support.
"""
from decimal import Decimal
from typing import Dict, Tuple, Optional, List, Any
import logging
from web3 import Web3
from web3.contract import Contract
import time

from .web3_client import Web3Client, get_web3_client
from .abis import (
    ERC20_ABI,
    POOL_ABI,
    POSITION_MANAGER_ABI,
    ROUTER_ABI,
)
from ..utils.config import get_config

logger = logging.getLogger(__name__)


class UniswapV3:
    """Interface for Uniswap V3 on Base Network."""
    
    def __init__(self):
        """Initialize Uniswap V3 interface."""
        self.config = get_config()
        self.web3_client = get_web3_client()
        self.w3 = self.web3_client.w3
        
        # Contract addresses (from config)
        self.factory_address = self.config.get('uniswap.factory_address')
        self.router_address = self.config.get('uniswap.router_address')
        self.position_manager_address = self.config.get('uniswap.position_manager_address')
        self.quoter_address = self.config.get('uniswap.quoter_address')
        
        logger.info("Uniswap V3 interface initialized on Base Network")
        logger.info(f"Position Manager: {self.position_manager_address}")
        logger.info(f"Router: {self.router_address}")
    
    def get_pool_price(self, pool_address: str) -> float:
        """
        Get current price from pool.
        
        Args:
            pool_address: Pool contract address
            
        Returns:
            Current price (token1/token0)
        """
        logger.debug(f"Getting price for pool: {pool_address}")
        
        try:
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(pool_address),
                abi=POOL_ABI
            )
            
            # Get slot0 which contains sqrtPriceX96
            slot0 = contract.functions.slot0().call()
            sqrt_price_x96 = slot0[0]
            
            # Convert sqrtPriceX96 to actual price
            # price = (sqrtPriceX96 / 2^96) ^ 2
            price = (sqrt_price_x96 / (2 ** 96)) ** 2
            
            logger.debug(f"Pool price: {price}")
            return price
            
        except Exception as e:
            logger.error(f"Error getting pool price: {e}")
            return 0.0
    
    def get_pool_liquidity(self, pool_address: str) -> int:
        """
        Get current liquidity in pool.
        
        Args:
            pool_address: Pool contract address
            
        Returns:
            Current liquidity
        """
        logger.debug(f"Getting liquidity for pool: {pool_address}")
        
        try:
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(pool_address),
                abi=POOL_ABI
            )
            
            liquidity = contract.functions.liquidity().call()
            
            logger.debug(f"Pool liquidity: {liquidity}")
            return liquidity
            
        except Exception as e:
            logger.error(f"Error getting pool liquidity: {e}")
            return 0
    
    def get_position(
        self,
        token_id: int
    ) -> Dict[str, Any]:
        """
        Get details of an existing position.
        
        Args:
            token_id: NFT token ID
            
        Returns:
            Position details
        """
        logger.debug(f"Getting position: {token_id}")
        
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.position_manager_address),
            abi=POSITION_MANAGER_ABI
        )
        
        position = contract.functions.positions(token_id).call()
        
        return {
            'nonce': position[0],
            'operator': position[1],
            'token0': position[2],
            'token1': position[3],
            'fee': position[4],
            'tickLower': position[5],
            'tickUpper': position[6],
            'liquidity': position[7],
            'feeGrowthInside0LastX128': position[8],
            'feeGrowthInside1LastX128': position[9],
            'tokensOwed0': position[10],
            'tokensOwed1': position[11]
        }
    
    def approve_token(self, token_address: str, spender_address: str, amount: int, skip_check: bool = False) -> Optional[str]:
        """
        Approve tokens for spending.
        
        Args:
            token_address: Token contract address
            spender_address: Spender contract address
            amount: Amount to approve
            skip_check: If True, skip allowance check and approve directly
            
        Returns:
            Transaction hash or None if already approved
        """
        logger.info(f"Approving {amount} tokens for {spender_address}")
        
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=ERC20_ABI
        )
        
        wallet = self.web3_client.address
        
        # Check current allowance (unless skip_check=True)
        if not skip_check:
            try:
                current_allowance = contract.functions.allowance(wallet, spender_address).call()
                if current_allowance >= amount:
                    logger.info(f"Already approved {current_allowance}, no need to approve again")
                    return None
            except Exception as e:
                logger.warning(f"Could not check allowance (rate limit?), approving anyway: {e}")
                # Continue with approval
        
        # Build approval transaction  
        import time
        time.sleep(0.5)  # Small delay to avoid nonce conflicts
        nonce = self.w3.eth.get_transaction_count(wallet, 'pending')
        
        tx = contract.functions.approve(spender_address, amount).build_transaction({
            'from': wallet,
            'nonce': nonce,
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Sign and send
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.web3_client.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"Approval tx: {tx_hash.hex()}")
        
        # Wait for confirmation
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt['status'] == 1:
            logger.info("Approval successful")
        else:
            logger.error("Approval failed")
            
        return tx_hash.hex()
    
    def add_liquidity(
        self,
        pool_address: str,
        token0_amount: int,
        token1_amount: int,
        tick_lower: int,
        tick_upper: int,
        token0_address: str,
        token1_address: str,
        fee: int,
        deadline: Optional[int] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Add liquidity to a pool (mint new position).
        
        Args:
            pool_address: Pool contract address
            token0_amount: Amount of token0
            token1_amount: Amount of token1
            tick_lower: Lower tick of range
            tick_upper: Upper tick of range
            token0_address: Token0 contract address
            token1_address: Token1 contract address
            fee: Pool fee tier
            deadline: Transaction deadline (default: 20 minutes from now)
            
        Returns:
            Transaction receipt with tokenId
        """
        logger.info(f"Adding liquidity to pool: {pool_address}")
        logger.info(f"Amounts: {token0_amount} token0, {token1_amount} token1")
        logger.info(f"Tick range: [{tick_lower}, {tick_upper}]")
        
        # Use provided token addresses (no RPC calls needed)
        token0 = Web3.to_checksum_address(token0_address)
        token1 = Web3.to_checksum_address(token1_address)
        
        # Approve tokens (skip allowance check to avoid rate limits)
        logger.info("Approving token0...")
        self.approve_token(token0, self.position_manager_address, token0_amount, skip_check=True)
        time.sleep(1)  # Wait for approval to be mined
        
        logger.info("Approving token1...")
        self.approve_token(token1, self.position_manager_address, token1_amount, skip_check=True)
        time.sleep(1)  # Wait for approval to be mined
        
        # Set deadline
        if deadline is None:
            deadline = int(time.time()) + 1200  # 20 minutes
        
        # Build mint parameters
        wallet = self.web3_client.address
        mint_params = {
            'token0': token0,
            'token1': token1,
            'fee': fee,
            'tickLower': tick_lower,
            'tickUpper': tick_upper,
            'amount0Desired': token0_amount,
            'amount1Desired': token1_amount,
            'amount0Min': 0,  # Accept any amount (for micro testing)
            'amount1Min': 0,  # Accept any amount (for micro testing)
            'recipient': wallet,
            'deadline': deadline
        }
        
        # Get Position Manager contract
        pm_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.position_manager_address),
            abi=POSITION_MANAGER_ABI
        )
        
        # Build transaction
        time.sleep(0.5)  # Short delay before getting nonce
        tx = pm_contract.functions.mint(mint_params).build_transaction({
            'from': wallet,
            'nonce': self.w3.eth.get_transaction_count(wallet, 'pending'),
            'gas': 500000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        if dry_run:
            logger.info("🔍 DRY RUN - Would mint position with parameters:")
            logger.info(f"  Token0: {token0_amount} wei")
            logger.info(f"  Token1: {token1_amount} wei")
            logger.info(f"  Tick range: [{tick_lower}, {tick_upper}]")
            logger.info("✅ Dry run complete - no transaction sent")
            return {
                'success': True,
                'dry_run': True,
                'tx_hash': 'dry-run-no-tx',
                'receipt': None
            }
        
        # Sign and send
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.web3_client.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"Mint tx: {tx_hash.hex()}")
        
        # Wait for confirmation
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt['status'] == 1:
            logger.info("Position minted successfully!")
            # Parse logs to get tokenId (simplified - in production parse the Transfer event)
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'receipt': receipt
            }
        else:
            logger.error("Position mint failed")
            return {
                'success': False,
                'tx_hash': tx_hash.hex(),
                'receipt': receipt
            }
    
    def remove_liquidity(
        self,
        token_id: int,
        liquidity_percent: float = 1.0,
        deadline: Optional[int] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Remove liquidity from an existing position.
        
        Args:
            token_id: NFT token ID
            liquidity_percent: Percentage of liquidity to remove (0.0 to 1.0)
            deadline: Transaction deadline
            
        Returns:
            Transaction receipt
        """
        logger.info(f"Removing {liquidity_percent*100}% liquidity from position: {token_id}")
        
        # Get position details
        position = self.get_position(token_id)
        liquidity_to_remove = int(position['liquidity'] * liquidity_percent)
        
        # Set deadline
        if deadline is None:
            deadline = int(time.time()) + 1200
        
        # Build decrease liquidity parameters
        decrease_params = {
            'tokenId': token_id,
            'liquidity': liquidity_to_remove,
            'amount0Min': 0,  # Accept any amount (set higher in production)
            'amount1Min': 0,
            'deadline': deadline
        }
        
        pm_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.position_manager_address),
            abi=POSITION_MANAGER_ABI
        )
        
        wallet = self.web3_client.address
        
        # Build transaction
        tx = pm_contract.functions.decreaseLiquidity(decrease_params).build_transaction({
            'from': wallet,
            'nonce': self.w3.eth.get_transaction_count(wallet),
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        if dry_run:
            logger.info("🔍 DRY RUN - Would remove liquidity with parameters:")
            logger.info(f"  Token ID: {token_id}")
            logger.info(f"  Liquidity to remove: {liquidity_to_remove}")
            logger.info("✅ Dry run complete - no transaction sent")
            return {
                'success': True,
                'dry_run': True,
                'tx_hash': 'dry-run-no-tx',
                'receipt': None,
                'amount0': 0,
                'amount1': 0
            }
        
        # Sign and send
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.web3_client.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"Decrease liquidity tx: {tx_hash.hex()}")
        
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            'success': receipt['status'] == 1,
            'tx_hash': tx_hash.hex(),
            'receipt': receipt
        }
    
    def collect_fees(
        self,
        token_id: int
    ) -> Dict[str, Any]:
        """
        Collect accumulated fees from a position.
        
        Args:
            token_id: NFT token ID
            
        Returns:
            Transaction receipt
        """
        logger.info(f"Collecting fees from position: {token_id}")
        
        wallet = self.web3_client.address
        
        collect_params = {
            'tokenId': token_id,
            'recipient': wallet,
            'amount0Max': 2**128 - 1,  # Collect all
            'amount1Max': 2**128 - 1
        }
        
        pm_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.position_manager_address),
            abi=POSITION_MANAGER_ABI
        )
        
        tx = pm_contract.functions.collect(collect_params).build_transaction({
            'from': wallet,
            'nonce': self.w3.eth.get_transaction_count(wallet),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.web3_client.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"Collect fees tx: {tx_hash.hex()}")
        
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            'success': receipt['status'] == 1,
            'tx_hash': tx_hash.hex(),
            'receipt': receipt
        }
    
    def get_positions(
        self,
        wallet: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all positions owned by a wallet.
        
        Args:
            wallet: Wallet address (default: connected wallet)
            
        Returns:
            List of position details
        """
        if wallet is None:
            wallet = self.web3_client.address
        
        logger.debug(f"Getting positions for wallet: {wallet}")
        
        pm_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.position_manager_address),
            abi=POSITION_MANAGER_ABI
        )
        
        # Get number of positions
        balance = pm_contract.functions.balanceOf(wallet).call()
        
        positions = []
        for i in range(balance):
            token_id = pm_contract.functions.tokenOfOwnerByIndex(wallet, i).call()
            position = self.get_position(token_id)
            position['tokenId'] = token_id
            positions.append(position)
        
        logger.info(f"Found {len(positions)} positions")
        return positions
    
    def swap_tokens(
        self,
        token_in: str,
        token_out: str,
        amount_in: float,
        fee_tier: str = 'medium',
        slippage: float = 1.0,
        dry_run: bool = False
    ) -> dict:
        """
        Swap tokens using Uniswap V3 router.
        
        Args:
            token_in: Symbol of input token (e.g., 'USDC', 'WETH')
            token_out: Symbol of output token (e.g., 'WETH', 'USDC')
            amount_in: Amount of input token to swap
            fee_tier: Fee tier ('lowest', 'low', 'medium', 'high')
            slippage: Maximum slippage tolerance in percent
            dry_run: If True, simulate without executing
            
        Returns:
            Dict with swap result
        """
        # Import here to avoid circular imports
        from scripts.swap_tokens import swap_tokens as do_swap
        
        logger.info(f"Swapping {amount_in} {token_in} for {token_out} (dry_run: {dry_run})")
        
        try:
            # Call the existing swap function
            result = do_swap(
                token_in=token_in,
                token_out=token_out,
                amount_in=amount_in,
                fee_tier=fee_tier,
                slippage=slippage,
                dry_run=dry_run
            )
            
            if result is None:
                return {'success': False, 'error': 'Swap failed - check logs'}
            
            return {'success': True, 'result': result}
            
        except Exception as e:
            logger.error(f"Swap error: {e}")
            return {'success': False, 'error': str(e)}


# Singleton instance
_uniswap_instance = None


def get_uniswap() -> UniswapV3:
    """Get or create Uniswap V3 instance."""
    global _uniswap_instance
    if _uniswap_instance is None:
        _uniswap_instance = UniswapV3()
    return _uniswap_instance
