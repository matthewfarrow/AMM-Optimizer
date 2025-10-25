# 🚀 Backend Deployment Guide

## Option 1: Railway (Recommended)

### Steps:
1. **Go to [Railway.app](https://railway.app)**
2. **Sign up/Login with GitHub**
3. **Click "New Project" → "Deploy from GitHub repo"**
4. **Select your AMM-Optimizer repository**
5. **Railway will auto-detect Python and deploy**

### Environment Variables to Set:
```
BASE_PRIVATE_KEY=0c48906942de66ecba5b59a5a074d1b223d8b051438e0f05c1c3b21d39eff6b4
ALCHEMY_API_KEY=iIkAsMgibgkR4Rwsh_Tm0
BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/iIkAsMgibgkR4Rwsh_Tm0
```

### After Deployment:
1. **Get your Railway URL** (e.g., `https://your-app.railway.app`)
2. **Update frontend environment variable:**
   ```bash
   vercel env add NEXT_PUBLIC_BACKEND_URL production
   # Enter: https://your-app.railway.app
   ```
3. **Redeploy frontend:**
   ```bash
   vercel --prod
   ```

## Option 2: Render

### Steps:
1. **Go to [Render.com](https://render.com)**
2. **Connect GitHub account**
3. **New → Web Service**
4. **Select AMM-Optimizer repository**
5. **Configure:**
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `python3 backend/start_backend.py`
   - **Environment:** Python 3

## Option 3: Heroku

### Steps:
1. **Install Heroku CLI**
2. **Create Heroku app:**
   ```bash
   heroku create tangerine-trading-backend
   ```
3. **Set environment variables:**
   ```bash
   heroku config:set BASE_PRIVATE_KEY=0c48906942de66ecba5b59a5a074d1b223d8b051438e0f05c1c3b21d39eff6b4
   heroku config:set ALCHEMY_API_KEY=iIkAsMgibgkR4Rwsh_Tm0
   ```
4. **Deploy:**
   ```bash
   git subtree push --prefix backend heroku main
   ```

## Testing Backend

Once deployed, test these endpoints:
- `GET /health` - Health check
- `GET /api/pools` - Get available pools
- `GET /api/analytics/{pool_address}/price-data` - Get price data

## Next Steps

After backend is deployed:
1. ✅ Update frontend with backend URL
2. ✅ Test complete end-to-end flow
3. ✅ Optimize performance
4. ✅ Monitor and maintain
