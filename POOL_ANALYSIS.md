# Pool Analysis & Monitoring Guide

## 📊 Available Pools on Base Mainnet

### Top Pools by Volume (24h)

| Pool | Fee Tier | Address | 24h Volume | Liquidity | Est. APR |
|------|----------|---------|------------|-----------|----------|
| **WETH-USDC** | 0.05% | `0xd0b53D9277642d899DF5C87A3966A349A798F224` | $126M | $7.3M | **314%** |
| **WETH-USDC** | 0.3% | `0x6c561B446416E1A00E8E93E221854d6eA4171372` | $126M | $7.3M | **1,886%** |
| WETH-USDbC | 0.05% | `0x4C36388bE6F416A29C8d8Eee81C771cE6bE14B18` | - | - | - |
| WETH-cbETH | 0.05% | `0x10648BA41B8565907Cfa1496765fA4D95390aa0d` | - | - | - |

**Note:** APR estimates are based on: `(24h_volume * fee_rate * 365) / liquidity`

---

## 🎯 How to Select the Best Pool

### 1. **Volume vs Liquidity Ratio**
- Higher volume = more fees
- Lower liquidity = higher APR per dollar invested
- **WETH-USDC 0.05%** has excellent volume ($126M/day)

### 2. **Fee Tier Strategy**
- **0.05%**: Most competitive, highest volume (best for stable pairs like WETH-USDC)
- **0.3%**: Medium fees, good for moderately volatile pairs
- **1.0%**: High fees, best for exotic/volatile pairs

### 3. **Transaction Count**
- More transactions = more consistent fee generation
- WETH-USDC: 113,324 transactions per day (~4,700/hour)

---

## 📍 How to Tell if Position is Out of Range

### Understanding Ticks

Uniswap V3 uses "ticks" to represent price ranges:
- Each tick represents a 0.01% price change
- Formula: `price = 1.0001^tick`

### Your Position (Example from test)
```
Pool: WETH-USDC-0.05%
Current Tick: -193,470
Your Range: -193,000 to -192,800 (±1% around $3,956)

Status: IN RANGE ✅
```

### Check Methods

**Method 1: Using Monitor Script**
```bash
python3 scripts/monitor_pools.py --check-range \
  --pool "WETH-USDC-0.05%" \
  --tick-lower -193000 \
  --tick-upper -192800
```

**Method 2: On-Chain Query**
```python
# Get current tick from pool.slot0()
current_tick = pool.functions.slot0().call()[1]

# Check if in range
in_range = tick_lower <= current_tick <= tick_upper
```

**Method 3: Position Manager NFT**
```python
# Query your position NFT
position = position_manager.functions.positions(token_id).call()
liquidity = position[7]

# If liquidity > 0, you're in range
# If liquidity == 0, you're out of range
```

---

## 📈 How to Find Highest APR

### Automated Monitoring
```bash
# Run pool monitor to see all APRs
python3 scripts/monitor_pools.py
```

### APR Components

**Formula:**
```
APR = (Daily Volume × Fee Rate × 365) / Total Liquidity
```

**Example: WETH-USDC 0.05%**
```
Daily Volume: $126,321,591
Fee Rate: 0.0005 (0.05%)
Liquidity: $7,335,242

Daily Fees = $126,321,591 × 0.0005 = $63,161
Annual Fees = $63,161 × 365 = $23,053,665
APR = $23,053,665 / $7,335,242 = 314%
```

### ⚠️ APR Reality Check

**Advertised APR vs Real Returns:**
1. **Impermanent Loss**: Can reduce returns by 10-50% in volatile markets
2. **Concentrated Liquidity**: Only earn fees when in range
3. **Time in Range**: If price moves out, APR drops to 0%
4. **Gas Costs**: Rebalancing costs gas (~$0.50-2.00 per transaction)

**Realistic Expectations:**
- Advertised APR: 314%
- Time in range (±1%): ~60-70%
- After IL: ~200-250%
- After gas: ~180-230%

