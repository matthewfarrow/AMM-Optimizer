# Quick Start Guide - Base Network & Uniswap V3

## Installation

1. **Clone and setup**:
```bash
cd /Users/mattfarrow/GitRepos/AMM-Optimizer
./setup.sh
```

2. **Configure your environment**:
Edit `.env` file:
```bash
BASE_PRIVATE_KEY=your_private_key_here
BASE_RPC_URL=https://mainnet.base.org
```

3. **Pools are pre-configured**:
Main pools on Base are already configured in `config/pools.yaml`:
- WETH-USDC (0.05%)
- WETH-USDbC (0.05%)
- Additional pools available

## Usage

### Run Examples
```bash
source venv/bin/activate
python scripts/examples.py
```

### Backtest a Strategy
```bash
python scripts/backtest.py --pool WETH-USDC --capital 10000 --days 30
```

### Run Optimizer (Once)
```bash
python scripts/run_optimizer.py \
  --strategy concentrated_follower \
  --pool WETH-USDC \
  --capital 5000 \
  --once
```

### Run Optimizer (Continuous)
```bash
python scripts/run_optimizer.py \
  --strategy concentrated_follower \
  --pool WETH-USDC \
  --capital 5000 \
  --interval 300
```

### Multi-Position Strategy
```bash
python scripts/run_optimizer.py \
  --strategy multi_position \
  --pool WETH-USDC \
  --capital 10000 \
  --interval 600
```

## Configuration

### Strategy Settings
Edit `config/config.yaml`:

```yaml
strategy:
  type: "concentrated_follower"
  rebalance_threshold: 0.05  # 5% price move triggers rebalance
  position_concentration: 0.5  # How concentrated (0-1)
  max_gas_cost_ratio: 0.02  # Max 2% gas costs
```

### Available Pools
Pre-configured in `config/pools.yaml`:

```yaml
pools:
  - name: "WETH-USDC"
    enabled: true  # Main pool
  - name: "WETH-USDbC" 
    enabled: true
  - name: "WETH-DAI"
    enabled: false
```

## Strategies Explained

### 1. Concentrated Follower
- **What**: Single position that closely tracks current price
- **Best for**: Low volatility, frequent rebalancing acceptable
- **Pros**: Maximum fee capture when price is stable
- **Cons**: Higher gas costs if price moves frequently
- **Gas cost**: ~$0.10-0.50 per rebalance on Base (very low!)

### 2. Multi-Position
- **What**: 3 positions with varying concentrations
- **Best for**: Medium volatility, wider coverage
- **Pros**: Less rebalancing, captures fees across ranges
- **Cons**: Less concentrated, lower fees per unit liquidity

## Key Features for Base Network

### Ultra-Low Gas Fees
Base has extremely low gas fees compared to Ethereum:
- Ethereum: ~$50-200 per rebalance
- Base: ~$0.10-0.50 per rebalance
- This enables much more aggressive rebalancing strategies!

### Uniswap V3 on Base
- Same proven contracts as Ethereum mainnet
- Deep liquidity in major pairs
- Lower fees = higher net APR

### Optimal Pairs
- **WETH-USDC**: Most liquid, 0.05% fee tier
- **WETH-USDbC**: Bridged USDC, also very liquid
- **Stablecoin pairs**: Ultra-tight ranges possible

## Key Concepts

### Concentration
Higher concentration = tighter range = more fees but more risk of going out of range.

```
Concentration 0.9: ±5% range  (very tight) - Great for Base due to low gas!
Concentration 0.5: ±15% range (medium)
Concentration 0.1: ±40% range (wide)
```

### Rebalancing
Position needs rebalancing when:
1. Price moves too far from center (threshold: 5%)
2. Price goes out of range
3. Enough time has passed (min: 1 hour)

**On Base**: You can rebalance more frequently due to low gas costs!

### Gas Costs
Each rebalance costs ~$0.10-0.50 on Base:
- Remove liquidity
- Collect fees  
- Add new liquidity

**Compare to Ethereum**: $50-200
**Compare to Avalanche**: $5-15

This means you can be MUCH more aggressive with rebalancing!

## Monitoring

Logs are saved to `logs/optimizer.log`

Watch logs in real-time:
```bash
tail -f logs/optimizer.log
```

## Safety

⚠️ **Before Running with Real Money**:

1. Test with small amounts first
2. Verify all pool addresses are correct (pre-configured)
3. Run in dry-run mode initially (use --once flag)
4. Monitor for at least 24 hours with small capital
5. Base is safe and battle-tested, but always start small!

## Troubleshooting

### "No price data available"
- Price data fetching from contracts not fully implemented
- Can fetch from DexScreener or The Graph
- See `IMPLEMENTATION_NOTES.md`

### "Transaction failed"
- Check slippage settings
- Verify pool has liquidity (major pools do)
- Check token approvals

### "Insufficient gas"
- Very rare on Base due to low gas fees
- Check ETH balance for gas

## Advanced Usage

### Why Base is Perfect for This

1. **Low Gas Costs**: Rebalance 50-200x cheaper than Ethereum
2. **Uniswap V3**: Same proven contracts
3. **Growing Liquidity**: Rapidly increasing TVL
4. **L2 Speed**: Fast confirmations
5. **High APR Potential**: Low gas = higher net APR

### Aggressive Strategies on Base

Because gas is so cheap, you can:
- Use tighter concentration factors
- Rebalance more frequently
- Capture more fees
- Experiment with multiple positions

Example: On Ethereum, a $1000 position might need $50 to rebalance (5% of capital).
On Base, same position costs $0.25 to rebalance (0.025% of capital).

This is a game-changer!

## Next Steps

1. **Set up your wallet** with BASE_PRIVATE_KEY
2. **Add some ETH** for gas (even $5-10 is plenty!)
3. **Test with small capital** ($100-500)
4. **Monitor performance** for a week
5. **Scale up gradually**

## Resources

- Base Network: https://base.org
- Uniswap V3 Docs: https://docs.uniswap.org/
- Pool Explorer: https://info.uniswap.org/#/base/
- Gas Tracker: https://basescan.org/gastracker

## Support

Check `IMPLEMENTATION_NOTES.md` for detailed implementation guidance.

Welcome to efficient LP optimization on Base! 🚀💙
