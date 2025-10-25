import { useBalance, useReadContract } from 'wagmi';
import { formatUnits } from 'viem';
import { TOKEN_ADDRESSES, ERC20_ABI } from '@/lib/contracts';
import { useState, useEffect } from 'react';

export interface TokenBalance {
  address: string;
  symbol: string;
  balance: string;
  decimals: number;
  formatted: string;
}

export function useTokenBalance(tokenAddress: string, userAddress?: `0x${string}`) {
  const [retryCount, setRetryCount] = useState(0);
  const maxRetries = 3;

        // Debug logging (reduced frequency - only log every 100th call to prevent rate limiting)
        if (retryCount === 0 && Math.random() < 0.01) {
          console.log('🔍 useTokenBalance called:', {
            tokenAddress,
            userAddress,
            retryCount
          });
        }

  // For native ETH
  if (tokenAddress === '0x0000000000000000000000000000000000000000') {
    const { data: ethBalance, isLoading, error, refetch } = useBalance({
      address: userAddress,
    });

    // Retry on error
    useEffect(() => {
      if (error && retryCount < maxRetries) {
        const timer = setTimeout(() => {
          setRetryCount(prev => prev + 1);
          refetch();
        }, 1000 * (retryCount + 1)); // Exponential backoff
        
        return () => clearTimeout(timer);
      }
    }, [error, retryCount, refetch]);

    return {
      balance: ethBalance?.value || 0n,
      formatted: ethBalance?.formatted || '0',
      decimals: 18,
      symbol: 'ETH',
      isLoading,
      error,
    };
  }

  // For ERC-20 tokens
  const { data: balance, isLoading: balanceLoading, error: balanceError, refetch: refetchBalance } = useReadContract({
    address: tokenAddress as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'balanceOf',
    args: userAddress ? [userAddress] : undefined,
    query: {
      enabled: !!userAddress,
      retry: 3,
      retryDelay: 1000,
    },
  });

  const { data: decimals, isLoading: decimalsLoading, refetch: refetchDecimals } = useReadContract({
    address: tokenAddress as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'decimals',
    query: {
      enabled: !!tokenAddress,
      retry: 3,
      retryDelay: 1000,
    },
  });

  const { data: symbol, isLoading: symbolLoading, refetch: refetchSymbol } = useReadContract({
    address: tokenAddress as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'symbol',
    query: {
      enabled: !!tokenAddress,
      retry: 3,
      retryDelay: 1000,
    },
  });

  // Retry on error for ERC-20 tokens
  useEffect(() => {
    if ((balanceError || !balance || !decimals || !symbol) && retryCount < maxRetries) {
      const timer = setTimeout(() => {
        setRetryCount(prev => prev + 1);
        refetchBalance();
        refetchDecimals();
        refetchSymbol();
      }, 1000 * (retryCount + 1)); // Exponential backoff
      
      return () => clearTimeout(timer);
    }
  }, [balanceError, balance, decimals, symbol, retryCount, refetchBalance, refetchDecimals, refetchSymbol]);

  const isLoading = balanceLoading || decimalsLoading || symbolLoading;
  const error = balanceError;

  const formatted = balance && decimals ? formatUnits(balance, decimals) : '0';

        // Debug logging for ERC-20 tokens (reduced frequency - only log every 100th call to prevent rate limiting)
        if (retryCount === 0 && Math.random() < 0.01) {
          console.log('🔍 ERC-20 token balance result:', {
            tokenAddress,
            userAddress,
            balance: balance?.toString(),
            decimals,
            symbol,
            formatted,
            isLoading,
            error: error?.message
          });
        }

  return {
    balance: balance || 0n,
    formatted,
    decimals: decimals || 18,
    symbol: symbol || 'UNKNOWN',
    isLoading,
    error,
  };
}

export function useTokenBalances(tokenAddresses: string[], userAddress?: `0x${string}`) {
  const balances = tokenAddresses.map(address => 
    useTokenBalance(address, userAddress)
  );

  return {
    balances,
    isLoading: balances.some(b => b.isLoading),
    error: balances.find(b => b.error)?.error,
  };
}

// Helper to get balance for specific tokens
export function useWETHBalance(userAddress?: `0x${string}`) {
  return useTokenBalance(TOKEN_ADDRESSES.WETH, userAddress);
}

export function useUSDCBalance(userAddress?: `0x${string}`) {
  return useTokenBalance(TOKEN_ADDRESSES.USDC, userAddress);
}

export function useETHBalance(userAddress?: `0x${string}`) {
  return useTokenBalance('0x0000000000000000000000000000000000000000', userAddress);
}