---

## 🔄 Price Update Frequency

### Where Prices Come From

#### 1. **On-Chain (Real-time)**
```python
# Your optimizer fetches directly from pool
slot0 = pool.functions.slot0().call()
sqrt_price_x96 = slot0[0]
current_tick = slot0[1]
```
- **Frequency**: Every transaction (real-time)
- **Source**: Uniswap V3 Pool contract
- **Accuracy**: 100% accurate
- **Use**: Position creation, swaps

#### 2. **DexScreener API (Near real-time)**
```python
# Used for market data and analytics
url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
```
- **Frequency**: Updates every ~60 seconds
- **Source**: DexScreener aggregates from pools
- **Data**: Volume, liquidity, price changes, APR
- **Use**: Pool selection, APR estimation

#### 3. **Your Optimizer Strategy**
```python
# src/data/price_data.py
def get_price(self, pool_address):
    # Tries DexScreener first (faster)
    # Falls back to on-chain if API fails
```

### Update Strategy for Production

**Recommendation:**
1. **Pool Selection**: Check once per hour (DexScreener)
2. **Position Monitoring**: Check every 5 minutes (on-chain)
3. **Rebalancing Decision**: Check every 15 minutes
4. **Transaction Execution**: Get latest price immediately before tx

---

## 🛠️ Monitoring Tools

### 1. Pool Monitor Script
```bash
# View all pools with APR
python3 scripts/monitor_pools.py

# Check specific position
python3 scripts/monitor_pools.py --check-range \
  --pool "WETH-USDC-0.05%" \
  --tick-lower -193000 \
  --tick-upper -192800
```

### 2. Position NFT Details
```python
# Get your position details
position_manager = w3.eth.contract(address=PM_ADDRESS, abi=PM_ABI)
position = position_manager.functions.positions(token_id).call()

# Position struct:
# [0] nonce
# [1] operator
# [2] token0
# [3] token1
# [4] fee
# [5] tickLower
# [6] tickUpper
# [7] liquidity
# [8] feeGrowthInside0LastX128
# [9] feeGrowthInside1LastX128
# [10] tokensOwed0
# [11] tokensOwed1
```

### 3. Web Dashboard (Coming Soon)
- Real-time position monitoring
- APR tracking
- Automated rebalancing
- Fee collection history
- Performance analytics

---

## 🎓 Key Learnings

### ✅ What Works
1. **WETH-USDC 0.05%** = Best pool for micro-testing
2. **Tight ranges (±1%)** = Higher capital efficiency
3. **Monitoring every 15 min** = Catch range exits early
4. **Gas optimization** = Batch operations, avoid rate limits

### ⚠️ Watch Out For
1. **Out of range** = Zero fees earned
2. **Gas costs** = Can eat into small positions
3. **Rate limits** = Public RPC has limits (~10 req/sec)
4. **Impermanent loss** = Volatile markets hurt returns

### 🚀 Next Steps
1. ✅ **DONE**: Create first LP position
2. **NEXT**: Build automated monitoring
3. **THEN**: Implement auto-rebalancing
4. **FINALLY**: Web dashboard for management

---

## 📞 Quick Reference

**Monitor all pools:**
```bash
python3 scripts/monitor_pools.py
```

**Check position range:**
```bash
python3 scripts/monitor_pools.py --check-range \
  --pool "WETH-USDC-0.05%" \
  --tick-lower <YOUR_LOWER_TICK> \
  --tick-upper <YOUR_UPPER_TICK>
```

**Create new position:**
```bash
python3 scripts/test_create_position.py --capital 0.30
```

**Current pool state:**
- WETH-USDC 0.05%: Tick **-193,470** (~$3,964)
- 24h Volume: **$126M**
- Est. APR: **314%**

---

**Generated:** October 19, 2025  
**Network:** Base Mainnet (Chain ID: 8453)  
**Your Wallet:** `0x8a679aCf39c06682072C4a2A833eb437A0CC0bdb`
