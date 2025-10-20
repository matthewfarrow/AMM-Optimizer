# 💰 ETH Usage Guide - Safe for 0.1 ETH!

## ✅ You're Safe! Here's the Math:

### Your Balance: 0.1 ETH (~$400)

### Recommended Test Amounts:

| Operation | ETH Used | USD Value | Purpose |
|-----------|----------|-----------|---------|
| **Wrap to WETH** | 0.0005 | ~$2 | Get WETH for LP pool |
| **Swap for USDC** | 0.005 | ~$20 | Get USDC for LP pool |
| **LP Position** | 0.00125 ETH + $2.50 USDC | ~$5 total | Create test position |
| **Gas (all ops)** | ~0.0002 | ~$0.80 | Transaction fees |
| **TOTAL USED** | **~0.007 ETH** | **~$28** | All operations |
| **REMAINING** | **0.093 ETH** | **~$372** | Safe buffer! |

## 🎯 Complete Test Flow

### Step 1: Wrap ETH → WETH
```bash
python scripts/wrap_eth.py --amount 0.0005
```
**Cost:** 0.0005 ETH + gas = ~0.00051 ETH total

### Step 2: Swap ETH → USDC
```bash
python scripts/get_testnet_tokens.py --amount 0.005
```
**Cost:** 0.005 ETH + gas = ~0.00506 ETH total

### Step 3: Create LP Position
```bash
python scripts/test_create_position.py --capital 5
```
**Cost:** Uses your WETH and USDC from above + gas
- WETH: 0.000625 (~$2.50)
- USDC: 2.50 USDC
- Gas: ~0.0001 ETH

**Total for all 3 steps: ~0.007 ETH (you'll have 0.093 ETH left!)**

## 📊 Scale Options

### Ultra-Conservative (Best for 0.1 ETH)
```bash
# Use defaults - very safe!
python scripts/wrap_eth.py              # 0.0005 ETH
python scripts/get_testnet_tokens.py    # 0.005 ETH
python scripts/test_create_position.py  # $5 position
```
**Total: 0.007 ETH used, 0.093 ETH remaining** ✅

### Conservative
```bash
python scripts/wrap_eth.py --amount 0.001       # 0.001 ETH
python scripts/get_testnet_tokens.py --amount 0.01   # 0.01 ETH  
python scripts/test_create_position.py --capital 10  # $10 position
```
**Total: 0.012 ETH used, 0.088 ETH remaining** ✅

### Moderate (Still Safe)
```bash
python scripts/wrap_eth.py --amount 0.002       # 0.002 ETH
python scripts/get_testnet_tokens.py --amount 0.02   # 0.02 ETH
python scripts/test_create_position.py --capital 20  # $20 position
```
**Total: 0.023 ETH used, 0.077 ETH remaining** ✅

### Aggressive (Use if you're confident)
```bash
python scripts/wrap_eth.py --amount 0.005       # 0.005 ETH
python scripts/get_testnet_tokens.py --amount 0.04   # 0.04 ETH
python scripts/test_create_position.py --capital 40  # $40 position
```
**Total: 0.046 ETH used, 0.054 ETH remaining** ⚠️

### Maximum (Not Recommended!)
```bash
python scripts/wrap_eth.py --amount 0.01        # 0.01 ETH
python scripts/get_testnet_tokens.py --amount 0.08   # 0.08 ETH
python scripts/test_create_position.py --capital 80  # $80 position
```
**Total: 0.091 ETH used, 0.009 ETH remaining** ❌ Too risky!

## 💡 Recommendations

### For 0.1 ETH Testnet Balance:

**First Test (Learn the system):**
- Use ultra-conservative defaults
- Total cost: 0.007 ETH
- You can do this ~14 times!

**Second Test (If first works):**
- Use conservative amounts  
- Total cost: 0.012 ETH
- You can do this ~8 times

**Third Test (If confident):**
- Use moderate amounts
- Total cost: 0.023 ETH
- You can do this ~4 times

## 🚨 Important Notes

### Gas Costs on Base Sepolia
- Gas price: ~0.001 gwei (almost free!)
- Wrap transaction: ~50,000 gas = 0.00005 ETH
- Swap transaction: ~300,000 gas = 0.0003 ETH
- LP mint: ~500,000 gas = 0.0005 ETH
- **Total gas per full cycle: ~0.0009 ETH**

### Why Small Amounts?
1. **Learning**: Test all features with minimal risk
2. **Debugging**: If something fails, you lose pennies not dollars
3. **Multiple Tests**: Run many tests to learn the system
4. **Safety Buffer**: Keep 0.09+ ETH for emergencies

### Can You Test Multiple Times?
**Yes!** With defaults (0.007 ETH per test):
- 1st test: 0.093 ETH remaining
- 2nd test: 0.086 ETH remaining
- 3rd test: 0.079 ETH remaining
- 4th test: 0.072 ETH remaining
- ...up to ~14 tests total!

## 🎓 Learning Path

### Week 1: Tiny Tests
```bash
# Use defaults - be conservative
# Learn how everything works
# Run 3-5 complete tests
# Cost: 0.02-0.035 ETH total
```

### Week 2: Small Tests
```bash
# Increase to $10 positions
# Test rebalancing logic
# Run 2-3 tests
# Cost: 0.024-0.036 ETH total
```

### Week 3: Medium Tests (If Successful)
```bash
# Increase to $20-40 positions
# Run continuous monitoring
# Test edge cases
# Cost: 0.046-0.092 ETH total
```

## ✅ Safety Checklist

Before running ANY command:

- [ ] Confirmed you have 0.1 ETH on Base Sepolia
- [ ] Using default tiny amounts for first test
- [ ] Understand you'll use ~0.007 ETH per test
- [ ] Know you can test ~14 times with 0.1 ETH
- [ ] Have buffer ETH left for emergencies

## 🎯 Quick Reference

**Default Safe Amounts:**
- `wrap_eth.py`: 0.0005 ETH (runs if no --amount specified)
- `get_testnet_tokens.py`: 0.005 ETH (runs if no --amount specified)
- `test_create_position.py`: $5 capital (runs if no --capital specified)

**Just run with no arguments for safest testing!**

```bash
python scripts/wrap_eth.py
python scripts/get_testnet_tokens.py  
python scripts/test_create_position.py
```

**Cost: 0.007 ETH - leaves you 0.093 ETH!** 🎉

---

**Ready to test safely? You're all set!** 💪
