# Tangerine.trading Deployment Guide

## 🚀 Deploying to tangerine.trading

### Prerequisites
- Domain: `tangerine.trading` (already configured with Namecheap)
- Vercel account
- GitHub repository

### Step 1: Frontend Deployment (Vercel)

1. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Sign in with GitHub
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Project:**
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`

3. **Environment Variables:**
   ```
   NEXT_PUBLIC_API_BASE_URL=https://tangerine-api.vercel.app
   NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=your-project-id
   NEXT_PUBLIC_CONTRACT_ADDRESS_BASE=0x0000000000000000000000000000000000000000
   NEXT_PUBLIC_CONTRACT_ADDRESS_BASE_SEPOLIA=0x0000000000000000000000000000000000000000
   ```

4. **Custom Domain:**
   - In Vercel dashboard, go to Project Settings → Domains
   - Add `tangerine.trading`
   - Add `www.tangerine.trading`
   - Update Namecheap DNS to point to Vercel

### Step 2: Backend API Deployment (Vercel)

1. **Create Separate Project:**
   - Create new Vercel project for backend
   - Root Directory: `backend`
   - Framework: Python

2. **Environment Variables:**
   ```
   PYTHONPATH=/var/task
   ```

3. **Custom Domain:**
   - Add `api.tangerine.trading` or use Vercel subdomain

### Step 3: DNS Configuration (Namecheap)

Update your DNS records in Namecheap:

```
Type: A Record
Host: @
Value: 76.76.19.61 (Vercel IP)

Type: CNAME Record  
Host: www
Value: cname.vercel-dns.com

Type: CNAME Record
Host: api
Value: tangerine-api.vercel.app
```

### Step 4: Alternative - Railway/Render Backend

If Vercel backend doesn't work well:

1. **Railway Deployment:**
   - Connect GitHub repository
   - Select `backend` folder
   - Set environment variables
   - Get Railway URL for API

2. **Render Deployment:**
   - Create new Web Service
   - Connect GitHub repository
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python api/main.py`

### Step 5: Update Frontend API URL

Once backend is deployed, update the frontend environment variable:
```
NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.com
```

### Step 6: Test Deployment

1. Visit `https://tangerine.trading`
2. Test all functionality:
   - Pool selection
   - Strategy configuration  
   - Position monitoring
3. Verify mobile responsiveness
4. Test wallet connection

### Current Status

✅ **Frontend:** Ready for deployment with futuristic design
✅ **Backend:** Has mock data fallback for offline functionality
✅ **Domain:** Configured with Namecheap
⏳ **Deployment:** Ready for Vercel deployment

### Features Available

- 🎨 Futuristic Gemini-inspired design
- 🔗 Wallet connection (RainbowKit)
- 📊 Pool selection with real Base network data
- ⚙️ Strategy configuration with analytics
- 📈 Position monitoring
- 📱 Mobile responsive design
- 🌙 Dark theme with glass morphism effects

The website is fully functional with mock data and will work even without the backend API running!


