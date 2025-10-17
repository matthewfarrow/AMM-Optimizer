"""
Logging configuration for the optimizer.
"""
import sys
from pathlib import Path
from loguru import logger
from .config import get_config


def setup_logging():
    """Configure logging based on config."""
    config = get_config()
    
    # Remove default handler
    logger.remove()
    
    # Console logging
    if config.get('logging.console', True):
        log_level = config.get('logging.level', 'INFO')
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level=log_level
        )
    
    # File logging
    log_file = config.get('logging.file', 'logs/optimizer.log')
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_path,
        rotation="500 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=config.get('logging.level', 'INFO')
    )
    
    return logger


# Initialize logging
log = setup_logging()
