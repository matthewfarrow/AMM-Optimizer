# Monitoring System Output Examples

## What You'll See Every 60 Seconds

The monitoring system prints a detailed status report every check interval (default: 60 seconds).

## Example 1: Position IN RANGE

When your position is actively earning fees:

```
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
```

**What this means:**
- ✅ Your position is **actively earning fees**
- Price is **centered** in your range (50% through)
- **50 ticks** away from both edges (safe margin)
- No action needed

---

## Example 2: Position Drifting (Still IN RANGE)

As price moves, but still earning fees:

```
================================================================================
📊 CHECK #5 - WETH-USDC Position 12345
================================================================================
💰 Current Price: 2008.123456 USDC per WETH
📏 Position Bounds:
   Lower: 1990.123456 (tick 204517)
   Upper: 2010.789012 (tick 204617)
🎯 Current Tick: 204605
📍 Distance from Lower Edge: 88 ticks
📍 Distance from Upper Edge: 12 ticks
✅ STATUS: IN RANGE (88.0% through range)
📈 Total Rebalances: 0
================================================================================
⏳ Next check in 60 seconds...
================================================================================
```

**What this means:**
- ✅ Still earning fees, but **approaching upper edge**
- Only **12 ticks** away from upper bound
- Price has moved 88% through your range
- **Next 12 tick move up** will trigger rebalance

---

## Example 3: Position OUT OF RANGE - Rebalancing

When price exits your range, automatic rebalancing starts:

```
================================================================================
📊 CHECK #6 - WETH-USDC Position 12345
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
Liquidity removed: 0xabc123...
Tokens collected: 0xdef456...
Creating new position with 0.0001 token0 and 0.2 token1
Current pool price: 2011.567890
Current tick: 204620, Tick spacing: 10
Position range: [204570, 204670]
✅ Position created! Token ID: 12346
Transaction: https://basescan.org/tx/0x789abc...
================================================================================
✅ REBALANCE COMPLETE!
📈 Total Rebalances: 1
🆕 New Position ID: 12346
================================================================================
⏳ Next check in 60 seconds...
================================================================================
```

**What happened:**
1. ⚠️ Price moved **ABOVE** upper bound by 3 ticks
2. 🔄 System automatically:
   - Removed all liquidity from old position
   - Collected tokens back to wallet
   - Created new position centered on current price (204620)
   - New range: [204570, 204670] (±50 ticks from current)
3. ✅ Position now **IN RANGE** again and earning fees
4. 🆕 New Position ID: 12346 (system tracks this automatically)

---

## Example 4: After Rebalance - Back IN RANGE

Next check shows new position is active:

```
================================================================================
📊 CHECK #7 - WETH-USDC Position 12346
================================================================================
💰 Current Price: 2011.234567 USDC per WETH
📏 Position Bounds:
   Lower: 2006.123456 (tick 204570)
   Upper: 2016.789012 (tick 204670)
🎯 Current Tick: 204618
📍 Distance from Lower Edge: 48 ticks
📍 Distance from Upper Edge: 52 ticks
✅ STATUS: IN RANGE (48.0% through range)
📈 Total Rebalances: 1
================================================================================
⏳ Next check in 60 seconds...
================================================================================
```

**What this means:**
- ✅ New position is **centered** and earning fees
- Position ID changed from 12345 → 12346
- Back to normal monitoring
- Total rebalances counter = 1

---

## Example 5: Multiple Rebalances in Volatile Market

During high volatility, you might see:

```
================================================================================
📊 CHECK #42 - WETH-USDC Position 12358
================================================================================
💰 Current Price: 1987.654321 USDC per WETH
📏 Position Bounds:
   Lower: 1983.123456 (tick 204320)
   Upper: 1993.789012 (tick 204420)
🎯 Current Tick: 204310
📍 Distance from Lower Edge: -10 ticks
📍 Distance from Upper Edge: 110 ticks
⚠️  STATUS: OUT OF RANGE (BELOW by 10 ticks)
🔧 ACTION REQUIRED: Rebalancing position...
================================================================================
🔄 Starting rebalance...
[... rebalancing process ...]
================================================================================
✅ REBALANCE COMPLETE!
📈 Total Rebalances: 15
🆕 New Position ID: 12359
================================================================================
⏳ Next check in 60 seconds...
================================================================================
```

**What this means:**
- Price dropped **BELOW** lower bound
- This is the **15th rebalance** today
- High volatility = more rebalances = more gas costs
- **Consider**: Wider tick range (--tick-range 100) to reduce frequency

---

## Key Indicators to Watch

### 📍 Distance from Edges

