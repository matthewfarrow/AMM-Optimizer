# 🚀 Tangerine.trading Deployment Guide

## Overview
This guide will help you deploy your AMM-Optimizer to your `tangerine.trading` domain.

## Prerequisites
- ✅ Domain: `tangerine.trading` (registered with Namecheap)
- ✅ GitHub repository: `https://github.com/matthewfarrow/AMM-Optimizer.git`
- ✅ Working application locally

## Deployment Options

### Option 1: Vercel (Recommended)
**Pros:** Free, easy setup, perfect for Next.js, automatic deployments
**Cons:** Backend needs separate hosting

#### Steps:
1. **Deploy Frontend to Vercel:**
   ```bash
   cd /Users/mattfarrow/GitRepos/AMM-Optimizer
   vercel login
   vercel --prod
   ```

2. **Connect Custom Domain:**
   - Go to Vercel Dashboard
   - Add `tangerine.trading` as custom domain
   - Update Namecheap DNS settings

3. **Deploy Backend Separately:**
   - Use Railway, Render, or Heroku for Python backend
   - Update frontend API URLs

### Option 2: Netlify
**Pros:** Free, good for static sites, easy domain setup
**Cons:** Backend needs separate hosting

### Option 3: Namecheap Hosting
**Pros:** Everything in one place
**Cons:** More complex setup, may need VPS

## Recommended: Vercel + Railway Setup

### Frontend (Vercel)
1. Deploy to Vercel
2. Connect `tangerine.trading` domain
3. Set environment variables

### Backend (Railway)
1. Deploy Python backend to Railway
2. Get backend URL
3. Update frontend to use backend URL

## Environment Variables Needed

### Frontend (Vercel)
```
NEXT_PUBLIC_ALCHEMY_API_KEY=your_alchemy_key
NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=your_project_id
NEXT_PUBLIC_ALCHEMY_RPC_URL=your_rpc_url
NEXT_PUBLIC_BACKEND_URL=https://your-backend.railway.app
```

### Backend (Railway)
```
BASE_PRIVATE_KEY=your_private_key
ALCHEMY_API_KEY=your_alchemy_key
```

## DNS Configuration (Namecheap)

After deploying to Vercel, you'll need to update your DNS:

1. **Go to Namecheap DNS settings**
2. **Add these records:**
   ```
   Type: A
   Host: @
   Value: 76.76.19.61 (Vercel IP)
   
   Type: CNAME
   Host: www
   Value: cname.vercel-dns.com
   ```

## Testing Checklist

- [ ] Frontend loads at `tangerine.trading`
- [ ] Wallet connection works
- [ ] Pool selection works
- [ ] Position creation works
- [ ] Monitor tab shows positions
- [ ] All API calls work

## Support

If you need help with any step, I can guide you through it!