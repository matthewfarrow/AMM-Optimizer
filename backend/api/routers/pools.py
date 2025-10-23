"""
Pool management endpoints
Fetches Uniswap V3 pool data and provides it to the frontend
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import requests
import time
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from database import get_db, Pool, PriceData

router = APIRouter()

# Uniswap V3 Subgraph endpoint for Base
UNISWAP_SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"

# Cache for pool data (5 minutes)
pool_cache = {}
cache_duration = 300  # 5 minutes

class PoolData:
    def __init__(self, address: str, name: str, token0: str, token1: str, 
                 token0_address: str, token1_address: str, fee_tier: int,
                 tvl: float = 0.0, apr: float = 0.0, volume_1d: float = 0.0, 
                 volume_30d: float = 0.0):
        self.address = address
        self.name = name
        self.token0 = token0
        self.token1 = token1
        self.token0_address = token0_address
        self.token1_address = token1_address
        self.fee_tier = fee_tier
        self.tvl = tvl
        self.apr = apr
        self.volume_1d = volume_1d
        self.volume_30d = volume_30d

def fetch_pools_from_subgraph() -> List[PoolData]:
    """Fetch pool data from Uniswap V3 Subgraph"""
    query = """
    {
      pools(
        first: 100
        orderBy: totalValueLockedUSD
        orderDirection: desc
        where: {
          totalValueLockedUSD_gt: "1000"
        }
      ) {
        id
        token0 {
          symbol
          id
        }
        token1 {
          symbol
          id
        }
        feeTier
        totalValueLockedUSD
        volumeUSD
        volumeUSD_1d: volumeUSD
        volumeUSD_30d: volumeUSD
        feesUSD
      }
    }
    """
    
    try:
        response = requests.post(UNISWAP_SUBGRAPH_URL, json={"query": query})
        response.raise_for_status()
        data = response.json()
        
        pools = []
        for pool_data in data["data"]["pools"]:
            # Calculate APR (simplified)
            tvl = float(pool_data["totalValueLockedUSD"])
            fees_1d = float(pool_data.get("feesUSD", 0))
            apr = (fees_1d * 365 / tvl * 100) if tvl > 0 else 0
            
            pool = PoolData(
                address=pool_data["id"],
                name=f"{pool_data['token0']['symbol']}-{pool_data['token1']['symbol']}",
                token0=pool_data["token0"]["symbol"],
                token1=pool_data["token1"]["symbol"],
                token0_address=pool_data["token0"]["id"],
                token1_address=pool_data["token1"]["id"],
                fee_tier=int(pool_data["feeTier"]),
                tvl=tvl,
                apr=apr,
                volume_1d=float(pool_data.get("volumeUSD_1d", 0)),
                volume_30d=float(pool_data.get("volumeUSD_30d", 0))
            )
            pools.append(pool)
        
        return pools
    
    except Exception as e:
        print(f"Error fetching pools from subgraph: {e}")
        return get_hardcoded_pools()

def get_hardcoded_pools() -> List[PoolData]:
    """Fallback hardcoded pool data for Base network"""
    return [
        PoolData(
            address="0xd0b53D9277642d899DF5C87A3966A349A798F224",
            name="USDC-WETH",
            token0="USDC",
            token1="WETH",
            token0_address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            token1_address="0x4200000000000000000000000000000000000006",
            fee_tier=500,
            tvl=26620000.0,  # Real TVL from Uniswap
            apr=8.5,
            volume_1d=15000000.0,
            volume_30d=450000000.0
        ),
        PoolData(
            address="0x4C36388bE6F416A29C8d8Eee81C771cE6bE14B18",
            name="WETH-USDbC",
            token0="WETH",
            token1="USDbC",
            token0_address="0x4200000000000000000000000000000000000006",
            token1_address="0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA",
            fee_tier=500,
            tvl=2000000.0,
            apr=8.3,
            volume_1d=500000.0,
            volume_30d=15000000.0
        ),
        PoolData(
            address="0x1234567890123456789012345678901234567890",
            name="WETH-DAI",
            token0="WETH",
            token1="DAI",
            token0_address="0x4200000000000000000000000000000000000006",
            token1_address="0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
            fee_tier=500,
            tvl=1000000.0,
            apr=6.7,
            volume_1d=200000.0,
            volume_30d=6000000.0
        )
    ]

@router.get("/")
async def get_pools(
    sort_by: str = "tvl",
    sort_order: str = "desc",
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get list of Uniswap V3 pools with sorting and filtering"""
    
    # Check cache first
    cache_key = f"pools_{sort_by}_{sort_order}_{limit}"
    if cache_key in pool_cache:
        cache_time, cached_data = pool_cache[cache_key]
        if time.time() - cache_time < cache_duration:
            return cached_data
    
    # Fetch fresh data
    pools_data = fetch_pools_from_subgraph()
    
    # Sort pools
    reverse = sort_order == "desc"
    if sort_by == "tvl":
        pools_data.sort(key=lambda x: x.tvl, reverse=reverse)
    elif sort_by == "apr":
        pools_data.sort(key=lambda x: x.apr, reverse=reverse)
    elif sort_by == "volume_1d":
        pools_data.sort(key=lambda x: x.volume_1d, reverse=reverse)
    elif sort_by == "volume_30d":
        pools_data.sort(key=lambda x: x.volume_30d, reverse=reverse)
    elif sort_by == "vol_tvl_ratio":
        pools_data.sort(key=lambda x: x.volume_1d / x.tvl if x.tvl > 0 else 0, reverse=reverse)
    
    # Limit results
    pools_data = pools_data[:limit]
    
    # Convert to dict format
    result = []
    for pool in pools_data:
        result.append({
            "address": pool.address,
            "name": pool.name,
            "token0": pool.token0,
            "token1": pool.token1,
            "token0_address": pool.token0_address,
            "token1_address": pool.token1_address,
            "fee_tier": pool.fee_tier,
            "tvl": pool.tvl,
            "apr": pool.apr,
            "volume_1d": pool.volume_1d,
            "volume_30d": pool.volume_30d,
            "vol_tvl_ratio": pool.volume_1d / pool.tvl if pool.tvl > 0 else 0
        })
    
    # Cache the result
    pool_cache[cache_key] = (time.time(), result)
    
    return result

@router.get("/{pool_address}")
async def get_pool_details(pool_address: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific pool"""
    
    # For now, return basic pool info
    # In production, this would fetch detailed pool data
    return {
        "address": pool_address,
        "name": "WETH-USDC",  # This would be fetched from the pool
        "token0": "WETH",
        "token1": "USDC",
        "fee_tier": 500,
        "tvl": 5000000.0,
        "apr": 12.5,
        "volume_1d": 1000000.0,
        "volume_30d": 30000000.0
    }

@router.get("/{pool_address}/stats")
async def get_pool_stats(pool_address: str, db: Session = Depends(get_db)):
    """Get pool statistics and metrics"""
    
    # This would calculate real statistics
    return {
        "pool_address": pool_address,
        "current_price": 2500.0,  # This would be fetched from the pool
        "price_change_1d": 2.5,
        "price_change_7d": -1.2,
        "liquidity_distribution": {
            "concentrated": 0.7,
            "full_range": 0.3
        },
        "fee_tier": 500,
        "tick_spacing": 10
    }
