"""
Configuration loader with environment variable substitution.
"""
import os
import yaml
from typing import Any, Dict
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration manager for the optimizer."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config.yaml file
        """
        # Load environment variables
        load_dotenv()
        
        # Set default paths
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        
        self.config_path = Path(config_path)
        self.pools_path = self.config_path.parent / "pools.yaml"
        
        # Load configurations
        self.config = self._load_yaml(self.config_path)
        self.pools = self._load_yaml(self.pools_path)
        
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML file with environment variable substitution."""
        with open(path, 'r') as f:
            content = f.read()
            
        # Replace environment variables
        content = self._substitute_env_vars(content)
        
        return yaml.safe_load(content)
    
    def _substitute_env_vars(self, content: str) -> str:
        """Substitute ${VAR_NAME} with environment variables."""
        import re
        
        pattern = r'\$\{([^}]+)\}'
        
        def replacer(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        
        return re.sub(pattern, replacer, content)
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value by dot-notation key."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_enabled_pools(self) -> list:
        """Get list of enabled pools."""
        return [pool for pool in self.pools.get('pools', []) if pool.get('enabled', False)]
    
    def get_pool_by_name(self, name: str) -> Dict[str, Any]:
        """Get pool configuration by name."""
        for pool in self.pools.get('pools', []):
            if pool['name'] == name:
                return pool
        return None
    
    @property
    def private_key(self) -> str:
        """Get private key from environment."""
        key = os.getenv('AVAX_PRIVATE_KEY')
        if not key:
            raise ValueError("AVAX_PRIVATE_KEY not set in environment")
        return key
    
    @property
    def rpc_url(self) -> str:
        """Get RPC URL."""
        return self.get('network.rpc_url', 'https://api.avax.network/ext/bc/C/rpc')
    
    @property
    def chain_id(self) -> int:
        """Get chain ID."""
        return self.get('network.chain_id', 43114)


# Global config instance
_config = None


def get_config() -> Config:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config():
    """Reload configuration from disk."""
    global _config
    _config = Config()
