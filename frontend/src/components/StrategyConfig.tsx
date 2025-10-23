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
import { TickMath, Position, Pool, Token, FeeAmount } from '@uniswap/v3-sdk';
import { Token as UniswapToken } from '@uniswap/sdk-core';
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
  const [amount0, setAmount0] = useState('0.10'); // Default to 10 cents for testing
  const [amount1, setAmount1] = useState('');
  const [checkInterval, setCheckInterval] = useState(60);
  const [priceData, setPriceData] = useState([]);
  const [volatilityData, setVolatilityData] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [outOfRangeData, setOutOfRangeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [coingeckoApiKey, setCoingeckoApiKey] = useState('');
  const [creatingPosition, setCreatingPosition] = useState(false);
  const [txHash, setTxHash] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<string>('');
  const [approvalChecked, setApprovalChecked] = useState(false);
  const [lastApprovalAttempt, setLastApprovalAttempt] = useState<number>(0);

  // Contract interaction hooks
  const { writeContract, data: hash, error: writeError, isPending } = useWriteContract();
  const { isLoading: isConfirming, isSuccess: isConfirmed } = useWaitForTransactionReceipt({
    hash: hash as `0x${string}`,
  });

  // Get token addresses and ensure correct ordering (token0 < token1 by address)
  const token0Address = getTokenAddress(pool.token0);
  const token1Address = getTokenAddress(pool.token1);
  
  // Ensure token0 < token1 by address (Uniswap V3 requirement)
  // WETH (0x420...) < USDC (0x833...) = false, so WETH is token0, USDC is token1
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
      const [priceResponse, volatilityResponse, recommendationsResponse] = await Promise.all([
        apiClient.getPriceData(pool.address, timeframe),
        apiClient.getVolatilityAnalysis(pool.address, timeframe),
        apiClient.getStrategyRecommendations(pool.address, 1000, 'medium')
      ]);
      
      setPriceData(priceResponse.data || []);
      setVolatilityData(volatilityResponse);
      setRecommendations(recommendationsResponse);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchOutOfRangeProbability = async () => {
    try {
      const response = await apiClient.getOutOfRangeProbability(
        pool.address,
        tickRange,
        checkInterval,
        timeframe
      );
      setOutOfRangeData(response);
    } catch (error) {
      console.error('Error fetching out of range probability:', error);
    }
  };

  // Uniswap V3 SDK calculations
  const calculateTokenAmounts = useMemo(() => {
    console.log('🔄 calculateTokenAmounts called:', {
      pool: pool?.address,
      currentPrice: volatilityData?.current_price,
      amount0,
      amount1,
      tickRange
    });

    if (!volatilityData?.current_price || (!amount0 && !amount1)) {
      console.log('❌ Missing required data for calculation');
      return { amount0: '', amount1: '' };
    }

    try {
      const currentPrice = volatilityData.current_price;
      console.log('💰 Current price:', currentPrice);
      
      // Simple tick calculation - avoid complex SDK calls that cause errors
      const tickSpacing = pool?.fee_tier === 500 ? 10 : pool?.fee_tier === 3000 ? 60 : 200;
      console.log('📏 Tick spacing:', tickSpacing);
      
      // Calculate tick bounds using simple math
      const currentTick = Math.floor(Math.log(currentPrice) / Math.log(1.0001));
      const tickLower = Math.floor((currentTick - tickRange) / tickSpacing) * tickSpacing;
      const tickUpper = Math.floor((currentTick + tickRange) / tickSpacing) * tickSpacing;
      
      console.log('🎯 Tick bounds:', { currentTick, tickLower, tickUpper, tickRange });

      // Simple calculation without complex SDK calls
      if (amount0) {
        // Calculate amount1 based on amount0 and current price
        const amount0Num = parseFloat(amount0);
        const amount1Num = amount0Num * currentPrice;
        
        console.log('💱 Amount calculation:', {
          amount0: amount0Num,
          currentPrice,
          amount1: amount1Num
        });
        
        return {
          amount0,
          amount1: amount1Num.toFixed(6)
        };
      } else if (amount1) {
        // Calculate amount0 based on amount1 and current price
        const amount1Num = parseFloat(amount1);
        const amount0Num = amount1Num / currentPrice;
        
        console.log('💱 Amount calculation:', {
          amount1: amount1Num,
          currentPrice,
          amount0: amount0Num
        });
        
        return {
          amount0: amount0Num.toFixed(6),
          amount1
        };
      }
    } catch (error) {
      console.error('Error calculating token amounts:', error);
    }

    return { amount0, amount1 };
  }, [volatilityData, amount0, amount1, tickRange, token0Address, token1Address, pool]);

  // Update amounts when calculation changes
  useEffect(() => {
    const calculated = calculateTokenAmounts;
    if (calculated.amount0 !== amount0 || calculated.amount1 !== amount1) {
      if (amount0 && !amount1) {
        setAmount1(calculated.amount1);
      } else if (amount1 && !amount0) {
        setAmount0(calculated.amount0);
      }
    }
  }, [calculateTokenAmounts]);

  // Allocation functions
  const handleAllocation = (percentage: number) => {
    const totalValue = parseFloat(token0Balance.formatted) * (volatilityData?.current_price || 0) + 
                      parseFloat(token1Balance.formatted);
    const targetValue = (totalValue * percentage) / 100;
    
    if (volatilityData?.current_price) {
      const amount0Value = targetValue / 2;
      const amount1Value = targetValue / 2;
      
      setAmount0((amount0Value / volatilityData.current_price).toFixed(6));
      setAmount1(amount1Value.toFixed(6));
    }
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

  const currentTick = slot0 ? slot0[1] : 0; // slot0[1] is the tick

  const createPosition = useCallback(async () => {
    console.log('🚀 createPosition called:', {
      address,
      currentPrice: volatilityData?.current_price,
      amount0,
      amount1,
      pool: pool?.address
    });

    if (!address || !volatilityData?.current_price) {
      console.error('❌ Missing required data:', { address, currentPrice: volatilityData?.current_price });
      toast.error('Missing required data');
      return;
    }

    // No minimum amount validation - allow any amount

    try {
      setCreatingPosition(true);
      console.log('✅ Starting position creation...');
      
      // Get correct tick spacing based on fee tier
      const tickSpacing = pool.fee_tier === 500 ? 10 : pool.fee_tier === 3000 ? 60 : 200;
      
      // Calculate tick bounds from ACTUAL current tick (not from price)
      const tickLower = currentTick - tickRange;
      const tickUpper = currentTick + tickRange;
      
      // Ensure ticks are aligned with tick spacing
      const alignedTickLower = Math.floor(tickLower / tickSpacing) * tickSpacing;
      const alignedTickUpper = Math.floor(tickUpper / tickSpacing) * tickSpacing;
      
      // Ensure tickLower < tickUpper
      const finalTickLower = Math.min(alignedTickLower, alignedTickUpper);
      const finalTickUpper = Math.max(alignedTickLower, alignedTickUpper);

      // Parse amounts with correct decimals
      const amount0Desired = parseUnits(amount0, token0Symbol === 'USDC' ? 6 : 18);
      const amount1Desired = parseUnits(amount1, token1Symbol === 'USDC' ? 6 : 18);
      
      // Calculate minimum amounts with 0.5% slippage
      const amount0Min = calculateSlippage(amount0Desired, 0.5);
      const amount1Min = calculateSlippage(amount1Desired, 0.5);

      // Set deadline (20 minutes from now)
      const deadline = Math.floor(Date.now() / 1000) + 20 * 60;

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

      // Create position with retry logic
      let retries = 3;
      while (retries > 0) {
        try {
          writeContract({
            address: UNISWAP_V3_ADDRESSES.NONFUNGIBLE_POSITION_MANAGER as `0x${string}`,
            abi: NONFUNGIBLE_POSITION_MANAGER_ABI,
            functionName: 'mint',
            args: [mintParams],
            value: 0n, // No ETH value for this position
            gas: 500000n, // Reasonable gas limit for Base network
          });
          toast.success('Position creation transaction submitted!');
          return;
        } catch (error: any) {
          if (error.message?.includes('rate limited') && retries > 1) {
            console.log(`Rate limited, retrying in 3 seconds... (${retries} retries left)`);
            await new Promise(resolve => setTimeout(resolve, 3000));
            retries--;
            continue;
          }
          throw error;
        }
      }
      
    } catch (error) {
      console.error('Error creating position:', error);
      toast.error('Failed to create position');
    } finally {
      setCreatingPosition(false);
    }
  }, [address, volatilityData, amount0, amount1, pool, currentTick, tickRange, token0Symbol, token1Symbol, finalToken0Address, finalToken1Address, writeContract]);

  const approveToken = useCallback(async (tokenAddress: string, amount: bigint) => {
    try {
      // Add retry logic for rate limiting
      let retries = 3;
      while (retries > 0) {
        try {
          writeContract({
            address: tokenAddress as `0x${string}`,
            abi: ERC20_ABI,
            functionName: 'approve',
            args: [UNISWAP_V3_ADDRESSES.NONFUNGIBLE_POSITION_MANAGER as `0x${string}`, amount],
            gas: 100000n, // Reasonable gas limit for ERC20 approval
          });
          toast.success('Approval transaction submitted!');
          return;
        } catch (error: any) {
          if (error.message?.includes('rate limited') && retries > 1) {
            console.log(`Rate limited, retrying in 2 seconds... (${retries} retries left)`);
            await new Promise(resolve => setTimeout(resolve, 2000));
            retries--;
            continue;
          }
          throw error;
        }
      }
    } catch (error) {
      console.error('Error approving token:', error);
      toast.error('Failed to approve token - try again in a few seconds');
    }
  }, [writeContract]);

  const handleSubmit = useCallback(async () => {
    if (!address) {
      toast.error('Please connect your wallet');
      return;
    }

    if (token0Insufficient || token1Insufficient) {
      toast.error('Insufficient token balance');
      return;
    }

    // Prevent rapid re-submission (5 second cooldown)
    const now = Date.now();
    if (now - lastApprovalAttempt < 5000) {
      console.log('⚠️  Cooldown active - preventing rapid retry');
      return;
    }
    setLastApprovalAttempt(now);

    // Prevent approval loop - if we're already loading, don't start again
    if (loading || creatingPosition) {
      console.log('⚠️  Already processing - preventing loop');
      return;
    }

    try {
      setLoading(true);
      
      const amount0BigInt = parseUnits(amount0, token0Symbol === 'USDC' ? 6 : 18);
      const amount1BigInt = parseUnits(amount1, token1Symbol === 'USDC' ? 6 : 18);
      
      // Check if approvals are needed
      console.log('🔍 Approval check:', {
        token0Symbol,
        token1Symbol,
        token0Allowance: token0Allowance?.toString(),
        token1Allowance: token1Allowance?.toString(),
        amount0BigInt: amount0BigInt.toString(),
        amount1BigInt: amount1BigInt.toString()
      });
      
      const needsToken0Approval = !token0Allowance || token0Allowance < amount0BigInt;
      const needsToken1Approval = !token1Allowance || token1Allowance < amount1BigInt;
      
      console.log('📋 Approval needed:', {
        needsToken0Approval,
        needsToken1Approval
      });
      
      if (needsToken0Approval) {
        setCurrentStep(`Approving ${token0Symbol} (1/3)`);
        toast.info(`Approving ${token0Symbol}...`);
        await approveToken(finalToken0Address, amount0BigInt);
        return; // Wait for approval transaction
      }
      
      if (needsToken1Approval) {
        setCurrentStep(`Approving ${token1Symbol} (2/3)`);
        toast.info(`Approving ${token1Symbol}...`);
        await approveToken(finalToken1Address, amount1BigInt);
        return; // Wait for approval transaction
      }
      
      // Both tokens are approved, create position
      console.log('✅ No approval needed - proceeding directly to position creation');
      setCurrentStep('Creating Position (3/3)');
      toast.info('Creating position...');
      await createPosition();
      
    } catch (error) {
      console.error('Error creating position:', error);
      toast.error('Failed to create position');
    } finally {
      setLoading(false);
    }
  }, [address, token0Insufficient, token1Insufficient, lastApprovalAttempt, loading, creatingPosition, amount0, amount1, token0Symbol, token1Symbol, token0Allowance, token1Allowance, finalToken0Address, finalToken1Address, createPosition, approveToken]);

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
      } else {
        // This was an approval transaction, now retry position creation
        toast.success('Token approved! Continuing with position creation...');
        setTimeout(() => {
          // Only retry if we're not already in a loop and not already processing
          if (!loading && !creatingPosition && !isPending) {
            console.log('🔄 Retrying position creation after approval...');
            handleSubmit();
          } else {
            console.log('⚠️  Skipping retry - already processing or in loop');
          }
        }, 2000); // Wait 2 seconds for the approval to be processed
      }
    }
  }, [isConfirmed, hash, currentStep, onComplete, handleSubmit]);

  // Handle transaction errors
  useEffect(() => {
    if (writeError) {
      toast.error(`Transaction failed: ${writeError.message}`);
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
            <p className="text-slate-400">Set up your liquidity position parameters</p>
          </div>
        </div>
      </div>

      {/* Pool Info */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center mr-3">
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
              <Label className="text-slate-400">Fee Tier</Label>
              <div className="text-white font-medium">
                {(pool.fee_tier / 10000).toFixed(2)}%
              </div>
            </div>
            <div>
              <Label className="text-slate-400">Current Price</Label>
              <div className="text-white font-medium">
                {volatilityData ? formatPrice(volatilityData.current_price) : 'Loading...'}
              </div>
            </div>
            <div>
              <Label className="text-slate-400">Volatility</Label>
              <div className="text-white font-medium">
                {volatilityData ? formatPercentage(volatilityData.volatility_percentage) : 'Loading...'}
              </div>
            </div>
            <div>
              <Label className="text-slate-400">TVL</Label>
              <div className="text-white font-medium">
                ${(pool.tvl / 1000000).toFixed(1)}M
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Price Chart */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-white flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                Price Chart
              </CardTitle>
              <div className="flex space-x-2">
                {['1d', '1m', '1y'].map((tf) => (
                  <Button
                    key={tf}
                    variant={timeframe === tf ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setTimeframe(tf)}
                    className={timeframe === tf ? 'bg-orange-500' : 'bg-slate-700'}
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
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={priceData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis 
                      dataKey="timestamp" 
                      stroke="#9CA3AF"
                      tickFormatter={(value) => new Date(value).toLocaleDateString()}
                    />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: '1px solid #374151',
                        borderRadius: '6px'
                      }}
                      formatter={(value) => [formatPrice(Number(value)), 'Price']}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="price" 
                      stroke="#F97316" 
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
        <Card className="bg-slate-800/90 border-slate-600 shadow-xl">
          <CardHeader>
            <CardTitle className="text-white font-semibold">Strategy Parameters</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Tick Range */}
            <div>
              <Label className="text-slate-200 font-medium">Tick Range (±{tickRange} ticks)</Label>
              <div className="mt-2">
                <Input
                  type="range"
                  min="10"
                  max="500"
                  value={tickRange}
                  onChange={(e) => setTickRange(Number(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-slate-400 mt-1">
                  <span>±10 ticks (0.1%)</span>
                  <span>±500 ticks (5%)</span>
                </div>
              </div>
              <div className="mt-2 text-sm text-slate-300">
                Range: ±{(tickRange / 100).toFixed(1)}% from current price
              </div>
            </div>

            {/* Wallet Balances */}
            <div className="space-y-2">
              <Label className="text-slate-200 font-medium flex items-center">
                <Wallet className="w-4 h-4 mr-2" />
                Wallet Balances
              </Label>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="bg-slate-700/50 p-3 rounded-lg">
                  <div className="text-slate-400">{token0Symbol}</div>
                  <div className="text-white font-medium">
                    {token0Balance.isLoading ? 'Loading...' : `${token0Balance.formatted} ${token0Balance.symbol}`}
                  </div>
                </div>
                <div className="bg-slate-700/50 p-3 rounded-lg">
                  <div className="text-slate-400">{token1Symbol}</div>
                  <div className="text-white font-medium">
                    {token1Balance.isLoading ? 'Loading...' : `${token1Balance.formatted} ${token1Balance.symbol}`}
                  </div>
                </div>
              </div>
            </div>

            {/* Amounts with Allocation Buttons */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-slate-200 font-medium">{token0Symbol} Amount</Label>
                <Input
                  type="number"
                  placeholder="0.0"
                  value={amount0}
                  onChange={(e) => setAmount0(e.target.value)}
                  className={`bg-slate-700 border-slate-600 text-white ${
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
                      className="bg-tangerine-primary/20 border-tangerine-primary hover:bg-tangerine-primary hover:text-white text-tangerine-black font-medium text-xs"
                    >
                      {percentage}%
                    </Button>
                  ))}
                </div>
              </div>
              <div>
                <Label className="text-slate-200 font-medium">{token1Symbol} Amount</Label>
                <Input
                  type="number"
                  placeholder="0.0"
                  value={amount1}
                  onChange={(e) => setAmount1(e.target.value)}
                  className={`bg-slate-700 border-slate-600 text-white ${
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
                      className="bg-tangerine-primary/20 border-tangerine-primary hover:bg-tangerine-primary hover:text-white text-tangerine-black font-medium text-xs"
                    >
                      {percentage}%
                    </Button>
                  ))}
                </div>
              </div>
            </div>

            {/* Check Interval */}
            <div>
              <Label className="text-slate-300">Check Interval (minutes)</Label>
              <Input
                type="number"
                min="1"
                max="60"
                value={checkInterval}
                onChange={(e) => setCheckInterval(Number(e.target.value))}
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>

            {/* Recommendations */}
            {recommendations && (
              <div className="space-y-2">
                <Label className="text-slate-300">AI Recommendations</Label>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-400">Recommended Range:</span>
                    <Badge variant="secondary">
                      ±{recommendations.recommendations.tick_range} ticks
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-400">Expected APR:</span>
                    <span className="text-orange-400 font-medium">
                      {formatPercentage(recommendations.recommendations.expected_apr)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-400">Liquidation Risk:</span>
                    <span className={`font-medium ${
                      recommendations.recommendations.liquidation_probability > 20 
                        ? 'text-red-400' 
                        : 'text-green-400'
                    }`}>
                      {formatPercentage(recommendations.recommendations.liquidation_probability)}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Real-time Risk Analysis */}
            {outOfRangeData && (
              <div className="space-y-2">
                <Label className="text-slate-300">Risk Analysis</Label>
                <div className={`p-3 rounded-lg border ${
                  outOfRangeData.risk_level === 'low' 
                    ? 'bg-green-900/20 border-green-800' 
                    : outOfRangeData.risk_level === 'medium'
                    ? 'bg-yellow-900/20 border-yellow-800'
                    : 'bg-red-900/20 border-red-800'
                }`}>
                  <div className="flex items-start space-x-2">
                    <AlertTriangle className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                      outOfRangeData.risk_level === 'low' 
                        ? 'text-green-400' 
                        : outOfRangeData.risk_level === 'medium'
                        ? 'text-yellow-400'
                        : 'text-red-400'
                    }`} />
                    <div className="space-y-1">
                      <div className={`text-sm font-medium ${
                        outOfRangeData.risk_level === 'low' 
                          ? 'text-green-300' 
                          : outOfRangeData.risk_level === 'medium'
                          ? 'text-yellow-300'
                          : 'text-red-300'
                      }`}>
                        Position has {outOfRangeData.out_of_range_probability}% chance of going out of range
                      </div>
                      <div className="text-xs text-slate-400">
                        Volatility: {outOfRangeData.volatility_percentage}% | 
                        Range: ${outOfRangeData.price_bounds.lower} - ${outOfRangeData.price_bounds.upper} | 
                        Check interval: {checkInterval} minutes
                      </div>
                      <div className="text-xs text-slate-300">
                        {outOfRangeData.recommendation}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Legacy Warnings */}
            {recommendations?.warnings && recommendations.warnings.length > 0 && (
              <div className="space-y-2">
                {recommendations.warnings.map((warning, index) => (
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
              className="w-full bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600"
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
                <div className="text-sm text-slate-400">
                  Transaction Hash: 
                  <a 
                    href={`https://basescan.org/tx/${hash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-orange-400 hover:text-orange-300 ml-1"
                  >
                    {hash.slice(0, 10)}...{hash.slice(-8)}
                  </a>
                </div>
                {isConfirmed && (
                  <div className="text-green-400 text-sm mt-1">
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





