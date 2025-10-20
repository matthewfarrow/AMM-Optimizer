# 🌐 Base Sepolia Testnet Configuration

## Quick Add to MetaMask

### Option 1: Use Chainlist (EASIEST)
1. Go to https://chainlist.org/
2. Search for "Base Sepolia"
3. Click "Add to MetaMask"
4. Done! ✅

### Option 2: Manual Configuration

**Network Name:** `Base Sepolia`

**RPC URL:** Choose one:
- `https://sepolia.base.org` (Official Base RPC - RECOMMENDED)
- `https://base-sepolia.blockpi.network/v1/rpc/public`
- `https://base-sepolia-rpc.publicnode.com`

**Chain ID:** `84532`

**Currency Symbol:** `ETH`

**Block Explorer:** `https://sepolia.basescan.org`

## 📝 Step-by-Step Manual Setup

1. Open MetaMask
2. Click network dropdown (top left)
3. Click "Add Network" or "Add Network Manually"
4. Enter the details above:
   ```
   Network Name: Base Sepolia
   RPC URL: https://sepolia.base.org
   Chain ID: 84532
   Currency Symbol: ETH
   Block Explorer: https://sepolia.basescan.org
   ```
5. Click "Save"
6. Switch to Base Sepolia network

## 🔗 Useful Links

### Testnet Faucets (Get Free ETH)
- **Alchemy Base Sepolia Faucet:** https://www.alchemy.com/faucets/base-sepolia
- **QuickNode Faucet:** https://faucet.quicknode.com/base/sepolia
- **Base Discord:** https://discord.gg/buildonbase (Ask in #faucet channel)

### Explorers
- **Base Sepolia Explorer:** https://sepolia.basescan.org
- **Your Wallet:** https://sepolia.basescan.org/address/0x8a679aCf39c06682072C4a2A833eb437A0CC0bdb

### Uniswap Interface
- **Uniswap on Base Sepolia:** https://app.uniswap.org/
  - Make sure to switch to Base Sepolia network first!
  - Then you can swap WETH → USDC directly in the UI

## ⚙️ Verify Connection

After adding the network, verify in your terminal:
```bash
python3 scripts/check_testnet.py
```

Should show:
- ✅ Connected to Base Sepolia (Chain ID: 84532)
- ✅ Your wallet address
- ✅ ETH balance

## 🎯 Next Steps After Adding Network

1. **Get Test ETH** (if you need more):
   - Visit https://www.alchemy.com/faucets/base-sepolia
   - Enter your wallet: `0x8a679aCf39c06682072C4a2A833eb437A0CC0bdb`
   - Claim free testnet ETH

2. **Swap WETH → USDC on Uniswap**:
   - Go to https://app.uniswap.org/
   - Connect MetaMask (should be on Base Sepolia)
   - Select WETH → USDC
   - Swap 0.002 WETH for USDC
   - This bypasses the liquidity issue we're having with direct swaps

3. **Test LP Position Creation**:
   ```bash
   python3 scripts/test_create_position.py
   ```

## 🐛 Troubleshooting

### "Network Already Exists"
- The network is already added! Just select it from the dropdown

### "Cannot Add Network"
- Try using a different RPC URL from the list above
- Clear MetaMask cache (Settings → Advanced → Clear Activity Tab Data)

### "Wrong Network in Scripts"
- Check your `.env` file has: `BASE_CHAIN_ID=84532`
- Restart terminal after changing `.env`

### "Can't Connect to Uniswap"
- Make sure MetaMask is on Base Sepolia network
- Refresh the Uniswap page
- Try disconnecting and reconnecting wallet

## 💡 Pro Tips

**For Uniswap Interface Swap:**
- Use the interface instead of our script for this initial swap
- It handles all the routing/liquidity automatically
- You can see the exact USDC amount before confirming
- Much faster than debugging testnet liquidity issues

**Current Status:**
- You have: 0.0825 ETH + 0.0225 WETH on Base Sepolia
- You need: Some USDC to create LP position
- Best solution: Use Uniswap UI to swap WETH → USDC (takes 2 min)

---

**TL;DR:** 
1. Go to https://chainlist.org/ → search "Base Sepolia" → Add to MetaMask
2. Or manually add with Chain ID `84532` and RPC `https://sepolia.base.org`
3. Go to https://app.uniswap.org/ → swap WETH → USDC
4. Then run `python3 scripts/test_create_position.py` 🚀
