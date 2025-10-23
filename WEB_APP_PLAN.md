# 🌐 Web App Architecture Plan

## 🚨 URGENT: UI Contrast & Readability Fixes (COMPLETED)

### Issues Fixed:
- **White text on light backgrounds** - Changed to dark text with proper contrast
- **"Start Juicing Yields" CTA** - Changed to "Launch App" for clarity
- **Allocation buttons (25%, 50%, 75%, 100%)** - Improved contrast with tangerine theme
- **Error messages** - Enhanced visibility with red background and better contrast
- **Card backgrounds** - Darkened for better text readability
- **Labels and inputs** - Improved font weights and colors

### Changes Made:
- Updated allocation buttons to use `bg-tangerine-primary/20 border-tangerine-primary` with dark text
- Enhanced error messages with `bg-red-500/10` background and `text-red-500`
- Improved card contrast with `bg-slate-800/90` and `text-slate-200`
- Changed CTA button text from "Start Juicing Yields" to "Launch App"
- Added font weights and better color contrast throughout

## 🎯 Project Overview

**Goal:** Create a user-friendly web application for automated Uniswap V3 liquidity management on Base Network.

**Target Users:** DeFi users who want to optimize LP positions without manual monitoring.

## 📁 Repository Structure

### Recommended: Monorepo Approach

```
AMM-Optimizer/
├── backend/              # Python API (existing code)
│   ├── src/             # Core logic (existing)
│   ├── api/             # NEW: FastAPI/Flask endpoints
│   ├── scripts/         # Existing scripts
│   └── requirements.txt
│
├── frontend/            # NEW: React/Next.js web app
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Dashboard, positions, analytics
│   │   ├── hooks/       # React hooks for web3
│   │   └── utils/       # Helper functions
│   ├── public/
│   └── package.json
│
├── shared/              # NEW: Shared types/constants
│   ├── types.ts         # TypeScript types
│   └── constants.ts     # Contract addresses, ABIs
│
└── docs/                # Documentation
    ├── API.md
    ├── DEPLOYMENT.md
    └── USER_GUIDE.md
```

**Why Monorepo?**
- ✅ Easier to keep frontend/backend in sync
- ✅ Shared types and constants
- ✅ Single deployment pipeline
- ✅ Better for small teams

**Alternative: Separate Repos**
- `AMM-Optimizer-Backend` (Python)
- `AMM-Optimizer-Frontend` (React)
- Use this if you want completely independent deployment

## 🎨 Frontend Tech Stack

### Recommended Stack:

```typescript
// Framework
Next.js 14 (App Router)  // React framework with SSR
TypeScript               // Type safety

// Web3 Libraries
Wagmi v2                 // React hooks for Ethereum
Viem                     // Low-level Ethereum library
RainbowKit               // Wallet connection UI

// UI Framework
Tailwind CSS             // Styling
shadcn/ui                // Component library
Recharts                 // Charts for analytics
Framer Motion            // Animations

// State Management
Zustand                  // Lightweight state management
React Query              // Server state caching
```

### Why This Stack?
- **Next.js**: Best React framework, great DX
- **Wagmi/Viem**: Industry standard for web3
- **RainbowKit**: Beautiful wallet connections
- **shadcn/ui**: Modern, customizable components
- **Lightweight**: No Redux bloat

## 🔧 Backend Tech Stack

### API Layer (NEW):

```python
# Add to your existing Python codebase
FastAPI                  # Modern Python API framework
Uvicorn                  # ASGI server
Pydantic                 # Data validation
SQLAlchemy               # Database ORM
Alembic                  # Database migrations
Celery                   # Background tasks
Redis                    # Task queue & caching
PostgreSQL               # Database

# Web3
web3.py                  # Existing
eth-account              # Existing
```

### API Endpoints Structure:

```python
# api/main.py
from fastapi import FastAPI

app = FastAPI()

# Authentication
POST /api/auth/nonce           # Get nonce for wallet
POST /api/auth/verify          # Verify signature

# Positions
GET  /api/positions            # List user's LP positions
GET  /api/positions/{id}       # Get position details
POST /api/positions            # Create new position
DELETE /api/positions/{id}     # Close position

# Analytics
GET  /api/analytics/summary    # Portfolio summary
GET  /api/analytics/performance # Historical performance
GET  /api/analytics/fees       # Fees earned

# Strategies
GET  /api/strategies           # Available strategies
POST /api/strategies/{id}/enable # Enable strategy
POST /api/strategies/{id}/disable # Disable strategy

# Pools
GET  /api/pools                # Available pools
GET  /api/pools/{address}/stats # Pool statistics

# Monitoring (Background)
POST /api/monitor/start        # Start monitoring
POST /api/monitor/stop         # Stop monitoring
GET  /api/monitor/status       # Get monitoring status
```

## 📊 Dashboard Pages

