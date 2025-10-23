# Deployment Guide

This guide covers deploying the AMM Optimizer to production on Base Network.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Smart         │
│   (Vercel)      │◄──►│   (Railway)     │◄──►│   Contracts     │
│   Next.js       │    │   FastAPI       │    │   (Base)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    ┌────▼────┐            ┌─────▼─────┐           ┌─────▼─────┐
    │  Users  │            │  Monitor  │           │  Uniswap  │
    │ (Wallets)│            │  Service  │           │    V3     │
    └─────────┘            └───────────┘           └───────────┘
```

## 📋 Prerequisites

### Required Accounts
- [Vercel](https://vercel.com) account (frontend)
- [Railway](https://railway.app) account (backend)
- [Base](https://base.org) wallet with ETH for gas
- [Basescan](https://basescan.org) account (contract verification)

### Required Tools
- Node.js 18+
- Python 3.11+
- Git
- [Railway CLI](https://docs.railway.app/develop/cli)
- [Vercel CLI](https://vercel.com/cli)

## 🚀 Step-by-Step Deployment

### Phase 1: Smart Contract Deployment

#### 1.1 Deploy to Base Sepolia (Testing)

```bash
# Set up environment
cp env.example .env
# Edit .env with your configuration

# Deploy to Base Sepolia
npx hardhat run scripts/deploy.ts --network baseSepolia

# Note the deployed contract address
# Example: 0x1234567890abcdef1234567890abcdef12345678
```

#### 1.2 Verify Contracts

```bash
# Verify on Basescan
npx hardhat verify --network baseSepolia <CONTRACT_ADDRESS>
```

#### 1.3 Deploy to Base Mainnet

```bash
# Deploy to Base Mainnet
npx hardhat run scripts/deploy.ts --network base

# Verify on Basescan
npx hardhat verify --network base <CONTRACT_ADDRESS>
```

### Phase 2: Backend Deployment (Railway)

#### 2.1 Prepare Backend

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create new project
railway init
```

#### 2.2 Configure Environment Variables

In Railway dashboard, set these environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Base Network
BASE_RPC_URL=https://mainnet.base.org
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org

# Contract Addresses
UNISWAP_V3_POSITION_MANAGER=0x03a520b32C04BF3bEEf7BFdF5497F0D5c9b18b5b
UNISWAP_V3_ROUTER=0x2626664c2603336E57B271c5C0b26F421741e481
LIQUIDITY_MANAGER_ADDRESS=<YOUR_DEPLOYED_CONTRACT_ADDRESS>

# Private Key (for monitoring service)
PRIVATE_KEY=<YOUR_PRIVATE_KEY>

# Backend Configuration
BACKEND_PORT=8000
ENVIRONMENT=production
```

#### 2.3 Deploy Backend

```bash
# Deploy to Railway
railway up

# Check deployment status
railway status

# View logs
railway logs
```

#### 2.4 Test Backend

```bash
# Get Railway URL
railway domain

# Test health endpoint
curl https://your-app.railway.app/api/health
```

### Phase 3: Frontend Deployment (Vercel)

#### 3.1 Prepare Frontend

```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login
```

#### 3.2 Configure Environment Variables

In Vercel dashboard, set these environment variables:

```bash
# WalletConnect
NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=<YOUR_PROJECT_ID>

# Backend API
NEXT_PUBLIC_API_BASE_URL=https://your-app.railway.app

# Contract Addresses
NEXT_PUBLIC_CONTRACT_ADDRESS_BASE=<YOUR_MAINNET_CONTRACT>
NEXT_PUBLIC_CONTRACT_ADDRESS_BASE_SEPOLIA=<YOUR_TESTNET_CONTRACT>

# Environment
NEXT_PUBLIC_ENVIRONMENT=production
```

#### 3.3 Deploy Frontend

```bash
# Deploy to Vercel
vercel --prod

# Check deployment
vercel ls
```

### Phase 4: Monitoring Service Setup

#### 4.1 Deploy Monitoring Service

```bash
# Create monitoring service in Railway
railway add

# Set environment variables for monitoring
railway variables set MONITORING_ENABLED=true
railway variables set CONTRACT_ADDRESS=<YOUR_CONTRACT_ADDRESS>
```

#### 4.2 Start Monitoring

```bash
# Deploy monitoring service
railway up --service monitoring
```

## 🔧 Configuration

### Production Environment Variables

#### Backend (.env.production)
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Base Network
BASE_RPC_URL=https://mainnet.base.org
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org

# Contract Addresses
UNISWAP_V3_POSITION_MANAGER=0x03a520b32C04BF3bEEf7BFdF5497F0D5c9b18b5b
UNISWAP_V3_ROUTER=0x2626664c2603336E57B271c5C0b26F421741e481
LIQUIDITY_MANAGER_ADDRESS=<YOUR_CONTRACT_ADDRESS>

# Private Key (for monitoring)
PRIVATE_KEY=<YOUR_PRIVATE_KEY>

# Backend Configuration
BACKEND_PORT=8000
ENVIRONMENT=production
LOG_LEVEL=INFO
```

