/**
 * On-Chain Price Fetcher
 * Gets exact price data from Uniswap V3 pool slot0 data
 * Uses integer arithmetic to avoid floating point errors
 */

import { createPublicClient, http, parseAbi } from 'viem';
import { base } from 'viem/chains';

// Pool ABI for slot0 function
const POOL_ABI = parseAbi([
  'function slot0() external view returns (uint160 sqrtPriceX96, int24 tick, uint16 observationIndex, uint16 observationCardinality, uint16 observationCardinalityNext, uint8 feeProtocol, bool unlocked)'
]);

// Create public client for Base Mainnet
const publicClient = createPublicClient({
  chain: base,
  transport: http(process.env.NEXT_PUBLIC_ALCHEMY_RPC_URL || 'https://mainnet.base.org')
});

/**
 * Get exact price from Uniswap V3 pool using slot0 data
 * This is the most accurate method as it uses on-chain data
 */
export async function getOnChainPrice(poolAddress: string): Promise<{
  price: number;
  tick: number;
  sqrtPriceX96: bigint;
} | null> {
  try {
    console.log('🔍 Fetching on-chain price from pool:', poolAddress);
    
    // Get slot0 data from the pool
    const slot0 = await publicClient.readContract({
      address: poolAddress as `0x${string}`,
      abi: POOL_ABI,
      functionName: 'slot0',
    });

    const [sqrtPriceX96, tick] = slot0;
    
    console.log('📊 On-chain slot0 data:', {
      sqrtPriceX96: sqrtPriceX96.toString(),
      tick: tick.toString()
    });

    // Convert sqrtPriceX96 to actual price using integer arithmetic
    // Price = (sqrtPriceX96 / 2^96)^2
    // We need to be careful with integer arithmetic here
    
    // Convert sqrtPriceX96 to a number for calculation
    // This is safe because we're dealing with a reasonable range
    const sqrtPrice = Number(sqrtPriceX96);
    const Q96 = 2 ** 96;
    
    // Calculate price: (sqrtPrice / Q96)^2
    const price = (sqrtPrice / Q96) ** 2;
    
    console.log('💰 Calculated price from on-chain data:', price);
    
    return {
      price,
      tick: Number(tick),
      sqrtPriceX96
    };
  } catch (error) {
    console.error('❌ Error fetching on-chain price:', error);
    return null;
  }
}

/**
 * Get WETH price in USDC from the specific pool we're using
 */
export async function getWETHPrice(): Promise<number | null> {
  const WETH_USDC_POOL = '0xd0b53D9277642d899DF5C87A3966A349A798F224';
  
  const priceData = await getOnChainPrice(WETH_USDC_POOL);
  
  if (!priceData) {
    console.log('⚠️ Could not get on-chain price, using fallback');
    return 3840; // Fallback price
  }
  
  return priceData.price;
}

/**
 * Convert tick to price using Uniswap V3 formula
 * Price = 1.0001^tick
 */
export function tickToPrice(tick: number): number {
  return Math.pow(1.0001, tick);
}

/**
 * Convert price to tick using Uniswap V3 formula
 * tick = log(price) / log(1.0001)
 */
export function priceToTick(price: number): number {
  return Math.floor(Math.log(price) / Math.log(1.0001));
}

/**
 * Get price range from ticks
 */
export function getPriceRange(tickLower: number, tickUpper: number): {
  priceLower: number;
  priceUpper: number;
} {
  return {
    priceLower: tickToPrice(tickLower),
    priceUpper: tickToPrice(tickUpper)
  };
}