### 1. **Overview/Home** (`/`)
```
┌─────────────────────────────────────┐
│ 🏠 Portfolio Overview               │
├─────────────────────────────────────┤
│ Total Value Locked:   $1,234.56     │
│ Total Fees Earned:    $45.67        │
│ Active Positions:     3             │
│ 24h Change:           +2.3%         │
├─────────────────────────────────────┤
│ [Chart: Value Over Time]            │
├─────────────────────────────────────┤
│ Active Positions:                   │
│ • WETH-USDC  | $500 | ±1% | +$12   │
│ • WETH-DAI   | $400 | ±2% | +$8    │
│ • ETH-USDC   | $334 | ±1% | +$5    │
└─────────────────────────────────────┘
```

### 2. **Positions** (`/positions`)
```
┌─────────────────────────────────────┐
│ 💎 My Positions                     │
│ [+ New Position]                    │
├─────────────────────────────────────┤
│ ┌─ WETH-USDC 0.05% ───────────────┐│
│ │ Value: $500.00                   ││
│ │ Range: $3,960 - $4,040 (±1%)    ││
│ │ Status: 🟢 In Range             ││
│ │ Fees: $12.34 (2.47% APR)        ││
│ │ Strategy: Concentrated Follower  ││
│ │ [View] [Rebalance] [Close]      ││
│ └─────────────────────────────────┘│
│                                     │
│ ┌─ WETH-DAI 0.3% ─────────────────┐│
│ │ Value: $400.00                   ││
│ │ Range: $3,920 - $4,080 (±2%)    ││
│ │ Status: 🟡 Near Edge            ││
│ │ Fees: $8.12 (2.03% APR)         ││
│ │ [View] [Rebalance] [Close]      ││
│ └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

### 3. **Analytics** (`/analytics`)
```
┌─────────────────────────────────────┐
│ 📊 Performance Analytics            │
├─────────────────────────────────────┤
│ Time Period: [7D] [30D] [90D] [All]│
├─────────────────────────────────────┤
│ [Chart: Portfolio Value Over Time]  │
│ [Chart: Fees Earned Daily]          │
│ [Chart: APR by Pool]                │
├─────────────────────────────────────┤
│ Key Metrics:                        │
│ • Total ROI:        +5.2%           │
│ • Avg APR:          12.3%           │
│ • Rebalances:       8               │
│ • Gas Spent:        0.02 ETH        │
│ • Net Profit:       $42.50          │
└─────────────────────────────────────┘
```

### 4. **Pool Explorer** (`/pools`)
```
┌─────────────────────────────────────┐
│ 🏊 Available Pools                  │
│ Search: [________]  Filter: [All ▼] │
├─────────────────────────────────────┤
│ Pool          | TVL    | APR  | Vol │
│───────────────┼────────┼──────┼─────│
│ WETH-USDC 0.05| $45M   | 15%  | $8M │
│ WETH-USDC 0.3 | $120M  | 12%  | $25M│
│ WETH-DAI 0.05 | $12M   | 18%  | $2M │
│ ETH-USDC 0.05 | $89M   | 14%  | $15M│
│                                     │
│ [Click row to add position]         │
└─────────────────────────────────────┘
```

### 5. **Settings** (`/settings`)
```
┌─────────────────────────────────────┐
│ ⚙️ Settings                          │
├─────────────────────────────────────┤
│ Strategy Settings:                  │
│ • Rebalance Threshold:   [5%]       │
│ • Min Profit to Rebalance: [$10]   │
│ • Max Gas Price:         [50 gwei]  │
│                                     │
│ Notifications:                      │
│ ☑ Email on rebalance                │
│ ☑ Alert when out of range           │
│ ☐ Daily portfolio summary           │
│                                     │
│ Network:                            │
│ • Chain: [Base Mainnet ▼]          │
│ • RPC: [Default ▼]                  │
│                                     │
│ [Save Changes]                      │
└─────────────────────────────────────┘
```

## 🔐 Authentication Flow

### Wallet-Based Auth (Recommended):

```typescript
// User connects wallet
1. User clicks "Connect Wallet"
2. RainbowKit shows wallet options
3. User selects MetaMask/WalletConnect
4. Wallet connects

// Sign-In with Ethereum (SIWE)
5. Backend generates nonce
6. User signs message with wallet
7. Backend verifies signature
8. Issue JWT token
9. Store token in localStorage

// Subsequent requests
10. Include JWT in Authorization header
11. Backend validates JWT
12. Return user data
```

**No email/password needed!** Wallet = Identity

## 🔄 Real-Time Updates

### WebSocket Architecture:

```python
# Backend sends updates via WebSocket
fastapi-socketio

