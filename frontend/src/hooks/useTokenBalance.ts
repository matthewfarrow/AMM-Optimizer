import { useBalance, useReadContract } from 'wagmi';
import { formatUnits } from 'viem';
import { TOKEN_ADDRESSES, ERC20_ABI } from '@/lib/contracts';

export interface TokenBalance {
  address: string;
  symbol: string;
  balance: string;
  decimals: number;
  formatted: string;
}

export function useTokenBalance(tokenAddress: string, userAddress?: `0x${string}`) {
  // For native ETH
  if (tokenAddress === '0x0000000000000000000000000000000000000000') {
    const { data: ethBalance, isLoading, error } = useBalance({
      address: userAddress,
    });

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
  const { data: balance, isLoading: balanceLoading, error: balanceError } = useReadContract({
    address: tokenAddress as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'balanceOf',
    args: userAddress ? [userAddress] : undefined,
    query: {
      enabled: !!userAddress,
    },
  });

  const { data: decimals, isLoading: decimalsLoading } = useReadContract({
    address: tokenAddress as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'decimals',
    query: {
      enabled: !!tokenAddress,
    },
  });

  const { data: symbol, isLoading: symbolLoading } = useReadContract({
    address: tokenAddress as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'symbol',
    query: {
      enabled: !!tokenAddress,
    },
  });

  const isLoading = balanceLoading || decimalsLoading || symbolLoading;
  const error = balanceError;

  const formatted = balance && decimals ? formatUnits(balance, decimals) : '0';

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
