#!/bin/bash

echo "🚀 Tangerine Trading Backend Deployment Helper"
echo "=============================================="
echo ""

echo "📋 Choose your deployment platform:"
echo "1) Railway (Recommended - Free tier available)"
echo "2) Render (Free tier available)"
echo "3) Heroku (Paid plans only)"
echo ""

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🚂 Deploying to Railway..."
        echo ""
        echo "📝 Manual steps:"
        echo "1. Go to https://railway.app"
        echo "2. Sign up/Login with GitHub"
        echo "3. Click 'New Project' → 'Deploy from GitHub repo'"
        echo "4. Select 'AMM-Optimizer' repository"
        echo "5. Railway will auto-detect Python and deploy"
        echo ""
        echo "🔧 Environment Variables to set in Railway:"
        echo "BASE_PRIVATE_KEY=0c48906942de66ecba5b59a5a074d1b223d8b051438e0f05c1c3b21d39eff6b4"
        echo "ALCHEMY_API_KEY=iIkAsMgibgkR4Rwsh_Tm0"
        echo "BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/iIkAsMgibgkR4Rwsh_Tm0"
        echo ""
        echo "🌐 After deployment, get your Railway URL and run:"
        echo "vercel env add NEXT_PUBLIC_BACKEND_URL production"
        echo "vercel --prod"
        ;;
    2)
        echo ""
        echo "🎨 Deploying to Render..."
        echo ""
        echo "📝 Manual steps:"
        echo "1. Go to https://render.com"
        echo "2. Connect GitHub account"
        echo "3. New → Web Service"
        echo "4. Select AMM-Optimizer repository"
        echo "5. Configure:"
        echo "   - Build Command: pip install -r backend/requirements.txt"
        echo "   - Start Command: python3 backend/start_backend.py"
        echo "   - Environment: Python 3"
        ;;
    3)
        echo ""
        echo "🟣 Deploying to Heroku..."
        echo ""
        echo "📝 Prerequisites:"
        echo "1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli"
        echo "2. Login: heroku login"
        echo ""
        echo "🚀 Commands to run:"
        echo "heroku create tangerine-trading-backend"
        echo "heroku config:set BASE_PRIVATE_KEY=0c48906942de66ecba5b59a5a074d1b223d8b051438e0f05c1c3b21d39eff6b4"
        echo "heroku config:set ALCHEMY_API_KEY=iIkAsMgibgkR4Rwsh_Tm0"
        echo "git subtree push --prefix backend heroku main"
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment guide complete!"
echo "📖 For detailed instructions, see: BACKEND_DEPLOYMENT.md"
echo ""
echo "🎯 After backend is deployed:"
echo "1. Update frontend with backend URL"
echo "2. Test complete end-to-end flow"
echo "3. Your app will be fully functional!"
