# AMM Liquidity Provider Optimizer

Automated liquidity provision optimizer for Blackhole DEX on Avalanche.

## Features

- **Automated Position Management**: Automatically close, unstake, and rebalance LP positions
- **Concentrated Liquidity Optimization**: Calculate optimal price bounds based on volatility and profitability
- **Multiple Strategy Support**:
  - Single hyper-concentrated position that follows price
  - Multiple positions spread across profitable ranges
  - Multi-pool capital allocation
- **Cost-Benefit Analysis**: Balance liquidity concentration vs rebalancing costs
- **Backtesting Framework**: Test strategies on historical data before deploying

## Project Structure

```
AMM-Optimizer/
├── config/                 # Configuration files
│   ├── config.yaml        # Main configuration
│   └── pools.yaml         # Pool configurations
├── src/
│   ├── dex/               # Blackhole DEX interface
│   ├── data/              # Price data collection and storage
│   ├── optimizer/         # Optimization algorithms
│   ├── strategies/        # LP strategies
│   ├── backtesting/       # Backtesting framework
│   └── utils/             # Utilities
├── tests/                 # Unit tests
├── scripts/               # Execution scripts
└── notebooks/             # Jupyter notebooks for experimentation

```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your settings in `config/config.yaml`

3. Set your private key in environment variable:
```bash
export AVAX_PRIVATE_KEY="your_private_key"
```

## Usage

### Backtesting
```bash
python scripts/backtest.py --strategy concentrated --pool AVAX-USDC
```

### Live Trading
```bash
python scripts/run_optimizer.py --strategy concentrated --pool AVAX-USDC
```

## Strategies

### 1. Concentrated Follower
Single position that closely tracks current price with narrow bounds.

### 2. Multi-Position Spread
Multiple positions across different price ranges to capture more fees.

### 3. Multi-Pool Allocator
Dynamically allocate capital across multiple pools based on profitability.

## Configuration

See `config/config.yaml.example` for all available options.

## Risk Warning

This software interacts with blockchain protocols and involves financial risk. Use at your own discretion.