#### Frontend (.env.production)
```bash
# WalletConnect
NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=<YOUR_PROJECT_ID>

# Backend API
NEXT_PUBLIC_API_BASE_URL=https://your-app.railway.app

# Contract Addresses
NEXT_PUBLIC_CONTRACT_ADDRESS_BASE=<YOUR_MAINNET_CONTRACT>
NEXT_PUBLIC_CONTRACT_ADDRESS_BASE_SEPOLIA=<YOUR_TESTNET_CONTRACT>

# Environment
NEXT_PUBLIC_ENVIRONMENT=production
```

## 🧪 Testing Production Deployment

### 1. Test Smart Contracts

```bash
# Test on Base Sepolia first
npx hardhat test --network baseSepolia

# Test on Base Mainnet
npx hardhat test --network base
```

### 2. Test Backend API

```bash
# Health check
curl https://your-app.railway.app/api/health

# Test pools endpoint
curl https://your-app.railway.app/api/pools

# Test whitelist
curl https://your-app.railway.app/api/whitelist/status/0x1234567890abcdef1234567890abcdef12345678
```

### 3. Test Frontend

```bash
# Visit your Vercel URL
# Test wallet connection
# Test pool selection
# Test strategy configuration
```

### 4. Test End-to-End

1. Connect wallet on frontend
2. Select a pool
3. Configure strategy
4. Deploy position
5. Verify position appears in monitoring

## 🔒 Security Checklist

### Smart Contracts
- [ ] Contracts verified on Basescan
- [ ] No hardcoded private keys
- [ ] Emergency functions tested
- [ ] Access controls verified

### Backend
- [ ] Environment variables secured
- [ ] Database credentials encrypted
- [ ] API rate limiting enabled
- [ ] CORS properly configured
- [ ] Private key stored securely

### Frontend
- [ ] No sensitive data in client code
- [ ] Environment variables prefixed with NEXT_PUBLIC_
- [ ] HTTPS enabled
- [ ] Content Security Policy configured

## 📊 Monitoring & Logging

### Backend Monitoring

```bash
# View Railway logs
railway logs

# Monitor specific service
railway logs --service monitoring

# Check metrics
railway metrics
```

### Frontend Monitoring

```bash
# View Vercel logs
vercel logs

# Check analytics
vercel analytics
```

### Smart Contract Monitoring

- Monitor contract events on Basescan
- Set up alerts for critical functions
- Track gas usage and costs

## 🚨 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check logs
railway logs

# Common fixes:
# - Check environment variables
# - Verify database connection
# - Check port configuration
```

#### Frontend Build Fails
```bash
# Check build logs
vercel logs

# Common fixes:
# - Check environment variables
# - Verify API URLs
# - Check for TypeScript errors
```

#### Smart Contract Deployment Fails
```bash
# Check gas prices
# Verify RPC URL
# Check private key balance
# Verify contract compilation
```

### Getting Help

1. Check logs first
2. Verify environment variables
3. Test on Base Sepolia first
4. Check Base network status
5. Contact support if needed

## 🔄 Updates & Maintenance

### Updating Smart Contracts

```bash
# Deploy new version
npx hardhat run scripts/deploy.ts --network base

# Update contract address in backend
railway variables set LIQUIDITY_MANAGER_ADDRESS=<NEW_ADDRESS>

# Update frontend
vercel env add NEXT_PUBLIC_CONTRACT_ADDRESS_BASE <NEW_ADDRESS>
```

### Updating Backend

```bash
# Deploy new version
railway up

# Check deployment
railway status
```

### Updating Frontend

```bash
# Deploy new version
vercel --prod

# Check deployment
vercel ls
```

## 📈 Scaling

### Database Scaling
- Upgrade to PostgreSQL Pro on Railway
- Set up read replicas
- Implement connection pooling

### Backend Scaling
- Enable auto-scaling on Railway
- Add load balancing
- Implement caching

### Frontend Scaling
- Enable Vercel Pro features
- Set up CDN
- Implement edge functions

---

**Deployment Complete!** 🎉

Your AMM Optimizer is now live on Base Network. Monitor the deployment and be ready to handle any issues that arise.






