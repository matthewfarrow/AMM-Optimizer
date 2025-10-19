# 🧪 Testing Your AMM Optimizer on Base Sepolia

## Quick Start (5 minutes)

### Step 1: Get Test ETH 💰

Visit the Base Sepolia faucet and get free test ETH:
**🔗 https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet**

- You'll get **0.05 ETH** (free, once per day)
- That's enough for ~250+ test transactions!

### Step 2: Setup Testnet 🔧

Run the setup script:
```bash
cd /Users/mattfarrow/GitRepos/AMM-Optimizer
./scripts/setup_testnet.sh
```

This will:
- Copy `.env.testnet` to `.env`
- Configure for Base Sepolia (Chain ID: 84532)
- Set testnet contract addresses

### Step 3: Add Your Private Key 🔑

**Option A: Use MetaMask**
1. Create a NEW account in MetaMask (don't use your main one!)
2. Export the private key
3. Add to `.env`:
   ```bash
   BASE_PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
   ```

**Option B: Generate New Wallet**
```bash
# If you have foundry installed
cast wallet new

# Copy the private key to .env
```

⚠️ **NEVER use your mainnet private key on testnet!**

### Step 4: Verify Setup ✅

```bash
python scripts/check_testnet.py
```

This will show:
- Network: Base Sepolia
- Your wallet address
- Your ETH balance
- Gas prices
- Estimated transaction costs

### Step 5: Find Test Pools 🔍

```bash
python scripts/find_pools.py
```

This will discover available Uniswap V3 pools on testnet.

### Step 6: Run Your First Test 🚀

```bash
python scripts/run_optimizer.py \
  --pool WETH-USDC \
  --capital 50 \
  --once
```

## What to Test

### Test 1: Single Position Creation ✅
```bash
python scripts/run_optimizer.py --pool WETH-USDC --capital 50 --once
```

**Expected:**
- ✅ Analyzes market conditions
- ✅ Calculates optimal range
- ✅ Creates concentrated liquidity position
- ✅ Returns transaction hash

### Test 2: Position Rebalancing 🔄
```bash
# Run continuously, checking every 5 minutes
python scripts/run_optimizer.py \
  --pool WETH-USDC \
  --capital 100 \
  --interval 300
```

**Expected:**
- ✅ Monitors price continuously
- ✅ Detects when price moves out of range
- ✅ Automatically rebalances position
- ✅ Logs all activities

### Test 3: Multi-Position Strategy 📊
```bash
python scripts/run_optimizer.py \
  --strategy multi_position \
  --pool WETH-USDC \
  --capital 200 \
  --once
```

**Expected:**
- ✅ Creates 3 positions at different ranges
- ✅ Spreads risk across ranges
- ✅ Better capital efficiency

### Test 4: Different Pools 🌊
```bash
# Test with different token pairs
python scripts/run_optimizer.py --pool WETH-DAI --capital 50 --once
python scripts/run_optimizer.py --pool USDC-DAI --capital 50 --once
```

## Monitoring Your Tests

### View Transactions
Check your transactions on Base Sepolia explorer:
**🔗 https://sepolia.basescan.org/address/YOUR_ADDRESS**

### Check Logs
All activity is logged to `logs/` directory:
```bash
tail -f logs/amm_optimizer_*.log
```

### View Positions
```bash
# See all your active positions
python scripts/view_positions.py
```

## Test Scenarios

### Scenario 1: Low Volatility Market 📉
- **Setup**: USDC-DAI pool (stable pair)
- **Expected**: Very tight ranges (±0.2%)
- **Rebalance**: Rarely (price stable)

### Scenario 2: High Volatility Market 📈
- **Setup**: WETH-USDC with high gas prices
- **Expected**: Wider ranges (±3-5%)
- **Rebalance**: Only when significant price moves

### Scenario 3: Gas Optimization ⛽
- **Setup**: Small position ($10-20)
- **Expected**: Optimizer avoids rebalancing if gas too high
- **Test**: Gas cost > 2% of position value

### Scenario 4: Out of Range 🎯
- **Setup**: Create position, wait for price to move
- **Expected**: Automatic rebalancing triggered
- **Monitor**: Check logs for rebalance decision

## Performance Metrics

After running tests, check your performance:

```python
# In your logs, you'll see:
total_return: 0.0%        # Total position value change
fees_earned: $X.XX       # Fees collected from trading
gas_costs: $X.XX         # Total gas spent
net_profit: $X.XX        # Fees - gas
roi: X.X%                # Return on investment
```

## Common Issues & Solutions

### Issue: "Insufficient funds"
**Solution:** Get more test ETH from faucet (0.05 ETH per day)

### Issue: "Pool not found"
**Solution:** Run `find_pools.py` to discover available testnet pools

### Issue: "Transaction reverted"
**Possible causes:**
- Slippage too low (increase to 1-2% in `.env.testnet`)
- Insufficient token approval
- Pool liquidity too low

### Issue: "Nonce too low"
**Solution:** Wait a few blocks or reset in MetaMask

## Safety Checklist ✅

Before testing:
- [ ] Using testnet configuration (Chain ID: 84532)
- [ ] Have test ETH in wallet (at least 0.01 ETH)
- [ ] Using separate testnet wallet (NOT mainnet keys)
- [ ] Backed up `.env` file
- [ ] Logs directory exists

## Expected Costs (Testnet)

Since Base Sepolia is a testnet, gas is nearly free:

| Action | Gas Used | Cost (ETH) | Cost (USD) |
|--------|----------|------------|------------|
| Open Position | ~200k | ~0.0002 | ~$0.50 |
| Close Position | ~150k | ~0.00015 | ~$0.38 |
| Rebalance | ~350k | ~0.00035 | ~$0.88 |
| Collect Fees | ~100k | ~0.0001 | ~$0.25 |

With 0.05 ETH, you can do **~140 rebalances**!

## After Successful Testing

Once you've verified everything works on testnet:

1. ✅ All strategies execute successfully
2. ✅ Rebalancing logic works correctly
3. ✅ Gas costs are reasonable
4. ✅ No errors in logs
5. ✅ Run for 24-48 hours without issues

**Then you're ready for mainnet:**

```bash
# Backup testnet config
cp .env .env.testnet.backup

# Restore mainnet config
cp .env.backup .env

# Or manually switch
BASE_RPC_URL=https://mainnet.base.org
BASE_CHAIN_ID=8453

# Add REAL private key with REAL funds
# Start with small amount (0.01-0.1 ETH)
```

## Resources

- **Base Sepolia Faucet**: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet
- **Base Sepolia Explorer**: https://sepolia.basescan.org/
- **Uniswap Interface**: https://app.uniswap.org/
- **Base Docs**: https://docs.base.org/
- **Discord Support**: https://discord.gg/buildonbase

---

**Happy Testing! 🧪🚀**

Questions? Check logs or run with verbose output:
```bash
python scripts/run_optimizer.py --pool WETH-USDC --capital 50 --once --verbose
```
