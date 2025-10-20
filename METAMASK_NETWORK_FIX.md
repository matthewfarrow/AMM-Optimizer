# 🔧 MetaMask Base Sepolia - Manual Fix

## The Issue
MetaMask sometimes blocks adding networks automatically. Here's how to fix it:

## ✅ Solution 1: Add Network Manually (MOST RELIABLE)

### Step-by-Step:
1. **Open MetaMask**
2. Click the **network dropdown** (shows current network at top)
3. Scroll down and click **"Add network"** or **"Add a network manually"**
4. Click **"Add a network manually"** (bottom of the list)
5. Fill in these EXACT details:

```
Network name: Base Sepolia
New RPC URL: https://sepolia.base.org
Chain ID: 84532
Currency symbol: ETH
Block explorer URL: https://sepolia.basescan.org
```

6. Click **"Save"**
7. MetaMask will switch to Base Sepolia automatically

## ✅ Solution 2: Try Different RPC URLs

If the first RPC doesn't work, try these alternatives:

### Option A: BlockPI
```
RPC URL: https://base-sepolia.blockpi.network/v1/rpc/public
```

### Option B: PublicNode
```
RPC URL: https://base-sepolia-rpc.publicnode.com
```

### Option C: Gateway.fm
```
RPC URL: https://base-sepolia.gateway.tenderly.co
```

Just change the "New RPC URL" field and try again!

## ✅ Solution 3: Clear MetaMask Cache

If manual add still fails:

1. **Settings** (click the 3 dots or account icon)
2. **Advanced**
3. **Clear activity tab data** (or "Reset account")
4. Confirm
5. Try adding the network again

## ✅ Solution 4: Update MetaMask

If nothing works, you might need to update:

1. Click the 3 dots (account menu)
2. Click **"Settings"**
3. Click **"About"**
4. If there's an update, install it
5. Restart browser
6. Try adding network again

## 🎯 Quick Verification

Once you add the network, verify it works:

```bash
# In your terminal
python3 scripts/check_testnet.py
```

Should output:
```
✅ Connected to Base Sepolia
✅ Chain ID: 84532
✅ Your wallet: 0x8a679aCf39c06682072C4a2A833eb437A0CC0bdb
✅ ETH Balance: 0.0825 ETH
```

## 🚨 Common Errors & Fixes

### Error: "Chain ID already exists"
- **Fix:** The network is already added! Just select it from the network dropdown

### Error: "Invalid RPC URL"
- **Fix:** Try a different RPC URL from the list above

### Error: "Failed to fetch"
- **Fix:** Your internet connection might be blocking the RPC. Try:
  1. Disable VPN if you have one
  2. Try a different WiFi network
  3. Use mobile hotspot temporarily

### Error: "Unable to add network"
- **Fix:** 
  1. Update MetaMask to latest version
  2. Try in a different browser (Chrome, Firefox, Brave)
  3. Clear browser cache

## 📱 Alternative: Use Mobile MetaMask

If desktop MetaMask is being stubborn:

1. Open MetaMask on your **mobile phone**
2. Add Base Sepolia network there (usually works better on mobile)
3. Use WalletConnect to connect mobile to Uniswap on desktop

## 🦄 Once Network is Added: Get USDC

### Step 1: Go to Uniswap
Visit: https://app.uniswap.org/

### Step 2: Connect Wallet
- Click "Connect Wallet"
- Select MetaMask
- Make sure you're on **Base Sepolia** network (check top right)

### Step 3: Swap
- From: WETH
- To: USDC
- Amount: 0.002 WETH
- Click "Swap"
- Confirm in MetaMask

You'll get about $8-10 worth of USDC (at current ETH prices)!

## 🎯 Then Test LP Creation

```bash
python3 scripts/test_create_position.py
```

This will create your first liquidity position! 🚀

---

## 💡 Pro Tip: Import Your Wallet to Fresh MetaMask

If all else fails:

1. Export your private key from current MetaMask (Settings → Security & Privacy → Reveal Secret Recovery Phrase)
2. Install MetaMask in a different browser (if you're in Chrome, try Firefox)
3. Import your wallet
4. Add Base Sepolia network in the fresh MetaMask

This often fixes persistent issues!

---

**Need Help?** Try the manual add first - it works 99% of the time! Just make sure Chain ID is exactly `84532` (no spaces, no typos).
