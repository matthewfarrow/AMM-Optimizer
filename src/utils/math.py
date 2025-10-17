"""
Math utilities for liquidity calculations.
"""
import math
from decimal import Decimal
from typing import Tuple


def price_to_tick(price: float, tick_spacing: int = 1) -> int:
    """
    Convert price to tick.
    
    Args:
        price: Price as token1/token0
        tick_spacing: Tick spacing (e.g., 60 for 0.3% fee tier)
    
    Returns:
        Tick value
    """
    tick = math.floor(math.log(price, 1.0001))
    return round(tick / tick_spacing) * tick_spacing


def tick_to_price(tick: int) -> float:
    """
    Convert tick to price.
    
    Args:
        tick: Tick value
    
    Returns:
        Price as token1/token0
    """
    return 1.0001 ** tick


def get_tick_range(
    current_price: float,
    price_range_percent: float,
    tick_spacing: int = 60
) -> Tuple[int, int]:
    """
    Calculate tick range around current price.
    
    Args:
        current_price: Current price (token1/token0)
        price_range_percent: Range as percent (e.g., 0.05 = 5%)
        tick_spacing: Tick spacing
    
    Returns:
        (lower_tick, upper_tick)
    """
    lower_price = current_price * (1 - price_range_percent)
    upper_price = current_price * (1 + price_range_percent)
    
    lower_tick = price_to_tick(lower_price, tick_spacing)
    upper_tick = price_to_tick(upper_price, tick_spacing)
    
    return lower_tick, upper_tick


def calculate_liquidity(
    amount0: float,
    amount1: float,
    price_current: float,
    price_lower: float,
    price_upper: float
) -> float:
    """
    Calculate liquidity for given amounts and price range.
    
    This is a simplified version. For production, use exact formulas
    from Uniswap V3 whitepaper.
    
    Args:
        amount0: Amount of token0
        amount1: Amount of token1
        price_current: Current price
        price_lower: Lower price bound
        price_upper: Upper price bound
    
    Returns:
        Liquidity value
    """
    if price_current <= price_lower:
        # Only token0
        sqrt_price_current = math.sqrt(price_current)
        sqrt_price_lower = math.sqrt(price_lower)
        sqrt_price_upper = math.sqrt(price_upper)
        return amount0 / (1/sqrt_price_lower - 1/sqrt_price_upper)
    
    elif price_current >= price_upper:
        # Only token1
        sqrt_price_lower = math.sqrt(price_lower)
        sqrt_price_upper = math.sqrt(price_upper)
        return amount1 / (sqrt_price_upper - sqrt_price_lower)
    
    else:
        # Mixed
        sqrt_price_current = math.sqrt(price_current)
        sqrt_price_lower = math.sqrt(price_lower)
        sqrt_price_upper = math.sqrt(price_upper)
        
        liquidity0 = amount0 / (1/sqrt_price_current - 1/sqrt_price_upper)
        liquidity1 = amount1 / (sqrt_price_current - sqrt_price_lower)
        
        return min(liquidity0, liquidity1)


def calculate_amounts_from_liquidity(
    liquidity: float,
    price_current: float,
    price_lower: float,
    price_upper: float
) -> Tuple[float, float]:
    """
    Calculate token amounts for given liquidity and price range.
    
    Args:
        liquidity: Liquidity amount
        price_current: Current price
        price_lower: Lower price bound
        price_upper: Upper price bound
    
    Returns:
        (amount0, amount1)
    """
    sqrt_price_current = math.sqrt(price_current)
    sqrt_price_lower = math.sqrt(price_lower)
    sqrt_price_upper = math.sqrt(price_upper)
    
    if price_current <= price_lower:
        amount0 = liquidity * (1/sqrt_price_lower - 1/sqrt_price_upper)
        amount1 = 0
    elif price_current >= price_upper:
        amount0 = 0
        amount1 = liquidity * (sqrt_price_upper - sqrt_price_lower)
    else:
        amount0 = liquidity * (1/sqrt_price_current - 1/sqrt_price_upper)
        amount1 = liquidity * (sqrt_price_current - sqrt_price_lower)
    
    return amount0, amount1


def calculate_concentration_factor(
    volatility: float,
    target_duration_hours: float,
    max_gas_ratio: float = 0.02
) -> float:
    """
    Calculate optimal concentration factor based on volatility.
    
    Higher volatility = less concentration to avoid frequent rebalancing.
    
    Args:
        volatility: Historical volatility (std dev of returns)
        target_duration_hours: Target hours before rebalancing
        max_gas_ratio: Maximum acceptable gas cost ratio
    
    Returns:
        Concentration factor (0-1, higher = more concentrated)
    """
    # Expected price move in target duration (simplified)
    expected_move = volatility * math.sqrt(target_duration_hours / 24)
    
    # Adjust for gas costs
    # If expected move is high, we need wider range to avoid gas costs
    concentration = 1 / (1 + expected_move / max_gas_ratio)
    
    return max(0.1, min(0.9, concentration))
