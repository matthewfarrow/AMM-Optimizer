# 🎯 Ready to Test on Base Sepolia!

## ✅ Setup Complete

Your AMM Optimizer is now configured for **Base Sepolia Testnet**!

## 🚀 Quick Start (3 Steps)

### 1. Get Free Test ETH (2 minutes)

Visit the official Base faucet:
**🔗 https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet**

You'll receive:
- **0.05 ETH** (free!)
- Good for **~140+ test transactions**
- Resets daily

### 2. Add Your Testnet Private Key (1 minute)

Edit `.env` file and add your testnet wallet private key:

```bash
BASE_PRIVATE_KEY=0xYOUR_TESTNET_PRIVATE_KEY_HERE
```

**⚠️ CRITICAL: Use a NEW wallet for testnet only!**
- Create a new MetaMask account
- Export the private key
- **NEVER use your mainnet wallet!**

### 3. Run Your First Test (30 seconds)

```bash
# Check setup
python scripts/check_testnet.py

# Run optimizer
python scripts/run_optimizer.py --pool WETH-USDC --capital 100 --once
```

## 📊 What's Configured

✅ **Network**: Base Sepolia Testnet
✅ **Chain ID**: 84532  
✅ **RPC**: https://sepolia.base.org
✅ **Uniswap V3**: Official testnet contracts
✅ **Explorer**: https://sepolia.basescan.org/

## 🧪 Test Strategy

### Phase 1: Basic Test (10 minutes)
```bash
# Single position - verify everything works
python scripts/run_optimizer.py --pool WETH-USDC --capital 50 --once
```

**Verify:**
- ✅ Transaction succeeds
- ✅ Position created
- ✅ Gas cost < $1
- ✅ Check on explorer

### Phase 2: Rebalancing Test (1 hour)
```bash
# Run continuously, check every 5 min
python scripts/run_optimizer.py --pool WETH-USDC --capital 100 --interval 300
```

**Verify:**
- ✅ Monitors price
- ✅ Detects out-of-range
- ✅ Auto-rebalances
- ✅ Logs properly

### Phase 3: Stress Test (24 hours)
```bash
# Overnight test with larger capital
python scripts/run_optimizer.py --pool WETH-USDC --capital 500 --interval 180
```

**Verify:**
- ✅ Runs without crashes
- ✅ Handles edge cases
- ✅ Performance metrics accurate
- ✅ Gas optimization working

## 📈 Expected Results

With **0.05 ETH testnet funds**:
- ~140 position rebalances possible
- Test all strategies multiple times
- Plenty for comprehensive testing

### Sample Output
```
2025-10-19 11:05:32 | INFO | Running strategy: Concentrated Follower
2025-10-19 11:05:32 | INFO | Pool: WETH-USDC, Capital: $100.00
2025-10-19 11:05:32 | INFO | Current price: $2,500.63
2025-10-19 11:05:32 | INFO | Volatility: 0.72%
2025-10-19 11:05:32 | INFO | Optimal range: ±1.00% ($2,440 - $2,565)
2025-10-19 11:05:32 | INFO | Gas cost: $0.37 (0.37%)
2025-10-19 11:05:32 | INFO | ✅ Position opened!
```

## 🔧 Helpful Commands

### Check Your Setup
```bash
python scripts/check_testnet.py
```
Shows: balance, network, gas prices, transaction estimates

### Find Available Pools
```bash
python scripts/find_pools.py
```
Discovers all Uniswap V3 pools on Base Sepolia

### Check Balance
```bash
python -c "
from src.dex.web3_client import get_web3_client
c = get_web3_client()
print(f'Balance: {c.w3.from_wei(c.w3.eth.get_balance(c.address), \"ether\")} ETH')
"
```

### View Logs
```bash
tail -f logs/amm_optimizer_*.log
```

### View on Explorer
```bash
# Replace with your address
open https://sepolia.basescan.org/address/YOUR_ADDRESS
```

## ⚠️ Important Notes

### Testnet vs Mainnet Differences

| Feature | Testnet | Mainnet |
|---------|---------|---------|
| ETH Cost | FREE | Real money |
| Liquidity | Low | High |
| Slippage | Higher (1-2%) | Lower (0.5%) |
| Gas Price | ~0.001 gwei | ~0.1 gwei |
| Risk | Zero | High |

### Safety Checklist

Before each test:
- [ ] Confirmed testnet mode (Chain ID: 84532)
- [ ] Using testnet-only wallet
- [ ] Have sufficient test ETH (>0.01 ETH)
- [ ] Logs directory accessible
- [ ] Explorer bookmarked for verification

## 🎓 Learning Objectives

Through testnet testing, you'll:

1. **Understand Strategy Behavior**
   - How tight vs wide ranges perform
   - When rebalancing triggers
   - Gas cost impact on profitability

2. **Optimize Parameters**
   - Best concentration factors
   - Optimal rebalance thresholds
   - Gas cost ratios

3. **Test Edge Cases**
   - High volatility periods
   - Low liquidity pools
   - Rapid price movements

4. **Build Confidence**
   - See actual on-chain transactions
   - Verify calculations are correct
   - Ensure error handling works

## 📚 Documentation

All guides are in the repo:

- `TESTNET_SETUP.md` - Detailed testnet configuration
- `TESTING_GUIDE.md` - Comprehensive testing scenarios
- `QUICKSTART_BASE.md` - General usage guide
- `LAUNCH_SUCCESS.md` - What's working now

## 🚨 Troubleshooting

**Problem**: Can't connect to testnet
```bash
# Check RPC in .env
BASE_RPC_URL=https://sepolia.base.org
BASE_CHAIN_ID=84532
```

**Problem**: No test ETH
- Visit faucet (once per day): https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet

**Problem**: Transaction fails
- Increase slippage in `.env.testnet`
- Check pool has liquidity: `python scripts/find_pools.py`

**Problem**: "Pool not found"
- Run `find_pools.py` to see available pools
- Some pools may not exist on testnet

## ✅ When You're Ready for Mainnet

After successful testnet testing:

1. All strategies work as expected ✅
2. Rebalancing logic verified ✅
3. No errors in 24hr test ✅
4. Performance metrics accurate ✅

Then:
```bash
# Restore mainnet config
cp .env.backup .env

# Or create new mainnet .env
# Add REAL private key with REAL funds
# Start with small capital (0.01-0.1 ETH)
```

---

## 🎯 Your Next Action

**Right now, do this:**

1. **Get test ETH**: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet
2. **Add private key** to `.env` (testnet wallet only!)
3. **Run check**: `python scripts/check_testnet.py`
4. **First test**: `python scripts/run_optimizer.py --pool WETH-USDC --capital 100 --once`

**That's it!** You'll see your optimizer in action on testnet!

---

**Questions?** Check the logs or docs. Everything is documented! 📖

**Ready to go!** 🚀