# Events:
- position_updated       # Position value changed
- rebalance_triggered    # Rebalance executed
- fees_collected         # Fees claimed
- price_alert            # Price near range edge
- gas_price_update       # Gas price changed
```

```typescript
// Frontend listens
useWebSocket('/ws/positions', {
  onPositionUpdate: (data) => {
    // Update UI instantly
  }
})
```

## 💾 Database Schema

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  wallet_address VARCHAR(42) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Positions table
CREATE TABLE positions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  pool_address VARCHAR(42) NOT NULL,
  token_id INTEGER NOT NULL,  -- NFT ID from Position Manager
  strategy VARCHAR(50),
  capital_usd DECIMAL(18, 2),
  tick_lower INTEGER,
  tick_upper INTEGER,
  status VARCHAR(20),  -- active, closed, out_of_range
  created_at TIMESTAMP DEFAULT NOW(),
  closed_at TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
  id UUID PRIMARY KEY,
  position_id UUID REFERENCES positions(id),
  type VARCHAR(20),  -- mint, burn, rebalance, collect
  tx_hash VARCHAR(66),
  gas_used INTEGER,
  gas_price_gwei DECIMAL(18, 9),
  block_number INTEGER,
  timestamp TIMESTAMP DEFAULT NOW()
);

-- Performance snapshots (for charts)
CREATE TABLE performance_snapshots (
  id UUID PRIMARY KEY,
  position_id UUID REFERENCES positions(id),
  value_usd DECIMAL(18, 2),
  fees_earned_usd DECIMAL(18, 2),
  timestamp TIMESTAMP DEFAULT NOW()
);
```

## 🚀 Deployment Strategy

### Development:
```bash
# Backend
cd backend
uvicorn api.main:app --reload

# Frontend
cd frontend
npm run dev
```

### Production:

**Backend:**
- Deploy to: Railway, Render, or DigitalOcean
- Use: Gunicorn + Uvicorn workers
- Redis for Celery tasks
- PostgreSQL database

**Frontend:**
- Deploy to: Vercel (best for Next.js)
- Auto-deploys from GitHub
- Edge functions for API routes

**Background Worker:**
- Separate Celery worker for monitoring
- Checks positions every 5 minutes
- Triggers rebalances automatically

## 📱 Mobile Responsiveness

All pages fully responsive:
- Desktop: Full dashboard
- Tablet: Simplified layout
- Mobile: Essential info only

Use Tailwind breakpoints:
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {/* Responsive grid */}
</div>
```

## 🔒 Security Considerations

1. **Private Keys**: NEVER store user private keys
2. **Transaction Signing**: Always on client side
3. **API Rate Limiting**: Prevent abuse
4. **Input Validation**: Sanitize all inputs
5. **HTTPS Only**: No HTTP in production
6. **CORS**: Restrict to your domain
7. **Audit Smart Contracts**: Before mainnet

## 📈 Phase 1 MVP (4-6 weeks)

**Week 1-2: Setup & Core Backend**
- [ ] Set up FastAPI
- [ ] Create auth endpoints (SIWE)
- [ ] Migrate existing Python code to API
- [ ] Set up PostgreSQL
- [ ] Create basic CRUD for positions

**Week 3-4: Frontend Foundation**
- [ ] Set up Next.js project
- [ ] Implement Wagmi + RainbowKit
- [ ] Create dashboard layout
- [ ] Build positions page
- [ ] Add wallet connection

**Week 5: Integration**
- [ ] Connect frontend to backend API
- [ ] Test position creation flow
- [ ] Implement real-time updates
- [ ] Add error handling

**Week 6: Polish & Deploy**
- [ ] Add analytics page
- [ ] Improve UI/UX
- [ ] Write documentation
- [ ] Deploy to testnet
- [ ] User testing

## 📈 Phase 2: Advanced Features (4-6 weeks)

- [ ] Advanced analytics (charts, graphs)
- [ ] Multiple strategy support
- [ ] Automated strategy recommendations
- [ ] Portfolio optimization
- [ ] Mobile app (React Native)
- [ ] Social features (leaderboard)

## 💰 Monetization Strategy

**Options:**
1. **Freemium**: Free basic, paid advanced strategies
2. **Performance Fee**: 10% of profits earned
3. **Subscription**: $10/month for unlimited
4. **Transaction Fee**: 0.1% per trade

## 🎯 Success Metrics

Track:
- Daily Active Users (DAU)
- Total Value Locked (TVL)
- Number of positions created
- Average ROI per user
- User retention rate

## 📝 Next Steps

1. **Finish Testing Backend**: Get LP positions working on testnet
2. **Choose Repo Structure**: Monorepo or separate?
3. **Set Up Frontend**: Initialize Next.js project
4. **Build MVP**: Focus on core features first
5. **Test Extensively**: Use testnet for all testing
6. **Deploy Gradually**: Testnet → Mainnet beta → Public

---

**Recommendation:** Start with monorepo, build MVP with core features, test thoroughly on testnet, then expand based on user feedback.

Ready to start building? 🚀
