# External Services Setup Guide

This guide helps you configure the external services needed for Tangerine Trading.

## 1. WalletConnect Project ID

### Steps:
1. Visit [WalletConnect Cloud](https://cloud.walletconnect.com/)
2. Sign up or log in to your account
3. Click "Create Project"
4. Fill in project details:
   - **Project Name**: Tangerine Trading
   - **Project Description**: Wedge-based liquidity management on Base Network
   - **Project URL**: Your domain (or localhost for development)
5. Copy the **Project ID**
6. Add to your `.env.local`:
   ```bash
   NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=278e88c0a5fd5156d817ce944b480586
   ```

## 2. Base Network RPC

### Option A: Public RPC (Free, Rate Limited)
```bash
BASE_RPC_URL=https://mainnet.base.org
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
```

### Option B: Alchemy (Recommended)
1. Visit [Alchemy](https://www.alchemy.com/)
2. Sign up and create a new app
3. Select "Base" network
4. Copy the HTTP URL
5. Add to your `.env`:
   ```bash
   BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/iIkAsMgibgkR4Rwsh_Tm0
   BASE_SEPOLIA_RPC_URL=https://base-sepolia.g.alchemy.com/v2/YOUR_API_KEY
   ```

### Steps:
1. Connect your wallet to Base Sepolia network
2. Visit a faucet
3. Request testnet ETH
4. Wait for confirmation

## 4. Environment Setup

### Update your `.env.local` file:
```bash
# WalletConnect Project ID
NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=278e88c0a5fd5156d817ce944b480586

# Backend API URL
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Contract Addresses (update with deployed addresses)
NEXT_PUBLIC_CONTRACT_ADDRESS_BASE=
NEXT_PUBLIC_CONTRACT_ADDRESS_BASE_SEPOLIA=

# Chain Configuration
NEXT_PUBLIC_CHAIN_ID=8453
```

## 5. Launch the Program

### Start all services:
```bash
python start_all_services.py
```

### Or start individually:
```bash
# Backend API
cd backend && python start_backend.py

# Frontend
npm run dev
```

### Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 6. Testing

1. Connect wallet on http://localhost:3000
2. Select a pool
3. Configure strategy
4. Deploy position
5. Monitor in dashboard

---

**Ready to slice some liquidity!** 🍊
