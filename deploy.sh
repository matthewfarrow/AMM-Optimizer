#!/bin/bash

# Tangerine.trading Deployment Script
echo "🚀 Deploying Tangerine.trading..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel@latest
fi

# Deploy frontend
echo "🎨 Deploying frontend..."
cd frontend
vercel --prod --yes
cd ..

# Deploy backend (separate project)
echo "🔧 Deploying backend API..."
cd backend
vercel --prod --yes
cd ..

echo "✅ Deployment complete!"
echo "🌐 Frontend: https://tangerine.trading"
echo "🔗 Backend: https://tangerine-api.vercel.app"


