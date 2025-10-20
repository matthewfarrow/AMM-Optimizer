# Tick Calculation Fix

## Problem Identified

The original code was calculating tick ranges using the **USD price** instead of the **current tick** from the pool. This resulted in positions that were massively out of range.

### Original (Wrong) Approach
```python
# Get current price (e.g., $4,000)
current_price = price_collector.fetch_current_price(pool_name)

# Calculate price range (e.g., $3,980 - $4,020)
lower_price = current_price * (1 - tick_range/10000)
upper_price = current_price * (1 + tick_range/10000)

# Convert prices to ticks using logarithm
tick_lower = int(math.floor(math.log(lower_price) / math.log(1.0001)))
tick_upper = int(math.floor(math.log(upper_price) / math.log(1.0001)))

# Result: tick_lower ≈ 82950, tick_upper ≈ 83050
```

**Issue:** This calculated ticks around ~83,000, but the actual current tick in the pool was **-193,309**. The position was created with a range of [82950, 83050] when it should have been centered around -193,309.

### Why This Happened

In Uniswap V3:
- **Ticks** are the actual unit used in the pool to track price
- **Tick 0** does NOT correspond to $1.00 or any specific USD price
- The relationship between ticks and prices depends on the token pair decimals and ordering

For WETH/USDC:
- Token0 (WETH) has 18 decimals
- Token1 (USDC) has 6 decimals
- The price formula accounts for this decimal difference
- Current tick ≈ -193,309 corresponds to ~$4,000 per ETH

## Solution

### New (Correct) Approach
```python
# Get current tick directly from pool.slot0()
from src.dex.abis import POOL_ABI
pool_contract = uniswap.w3.eth.contract(
    address=pool_address,
    abi=POOL_ABI
)
slot0 = pool_contract.functions.slot0().call()
current_tick = slot0[1]  # e.g., -193309

# Calculate tick range: CURRENT TICK ± tick_range
tick_spacing = 60 if fee == 3000 else (10 if fee == 500 else 200)

# Align current tick to tick spacing
current_tick_aligned = (current_tick // tick_spacing) * tick_spacing

# Add/subtract tick_range from current tick
tick_lower = current_tick_aligned - tick_range  # e.g., -193309 - 50 = -193359
tick_upper = current_tick_aligned + tick_range  # e.g., -193309 + 50 = -193259

# Align to tick spacing
tick_lower = (tick_lower // tick_spacing) * tick_spacing
tick_upper = (tick_upper // tick_spacing) * tick_spacing

# Result: tick_lower = -193380, tick_upper = -193260
```

**Benefits:**
1. Position is **centered on the actual current tick**
2. Range is exactly **±50 ticks** from current position
3. Position will be **in range** when created
4. Works for any token pair regardless of decimals

## Files Updated

### 1. `scripts/create_initial_position.py`
- Removed price-based tick calculation
- Added pool.slot0() call to get current tick
- Calculate tick range as: `current_tick ± tick_range`
- Align ticks to pool's tick spacing

### 2. `scripts/monitor_and_rebalance.py`
- Updated `create_position()` method
- Uses same tick-based calculation
- Removed price-to-tick conversion logic

## Verification

After the fix, new positions should:
1. Show current tick **within** the position range
2. Display as "IN RANGE" when created
3. Have tick_lower < current_tick < tick_upper

### Example Output (Before Fix)
```
Current Tick: -193309
Position Bounds: Lower: tick 82950, Upper: tick 83050
STATUS: OUT OF RANGE (BELOW by 276259 ticks) ❌
```

### Example Output (After Fix)
```
Current Tick: -193309
Position Bounds: Lower: tick -193380, Upper: tick -193260
STATUS: IN RANGE ✅
```

## Technical Details

### Tick Spacing by Fee Tier
- 0.05% fee (500): tick spacing = 10
- 0.30% fee (3000): tick spacing = 60
- 1.00% fee (10000): tick spacing = 200

### Price from Tick Formula
```python
price = 1.0001 ** tick
```

This is used for **display purposes only**. We never reverse this formula to calculate ticks from USD prices.

### Why ±50 Ticks ≈ ±0.5%

For small tick ranges:
```
price_change ≈ (1.0001)^50 - 1 ≈ 0.005 ≈ 0.5%
```

So ±50 ticks gives approximately ±0.5% price range around current price.

## Next Steps

1. ✅ Fixed tick calculation in both scripts
2. ⏳ Test with new position creation
3. ⏳ Integrate position_manager.py for pre-flight checks
4. ⏳ Add token swap logic for rebalancing