| Distance | Status | Action |
|----------|--------|--------|
| 40-60 ticks | 🟢 Safe | Position is well-centered |
| 10-40 ticks | 🟡 Caution | Getting close to edge |
| 0-10 ticks | 🟠 Warning | About to exit range |
| Negative | 🔴 Out of Range | Rebalancing triggered |

### 📈 Position Through Range

| Percentage | Meaning |
|------------|---------|
| 40-60% | Centered - optimal |
| 20-40% or 60-80% | Drifting - still good |
| 0-20% or 80-100% | Near edge - watch closely |

### 🔄 Rebalance Frequency

| Rebalances/Hour | Market Condition | Recommendation |
|----------------|------------------|----------------|
| 0-1 | Stable | Current settings are good |
| 2-5 | Moderate volatility | Monitor gas costs vs fees earned |
| 6+ | High volatility | Consider wider tick range (100-200) |

---

## Understanding Price vs Tick

**Current Tick** is the raw pool state (integer)
**Current Price** is calculated as: `price = 1.0001 ^ tick`

Example:
- Tick 204567 = Price ~2000.45 USDC per WETH
- Tick 204617 = Price ~2010.78 USDC per WETH
- 50 tick difference ≈ 0.5% price change

---

## Stopping the Monitor

Press `Ctrl+C` at any time to stop:

```
^C
⛔ Monitoring stopped by user
Final position ID: 12346
Total rebalances performed: 5
```

Your final position remains active and earning fees. You can:
1. Resume monitoring with `--position-id 12346`
2. Manually close the position
3. Let it run without monitoring

---

## Pro Tips

### 1. Monitor in Screen/Tmux

For continuous monitoring, use `screen` or `tmux`:

```bash
# Start screen session
screen -S lp-monitor

# Run monitoring
python scripts/monitor_and_rebalance.py --pool WETH-USDC --fee 500 --amount0 0.0001 --amount1 0.2 --position-id 12345

# Detach: Ctrl+A then D
# Reattach: screen -r lp-monitor
```

### 2. Log to File

Save output to a file for later analysis:

```bash
python scripts/monitor_and_rebalance.py \
  --pool WETH-USDC \
  --fee 500 \
  --amount0 0.0001 \
  --amount1 0.2 \
  --position-id 12345 \
  2>&1 | tee monitor.log
```

### 3. Watch Specific Metrics

Use grep to filter output:

```bash
# Only show price changes
tail -f monitor.log | grep "Current Price"

# Only show rebalances
tail -f monitor.log | grep -A5 "OUT OF RANGE"
```

---

## Complete Output Walkthrough

Here's what a full monitoring session looks like:

```bash
$ python scripts/monitor_and_rebalance.py --pool WETH-USDC --fee 500 --amount0 0.0001 --amount1 0.2 --position-id 12345

Using existing position: 12345
🚀 Starting monitoring loop...
Will check position every 60 seconds

# CHECK #1 - Position is centered, all good
================================================================================
📊 CHECK #1 - WETH-USDC Position 12345
================================================================================
💰 Current Price: 2000.123456 USDC per WETH
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

# [60 seconds pass...]

# CHECK #2 - Price moved up slightly, still safe
================================================================================
📊 CHECK #2 - WETH-USDC Position 12345
================================================================================
💰 Current Price: 2005.456789 USDC per WETH
📏 Position Bounds:
   Lower: 1990.123456 (tick 204517)
   Upper: 2010.789012 (tick 204617)
🎯 Current Tick: 204590
📍 Distance from Lower Edge: 73 ticks
📍 Distance from Upper Edge: 27 ticks
✅ STATUS: IN RANGE (73.0% through range)
📈 Total Rebalances: 0
================================================================================
⏳ Next check in 60 seconds...
================================================================================

# [60 seconds pass...]

# CHECK #3 - Price moved out of range! Rebalancing...
================================================================================
📊 CHECK #3 - WETH-USDC Position 12345
================================================================================
💰 Current Price: 2011.234567 USDC per WETH
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
Liquidity removed: 0xabc123...
Tokens collected: 0xdef456...
Creating new position with 0.0001 token0 and 0.2 token1
Current pool price: 2011.234567
Position range: [204570, 204670]
✅ Position created! Token ID: 12346
================================================================================
✅ REBALANCE COMPLETE!
📈 Total Rebalances: 1
🆕 New Position ID: 12346
================================================================================
⏳ Next check in 60 seconds...
================================================================================

# [Monitoring continues with new position 12346...]

# User presses Ctrl+C
^C
⛔ Monitoring stopped by user
Final position ID: 12346
Total rebalances performed: 1
```

**That's it!** The system handles everything automatically and keeps you informed every step of the way. 🚀
