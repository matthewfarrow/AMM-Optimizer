# MVP Automated Rebalancing System

## Overview

This MVP system automatically monitors and rebalances a Uniswap V3 concentrated liquidity position.

**Key Features:**
- ✅ Concentrated liquidity: ±50 ticks (±0.5% from current price)
- ✅ Automated monitoring: Checks position every 1 minute
- ✅ Auto-rebalancing: Closes old position and creates new one when out of range
- ✅ Continuous operation: Runs indefinitely until stopped

## Quick Start

### 1. Create Initial Position

First, create your concentrated liquidity position:

```bash
python scripts/create_initial_position.py \
  --pool WETH-USDC \
  --fee 500 \
  --amount0 0.0001 \
  --amount1 0.2 \
  --tick-range 50
```

**Parameters:**
- `--pool`: Token pair (e.g., WETH-USDC, WETH-DAI)
- `--fee`: Fee tier in basis points (500 = 0.05%, 3000 = 0.3%)
- `--amount0`: Amount of first token (WETH in this case)
- `--amount1`: Amount of second token (USDC in this case)
- `--tick-range`: Position width in ticks (default: 50 = ±0.5%)

**Output:**
```
✅ POSITION CREATED SUCCESSFULLY!
Position Token ID: 12345
Transaction: https://basescan.org/tx/0x...
Pool: WETH-USDC
Fee Tier: 0.05%
Current Tick: 204567
Range: [204517, 204617]
```

**Save the Position Token ID** - you'll need it for monitoring!

### 2. Start Automated Monitoring

Now start the monitoring loop (runs forever until you stop it):

```bash
python scripts/monitor_and_rebalance.py \
  --pool WETH-USDC \
  --fee 500 \
  --amount0 0.0001 \
  --amount1 0.2 \
  --position-id 12345 \
  --interval 60
```

**Parameters:**
- `--pool`: Same pool as initial position
- `--fee`: Same fee tier as initial position
- `--amount0`: Amount for new positions after rebalancing
- `--amount1`: Amount for new positions after rebalancing
- `--position-id`: Token ID from step 1 (optional if creating new)
- `--interval`: Check interval in seconds (default: 60)

### 3. Monitor the Output

The system will continuously log detailed status every 60 seconds:

```
🚀 Starting monitoring loop...
Will check position every 60 seconds

================================================================================
📊 CHECK #1 - WETH-USDC Position 12345
================================================================================
💰 Current Price: 2000.456789 USDC per WETH
📏 Position Bounds:
   Lower: 1990.123456 (tick 204517)
   Upper: 2010.789012 (tick 204617)
🎯 Current Tick: 204567
📍 Distance from Lower Edge: 50 ticks
📍 Distance from Upper Edge: 50 ticks
✅ STATUS: IN RANGE (50.0% through range)
📈 Total Rebalances: 0
================================================================================
⏳ Next check in 60 seconds...
================================================================================

================================================================================
📊 CHECK #2 - WETH-USDC Position 12345
================================================================================
💰 Current Price: 2001.234567 USDC per WETH
📏 Position Bounds:
   Lower: 1990.123456 (tick 204517)
   Upper: 2010.789012 (tick 204617)
🎯 Current Tick: 204570
📍 Distance from Lower Edge: 53 ticks
📍 Distance from Upper Edge: 47 ticks
✅ STATUS: IN RANGE (53.0% through range)
📈 Total Rebalances: 0
================================================================================
⏳ Next check in 60 seconds...
================================================================================

================================================================================
📊 CHECK #3 - WETH-USDC Position 12345
================================================================================
💰 Current Price: 2011.567890 USDC per WETH
📏 Position Bounds:
   Lower: 1990.123456 (tick 204517)
   Upper: 2010.789012 (tick 204617)
🎯 Current Tick: 204620
📍 Distance from Lower Edge: 103 ticks
📍 Distance from Upper Edge: -3 ticks
⚠️  STATUS: OUT OF RANGE (ABOVE by 3 ticks)
🔧 ACTION REQUIRED: Rebalancing position...
================================================================================
🔄 Starting rebalance...
Removing liquidity from position 12345
Liquidity removed: 0x...
Tokens collected: 0x...
Creating new position with 0.0001 token0 and 0.2 token1
Current pool price: 2011.567890
Current tick: 204620, Tick spacing: 10
Position range: [204570, 204670]
✅ Position created! Token ID: 12346
Transaction: https://basescan.org/tx/0x...
================================================================================
✅ REBALANCE COMPLETE!
📈 Total Rebalances: 1
🆕 New Position ID: 12346
================================================================================
⏳ Next check in 60 seconds...
================================================================================
```

### 4. Stop Monitoring

Press `Ctrl+C` to stop the monitoring loop:

```
^C
⛔ Monitoring stopped by user
Final position ID: 12346
Total rebalances performed: 1
```

## How It Works

### Position Range Calculation

The system creates positions with a tight range around the current price:

1. **Get current tick** from the pool (e.g., tick = 204567)
2. **Calculate range**: [current_tick - 50, current_tick + 50]
3. **Round to tick spacing**: Adjust to valid tick boundaries (usually every 10 ticks for 0.05% pools)
4. **Result**: Position active within ±0.5% of current price

**Example:**
- Current price: $2000 USDC per ETH
- Current tick: 204567
- Position range: [204517, 204617]
- Price range: [$1990, $2010] (±0.5%)

### Monitoring Process

Every 60 seconds, the system:

