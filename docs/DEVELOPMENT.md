# Development Setup

This guide covers setting up Tangerine Trading for local development.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- A Base Network wallet with testnet ETH

## Environment Setup

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd AMM-Optimizer

# Install root dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env
```

#### Required Environment Variables

**Backend (.env):**
```bash
# Base Network Configuration
BASE_RPC_URL=https://mainnet.base.org
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org

# Contract Addresses (Base Mainnet)
UNISWAP_V3_POSITION_MANAGER=0x03a520b32C04BF3bEEf7BFdF5497F0D5c9b18b5b
UNISWAP_V3_ROUTER=0x2626664c2603336E57B271c5C0b26F421741e481

# Private Key (for deployment) - NEVER COMMIT TO GIT
PRIVATE_KEY=your_private_key_here
WALLET_ADDRESS=your_wallet_address_here

# Backend Configuration
BACKEND_PORT=8000
DATABASE_URL=sqlite:///./app.db
```

**Frontend (.env.local):**
```bash
# WalletConnect Project ID (get from https://cloud.walletconnect.com/)
NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=278e88c0a5fd5156d817ce944b480586

# Backend API URL
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Contract Addresses (set after deployment)
NEXT_PUBLIC_CONTRACT_ADDRESS_BASE=0x...
NEXT_PUBLIC_CONTRACT_ADDRESS_BASE_SEPOLIA=0x...

# Environment
NEXT_PUBLIC_ENVIRONMENT=development
```

## Running Services

### Option 1: Start All Services (Recommended)
```bash
python start_all_services.py
```

This starts:
- Backend API on port 8000
- Frontend on port 3000
- Monitoring service

### Option 2: Start Services Individually

#### Backend API
```bash
cd backend
python start_backend.py
```

#### Frontend
```bash
npm run dev
```

## Testing

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

## Common Issues

### Contract Compilation Errors
- Ensure OpenZeppelin contracts are installed: `npm install @openzeppelin/contracts`
- Check Solidity version compatibility in `hardhat.config.ts`

### Backend Connection Issues
- Verify RPC URL is accessible
- Check environment variables are loaded
- Ensure database file permissions

### Frontend Build Errors
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npm run type-check`
- Verify environment variables are prefixed with `NEXT_PUBLIC_`

---

**Happy coding!** 🍊
