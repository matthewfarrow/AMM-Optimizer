# 🍊 Tangerine Trading

> Slice your liquidity into optimized wedges. Each wedge, an isolated strategy. Together, complete market coverage.

Tangerine Trading leverages advanced AI to optimize your concentrated liquidity positions on Uniswap V3 for Base Network. Experience the next generation of automated yield farming through intelligent wedge-based strategies.

## 🚀 Quick Start (3 steps)

### 1. Setup Environment
```bash
# Clone and install dependencies
git clone <repository-url>
cd AMM-Optimizer
npm install
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Copy environment template
cp env.example .env
# Edit .env with your configuration (see docs/DEVELOPMENT.md)
```

### 2. Start Services
```bash
# Start all services (API + Frontend + Monitoring)
python start_all_services.py

# Or start individually:
# Backend API: cd backend && python start_backend.py
# Frontend: npm run dev
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🍊 Features

### ✅ Implemented
- [x] **Wedge Strategy Engine**: Each liquidity wedge operates as an isolated strategy
- [x] **Smart Contract**: Multicall rebalancing with whitelist management
- [x] **Pool Data Aggregation**: Real-time Uniswap V3 pool data
- [x] **Volatility Analysis**: AI-powered risk calculations
- [x] **Interactive Charts**: Real-time price visualization
- [x] **Strategy Configuration**: Wedge-based position setup
- [x] **Position Monitoring**: Automated rebalancing dashboard
- [x] **Wallet Integration**: MetaMask, Rainbow, and more
- [x] **Responsive Design**: Mobile and desktop optimized

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
cd backend && python start_backend.py

# Start monitoring service
cd backend && python start_monitor.py
```

### Frontend Development
```bash
# Start development server
npm run dev

# Build for production
npm run build
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

# Private Key (for deployment) - NEVER COMMIT TO GIT
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

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](link-to-issues)
- **Discord**: [Community Server](link-to-discord)
- **Email**: support@tangerine.trading

## 🙏 Acknowledgments

- Uniswap V3 for the concentrated liquidity protocol
- Base Network for low-cost transactions
- RainbowKit for wallet connection
- shadcn/ui for beautiful components
- The DeFi community for inspiration

---

**Built for Base Hackathon 2024** 🏆

**Slice. Optimize. Conquer.** 🍊