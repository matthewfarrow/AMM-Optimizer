"""
Uniswap V3 interface for Base Network.
"""
from decimal import Decimal
from typing import Dict, Tuple, Optional
import logging
from web3 import Web3
from .web3_client import Web3Client
from .abis import (
    ERC20_ABI,
    POOL_ABI,
    POSITION_MANAGER_ABI,
    ROUTER_ABI,
)

logger = logging.getLogger(__name__)


class UniswapV3:
    """Interface for Uniswap V3 on Base Network."""
    
    # Uniswap V3 ABIs - simplified versions
    # For production, use the full ABIs from Uniswap V3 documentation
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
        }
    ]
    
    POSITION_MANAGER_ABI = []  # Add full ABI for production
    ROUTER_ABI = []  # Add full ABI for production
    
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
        
        log.info("Uniswap V3 interface initialized on Base Network")
    
    def get_pool_price(self, pool_address: str) -> float:
        """
        Get current price from pool.
        
        Args:
            pool_address: Pool contract address
            
        Returns:
            Current price (token1/token0)
        """
        log.debug(f"Getting price for pool: {pool_address}")
        
        try:
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(pool_address),
                abi=self.POOL_ABI
            )
            
            slot0 = contract.functions.slot0().call()
            sqrtPriceX96 = slot0[0]
            
            # Convert sqrtPriceX96 to price
            price = (sqrtPriceX96 / (2 ** 96)) ** 2
            
            log.debug(f"Pool price: {price}")
            return price
            
        except Exception as e:
            log.error(f"Error getting pool price: {e}")
            raise
    
    def get_pool_liquidity(self, pool_address: str) -> int:
        """
        Get total liquidity in pool.
        
        Args:
            pool_address: Pool contract address
            
        Returns:
            Total liquidity
        """
        log.debug(f"Getting liquidity for pool: {pool_address}")
        
        try:
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(pool_address),
                abi=self.POOL_ABI
            )
            
            liquidity = contract.functions.liquidity().call()
            
            log.debug(f"Pool liquidity: {liquidity}")
            return liquidity
            
        except Exception as e:
            log.error(f"Error getting pool liquidity: {e}")
            raise
    
    def get_position(
        self,
        token_id: int
    ) -> Dict[str, Any]:
        """
        Get position details.
        
        Args:
            token_id: NFT token ID representing the position
            
        Returns:
            Position details dict
        """
        log.debug(f"Getting position: {token_id}")
        
        # TODO: Implement actual contract call to position manager
        # position = contract.functions.positions(token_id).call()
        
        raise NotImplementedError("Implement with full Uniswap V3 Position Manager ABI")
    
    def add_liquidity(
        self,
        pool_address: str,
        token0_amount: float,
        token1_amount: float,
        tick_lower: int,
        tick_upper: int,
        slippage: float = 0.005
    ) -> str:
        """
        Add liquidity to Uniswap V3 pool.
        
        Args:
            pool_address: Pool address
            token0_amount: Amount of token0
            token1_amount: Amount of token1
            tick_lower: Lower tick
            tick_upper: Upper tick
            slippage: Slippage tolerance
            
        Returns:
            Transaction hash
        """
        log.info(f"Adding liquidity to pool: {pool_address}")
        log.info(f"Amounts: {token0_amount} token0, {token1_amount} token1")
        log.info(f"Tick range: [{tick_lower}, {tick_upper}]")
        
        # TODO: Implement with Uniswap V3 Position Manager
        # 1. Approve token0
        # 2. Approve token1
        # 3. Call mint() function on Position Manager
        
        raise NotImplementedError("Implement with full Uniswap V3 ABIs")
    
    def remove_liquidity(
        self,
        token_id: int,
        liquidity_percent: float = 1.0
    ) -> str:
        """
        Remove liquidity from position.
        
        Args:
            token_id: Position token ID
            liquidity_percent: Percent of liquidity to remove (0-1)
            
        Returns:
            Transaction hash
        """
        log.info(f"Removing {liquidity_percent*100}% liquidity from position: {token_id}")
        
        # TODO: Implement with Uniswap V3 Position Manager
        # Call decreaseLiquidity() then collect()
        
        raise NotImplementedError("Implement with full Uniswap V3 ABIs")
    
    def collect_fees(self, token_id: int) -> str:
        """
        Collect accumulated fees from position.
        
        Args:
            token_id: Position token ID
            
        Returns:
            Transaction hash
        """
        log.info(f"Collecting fees from position: {token_id}")
        
        # TODO: Implement with Uniswap V3 Position Manager
        # Call collect() function
        
        raise NotImplementedError("Implement with full Uniswap V3 ABIs")
    
    def get_positions_for_wallet(
        self,
        wallet_address: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all LP positions for wallet.
        
        Args:
            wallet_address: Wallet address (defaults to current wallet)
            
        Returns:
            List of position dicts
        """
        wallet = wallet_address or self.web3_client.address
        log.debug(f"Getting positions for wallet: {wallet}")
        
        # TODO: Implement - query position manager for wallet's NFTs
        # Use balanceOf() and tokenOfOwnerByIndex() to enumerate NFTs
        
        raise NotImplementedError("Implement with full Uniswap V3 ABIs")
    
    def rebalance_position(
        self,
        token_id: int,
        new_tick_lower: int,
        new_tick_upper: int
    ) -> Tuple[str, str]:
        """
        Rebalance position by closing old and opening new.
        
        Args:
            token_id: Current position token ID
            new_tick_lower: New lower tick
            new_tick_upper: New upper tick
            
        Returns:
            (close_tx_hash, open_tx_hash)
        """
        log.info(f"Rebalancing position {token_id} to ticks [{new_tick_lower}, {new_tick_upper}]")
        
        # Get current position details
        position = self.get_position(token_id)
        
        # Remove all liquidity
        close_tx = self.remove_liquidity(token_id, 1.0)
        self.web3_client.wait_for_transaction(close_tx)
        
        # Collect fees
        collect_tx = self.collect_fees(token_id)
        self.web3_client.wait_for_transaction(collect_tx)
        
        # Get new balances
        def _extract_amount(source: Any, keys: Tuple[str, ...]) -> float:
            if not isinstance(source, dict):
                return 0.0
            for key in keys:
                if key not in source or source[key] in (None, ''):
                    continue
                value = source[key]
                if isinstance(value, dict):
                    nested = _extract_amount(value, keys)
                    if nested:
                        return nested
                    continue
                try:
                    return float(value)
                except (TypeError, ValueError):
                    continue
            return 0.0
        
        base_keys_token0 = ('token0_amount', 'amount0', 'principal0', 'principal_token0')
        base_keys_token1 = ('token1_amount', 'amount1', 'principal1', 'principal_token1')
        fee_keys_token0 = ('token0', 'amount0', 'token0_amount')
        fee_keys_token1 = ('token1', 'amount1', 'token1_amount')
        owed_keys_token0 = ('tokensOwed0', 'tokens_owed0', 'fees0', 'fees_token0')
        owed_keys_token1 = ('tokensOwed1', 'tokens_owed1', 'fees1', 'fees_token1')
        
        base_token0 = _extract_amount(position, base_keys_token0)
        if not base_token0:
            base_token0 = _extract_amount(position.get('amounts'), fee_keys_token0)
        if not base_token0:
            base_token0 = _extract_amount(position.get('balances'), fee_keys_token0)
        
        base_token1 = _extract_amount(position, base_keys_token1)
        if not base_token1:
            base_token1 = _extract_amount(position.get('amounts'), fee_keys_token1)
        if not base_token1:
            base_token1 = _extract_amount(position.get('balances'), fee_keys_token1)
        
        collected_fee0 = _extract_amount(position.get('collected_fees'), fee_keys_token0)
        collected_fee1 = _extract_amount(position.get('collected_fees'), fee_keys_token1)
        
        if not collected_fee0 and not collected_fee1:
            fees_dict = position.get('fees') or position.get('uncollected_fees')
            collected_fee0 = _extract_amount(fees_dict, fee_keys_token0)
            collected_fee1 = _extract_amount(fees_dict, fee_keys_token1)
        
        if not collected_fee0:
            collected_fee0 = _extract_amount(position, owed_keys_token0)
        if not collected_fee1:
            collected_fee1 = _extract_amount(position, owed_keys_token1)
        
        if isinstance(collect_tx, dict):
            collected_fee0 = _extract_amount(collect_tx, fee_keys_token0) or collected_fee0
            collected_fee1 = _extract_amount(collect_tx, fee_keys_token1) or collected_fee1
        elif isinstance(collect_tx, (list, tuple)):
            temp_fee_map = {}
            if len(collect_tx) >= 1:
                temp_fee_map['amount0'] = collect_tx[0]
            if len(collect_tx) >= 2:
                temp_fee_map['amount1'] = collect_tx[1]
            collected_fee0 = _extract_amount(temp_fee_map, fee_keys_token0) or collected_fee0
            collected_fee1 = _extract_amount(temp_fee_map, fee_keys_token1) or collected_fee1
        
        token0_amount = base_token0 + collected_fee0
        token1_amount = base_token1 + collected_fee1
        
        if not token0_amount and not token1_amount:
            liquidity = _extract_amount(position, ('liquidity',))
            lower_tick = (
                position.get('tickLower')
                or position.get('lower_tick')
                or position.get('tick_lower')
            )
            upper_tick = (
                position.get('tickUpper')
                or position.get('upper_tick')
                or position.get('tick_upper')
            )
            
            pool_address = position.get('pool')
            if liquidity and lower_tick is not None and upper_tick is not None and pool_address:
                try:
                    current_price = self.get_pool_price(pool_address)
                    amount0_principal, amount1_principal = calculate_amounts_from_liquidity(
                        liquidity=liquidity,
                        price_current=current_price,
                        price_lower=tick_to_price(int(lower_tick)),
                        price_upper=tick_to_price(int(upper_tick))
                    )
                    token0_amount = amount0_principal + collected_fee0
                    token1_amount = amount1_principal + collected_fee1
                except Exception as exc:
                    log.debug(f"Unable to derive token amounts from liquidity: {exc}")
        
        # Add liquidity with new range
        open_tx = self.add_liquidity(
            pool_address=position['pool'],
            token0_amount=token0_amount,
            token1_amount=token1_amount,
            tick_lower=new_tick_lower,
            tick_upper=new_tick_upper
        )
        
        log.info(f"Position rebalanced. Old: {token_id}, New TX: {open_tx}")
        
        return close_tx, open_tx


# Global instance
_uniswap_v3 = None


def get_uniswap_v3() -> UniswapV3:
    """Get global Uniswap V3 instance."""
    global _uniswap_v3
    if _uniswap_v3 is None:
        _uniswap_v3 = UniswapV3()
    return _uniswap_v3
