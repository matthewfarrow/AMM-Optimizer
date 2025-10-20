# Quick Start Commands - Testnet Testing

## ⚡ Quick Setup (3 Commands)
**Safe for 0.1 ETH testnet balance!**

### 1. Wrap ETH to WETH
```bash
python scripts/wrap_eth.py --amount 0.0005
```
Wraps 0.0005 ETH → WETH (~$2 worth - very safe!).

### 2. Get Test USDC
```bash
python scripts/get_testnet_tokens.py --amount 0.005
```
Swaps 0.005 test ETH for ~$20 test USDC.

### 3. Create Your First LP Position
```bash
python scripts/test_create_position.py --capital 5
```
Creates a tiny $5 LP position on Base Sepolia testnet.

**Total ETH used: ~0.006 ETH (leaves you with 0.094 ETH for more tests!)**

---

## 📋 All Available Scripts

### Testnet Setup
```bash
# Check your testnet connection and balance
python scripts/check_testnet.py

# Find available Uniswap pools
python scripts/find_pools.py

# Wrap ETH to WETH (tiny amount!)
python scripts/wrap_eth.py --amount 0.0005

# Swap ETH for USDC (small amount!)
python scripts/get_testnet_tokens.py --amount 0.005
```

### LP Position Management
```bash
# Create tiny test LP position ($5 = safe!)
python scripts/test_create_position.py --capital 5

# Run continuous optimization (use tiny capital!)
python scripts/run_optimizer.py \
  --pool WETH-USDC \
  --capital 10 \
  --interval 300 \
  --strategy concentrated_follower
```

---

## 🎯 First Time? Follow This!

**Complete setup in 5 minutes (only uses 0.006 ETH!):**

```bash
# Step 1: Check you're connected to testnet
python scripts/check_testnet.py

# Step 2: Wrap tiny amount of ETH (for WETH)
python scripts/wrap_eth.py --amount 0.0005

# Step 3: Get small amount of USDC
python scripts/get_testnet_tokens.py --amount 0.005

# Step 4: Create tiny LP position
python scripts/test_create_position.py --capital 5
```

**Done! You now have a real LP position on testnet!** 🚀
**And you still have ~0.094 ETH left for more testing!**

---

## 💡 Common Use Cases

### Test with Tiny Capital (Safest!)
```bash
python scripts/test_create_position.py --capital 3
```

### Test with Small Capital
```bash
python scripts/test_create_position.py --capital 10
```

### Test with Medium Capital (if you have more ETH)
```bash
python scripts/test_create_position.py --capital 25
```

### Monitor and Auto-Rebalance
```bash
python scripts/run_optimizer.py \
  --pool WETH-USDC \
  --capital 10 \
  --interval 300
```

### Check Logs
```bash
tail -f logs/optimizer.log
```

---

## 🆘 Troubleshooting

### "Insufficient WETH"
```bash
python scripts/wrap_eth.py --amount 0.0005
```

### "Insufficient USDC"
```bash
python scripts/get_testnet_tokens.py --amount 0.005
```

### "Not enough ETH"
You only have 0.1 ETH on testnet. Use tiny amounts:
- Wrap: 0.0005 ETH
- Swap: 0.005 ETH  
- Position: $5 capital
- Total: ~0.006 ETH used

### "Not connected to testnet"
Check your `.env` file:
```bash
BASE_CHAIN_ID=84532
BASE_RPC_URL=https://sepolia.base.org
```

---

**That's it! You're ready to test!** 🎉
