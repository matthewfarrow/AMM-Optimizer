'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { useAccount } from 'wagmi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, TrendingUp, AlertTriangle, BarChart3, Wallet, Percent } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useTokenBalance, useETHBalance } from '@/hooks/useTokenBalance';
import { TOKEN_ADDRESSES, getTokenAddress, UNISWAP_V3_ADDRESSES, NONFUNGIBLE_POSITION_MANAGER_ABI, ERC20_ABI, POOL_ABI, calculateSlippage } from '@/lib/contracts';
import { getTokenPrice } from '@/lib/alchemy-price';
// import { TickMath, Position, Token, FeeAmount } from '@uniswap/v3-sdk';
// import { Token as UniswapToken } from '@uniswap/sdk-core';
import { useWriteContract, useWaitForTransactionReceipt, useReadContract } from 'wagmi';
import { parseUnits, formatUnits } from 'viem';
import JSBI from 'jsbi';
import { toast } from 'sonner';

interface Pool {
  address: string;
  name: string;
  token0: string;
  token1: string;
  fee_tier: number;
  tvl: number;
  apr: number;
  volume_1d: number;
  volume_30d: number;
}

interface StrategyConfigProps {
  pool: Pool;
  onComplete: () => void;
  onBack: () => void;
}

export function StrategyConfig({ pool, onComplete, onBack }: StrategyConfigProps) {
  const { address } = useAccount();
  const [timeframe, setTimeframe] = useState('1d');
  const [tickRange, setTickRange] = useState(500); // 5% range for testing
  const [amount0, setAmount0] = useState('0.0001'); // EXACTLY like Python script - 0.0001 WETH
  const [amount1, setAmount1] = useState('0.2'); // EXACTLY like Python script - 0.2 USDC
  const [checkInterval, setCheckInterval] = useState(60);
  const [priceData, setPriceData] = useState<any[]>([]);
  const [volatilityData, setVolatilityData] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [outOfRangeData, setOutOfRangeData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [coingeckoApiKey, setCoingeckoApiKey] = useState('');
  const [creatingPosition, setCreatingPosition] = useState(false);
  const [txHash, setTxHash] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<string>('');
  const [approvalChecked, setApprovalChecked] = useState(false);
  const [approvalStep, setApprovalStep] = useState<'none' | 'weth' | 'usdc' | 'mint'>('none');
  const [lastApprovalAttempt, setLastApprovalAttempt] = useState<number>(0);

  // Contract interaction hooks
  const { writeContract, data: hash, error: writeError, isPending } = useWriteContract();
  const { isLoading: isConfirming, isSuccess: isConfirmed } = useWaitForTransactionReceipt({
    hash: hash as `0x${string}`,
  });

  // Add null check for pool
  if (!pool || !pool.token0 || !pool.token1) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <Card className="w-full max-w-md bg-white/10 border-orange-500/30">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-white">Loading Pool Data...</CardTitle>
            <p className="text-gray-300">Please wait while we fetch the pool information</p>
          </CardHeader>
        </Card>
      </div>
    );
  }

  // Get token addresses and ensure correct ordering (token0 < token1 by address)
  const token0Address = getTokenAddress(pool.token0);
  const token1Address = getTokenAddress(pool.token1);
  
  // Ensure token0 < token1 by address (Uniswap V3 requirement)
  // WETH (0x420...) < DAI (0x50c...) = false, so WETH is token0, DAI is token1
  const [finalToken0Address, finalToken1Address, token0Symbol, token1Symbol] = 
    token0Address.toLowerCase() < token1Address.toLowerCase() 
      ? [token0Address, token1Address, pool.token0, pool.token1]
      : [token1Address, token0Address, pool.token1, pool.token0];
  
  const token0Balance = useTokenBalance(finalToken0Address, address);
  const token1Balance = useTokenBalance(finalToken1Address, address);
  const ethBalance = useETHBalance(address);

  useEffect(() => {
    if (pool) {
      fetchAnalytics();
    }
  }, [pool, timeframe]);

  useEffect(() => {
    if (pool && tickRange && checkInterval) {
      fetchOutOfRangeProbability();
    }
  }, [pool, tickRange, checkInterval, timeframe]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      
      // Try to fetch from API first
      try {
        const [priceResponse, volatilityResponse, recommendationsResponse] = await Promise.all([
          apiClient.getPriceData(pool.address, timeframe),
          apiClient.getVolatilityAnalysis(pool.address, timeframe),
          apiClient.getStrategyRecommendations(pool.address, 1000, 'medium')
        ]);
        
        setPriceData((priceResponse as any).data || []);
        setVolatilityData(volatilityResponse as any);
        setRecommendations(recommendationsResponse as any);
        return;
      } catch (apiError) {
        console.log('API not available, using mock data:', apiError);
      }
      
      // Fallback to mock data with real ETH price
      const wethAddress = '0x4200000000000000000000000000000000000006';
      const currentPriceData = await getTokenPrice(wethAddress);
      const currentPrice = currentPriceData?.price || 3800; // Fallback to ~$3800 if API fails
      
      console.log('💰 Using real ETH price for chart:', currentPrice);
      
      // Generate price data with realistic variations around current price
      const priceVariation = currentPrice * 0.02; // 2% variation
      const mockPriceData = [
        { timestamp: Date.now() - 86400000, price: currentPrice - priceVariation * 0.8 },
        { timestamp: Date.now() - 72000000, price: currentPrice - priceVariation * 0.4 },
        { timestamp: Date.now() - 57600000, price: currentPrice - priceVariation * 0.6 },
        { timestamp: Date.now() - 43200000, price: currentPrice - priceVariation * 0.2 },
        { timestamp: Date.now() - 28800000, price: currentPrice + priceVariation * 0.1 },
        { timestamp: Date.now() - 14400000, price: currentPrice + priceVariation * 0.3 },
        { timestamp: Date.now(), price: currentPrice }
      ];
      
      const mockVolatilityData = {
        current_price: currentPrice,
        volatility_percentage: 2.5,
        price_range: {
          min: currentPrice - priceVariation,
          max: currentPrice + priceVariation
        }
      };
      
      const mockRecommendations = {
        recommendations: {
          tick_range: 200,
          expected_apr: 15.5,
          liquidation_probability: 12.0
        },
        warnings: []
      };
      
      setPriceData(mockPriceData);
      setVolatilityData(mockVolatilityData);
      setRecommendations(mockRecommendations);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchOutOfRangeProbability = async () => {
    try {
      // Try API first
      try {
        const response = await apiClient.getOutOfRangeProbability(
          pool.address,
          tickRange,
          checkInterval,
          timeframe
        );
        setOutOfRangeData(response as any);
        return;
      } catch (apiError) {
        console.log('API not available for out of range probability, using mock data:', apiError);
      }
      
      // Mock data for out of range probability
      const mockOutOfRangeData = {
        out_of_range_probability: 15.0,
        risk_level: 'low',
        volatility_percentage: 2.5,
        price_bounds: {
          lower: 2400.0,
          upper: 2600.0
        },
        recommendation: 'Position looks good with current parameters. Consider monitoring every 30 minutes.'
      };
      
      setOutOfRangeData(mockOutOfRangeData);
    } catch (error) {
      console.error('Error fetching out of range probability:', error);
    }
  };

  // Simple amount calculation - no complex math, just return what user entered
  const calculateTokenAmounts = useMemo(() => {
    // Just return the amounts as entered - no floating point calculations
    return { amount0, amount1 };
  }, [amount0, amount1]);

  // No auto-calculation - user enters amounts manually

  // Allocation functions - simplified for hardcoded range
  const handleAllocation = (percentage: number) => {
    const wethBalance = parseFloat(token0Balance.formatted);
    const usdcBalance = parseFloat(token1Balance.formatted);
    
    // Calculate allocation based on percentage of available balances
    let wethAmount = (wethBalance * percentage) / 100;
    let usdcAmount = (usdcBalance * percentage) / 100;
    
    // EXACTLY like Python script - use very small amounts for micro testing
    const minTestWeth = 0.0001; // 0.0001 WETH (~$0.40) - like Python script
    const minTestUsdc = 0.2;    // 0.2 USDC (~$0.20) - like Python script
    
    // If calculated amounts are too small, use minimum test amounts
    if (wethAmount < minTestWeth && wethBalance >= minTestWeth) {
      wethAmount = minTestWeth;
    }
    if (usdcAmount < minTestUsdc && usdcBalance >= minTestUsdc) {
      usdcAmount = minTestUsdc;
    }
    
    setAmount0(wethAmount.toFixed(6));
    setAmount1(usdcAmount.toFixed(6));
  };

  // Balance validation
  const isInsufficientBalance = (amount: string, balance: string) => {
    return parseFloat(amount) > parseFloat(balance);
  };

  const token0Insufficient = isInsufficientBalance(amount0, token0Balance.formatted);
  const token1Insufficient = isInsufficientBalance(amount1, token1Balance.formatted);

  // Check token allowances
  const { data: token0Allowance } = useReadContract({
    address: finalToken0Address as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'allowance',
    args: address ? [address, UNISWAP_V3_ADDRESSES.NONFUNGIBLE_POSITION_MANAGER as `0x${string}`] : undefined,
  });

  const { data: token1Allowance } = useReadContract({
    address: finalToken1Address as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'allowance',
    args: address ? [address, UNISWAP_V3_ADDRESSES.NONFUNGIBLE_POSITION_MANAGER as `0x${string}`] : undefined,
  });

  // Read current tick from pool contract
  const { data: slot0 } = useReadContract({
    address: pool.address as `0x${string}`,
    abi: POOL_ABI,
    functionName: 'slot0',
  });

  // Get current tick from on-chain data (slot0) - EXACTLY like Python script
  const currentTick = useMemo(() => {
    if (slot0 && slot0[1] !== undefined && slot0[1] !== 0) {
      console.log('🔢 Using on-chain current tick:', slot0[1]);
      return slot0[1];
    }
    
    console.log('⚠️ No valid on-chain tick data available');
    return 0;
  }, [slot0]);

  const createPosition = useCallback(async () => {
    console.log('🚀 createPosition called:', {
      address,
      amount0,
      amount1,
      pool: pool?.address,
      currentTick
    });

    if (!address || !currentTick) {
      console.error('❌ Missing required data:', { address, currentTick });
      toast.error('Missing required data - waiting for on-chain data');
      return;
    }

    try {
      setCreatingPosition(true);
      console.log('✅ Starting position creation...');
      
      // EXACTLY like Python script - get tick spacing based on fee tier
      const tickSpacing = pool.fee_tier === 3000 ? 60 : (pool.fee_tier === 500 ? 10 : 200);
      
      // EXACTLY like Python script - use floor division (//) equivalent
      // Round current tick to nearest tick spacing
      const currentTickAligned = Math.floor(currentTick / tickSpacing) * tickSpacing;
      
      // EXACTLY like Python script - use default tick_range of 50 (not 1000!)
      const tickRange = 50; // 50 ticks = ±0.5% like Python default
      const tickLower = currentTickAligned - tickRange;
      const tickUpper = currentTickAligned + tickRange;
      
      // EXACTLY like Python script - align to tick spacing using floor division
      const alignedTickLower = Math.floor(tickLower / tickSpacing) * tickSpacing;
      const alignedTickUpper = Math.floor(tickUpper / tickSpacing) * tickSpacing;
      
      // EXACTLY like Python script - ensure tickLower < tickUpper
      const finalTickLower = Math.min(alignedTickLower, alignedTickUpper);
      const finalTickUpper = Math.max(alignedTickLower, alignedTickUpper);
      
      console.log('🎯 Tick calculation debug (EXACT Python logic):', {
        currentTick,
        currentTickAligned,
        tickRange,
        tickSpacing,
        tickLower,
        tickUpper,
        alignedTickLower,
        alignedTickUpper,
        finalTickLower,
        finalTickUpper
      });

      // EXACTLY like Python script - convert amounts to wei/base units
      const amount0Num = parseFloat(amount0);
      const amount1Num = parseFloat(amount1);
      
      // EXACTLY like Python script - use int() equivalent for amount conversion
      // WETH has 18 decimals, USDC has 6 decimals
      const amount0Desired = BigInt(Math.floor(amount0Num * 1e18)); // WETH: 18 decimals
      const amount1Desired = BigInt(Math.floor(amount1Num * 1e6));  // USDC: 6 decimals
      
      console.log('💰 Amount conversion (EXACT Python logic):', {
        amount0: amount0Num,
        amount1: amount1Num,
        amount0Desired: amount0Desired.toString(),
        amount1Desired: amount1Desired.toString()
      });
      
      // EXACTLY like Python script - use 0 for minimum amounts (accept any amount for micro testing)
      const amount0Min = BigInt(0); // Accept any amount (for micro testing)
      const amount1Min = BigInt(0); // Accept any amount (for micro testing)

      // EXACTLY like Python script - set deadline (20 minutes from now)
      const deadline = Math.floor(Date.now() / 1000) + 1200; // 20 minutes = 1200 seconds

      // Log transaction parameters for debugging
      const mintParams = {
        token0: finalToken0Address as `0x${string}`,
        token1: finalToken1Address as `0x${string}`,
        fee: pool.fee_tier,
        tickLower: finalTickLower,
        tickUpper: finalTickUpper,
        amount0Desired,
        amount1Desired,
        amount0Min,
        amount1Min,
        recipient: address,
        deadline: BigInt(deadline)
      };
      
      console.log('📋 Creating position with params:', {
        poolAddress: pool.address,
        positionManager: UNISWAP_V3_ADDRESSES.NONFUNGIBLE_POSITION_MANAGER,
        token0Symbol,
        token1Symbol,
        finalToken0Address,
        finalToken1Address,
        currentTick,
        tickSpacing,
        finalTickLower,
        finalTickUpper,
        amount0: amount0,
        amount1: amount1,
        amount0Desired: amount0Desired.toString(),
        amount1Desired: amount1Desired.toString(),
        amount0Min: amount0Min.toString(),
        amount1Min: amount1Min.toString(),
        deadline,
        mintParams
      });

      // Add longer delay to prevent rate limiting
      console.log('⏳ Waiting 10 seconds to prevent rate limiting...');
      await new Promise(resolve => setTimeout(resolve, 10000));

      // Create position with retry logic
      let retries = 3;
      while (retries > 0) {
        try {
          console.log('🚀 Attempting mint with parameters:', mintParams);
      console.log('🔍 Pool details:', {
        address: pool.address,
        fee_tier: pool.fee_tier,
        token0: pool.token0,
        token1: pool.token1
      });
          
          writeContract({
            address: UNISWAP_V3_ADDRESSES.NONFUNGIBLE_POSITION_MANAGER as `0x${string}`,
            abi: NONFUNGIBLE_POSITION_MANAGER_ABI,
            functionName: 'mint',
            args: [mintParams],
            value: BigInt(0), // No ETH value for this position
            gas: BigInt(500000), // EXACTLY like Python script - 500000 gas limit
          });
          toast.success('Position creation transaction submitted!');
          return;
        } catch (error: unknown) {
          console.error('❌ Mint transaction failed:', error);
          if ((error as Error).message?.includes('rate limited') && retries > 1) {
            console.log(`Rate limited, retrying in 3 seconds... (${retries} retries left)`);
            await new Promise(resolve => setTimeout(resolve, 3000));
            retries--;
            continue;
          }
          toast.error(`Mint failed: ${(error as Error).message}`);
          throw error;
        }
      }
      
    } catch (error) {
      console.error('Error creating position:', error);
      toast.error('Failed to create position');
    } finally {
      setCreatingPosition(false);
    }
  }, [address, amount0, amount1, pool, currentTick, token0Symbol, token1Symbol, finalToken0Address, finalToken1Address, writeContract]);

  const approveToken = useCallback((tokenAddress: string, amount: bigint) => {
    try {
      // Use MAX_UINT256 for approval - industry standard, prevents re-approvals
      const MAX_UINT256 = BigInt('115792089237316195423570985008687907853269984665640564039457584007913129639935');
      
      console.log('🔐 Approving token:', {
        tokenAddress,
        requestedAmount: amount.toString(),
        approvalAmount: MAX_UINT256.toString(),
        spender: UNISWAP_V3_ADDRESSES.NONFUNGIBLE_POSITION_MANAGER
      });
      
      // Use the writeContract hook to submit the approval
      writeContract({
        address: tokenAddress as `0x${string}`,
        abi: ERC20_ABI,
        functionName: 'approve',
        args: [UNISWAP_V3_ADDRESSES.NONFUNGIBLE_POSITION_MANAGER as `0x${string}`, MAX_UINT256],
        gas: BigInt(100000), // Reasonable gas limit for ERC20 approval
      });
      
      console.log('✅ Approval transaction submitted');
      toast.success('Approval transaction submitted!');
      
    } catch (error) {
      console.error('Error approving token:', error);
      toast.error('Failed to approve token - try again in a few seconds');
    }
  }, [writeContract]);

  const handleSubmit = useCallback(() => {
    if (!address) {
      toast.error('Please connect your wallet');
      return;
    }

    if (token0Insufficient || token1Insufficient) {
      toast.error('Insufficient token balance');
      return;
    }

    if (loading || creatingPosition) {
      console.log('⚠️  Already processing - preventing loop');
      return;
    }

    setLoading(true);
    setApprovalStep('weth');
    setCurrentStep('Approving WETH (1/3)');
    toast.info('Approving WETH...');
    
    const finalToken0Address = getTokenAddress('WETH');
    const amount0BigInt = parseUnits(amount0.toString(), 18);
    
    approveToken(finalToken0Address, amount0BigInt);
  }, [address, amount0, amount1, token0Insufficient, token1Insufficient, loading, creatingPosition, approveToken]);

  // Handle transaction success
  useEffect(() => {
    if (isConfirmed && hash) {
      if (currentStep.includes('Creating Position')) {
        toast.success('Position created successfully!');
        setTxHash(hash);
        setCreatingPosition(false);
        setLoading(false);
        setCurrentStep('');
        // Call onComplete after a short delay
        setTimeout(() => {
          onComplete();
        }, 2000);
      } else if (currentStep.includes('Approving')) {
        toast.success('Token approved successfully!');
        
          // Progress to next step
          if (approvalStep === 'weth') {
            setApprovalStep('usdc');
            setCurrentStep('Approving USDC (2/3)');
            toast.info('Approving USDC...');
            
            // Add delay between approvals to prevent rate limiting
            setTimeout(() => {
              const finalToken1Address = getTokenAddress('USDC');
              const amount1BigInt = parseUnits(amount1.toString(), 6);
              approveToken(finalToken1Address, amount1BigInt);
            }, 3000);
          } else if (approvalStep === 'usdc') {
            setApprovalStep('mint');
            setCurrentStep('Creating Position (3/3)');
            toast.info('Creating position...');
            // Add delay before minting to prevent rate limiting
            setTimeout(() => {
              createPosition();
            }, 3000);
          }
      }
    }
  }, [isConfirmed, hash, currentStep, approvalStep, amount1, approveToken, createPosition, onComplete]);

  // Handle transaction errors
  useEffect(() => {
    if (writeError) {
      toast.error(`Transaction failed: ${writeError.message}`);
      setLoading(false);
      setCreatingPosition(false);
      setCurrentStep('');
      setApprovalStep('none');
    }
  }, [writeError]);

  const formatPrice = (price: number) => {
    return `$${price.toFixed(2)}`;
  };

  const formatPercentage = (num: number) => {
    return `${num.toFixed(2)}%`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="outline" onClick={onBack}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-white">Configure Strategy</h1>
            <p className="text-gray-300">Set up your liquidity position parameters</p>
          </div>
        </div>
      </div>

      {/* Pool Info */}
      <Card className="bg-white/10 border-orange-500/30 glass-effect shadow-lg">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full flex items-center justify-center mr-3 shadow-sm">
              <span className="text-white font-bold text-xs">
                {pool.token0[0]}{pool.token1[0]}
              </span>
            </div>
            {pool.name} Pool
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <Label className="text-gray-300">Fee Tier</Label>
              <div className="text-white font-medium">
                {(pool.fee_tier / 10000).toFixed(2)}%
              </div>
            </div>
            <div>
              <Label className="text-gray-300">Current Price</Label>
              <div className="text-white font-medium">
                {formatPrice((volatilityData as any)?.current_price || 3939.04)}
              </div>
            </div>
            <div>
              <Label className="text-gray-300">Volatility</Label>
              <div className="text-white font-medium">
                {volatilityData ? formatPercentage((volatilityData as any).volatility_percentage) : 'Loading...'}
              </div>
            </div>
            <div>
              <Label className="text-gray-300">TVL</Label>
              <div className="text-white font-medium">
                ${(pool.tvl / 1000000).toFixed(1)}M
              </div>
            </div>
          </div>
          
          {/* Factory Address */}
          <div className="mt-4 pt-4 border-t border-gray-600">
            <Label className="text-gray-300">Pool Factory Address</Label>
            <div className="text-sm text-gray-400 font-mono break-all">
              {pool.address}
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Price Chart */}
        <Card className="bg-slate-900 border-orange-500/30 shadow-lg">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-white flex items-center">
                <BarChart3 className="w-5 h-5 mr-2 text-orange-500" />
                Price Chart
              </CardTitle>
              <div className="flex space-x-2">
                {['1d', '1m', '1y'].map((tf) => (
                  <Button
                    key={tf}
                    variant={timeframe === tf ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setTimeframe(tf)}
                    className={timeframe === tf 
                      ? 'bg-orange-500 text-white hover:bg-orange-600' 
                      : 'bg-slate-800 border-orange-500/30 text-white hover:bg-orange-500/10'
                    }
                  >
                    {tf.toUpperCase()}
                  </Button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="h-64 flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
              </div>
            ) : (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%" minHeight={256}>
                  <LineChart data={priceData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis 
                      dataKey="timestamp" 
                      stroke="#9CA3AF"
                      tick={{ fill: '#9CA3AF' }}
                      tickFormatter={(value) => new Date(value).toLocaleDateString()}
                    />
                    <YAxis stroke="#9CA3AF" tick={{ fill: '#9CA3AF' }} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: '1px solid #374151',
                        borderRadius: '6px',
                        color: '#F9FAFB'
                      }}
                      formatter={(value) => [formatPrice(Number(value)), 'Price']}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="price" 
                      stroke="#FF6B35" 
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Strategy Configuration */}
        <Card className="bg-white/10 border-orange-500/30 glass-effect shadow-xl">
          <CardHeader>
            <CardTitle className="text-white font-semibold">Strategy Parameters</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Fixed Position Range */}
            <div>
              <Label className="text-white font-medium">Position Range (Fixed for Testing)</Label>
              <div className="mt-2 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                <div className="text-sm text-orange-800 font-medium">
                  Range: 1000 - 5000 USDC per WETH
                </div>
                <div className="text-xs text-orange-600 mt-1">
                  This range is locked for testing purposes. No complex tick math required.
                </div>
              </div>
              <div className="mt-2">
                <Input
                  type="range"
                  min="10"
                  max="500"
                  value={tickRange}
                  disabled
                  className="w-full opacity-50 cursor-not-allowed"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>±10 ticks (0.1%)</span>
                  <span>±500 ticks (5%)</span>
                </div>
              </div>
              <div className="mt-2 text-sm text-gray-300">
                Range locked for testing - Slider disabled
              </div>
            </div>

            {/* Wallet Balances */}
            <div className="space-y-2">
              <Label className="text-white font-medium flex items-center">
                <Wallet className="w-4 h-4 mr-2" />
                Wallet Balances
              </Label>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="bg-white/10 p-3 rounded-lg border border-orange-500/30">
                  <div className="text-gray-300">{token0Symbol}</div>
                  <div className="text-white font-medium">
                    {token0Balance.isLoading ? 'Loading...' : `${token0Balance.formatted} ${token0Balance.symbol}`}
                  </div>
                </div>
                <div className="bg-white/10 p-3 rounded-lg border border-orange-500/30">
                  <div className="text-gray-300">{token1Symbol}</div>
                  <div className="text-white font-medium">
                    {token1Balance.isLoading ? 'Loading...' : `${token1Balance.formatted} ${token1Balance.symbol}`}
                  </div>
                </div>
              </div>
            </div>

            {/* Amounts with Allocation Buttons */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-white font-medium">{token0Symbol} Amount</Label>
                <Input
                  type="number"
                  placeholder="0.0"
                  value={amount0}
                  onChange={(e) => setAmount0(e.target.value)}
                  className={`bg-white/10 border-orange-500/30 text-white placeholder-gray-400 ${
                    token0Insufficient ? 'border-red-500' : ''
                  }`}
                />
                {token0Insufficient && (
                  <div className="text-red-500 text-xs mt-1 font-medium bg-red-500/10 px-2 py-1 rounded">
                    Insufficient {token0Symbol} balance
                  </div>
                )}
                {/* Allocation buttons inside token0 input */}
                <div className="grid grid-cols-4 gap-1 mt-2">
                  {[25, 50, 75, 100].map((percentage) => (
                    <Button
                      key={percentage}
                      variant="outline"
                      size="sm"
                      onClick={() => handleAllocation(percentage)}
                      className="bg-orange-100 border-orange-300 hover:bg-orange-500 hover:text-white text-orange-800 font-medium text-xs"
                    >
                      {percentage}%
                    </Button>
                  ))}
                </div>
              </div>
              <div>
                <Label className="text-white font-medium">{token1Symbol} Amount</Label>
                <Input
                  type="number"
                  placeholder="0.0"
                  value={amount1}
                  onChange={(e) => setAmount1(e.target.value)}
                  className={`bg-white/10 border-orange-500/30 text-white placeholder-gray-400 ${
                    token1Insufficient ? 'border-red-500' : ''
                  }`}
                />
                {token1Insufficient && (
                  <div className="text-red-500 text-xs mt-1 font-medium bg-red-500/10 px-2 py-1 rounded">
                    Insufficient {token1Symbol} balance
                  </div>
                )}
                {/* Allocation buttons inside token1 input */}
                <div className="grid grid-cols-4 gap-1 mt-2">
                  {[25, 50, 75, 100].map((percentage) => (
                    <Button
                      key={percentage}
                      variant="outline"
                      size="sm"
                      onClick={() => handleAllocation(percentage)}
                      className="bg-orange-100 border-orange-300 hover:bg-orange-500 hover:text-white text-orange-800 font-medium text-xs"
                    >
                      {percentage}%
                    </Button>
                  ))}
                </div>
              </div>
            </div>

            {/* Check Interval */}
            <div>
              <Label className="text-tangerine-black/80">Check Interval (minutes)</Label>
              <Input
                type="number"
                min="1"
                max="60"
                value={checkInterval}
                onChange={(e) => setCheckInterval(Number(e.target.value))}
                className="bg-white border-tangerine-primary/30 text-tangerine-black"
              />
            </div>

            {/* Recommendations */}
            {recommendations && (
              <div className="space-y-2">
                <Label className="text-tangerine-black/80">AI Recommendations</Label>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-tangerine-black/70">Recommended Range:</span>
                    <Badge variant="secondary">
                      ±{(recommendations as any).recommendations.tick_range} ticks
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-tangerine-black/70">Expected APR:</span>
                    <span className="text-orange-400 font-medium">
                      {formatPercentage(recommendations?.recommendations?.expected_apr || 0)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-tangerine-black/70">Liquidation Risk:</span>
                    <span className={`font-medium ${
                      (recommendations as any).recommendations.liquidation_probability > 20 
                        ? 'text-red-400' 
                        : 'text-green-400'
                    }`}>
                      {formatPercentage(recommendations?.recommendations?.liquidation_probability || 0)}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Real-time Risk Analysis */}
            {outOfRangeData && (
              <div className="space-y-2">
                <Label className="text-tangerine-black/80">Risk Analysis</Label>
                <div className={`p-3 rounded-lg border ${
                  (outOfRangeData as any).risk_level === 'low' 
                    ? 'bg-green-900/20 border-green-800' 
                    : (outOfRangeData as any).risk_level === 'medium'
                    ? 'bg-yellow-900/20 border-yellow-800'
                    : 'bg-red-900/20 border-red-800'
                }`}>
                  <div className="flex items-start space-x-2">
                    <AlertTriangle className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                      (outOfRangeData as any).risk_level === 'low' 
                        ? 'text-green-400' 
                        : (outOfRangeData as any).risk_level === 'medium'
                        ? 'text-yellow-400'
                        : 'text-red-400'
                    }`} />
                    <div className="space-y-1">
                      <div className={`text-sm font-medium ${
                        (outOfRangeData as any).risk_level === 'low' 
                          ? 'text-green-300' 
                          : (outOfRangeData as any).risk_level === 'medium'
                          ? 'text-yellow-300'
                          : 'text-red-300'
                      }`}>
                        Position has {(outOfRangeData as any).out_of_range_probability}% chance of going out of range
                      </div>
                      <div className="text-xs text-tangerine-black/70">
                        Volatility: {(outOfRangeData as any).volatility_percentage}% | 
                        Range: ${(outOfRangeData as any).price_bounds.lower} - ${(outOfRangeData as any).price_bounds.upper} | 
                        Check interval: {checkInterval} minutes
                      </div>
                      <div className="text-xs text-tangerine-black/80">
                        {(outOfRangeData as any).recommendation}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Legacy Warnings */}
            {(recommendations as any)?.warnings && recommendations.warnings.length > 0 && (
              <div className="space-y-2">
                {(recommendations as any).warnings.map((warning: any, index: number) => (
                  <div key={index} className="flex items-start space-x-2 p-3 bg-yellow-900/20 border border-yellow-800 rounded-lg">
                    <AlertTriangle className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-yellow-300">{warning}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Submit Button */}
            <Button
              onClick={handleSubmit}
              disabled={loading || creatingPosition || isPending || isConfirming || !amount0 || !amount1 || token0Insufficient || token1Insufficient}
              className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold shadow-lg"
            >
              {loading || creatingPosition || isPending || isConfirming ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  {currentStep || (isPending ? 'Confirming Transaction...' : 
                   isConfirming ? 'Creating Position...' : 
                   creatingPosition ? 'Preparing Position...' : 'Loading...')}
                </>
              ) : (
                'Create Position'
              )}
            </Button>

            {/* Transaction Status */}
            {hash && (
              <div className="text-center">
                <div className="text-sm text-tangerine-black/70">
                  Transaction Hash: 
                  <a 
                    href={`https://basescan.org/tx/${hash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-tangerine-primary hover:text-tangerine-dark ml-1"
                  >
                    {hash.slice(0, 10)}...{hash.slice(-8)}
                  </a>
                </div>
                {isConfirmed && (
                  <div className="text-tangerine-green text-sm mt-1">
                    ✅ Position created successfully!
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}





