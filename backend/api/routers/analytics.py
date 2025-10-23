"""
Analytics endpoints for price data, volatility, and strategy recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import os
from pycoingecko import CoinGeckoAPI

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from database import get_db, PriceData

router = APIRouter()

# Initialize CoinGecko API
cg = CoinGeckoAPI()

# Cache for price data (5 minutes)
price_cache = {}
cache_duration = 300  # 5 minutes

def get_coingecko_api_key() -> Optional[str]:
    """Get CoinGecko API key from environment or return None for free tier"""
    return os.getenv('COINGECKO_API_KEY')

def fetch_real_price_data(pool_address: str, timeframe: str = "1d") -> List[dict]:
    """Fetch real price data from CoinGecko"""
    cache_key = f"price_{pool_address}_{timeframe}"
    
    # Check cache first
    if cache_key in price_cache:
        cache_time, cached_data = price_cache[cache_key]
        if datetime.now().timestamp() - cache_time < cache_duration:
            return cached_data
    
    try:
        # Map pool addresses to CoinGecko coin IDs
        pool_to_coin = {
            "0xd0b53D9277642d899DF5C87A3966A349A798F224": "ethereum",  # WETH/USDC
            "0x4C36388bE6F416A29C8d8Eee81C771cE6bE14B18": "ethereum",  # WETH/USDbC
            "0x1234567890123456789012345678901234567890": "ethereum",  # WETH/DAI
        }
        
        coin_id = pool_to_coin.get(pool_address, "ethereum")  # Default to ETH
        
        # Determine days based on timeframe
        if timeframe == "1d":
            days = 1
        elif timeframe == "1m":
            days = 30
        elif timeframe == "1y":
            days = 365
        else:
            days = 1
        
        # Fetch price data from CoinGecko
        price_data = cg.get_coin_market_chart_by_id(
            id=coin_id,
            vs_currency='usd',
            days=days,
            api_key=get_coingecko_api_key()
        )
        
        # Process the data
        processed_data = []
        for price_point in price_data['prices']:
            timestamp = datetime.fromtimestamp(price_point[0] / 1000)
            price = price_point[1]
            
            processed_data.append({
                "timestamp": timestamp.isoformat(),
                "price": round(price, 2),
                "volume": 0  # Volume not available in this endpoint
            })
        
        # Cache the result
        price_cache[cache_key] = (datetime.now().timestamp(), processed_data)
        
        return processed_data
        
    except Exception as e:
        print(f"Error fetching price data from CoinGecko: {e}")
        # Fallback to mock data
        return generate_mock_price_data(pool_address, timeframe)

# Mock price data for development (fallback)
def generate_mock_price_data(pool_address: str, timeframe: str = "1d") -> List[dict]:
    """Generate mock price data for testing"""
    now = datetime.utcnow()
    
    if timeframe == "1d":
        hours = 24
        interval = 1  # 1 hour intervals
    elif timeframe == "1m":
        hours = 24 * 30
        interval = 6  # 6 hour intervals
    elif timeframe == "1y":
        hours = 24 * 365
        interval = 24  # 1 day intervals
    else:
        hours = 24
        interval = 1
    
    data = []
    base_price = 2500.0  # Base price for WETH/USDC
    
    for i in range(0, hours, interval):
        timestamp = now - timedelta(hours=hours-i)
        # Generate realistic price movement with some volatility
        price_change = np.random.normal(0, 0.02)  # 2% standard deviation
        price = base_price * (1 + price_change)
        base_price = price  # Random walk
        
        data.append({
            "timestamp": timestamp.isoformat(),
            "price": round(price, 2),
            "volume": np.random.uniform(100000, 1000000)
        })
    
    return data

def calculate_volatility(prices: List[float]) -> float:
    """Calculate standard deviation of price changes"""
    if len(prices) < 2:
        return 0.0
    
    price_changes = []
    for i in range(1, len(prices)):
        change = (prices[i] - prices[i-1]) / prices[i-1]
        price_changes.append(change)
    
    return np.std(price_changes) * 100  # Return as percentage

def calculate_liquidation_probability(volatility: float, tick_range: int) -> float:
    """Calculate probability of position going out of range"""
    # Simplified calculation based on volatility and tick range
    # In reality, this would be more sophisticated
    range_percentage = tick_range / 100  # Convert ticks to percentage
    probability = min(volatility / range_percentage, 1.0) * 100
    return round(probability, 2)

@router.get("/{pool_address}/price-data")
async def get_price_data(
    pool_address: str,
    timeframe: str = Query("1d", regex="^(1d|1m|1y)$"),
    db: Session = Depends(get_db)
):
    """Get price data for a pool over specified timeframe"""
    
    # Fetch real price data from CoinGecko
    price_data = fetch_real_price_data(pool_address, timeframe)
    
    return {
        "pool_address": pool_address,
        "timeframe": timeframe,
        "data": price_data,
        "count": len(price_data)
    }

@router.get("/{pool_address}/volatility")
async def get_volatility_analysis(
    pool_address: str,
    timeframe: str = Query("1d", regex="^(1d|1m|1y)$"),
    db: Session = Depends(get_db)
):
    """Get volatility analysis for a pool"""
    
    # Get price data
    price_data = fetch_real_price_data(pool_address, timeframe)
    prices = [point["price"] for point in price_data]
    
    # Calculate metrics
    volatility = calculate_volatility(prices)
    current_price = prices[-1] if prices else 0
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0
    
    # Calculate price ranges
    price_range_1d = {
        "low": min(prices[-24:]) if len(prices) >= 24 else min_price,
        "high": max(prices[-24:]) if len(prices) >= 24 else max_price
    }
    
    price_range_30d = {
        "low": min(prices[-720:]) if len(prices) >= 720 else min_price,
        "high": max(prices[-720:]) if len(prices) >= 720 else max_price
    }
    
    price_range_1y = {
        "low": min_price,
        "high": max_price
    }
    
    return {
        "pool_address": pool_address,
        "timeframe": timeframe,
        "current_price": current_price,
        "volatility_percentage": round(volatility, 2),
        "price_ranges": {
            "1d": price_range_1d,
            "30d": price_range_30d,
            "1y": price_range_1y
        },
        "volatility_bands": {
            "upper_1std": current_price * (1 + volatility/100),
            "lower_1std": current_price * (1 - volatility/100),
            "upper_2std": current_price * (1 + 2*volatility/100),
            "lower_2std": current_price * (1 - 2*volatility/100)
        }
    }

@router.get("/{pool_address}/strategy-recommendations")
async def get_strategy_recommendations(
    pool_address: str,
    capital_usd: float = Query(1000.0, ge=100.0),
    risk_tolerance: str = Query("medium", regex="^(low|medium|high)$"),
    db: Session = Depends(get_db)
):
    """Get strategy recommendations based on pool analytics"""
    
    # Get volatility data
    volatility_data = await get_volatility_analysis(pool_address, "1d", db)
    volatility = volatility_data["volatility_percentage"]
    current_price = volatility_data["current_price"]
    
    # Calculate recommended tick ranges based on risk tolerance
    if risk_tolerance == "low":
        tick_range = max(200, int(volatility * 10))  # Wider range for lower risk
        check_interval = 300  # 5 minutes
    elif risk_tolerance == "medium":
        tick_range = max(100, int(volatility * 5))   # Medium range
        check_interval = 180  # 3 minutes
    else:  # high
        tick_range = max(50, int(volatility * 2))    # Tighter range for higher risk
        check_interval = 60   # 1 minute
    
    # Calculate liquidation probability
    liquidation_prob = calculate_liquidation_probability(volatility, tick_range)
    
    # Calculate expected APR (simplified)
    base_apr = 8.0  # Base APR for the pool
    concentration_multiplier = 200 / tick_range if tick_range > 0 else 1
    expected_apr = base_apr * concentration_multiplier
    
    # Calculate optimal token amounts
    # For WETH/USDC pair, assume 50/50 split
    token0_amount = capital_usd / 2 / current_price  # WETH amount
    token1_amount = capital_usd / 2  # USDC amount
    
    return {
        "pool_address": pool_address,
        "capital_usd": capital_usd,
        "risk_tolerance": risk_tolerance,
        "recommendations": {
            "tick_range": tick_range,
            "check_interval_seconds": check_interval,
            "token0_amount": round(token0_amount, 6),
            "token1_amount": round(token1_amount, 2),
            "expected_apr": round(expected_apr, 2),
            "liquidation_probability": liquidation_prob,
            "volatility": volatility
        },
        "warnings": [
            f"Position has {liquidation_prob}% chance of going out of range",
            f"Volatility is {volatility}% - consider wider range if too high",
            "Monitor gas costs vs expected returns"
        ] if liquidation_prob > 20 else []
    }

@router.get("/{pool_address}/liquidation-probability")
async def get_liquidation_probability(
    pool_address: str,
    tick_range: int = Query(50, ge=10, le=1000),
    timeframe: str = Query("1d", regex="^(1d|1m|1y)$"),
    db: Session = Depends(get_db)
):
    """Calculate liquidation probability for a given tick range"""
    
    # Get volatility data
    volatility_data = await get_volatility_analysis(pool_address, timeframe, db)
    volatility = volatility_data["volatility_percentage"]
    
    # Calculate probability
    probability = calculate_liquidation_probability(volatility, tick_range)
    
    return {
        "pool_address": pool_address,
        "tick_range": tick_range,
        "timeframe": timeframe,
        "volatility_percentage": volatility,
        "liquidation_probability": probability,
        "recommendation": "Consider wider range" if probability > 30 else "Range looks good"
    }

@router.get("/{pool_address}/out-of-range-probability")
async def get_out_of_range_probability(
    pool_address: str,
    tick_range: int = Query(50, ge=10, le=1000),
    check_interval_minutes: int = Query(60, ge=1, le=1440),
    timeframe: str = Query("1d", regex="^(1d|1m|1y)$"),
    db: Session = Depends(get_db)
):
    """Calculate probability of position going out of range over specified time interval"""
    
    # Get volatility data
    volatility_data = await get_volatility_analysis(pool_address, timeframe, db)
    volatility = volatility_data["volatility_percentage"]
    current_price = volatility_data["current_price"]
    
    # Convert volatility from percentage to decimal
    volatility_decimal = volatility / 100
    
    # Calculate range bounds in price terms
    range_percentage = tick_range / 100  # Convert ticks to percentage
    price_lower = current_price * (1 - range_percentage / 100)
    price_upper = current_price * (1 + range_percentage / 100)
    
    # Calculate time-adjusted volatility
    # Assuming volatility scales with square root of time
    time_factor = np.sqrt(check_interval_minutes / (24 * 60))  # Normalize to daily
    adjusted_volatility = volatility_decimal * time_factor
    
    # Calculate probability using normal distribution
    # P(out of range) = 1 - P(price stays within bounds)
    from scipy.stats import norm
    
    # Calculate z-scores for upper and lower bounds
    z_upper = (price_upper - current_price) / (current_price * adjusted_volatility)
    z_lower = (price_lower - current_price) / (current_price * adjusted_volatility)
    
    # Calculate probability of staying within range
    prob_within_range = norm.cdf(z_upper) - norm.cdf(z_lower)
    prob_out_of_range = 1 - prob_within_range
    
    # Convert to percentage
    prob_out_of_range_pct = max(0, min(100, prob_out_of_range * 100))
    
    return {
        "pool_address": pool_address,
        "tick_range": tick_range,
        "check_interval_minutes": check_interval_minutes,
        "timeframe": timeframe,
        "volatility_percentage": volatility,
        "current_price": current_price,
        "price_bounds": {
            "lower": round(price_lower, 2),
            "upper": round(price_upper, 2)
        },
        "out_of_range_probability": round(prob_out_of_range_pct, 2),
        "risk_level": "low" if prob_out_of_range_pct < 20 else "medium" if prob_out_of_range_pct < 50 else "high",
        "recommendation": get_risk_recommendation(prob_out_of_range_pct, tick_range)
    }

def get_risk_recommendation(probability: float, tick_range: int) -> str:
    """Get recommendation based on risk level"""
    if probability < 20:
        return "Low risk - position looks good"
    elif probability < 50:
        return "Medium risk - consider monitoring closely"
    else:
        return "High risk - consider wider range or shorter check interval"
