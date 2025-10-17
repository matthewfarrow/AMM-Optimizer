# Quick Start Guide

## Installation

1. **Clone and setup**:
```bash
cd /Users/mattfarrow/GitRepos/AMM-Optimizer
./setup.sh
```

2. **Configure your environment**:
Edit `.env` file:
```bash
AVAX_PRIVATE_KEY=your_private_key_here
AVAX_RPC_URL=https://api.avax.network/ext/bc/C/rpc
```

3. **Configure pools**:
Edit `config/pools.yaml` with actual Blackhole DEX pool addresses.

## Usage

### Run Examples
```bash
source venv/bin/activate
python scripts/examples.py
```

### Backtest a Strategy
```bash
python scripts/backtest.py --pool AVAX-USDC --capital 10000 --days 30
```

### Run Optimizer (Once)
```bash
python scripts/run_optimizer.py \
  --strategy concentrated_follower \
  --pool AVAX-USDC \
  --capital 5000 \
  --once
```

### Run Optimizer (Continuous)
```bash
python scripts/run_optimizer.py \
  --strategy concentrated_follower \
  --pool AVAX-USDC \
  --capital 5000 \
  --interval 300
```

### Multi-Position Strategy
```bash
python scripts/run_optimizer.py \
  --strategy multi_position \
  --pool AVAX-USDC \
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

### Pool Settings
Edit `config/pools.yaml`:

```yaml
pools:
  - name: "AVAX-USDC"
    address: "0x..."  # Add actual address
    enabled: true
    priority: 1
```

## Strategies Explained

### 1. Concentrated Follower
- **What**: Single position that closely tracks current price
- **Best for**: Low volatility, frequent rebalancing acceptable
- **Pros**: Maximum fee capture when price is stable
- **Cons**: High gas costs if price moves a lot

### 2. Multi-Position
- **What**: 3 positions with varying concentrations
- **Best for**: Medium volatility, want wider coverage
- **Pros**: Less rebalancing, captures fees across ranges
- **Cons**: Less concentrated, lower fees per unit liquidity

### 3. Multi-Pool (To Implement)
- **What**: Allocate capital across multiple pools
- **Best for**: Diversification, maximize overall returns
- **Pros**: Risk diversification, chase highest APR
- **Cons**: Complex, more gas costs

## Key Concepts

### Concentration
Higher concentration = tighter range = more fees but more risk of going out of range.

```
Concentration 0.9: ±5% range  (very tight)
Concentration 0.5: ±15% range (medium)
Concentration 0.1: ±40% range (wide)
```

### Rebalancing
Position needs rebalancing when:
1. Price moves too far from center (threshold: 5%)
2. Price goes out of range
3. Enough time has passed (min: 1 hour)

### Gas Costs
Each rebalance costs ~$5-10 in AVAX at 25 gwei:
- Unstake position
- Remove liquidity
- Collect fees
- Add new liquidity
- Stake position

## Monitoring

Logs are saved to `logs/optimizer.log`

Watch logs in real-time:
```bash
tail -f logs/optimizer.log
```

## Safety

⚠️ **Before Running with Real Money**:

1. Test with small amounts first
2. Verify all pool addresses are correct
3. Check Blackhole DEX ABIs are implemented
4. Backtest on historical data
5. Run in dry-run mode initially
6. Monitor for at least 24 hours with small capital

## Troubleshooting

### "No price data available"
- Price data fetching not implemented yet
- See `IMPLEMENTATION_NOTES.md` for how to add

### "Contract call failed"
- Blackhole DEX ABIs not added yet
- Get ABIs from Blackhole docs or SnowTrace

### "Insufficient gas"
- Increase `gas_price_gwei` in config
- Check AVAX balance

### "Transaction failed"
- Check slippage settings
- Verify pool has liquidity
- Check token approvals

## Advanced Usage

### Custom Strategy
Create new file `src/strategies/my_strategy.py`:

```python
from .base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def analyze(self, pool_name, capital_usd):
        # Your logic here
        pass
    
    def execute(self, analysis):
        # Your execution here
        pass
```

### Modify Optimizer Logic
Edit `src/optimizer/liquidity_optimizer.py` to change:
- How ranges are calculated
- Concentration factors
- Rebalancing triggers

### Add Price Data Source
Edit `src/data/price_data.py`:

```python
def fetch_current_price(self, pool_name):
    # Add your price source here
    # Options: DexScreener, The Graph, direct contract call
    pass
```

## Next Steps

1. **Add Blackhole DEX integration** (see IMPLEMENTATION_NOTES.md)
2. **Implement price data fetching**
3. **Test with small capital on mainnet**
4. **Monitor and optimize**
5. **Scale up gradually**

## Resources

- Project docs: `IMPLEMENTATION_NOTES.md`
- Config: `config/config.yaml`
- Pools: `config/pools.yaml`
- Logs: `logs/optimizer.log`

## Support

Check `IMPLEMENTATION_NOTES.md` for detailed implementation guidance.

Good luck! 🚀
