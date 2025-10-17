"""
System Architecture Diagram Generator
Creates a visual representation of the optimizer architecture.
"""

architecture_diagram = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    AMM LIQUIDITY OPTIMIZER ARCHITECTURE                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  run_optimizer.py  │  backtest.py  │  examples.py                           │
│  • CLI arguments   │  • Historical │  • Test config                         │
│  • Loop control    │  • Simulation │  • Examples                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STRATEGY LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  Concentrated    │  │  Multi-Position  │  │   Multi-Pool     │          │
│  │    Follower      │  │    Strategy      │  │    Strategy      │          │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤          │
│  │ • Single pos     │  │ • 3 positions    │  │ • Cross-pool     │          │
│  │ • Tight range    │  │ • Varied ranges  │  │ • Allocation     │          │
│  │ • Follow price   │  │ • Less rebalance │  │ • Diversified    │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                │                                             │
│                    Implements: analyze() & execute()                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌──────────────────────────┐  ┌──────────────────────────────────────┐
│   OPTIMIZER LAYER        │  │        DATA LAYER                     │
├──────────────────────────┤  ├──────────────────────────────────────┤
│ LiquidityOptimizer       │  │  PriceDataCollector                  │
│ ┌──────────────────────┐ │  │  ┌────────────────────────────────┐ │
│ │ calculate_optimal_   │ │  │  │ • fetch_current_price()        │ │
│ │   range()            │ │  │  │ • fetch_historical_prices()    │ │
│ │                      │ │  │  │ • calculate_volatility()       │ │
│ │ • Volatility         │ │  │  │ • calculate_price_move_prob()  │ │
│ │ • Gas costs          │ │  │  │ • get_fee_apr()                │ │
│ │ • Concentration      │ │  │  └────────────────────────────────┘ │
│ │ • Tick ranges        │ │  │                                      │
│ │                      │ │  │  Data Sources:                       │
│ │ should_rebalance()   │ │  │  • DexScreener API                   │
│ │                      │ │  │  • The Graph                         │
│ │ • Check thresholds   │ │  │  • Direct pool contracts             │
│ │ • Time limits        │ │  │  • Custom indexer                    │
│ │ • Price deviation    │ │  │                                      │
│ └──────────────────────┘ │  └──────────────────────────────────────┘
└──────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXECUTION LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                        BlackholeDEX                                 │    │
│  ├────────────────────────────────────────────────────────────────────┤    │
│  │  • get_pool_price()         • add_liquidity()                      │    │
│  │  • get_pool_liquidity()     • remove_liquidity()                   │    │
│  │  • get_position()           • stake_position()                     │    │
│  │  • get_positions_for_wallet()  • unstake_position()                │    │
│  │  • collect_fees()           • rebalance_position()                 │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                   │                                          │
│                                   ▼                                          │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                        Web3Client                                   │    │
│  ├────────────────────────────────────────────────────────────────────┤    │
│  │  • send_transaction()                                              │    │
│  │  • call_contract_function()                                        │    │
│  │  • execute_contract_function()                                     │    │
│  │  • wait_for_transaction()                                          │    │
│  │  • estimate_gas()                                                  │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BLOCKCHAIN LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                         Avalanche C-Chain                                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  Blackhole DEX   │  │  Blackhole DEX   │  │  Blackhole DEX   │          │
│  │     Router       │  │  Position Mgr    │  │    Staking       │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════════════════════

                              DATA FLOW EXAMPLE

┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. User runs: python scripts/run_optimizer.py --pool AVAX-USDC --capital 5000│
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. Strategy.analyze() called                                                 │
│    • Fetch current price from PriceDataCollector                            │
│    • Calculate volatility from historical data                              │
│    • Call LiquidityOptimizer.calculate_optimal_range()                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. Optimizer calculates optimal range                                        │
│    • Volatility: 0.05 (5%)                                                  │
│    • Gas cost: $7.50                                                        │
│    • Concentration factor: 0.65                                             │
│    • Optimal range: ±8% (ticks: [195500, 198200])                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. Strategy decides action                                                   │
│    • Action: "open_position"                                                │
│    • Lower tick: 195500                                                     │
│    • Upper tick: 198200                                                     │
│    • Capital: $5000                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. Strategy.execute() called                                                 │
│    • Calculate token amounts (token0: X AVAX, token1: Y USDC)              │
│    • Call BlackholeDEX.add_liquidity()                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. BlackholeDEX executes                                                     │
│    • Approve token0 (AVAX)                                                  │
│    • Approve token1 (USDC)                                                  │
│    • Call router.addLiquidity() via Web3Client                              │
│    • Wait for transaction confirmation                                      │
│    • Stake position for rewards                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 7. Position created on-chain                                                 │
│    • NFT minted representing position                                       │
│    • Liquidity added to pool                                                │
│    • Position staked for rewards                                            │
│    • Transaction hash returned                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 8. Monitoring loop begins                                                    │
│    • Wait 5 minutes (interval)                                              │
│    • Check current price                                                    │
│    • Determine if rebalance needed                                          │
│    • If yes: close old position, open new position                          │
│    • If no: continue monitoring                                             │
│    • Repeat...                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════════════════════

                         REBALANCING DECISION TREE

                          ┌─────────────────┐
                          │  Check Position │
                          └────────┬────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
         ┌────────────────────┐         ┌──────────────────┐
         │ Price out of range?│         │ Price deviation  │
         │                    │         │ > threshold?     │
         └────────┬───────────┘         └────────┬─────────┘
                  │                              │
          YES ────┤                      YES ────┤
                  │                              │
                  ▼                              ▼
         ┌────────────────────┐         ┌──────────────────┐
         │ Min time elapsed?  │         │ Min time elapsed?│
         └────────┬───────────┘         └────────┬─────────┘
                  │                              │
          YES ────┼──────────────────────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │ Gas cost < max %?  │
         └────────┬───────────┘
                  │
          YES ────┤
                  │
                  ▼
         ┌────────────────────┐
         │  REBALANCE!        │
         │                    │
         │ 1. Unstake         │
         │ 2. Remove liquidity│
         │ 3. Collect fees    │
         │ 4. Add new liquidity│
         │ 5. Stake           │
         └────────────────────┘

                  NO (all checks)
                  │
                  ▼
         ┌────────────────────┐
         │      HOLD          │
         │  Continue monitoring│
         └────────────────────┘

════════════════════════════════════════════════════════════════════════════════
"""

print(architecture_diagram)
