# AMM Liquidity Optimizer

Automated Uniswap V3 liquidity management on Base Network with intelligent rebalancing, volatility analysis, and risk management.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### 1. Clone and Setup

```bash
git clone <repository-url>
cd AMM-Optimizer

# Install Python dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Install Node.js dependencies
cd frontend
npm install
cd ..

# Install Hardhat dependencies
npm install
```

### 2. Environment Setup

Create environment files:

```bash
# Copy example environment files
cp env.example .env
cp frontend/env.local.example frontend/.env.local

# Edit the files with your configuration
# - Add your private key for deployment
# - Add WalletConnect project ID
# - Set contract addresses after deployment
```

### 3. Start All Services

```bash
# Start everything (API + Frontend + Monitoring)
python start_all_services.py

# Or start individually:
# Backend API: cd backend/api && python main.py
# Frontend: cd frontend && npm run dev
# Monitoring: cd backend && python start_monitor.py
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🏗️ Architecture

### Smart Contracts (`contracts/`)
- **LiquidityManager.sol**: Main contract for position management
- Multicall pattern for efficient rebalancing
- Whitelist enforcement for beta testing
- Emergency withdrawal functions

### Backend (`backend/`)
- **FastAPI Server**: REST API for frontend communication
- **Monitoring Service**: Automated position monitoring and rebalancing
- **Database**: SQLite for MVP (easily upgradeable to PostgreSQL)

### Frontend (`frontend/`)
- **Next.js 14**: Modern React framework with App Router
- **Web3 Integration**: wagmi + RainbowKit for wallet connection
- **UI Components**: shadcn/ui + Tailwind CSS
- **Three-Tab Interface**: Pool Selection → Strategy Configuration → Monitoring

## 📋 Features

### ✅ Implemented
- [x] Smart contract with multicall rebalancing
- [x] Whitelist management system
- [x] Pool data aggregation from Uniswap
- [x] Volatility analysis and risk calculations
- [x] Interactive price charts
- [x] Strategy configuration interface
- [x] Position monitoring dashboard
- [x] Wallet connection (MetaMask, Rainbow, etc.)
- [x] Responsive design for mobile/desktop

### 🔄 In Progress
- [ ] Real-time position monitoring
- [ ] Smart contract deployment to Base
- [ ] End-to-end testing

### 📅 Planned
- [ ] Multi-position support
- [ ] Advanced analytics
- [ ] Mobile app
- [ ] Governance token

## 🛠️ Development

### Smart Contract Development

```bash
# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test

# Deploy to Base Sepolia
npx hardhat run scripts/deploy.ts --network baseSepolia

# Deploy to Base Mainnet
npx hardhat run scripts/deploy.ts --network base
```

### Backend Development

```bash
# Start API server
cd backend/api
python main.py

# Start monitoring service
cd backend
python start_monitor.py

# Run tests
pytest backend/tests/
```

### Frontend Development

```bash
cd frontend

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Base Network Configuration
BASE_RPC_URL=https://mainnet.base.org
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org

# Contract Addresses
UNISWAP_V3_POSITION_MANAGER=0x03a520b32C04BF3bEEf7BFdF5497F0D5c9b18b5b
UNISWAP_V3_ROUTER=0x2626664c2603336E57B271c5C0b26F421741e481

# Private Key (for deployment)
PRIVATE_KEY=your_private_key_here

# Backend Configuration
BACKEND_PORT=8000
DATABASE_URL=sqlite:///./app.db
```

#### Frontend (.env.local)
```bash
# WalletConnect Project ID
NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=your_project_id

# Backend API URL
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Contract Addresses
NEXT_PUBLIC_CONTRACT_ADDRESS_BASE=0x...
NEXT_PUBLIC_CONTRACT_ADDRESS_BASE_SEPOLIA=0x...
```

## 🚨 Security & Risk Management

### Beta Testing Notice
⚠️ **This application is in beta testing phase. Please use only test funds that you are willing to lose.**

### Security Features
- Whitelist enforcement for beta access
- Non-custodial design (users control their funds)
- Emergency withdrawal functions
- Gas cost validation before rebalancing
- Rate limiting on API endpoints

### Risk Controls
- Liquidation probability calculations
- Volatility-based position sizing
- Minimum profitability thresholds
- Configurable check intervals

## 📊 API Documentation

### Core Endpoints

#### Pools
- `GET /api/pools` - List all Uniswap V3 pools
- `GET /api/pools/{address}` - Get pool details
- `GET /api/pools/{address}/stats` - Get pool statistics

#### Analytics
- `GET /api/analytics/{address}/price-data` - Get price history
- `GET /api/analytics/{address}/volatility` - Get volatility analysis
- `GET /api/analytics/{address}/strategy-recommendations` - Get AI recommendations

#### Positions
- `GET /api/positions/user/{address}` - Get user positions
- `POST /api/positions/create` - Create new position
- `POST /api/positions/{id}/pause` - Pause position monitoring

#### Whitelist
- `GET /api/whitelist/status/{address}` - Check whitelist status
- `POST /api/whitelist/signup` - Sign up for beta access

## 🧪 Testing

### Smart Contract Tests
```bash
npx hardhat test
```

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### End-to-End Testing
```bash
# Start all services
python start_all_services.py

# In another terminal, run E2E tests
npm run test:e2e
```

## 🚀 Deployment

### Smart Contracts
1. Deploy to Base Sepolia testnet
2. Verify contracts on Basescan
3. Deploy to Base Mainnet
4. Update environment variables

### Backend
1. Deploy to Railway/Render/DigitalOcean
2. Set up PostgreSQL database
3. Configure environment variables
4. Set up monitoring and logging

### Frontend
1. Build production bundle
2. Deploy to Vercel/Netlify
3. Configure environment variables
4. Set up custom domain

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: [Project Wiki](link-to-wiki)
- **Issues**: [GitHub Issues](link-to-issues)
- **Discord**: [Community Server](link-to-discord)
- **Email**: support@ammoptimizer.com

## 🙏 Acknowledgments

- Uniswap V3 for the concentrated liquidity protocol
- Base Network for low-cost transactions
- RainbowKit for wallet connection
- shadcn/ui for beautiful components
- The DeFi community for inspiration

---

**Built for Base Hackathon 2024** 🏆