1. **Fetches current tick** from the pool
2. **Checks if in range**: `tick_lower <= current_tick <= tick_upper`
3. **If OUT OF RANGE**:
   - Remove all liquidity from old position
   - Collect tokens back to wallet
   - Calculate new range around current price
   - Create new position with fresh range
   - Continue monitoring with new position ID

### Rebalancing Logic

When the price exits the position range:

```python
Old Position:
  Tick Range: [204517, 204617]
  Current Tick: 204620  ← OUT OF RANGE!
  
Rebalancing:
  1. Remove liquidity from position 12345
  2. Collect tokens (0.0001 WETH, 0.2 USDC)
  3. Get new current tick: 204620
  4. Calculate new range: [204570, 204670]
  5. Create new position 12346

New Position:
  Tick Range: [204570, 204670]
  Current Tick: 204620  ← IN RANGE ✅
```

## Available Pools

You can monitor any of these pools on Base Mainnet:

| Pool | Fee | Best For |
|------|-----|----------|
| WETH-USDC | 500 (0.05%) | **Recommended** - High volume, tight spreads |
| WETH-USDC | 3000 (0.3%) | Alternative with wider range |
| WETH-USDbC | 500 (0.05%) | Bridged USDC pool |
| WETH-cbETH | 500 (0.05%) | ETH derivative pairs |
| WETH-DAI | 500 (0.05%) | Stablecoin alternative |

## Configuration Options

### Tick Range

Adjust concentration of liquidity:

- `--tick-range 25`: ±0.25% (very concentrated, frequent rebalancing)
- `--tick-range 50`: ±0.5% (default, balanced)
- `--tick-range 100`: ±1% (wider range, less rebalancing)

### Check Interval

Adjust monitoring frequency:

- `--interval 60`: Every 1 minute (default, MVP spec)
- `--interval 300`: Every 5 minutes (less RPC calls)
- `--interval 3600`: Every 1 hour (minimal monitoring)

## Gas Costs

Each rebalance involves 3 transactions:

1. **Decrease Liquidity**: ~50,000 gas (~$0.0001)
2. **Collect Tokens**: ~40,000 gas (~$0.00008)
3. **Create New Position**: ~200,000 gas (~$0.0004)

**Total per rebalance**: ~$0.0006 at current Base gas prices

## Safety Features

- **No slippage protection**: For micro-testing only (set `amount0Min=0`, `amount1Min=0`)
- **Manual stop**: Must press Ctrl+C to stop (no auto-shutdown)
- **Position tracking**: Logs every rebalance with transaction hashes
- **Error handling**: Logs errors but may crash on critical failures

## Monitoring Tips

### Watch for Volatility

High volatility = more rebalances = more gas costs:

- **Stable markets**: Position may stay in range for hours
- **Volatile markets**: May rebalance every few minutes
- **Consider**: Wider tick range (100-200) for volatile assets

### Track Rebalancing Frequency

Monitor the rebalance counter:

```
Total rebalances: 15  ← Rebalanced 15 times

If rebalancing too frequently:
  1. Increase --tick-range to 100 or 200
  2. Choose less volatile pool
  3. Use wider fee tier (3000 instead of 500)
```

### Check Gas Costs

Each rebalance costs ~$0.0006 in gas. Calculate break-even:

```
Cost per rebalance: $0.0006
Rebalances per day: 20
Daily gas cost: $0.012

Ensure LP fees earned > gas costs!
```

## Troubleshooting

### Position Not Creating

```
Error: insufficient funds for transfer
```

**Solution**: Ensure you have enough tokens in wallet:
- Check balances: `python scripts/check_mainnet.py`
- Wrap ETH: `python scripts/wrap_eth.py`

### Rate Limiting Errors

```
Error: 429 Too Many Requests
```

**Solution**: Increase check interval:
```bash
--interval 120  # Check every 2 minutes instead
```

### Position Shows Out of Range Immediately

This is normal! The price may have moved while creating the position. The system will automatically rebalance on the next check.

## Next Steps

Once the MVP is working:

1. **Add slippage protection** - Calculate proper `amount0Min` and `amount1Min`
2. **Implement profitability check** - Only rebalance if fees earned > gas costs
3. **Add fee collection** - Automatically collect accumulated fees
4. **Build web dashboard** - Visualize positions and rebalancing history
5. **Multi-position support** - Monitor multiple positions simultaneously

## Example Session

Here's a complete example session:

```bash
# Step 1: Check you have tokens
python scripts/check_mainnet.py

# Step 2: Wrap some ETH if needed
python scripts/wrap_eth.py --amount 0.001

# Step 3: Create initial position
python scripts/create_initial_position.py \
  --pool WETH-USDC \
  --fee 500 \
  --amount0 0.0001 \
  --amount1 0.2
  
# Output: Position Token ID: 12345

# Step 4: Start monitoring
python scripts/monitor_and_rebalance.py \
  --pool WETH-USDC \
  --fee 500 \
  --amount0 0.0001 \
  --amount1 0.2 \
  --position-id 12345

# Let it run... press Ctrl+C when done
```

## Summary

You now have a working MVP that:
- ✅ Creates concentrated positions (±50 ticks / ±0.5%)
- ✅ Monitors position range every 60 seconds
- ✅ Automatically rebalances when out of range
- ✅ Runs continuously until stopped
- ✅ Logs all activity with transaction hashes

**Total time to launch**: ~2 minutes

**Ready to run on Base Mainnet!** 🚀
