#!/bin/bash

# Set up Vercel environment variables
echo "Setting up Vercel environment variables..."

# Alchemy API Key
echo "iIkAsMgibgkR4Rwsh_Tm0" | vercel env add NEXT_PUBLIC_ALCHEMY_API_KEY production

# WalletConnect Project ID  
echo "278e88c0a5fd5156d817ce944b480586" | vercel env add NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID production

# Alchemy RPC URL
echo "https://base-mainnet.g.alchemy.com/v2/iIkAsMgibgkR4Rwsh_Tm0" | vercel env add NEXT_PUBLIC_ALCHEMY_RPC_URL production

echo "Environment variables set up complete!"
echo "Now redeploy to apply the changes:"
echo "vercel --prod"
