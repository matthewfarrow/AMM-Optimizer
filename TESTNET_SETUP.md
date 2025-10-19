# Base Sepolia Testnet Setup Guide

## Quick Start on Base Sepolia Testnet

### 1. Get Test ETH

**Option A: Base Sepolia Faucet (Recommended)**
- Go to: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet
- Connect your wallet
- Get 0.05 ETH (free, once per day)

**Option B: Sepolia Bridge**
- Get Sepolia ETH from: https://sepoliafaucet.com/
- Bridge to Base Sepolia: https://bridge.base.org/

**Option C: Alchemy Faucet**
- Go to: https://sepoliafaucet.com/
- Sign in with Alchemy account
- Request Sepolia ETH

### 2. Configure for Testnet

Copy the testnet config:
```bash
cp .env.testnet .env
```

Or use environment variable to switch:
```bash
export USE_TESTNET=true
```

### 3. Add Your Testnet Private Key

Edit `.env` and replace:
```bash
BASE_PRIVATE_KEY=your_testnet_private_key_here
```

**⚠️ IMPORTANT**: Use a NEW wallet for testnet only! Never use your mainnet private key!

### 4. Create a Test Wallet (Optional)

If you don't have a testnet wallet:
```bash
# Install cast (foundry)
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Generate new wallet
cast wallet new

# This will output:
# Address: 0x...
# Private Key: 0x...
```

Save the private key to `.env` file.

### 5. Test Liquidity Pools on Base Sepolia

**Available Test Pools:**

1. **WETH-USDC** (0.3% fee)
   - WETH: `0x4200000000000000000000000000000000000006`
   - USDC: `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
   - Pool: Check Uniswap V3 Factory

2. **WETH-DAI** (0.3% fee)
   - Good for testing stable pairs

**Finding Pool Addresses:**
```bash
# We can query the factory to get pool addresses
python scripts/find_pools.py --network testnet
```

### 6. Run on Testnet

Once configured:

```bash
# Single test run
python scripts/run_optimizer.py \
  --pool WETH-USDC \
  --capital 100 \
  --once

# Continuous monitoring (5 min intervals)
python scripts/run_optimizer.py \
  --pool WETH-USDC \
  --capital 500 \
  --interval 300
```

### 7. Verify Transactions

View your transactions on Base Sepolia explorer:
- https://sepolia.basescan.org/

## Testnet vs Mainnet Differences

| Feature | Mainnet | Testnet |
|---------|---------|---------|
| Chain ID | 8453 | 84532 |
| RPC URL | mainnet.base.org | sepolia.base.org |
| ETH | Real money | Free (faucet) |
| Gas Costs | Real | Free |
| Pools | High liquidity | Low liquidity |
| Slippage | Low (~0.5%) | Higher (~1-2%) |

## Testing Strategy

1. **Phase 1**: Deploy small position (0.01 ETH)
   - Verify contract calls work
   - Check position creation
   - Test fee collection

2. **Phase 2**: Test rebalancing
   - Wait for price to move 3%
   - Verify automatic rebalancing
   - Check gas costs

3. **Phase 3**: Test edge cases
   - Out of range positions
   - High volatility
   - Multiple positions

4. **Phase 4**: Run continuous monitoring
   - 24 hour test run
   - Monitor logs
   - Verify performance metrics

## Useful Commands

```bash
# Check your testnet ETH balance
python -c "
from src.dex.web3_client import get_web3_client
client = get_web3_client()
balance = client.w3.eth.get_balance(client.address)
print(f'Balance: {client.w3.from_wei(balance, \"ether\")} ETH')
"

# Check pool price
python scripts/check_pool.py --pool WETH-USDC --network testnet

# View your positions
python scripts/view_positions.py --network testnet

# Simulate without executing
python scripts/run_optimizer.py \
  --pool WETH-USDC \
  --capital 100 \
  --dry-run
```

## Common Issues

**Issue: "Insufficient funds"**
- Solution: Get more test ETH from faucet

**Issue: "Pool not found"**
- Solution: Pool might not exist on testnet, use find_pools.py to discover available pools

**Issue: "Transaction reverted"**
- Solution: Increase slippage tolerance in .env.testnet

**Issue: "Nonce too low"**
- Solution: Reset transaction history in wallet

## Resources

- **Base Sepolia Faucet**: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet
- **Base Docs**: https://docs.base.org/
- **Uniswap V3 Docs**: https://docs.uniswap.org/
- **Base Sepolia Explorer**: https://sepolia.basescan.org/
- **Bridge**: https://bridge.base.org/

## Next Steps After Testing

Once your testnet tests are successful:

1. ✅ Verify all strategies work as expected
2. ✅ Confirm gas costs are reasonable
3. ✅ Test rebalancing logic
4. ✅ Monitor for 24-48 hours

Then switch to mainnet:
```bash
cp .env.mainnet .env
# Add real private key
# Start with small capital (0.01-0.1 ETH)
```

---

**Ready to test!** Get some test ETH and start optimizing! 🚀
