"""
Web3 connection and transaction management.
"""
from typing import Optional, Dict, Any
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from ..utils.config import get_config
from ..utils.logger import log


class Web3Client:
    """Web3 client for Avalanche network."""
    
    def __init__(self, rpc_url: Optional[str] = None, private_key: Optional[str] = None):
        """
        Initialize Web3 client.
        
        Args:
            rpc_url: RPC URL (defaults to config)
            private_key: Private key (defaults to config)
        """
        config = get_config()
        
        self.rpc_url = rpc_url or config.rpc_url
        self.private_key = private_key or config.private_key
        self.chain_id = config.chain_id
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Add POA middleware for Avalanche C-Chain
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Set up account
        self.account = Account.from_key(self.private_key)
        self.address = self.account.address
        
        log.info(f"Web3 client initialized for address: {self.address}")
        
        # Check connection
        if not self.w3.is_connected():
            raise ConnectionError(f"Cannot connect to RPC: {self.rpc_url}")
        
        log.info(f"Connected to Avalanche C-Chain (Chain ID: {self.chain_id})")
    
    def get_balance(self, address: Optional[str] = None) -> float:
        """
        Get AVAX balance.
        
        Args:
            address: Address to check (defaults to wallet address)
        
        Returns:
            Balance in AVAX
        """
        addr = address or self.address
        balance_wei = self.w3.eth.get_balance(addr)
        return self.w3.from_wei(balance_wei, 'ether')
    
    def get_token_balance(self, token_address: str, address: Optional[str] = None) -> float:
        """
        Get ERC20 token balance.
        
        Args:
            token_address: Token contract address
            address: Address to check (defaults to wallet address)
        
        Returns:
            Token balance
        """
        addr = address or self.address
        
        # ERC20 ABI (simplified)
        erc20_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]
        
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=erc20_abi
        )
        
        balance = contract.functions.balanceOf(Web3.to_checksum_address(addr)).call()
        decimals = contract.functions.decimals().call()
        
        return balance / (10 ** decimals)
    
    def estimate_gas(self, transaction: Dict[str, Any]) -> int:
        """
        Estimate gas for transaction.
        
        Args:
            transaction: Transaction dict
        
        Returns:
            Estimated gas
        """
        return self.w3.eth.estimate_gas(transaction)
    
    def get_gas_price(self) -> int:
        """Get current gas price in wei."""
        config = get_config()
        gas_price_gwei = config.get('network.gas_price_gwei', 25)
        return self.w3.to_wei(gas_price_gwei, 'gwei')
    
    def send_transaction(
        self,
        to: str,
        data: str = None,
        value: int = 0,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None
    ) -> str:
        """
        Send transaction.
        
        Args:
            to: Destination address
            data: Transaction data
            value: Value in wei
            gas_limit: Gas limit (auto-estimated if not provided)
            gas_price: Gas price in wei (uses config default if not provided)
        
        Returns:
            Transaction hash
        """
        nonce = self.w3.eth.get_transaction_count(self.address)
        
        transaction = {
            'from': self.address,
            'to': Web3.to_checksum_address(to),
            'value': value,
            'nonce': nonce,
            'chainId': self.chain_id,
            'gasPrice': gas_price or self.get_gas_price()
        }
        
        if data:
            transaction['data'] = data
        
        # Estimate gas if not provided
        if gas_limit is None:
            estimated_gas = self.estimate_gas(transaction)
            gas_limit = int(estimated_gas * 1.2)  # 20% buffer
        
        transaction['gas'] = gas_limit
        
        # Sign and send
        signed_txn = self.account.sign_transaction(transaction)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        log.info(f"Transaction sent: {tx_hash.hex()}")
        
        return tx_hash.hex()
    
    def wait_for_transaction(self, tx_hash: str, timeout: int = 120) -> Dict[str, Any]:
        """
        Wait for transaction confirmation.
        
        Args:
            tx_hash: Transaction hash
            timeout: Timeout in seconds
        
        Returns:
            Transaction receipt
        """
        log.info(f"Waiting for transaction: {tx_hash}")
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        
        if receipt['status'] == 1:
            log.info(f"Transaction confirmed: {tx_hash}")
        else:
            log.error(f"Transaction failed: {tx_hash}")
        
        return receipt
    
    def call_contract_function(
        self,
        contract_address: str,
        abi: list,
        function_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Call contract view function.
        
        Args:
            contract_address: Contract address
            abi: Contract ABI
            function_name: Function name
            *args: Function arguments
            **kwargs: Additional options
        
        Returns:
            Function result
        """
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=abi
        )
        
        function = getattr(contract.functions, function_name)
        return function(*args).call(**kwargs)
    
    def execute_contract_function(
        self,
        contract_address: str,
        abi: list,
        function_name: str,
        *args,
        value: int = 0,
        gas_limit: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Execute contract function (send transaction).
        
        Args:
            contract_address: Contract address
            abi: Contract ABI
            function_name: Function name
            *args: Function arguments
            value: ETH value to send
            gas_limit: Gas limit
            **kwargs: Additional options
        
        Returns:
            Transaction hash
        """
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=abi
        )
        
        function = getattr(contract.functions, function_name)
        transaction = function(*args).build_transaction({
            'from': self.address,
            'value': value,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'chainId': self.chain_id,
            'gasPrice': self.get_gas_price()
        })
        
        if gas_limit:
            transaction['gas'] = gas_limit
        else:
            estimated_gas = self.estimate_gas(transaction)
            transaction['gas'] = int(estimated_gas * 1.2)
        
        signed_txn = self.account.sign_transaction(transaction)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        log.info(f"Contract function executed: {function_name} - TX: {tx_hash.hex()}")
        
        return tx_hash.hex()


# Global Web3 client instance
_web3_client = None


def get_web3_client() -> Web3Client:
    """Get global Web3 client instance."""
    global _web3_client
    if _web3_client is None:
        _web3_client = Web3Client()
    return _web3_client
