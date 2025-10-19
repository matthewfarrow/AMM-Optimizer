#!/bin/bash

# Quick setup script for Base Sepolia testnet

echo "🚀 Setting up Base Sepolia Testnet..."
echo ""

# Check if .env.testnet exists
if [ ! -f .env.testnet ]; then
    echo "❌ .env.testnet not found!"
    exit 1
fi

# Backup current .env if it exists
if [ -f .env ]; then
    echo "📦 Backing up current .env to .env.backup"
    cp .env .env.backup
fi

# Copy testnet config
echo "📝 Copying testnet configuration..."
cp .env.testnet .env

echo ""
echo "✅ Testnet configuration activated!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1️⃣  Add your testnet private key to .env:"
echo "   BASE_PRIVATE_KEY=your_testnet_private_key_here"
echo ""
echo "2️⃣  Get test ETH from faucet:"
echo "   🔗 https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet"
echo ""
echo "3️⃣  Check your setup:"
echo "   python scripts/check_testnet.py"
echo ""
echo "4️⃣  Find available pools:"
echo "   python scripts/find_pools.py"
echo ""
echo "5️⃣  Run the optimizer:"
echo "   python scripts/run_optimizer.py --pool WETH-USDC --capital 100 --once"
echo ""
echo "⚠️  IMPORTANT: Use a NEW wallet for testnet - NEVER use your mainnet private key!"
echo ""
