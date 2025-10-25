/**
 * Alchemy Price API Integration
 * Fetches real-time token prices from Alchemy's price API
 */

const ALCHEMY_API_KEY = process.env.NEXT_PUBLIC_ALCHEMY_API_KEY;
const BASE_CHAIN_ID = 8453; // Base Mainnet

export interface TokenPrice {
  address: string;
  symbol: string;
  price: number;
  priceChange24h: number;
  marketCap?: number;
  volume24h?: number;
}

export interface PriceResponse {
  data: {
    [address: string]: {
      price: number;
      priceChange24h: number;
      marketCap?: number;
      volume24h?: number;
    };
  };
}

/**
 * Get token price from backend API (preferred) or fallback to external APIs
 */
export async function getTokenPrice(tokenAddress: string): Promise<TokenPrice | null> {
  // First try backend API (most reliable)
  try {
    console.log('🔍 Fetching price from backend API for:', tokenAddress);
    
    // Use the WETH-USDC pool address for price data
    const poolAddress = '0xd0b53D9277642d899DF5C87A3966A349A798F224';
    const response = await fetch(
      `http://localhost:8000/api/analytics/${poolAddress}/price-data?timeframe=1d`
    );

    if (response.ok) {
      const data = await response.json();
      console.log('💰 Backend price data received:', data);
      
      if (data.data && data.data.length > 0) {
        // Get the latest price
        const latestPrice = data.data[data.data.length - 1];
        
        // For WETH/ETH on Base
        if (tokenAddress.toLowerCase() === '0x4200000000000000000000000000000000000006'.toLowerCase()) {
          return {
            address: tokenAddress,
            symbol: 'WETH',
            price: latestPrice.price,
            priceChange24h: 0, // TODO: Calculate 24h change
          };
        }
        
        // For USDC on Base
        if (tokenAddress.toLowerCase() === '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'.toLowerCase()) {
          return {
            address: tokenAddress,
            symbol: 'USDC',
            price: 1.0,
            priceChange24h: 0,
          };
        }
      }
    }
  } catch (error) {
    console.error('Error fetching price from backend:', error);
  }

  // Fallback to Alchemy API if backend fails
  if (ALCHEMY_API_KEY) {
    try {
      const response = await fetch(
        `https://api.g.alchemy.com/prices/v1/${BASE_CHAIN_ID}/tokens/by-address`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${ALCHEMY_API_KEY}`,
          },
          body: JSON.stringify({
            addresses: [tokenAddress.toLowerCase()],
          }),
        }
      );

      if (response.ok) {
        const data: PriceResponse = await response.json();
        const tokenData = data.data[tokenAddress.toLowerCase()];

        if (tokenData) {
          return {
            address: tokenAddress,
            symbol: getTokenSymbol(tokenAddress),
            price: tokenData.price,
            priceChange24h: tokenData.priceChange24h,
            marketCap: tokenData.marketCap,
            volume24h: tokenData.volume24h,
          };
        }
      }
    } catch (error) {
      console.warn('Alchemy API failed:', error);
    }
  }

  // Fallback to Uniswap V3 Subgraph API (free, no key required)
  try {
    console.log('🔍 Fetching price from Uniswap V3 for:', tokenAddress);
    
    // For WETH/ETH on Base
    if (tokenAddress.toLowerCase() === '0x4200000000000000000000000000000000000006'.toLowerCase()) {
      const price = await getWETHPriceFromPool();
      console.log('💰 WETH price from Uniswap V3 pool:', price);
      
      if (price) {
        return {
          address: tokenAddress,
          symbol: 'WETH',
          price: price,
          priceChange24h: 0, // TODO: Add 24h change calculation
        };
      }
    }
    
    // For USDC on Base
    if (tokenAddress.toLowerCase() === '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'.toLowerCase()) {
      console.log('💰 USDC price: 1.0');
      return {
        address: tokenAddress,
        symbol: 'USDC',
        price: 1.0,
        priceChange24h: 0,
      };
    }

    console.log('❌ Unknown token address for Uniswap V3:', tokenAddress);
    return null;
  } catch (error) {
    console.error('Error fetching token price from Uniswap V3:', error);
  }

  // Final fallback to hardcoded prices
  console.log('🔄 Using hardcoded fallback prices for:', tokenAddress);
  
  // For WETH/ETH on Base
  if (tokenAddress.toLowerCase() === '0x4200000000000000000000000000000000000006'.toLowerCase()) {
    return {
      address: tokenAddress,
      symbol: 'WETH',
      price: 3800, // Current ETH price fallback
      priceChange24h: 0,
    };
  }
  
  // For USDC on Base
  if (tokenAddress.toLowerCase() === '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'.toLowerCase()) {
    return {
      address: tokenAddress,
      symbol: 'USDC',
      price: 1.0,
      priceChange24h: 0,
    };
  }

  console.log('❌ Unknown token address:', tokenAddress);
  return null;
}

/**
 * Get multiple token prices
 */
export async function getTokenPrices(tokenAddresses: string[]): Promise<TokenPrice[]> {
  if (!ALCHEMY_API_KEY) {
    console.warn('Alchemy API key not found');
    return [];
  }

  try {
    const response = await fetch(
      `https://api.g.alchemy.com/prices/v1/${BASE_CHAIN_ID}/tokens/by-address`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${ALCHEMY_API_KEY}`,
        },
        body: JSON.stringify({
          addresses: tokenAddresses.map(addr => addr.toLowerCase()),
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`Alchemy API error: ${response.status} ${response.statusText}`);
    }

    const data: PriceResponse = await response.json();
    
    return tokenAddresses
      .map(address => {
        const tokenData = data.data[address.toLowerCase()];
        if (!tokenData) return null;
        
        return {
          address,
          symbol: getTokenSymbol(address),
          price: tokenData.price,
          priceChange24h: tokenData.priceChange24h,
          marketCap: tokenData.marketCap,
          volume24h: tokenData.volume24h,
        };
      })
      .filter((price): price is TokenPrice => price !== null);
  } catch (error) {
    console.error('Error fetching token prices:', error);
    return [];
  }
}

/**
 * Get WETH/USDC price ratio
 */
export async function getWETHUSDCRatio(): Promise<number | null> {
  const WETH_ADDRESS = '0x4200000000000000000000000000000000000006'; // WETH on Base
  const USDC_ADDRESS = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'; // USDC on Base

  try {
    const prices = await getTokenPrices([WETH_ADDRESS, USDC_ADDRESS]);
    
    if (prices.length !== 2) {
      return null;
    }

    const wethPrice = prices.find(p => p.address.toLowerCase() === WETH_ADDRESS.toLowerCase());
    const usdcPrice = prices.find(p => p.address.toLowerCase() === USDC_ADDRESS.toLowerCase());

    if (!wethPrice || !usdcPrice) {
      return null;
    }

    // Return WETH price in USDC
    return wethPrice.price / usdcPrice.price;
  } catch (error) {
    console.error('Error calculating WETH/USDC ratio:', error);
    return null;
  }
}

/**
 * Get token symbol from address (Base Mainnet tokens)
 */
function getTokenSymbol(address: string): string {
  const tokenSymbols: { [key: string]: string } = {
    '0x4200000000000000000000000000000000000006': 'WETH',
    '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913': 'USDC',
    '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb': 'DAI',
    '0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22': 'cbETH',
  };

  return tokenSymbols[address.toLowerCase()] || 'UNKNOWN';
}

/**
 * Format price for display
 */
export function formatPrice(price: number, decimals: number = 2): string {
  if (price < 0.01) {
    return price.toExponential(4);
  }
  return price.toFixed(decimals);
}

/**
 * Format price change for display
 */
export function formatPriceChange(change: number): string {
  const sign = change >= 0 ? '+' : '';
  return `${sign}${change.toFixed(2)}%`;
}

/**
 * Get WETH price from Uniswap V3 WETH-USDC pool on Base
 */
async function getWETHPriceFromPool(): Promise<number | null> {
  try {
    // Uniswap V3 Subgraph API for Base Mainnet
    const UNISWAP_SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/ianlapham/uniswap-v3-base';
    
    // WETH-USDC 0.05% pool on Base Mainnet (the one we're actually using)
    const WETH_USDC_POOL_ADDRESS = '0xd0b53D9277642d899DF5C87A3966A349A798F224';

    const query = `
      {
        pool(id: "${WETH_USDC_POOL_ADDRESS}") {
          token0Price
          token1Price
          token0 {
            symbol
            id
          }
          token1 {
            symbol
            id
          }
        }
      }
    `;

    const response = await fetch(UNISWAP_SUBGRAPH_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error(`GraphQL request failed: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.errors) {
      console.error('GraphQL errors:', data.errors);
      return null;
    }

    const pool = data.data?.pool;
    if (!pool) {
      console.error('No pool data found');
      return null;
    }

    // Check which token is WETH and return the appropriate price
    const wethAddress = '0x4200000000000000000000000000000000000006';
    const usdcAddress = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';
    
    if (pool.token0.id.toLowerCase() === wethAddress.toLowerCase()) {
      // WETH is token0, so token0Price is WETH price in USDC
      return parseFloat(pool.token0Price);
    } else if (pool.token1.id.toLowerCase() === wethAddress.toLowerCase()) {
      // WETH is token1, so token1Price is WETH price in USDC
      return parseFloat(pool.token1Price);
    }

    console.error('WETH not found in pool tokens');
    return null;
  } catch (error) {
    console.error('Error fetching WETH price from pool:', error);
    return null;
  }
}
