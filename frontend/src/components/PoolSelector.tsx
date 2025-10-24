'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, TrendingUp, DollarSign, Activity } from 'lucide-react';
import { apiClient } from '@/lib/api';

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
  vol_tvl_ratio: number;
}

interface PoolSelectorProps {
  onPoolSelect: (pool: Pool) => void;
}

export function PoolSelector({ onPoolSelect }: PoolSelectorProps) {
  const [pools, setPools] = useState<Pool[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('tvl');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    fetchPools();
  }, [sortBy, sortOrder]);

  const fetchPools = async () => {
    try {
      setLoading(true);
      
      // Try to fetch from API first
      try {
        const data = await apiClient.getPools({
          sort_by: sortBy,
          sort_order: sortOrder,
          limit: 50,
        });
        setPools(data as any);
        return;
      } catch (apiError) {
        console.log('API not available, using mock data:', apiError);
      }
      
      // Fallback to mock data if API is not available
      const mockPools = [
        {
          address: "0xd0b53D9277642d899DF5C87A3966A349A798F224",
          name: "WETH-USDC",
          token0: "WETH",
          token1: "USDC",
          fee_tier: 500,
          tvl: 8348862.46,
          apr: 72.62,
          volume_1d: 180991850.31,
          volume_30d: 5429755509.3,
          vol_tvl_ratio: 21.7
        },
        {
          address: "0x6c561B446416E1A00E8E93E221854d6eA4171372",
          name: "WETH-USDC",
          token0: "WETH",
          token1: "USDC",
          fee_tier: 3000,
          tvl: 27360560.71,
          apr: 15.2,
          volume_1d: 67910135.12,
          volume_30d: 2037304053.6,
          vol_tvl_ratio: 2.48
        },
        {
          address: "0x93e8542E6CA0eFFfb9D57a270b76712b968A38f5",
          name: "WETH-DAI",
          token0: "WETH",
          token1: "DAI",
          fee_tier: 500,
          tvl: 2000000.0,
          apr: 25.5,
          volume_1d: 800000.0,
          volume_30d: 24000000.0,
          vol_tvl_ratio: 0.4
        },
        {
          address: "0xDcf81663E68f076EF9763442DE134Fd0699de4ef",
          name: "WETH-DAI",
          token0: "WETH",
          token1: "DAI",
          fee_tier: 3000,
          tvl: 1200000.0,
          apr: 18.7,
          volume_1d: 500000.0,
          volume_30d: 15000000.0,
          vol_tvl_ratio: 0.42
        }
      ];
      
      // Sort mock data
      const sortedPools = [...mockPools].sort((a, b) => {
        const reverse = sortOrder === 'desc';
        let comparison = 0;
        
        switch (sortBy) {
          case 'tvl':
            comparison = a.tvl - b.tvl;
            break;
          case 'apr':
            comparison = a.apr - b.apr;
            break;
          case 'volume_1d':
            comparison = a.volume_1d - b.volume_1d;
            break;
          case 'volume_30d':
            comparison = a.volume_30d - b.volume_30d;
            break;
          case 'vol_tvl_ratio':
            comparison = a.vol_tvl_ratio - b.vol_tvl_ratio;
            break;
          default:
            comparison = a.tvl - b.tvl;
        }
        
        return reverse ? -comparison : comparison;
      });
      
      setPools(sortedPools);
    } catch (error) {
      console.error('Error fetching pools:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredPools = pools.filter(pool =>
    pool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    pool.token0.toLowerCase().includes(searchTerm.toLowerCase()) ||
    pool.token1.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return `$${(num / 1000000).toFixed(1)}M`;
    } else if (num >= 1000) {
      return `$${(num / 1000).toFixed(1)}K`;
    }
    return `$${num.toFixed(0)}`;
  };

  const formatPercentage = (num: number) => {
    return `${num.toFixed(2)}%`;
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white mb-2 gradient-text">Select a Pool</h1>
        <p className="text-gray-300">
          Choose a Uniswap V3 pool to provide liquidity to
        </p>
      </div>

      {/* Filters */}
      <Card className="glass-effect border-tangerine-primary/30 shadow-lg neon-border">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Search pools by token name..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 glass-effect border-tangerine-primary/30 text-white placeholder-gray-400 focus:border-tangerine-primary focus:ring-tangerine-primary/20"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-40 glass-effect border-tangerine-primary/30 text-white focus:border-tangerine-primary focus:ring-tangerine-primary/20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="tvl">TVL</SelectItem>
                  <SelectItem value="apr">APR</SelectItem>
                  <SelectItem value="volume_1d">1D Volume</SelectItem>
                  <SelectItem value="volume_30d">30D Volume</SelectItem>
                  <SelectItem value="vol_tvl_ratio">Vol/TVL</SelectItem>
                </SelectContent>
              </Select>
              
              <Button
                variant="outline"
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="glass-effect border-tangerine-primary/30 text-white hover:bg-tangerine-primary/10 hover:border-tangerine-primary"
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Pools Table */}
      <Card className="glass-effect border-tangerine-primary/30 shadow-lg neon-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <Activity className="w-5 h-5 mr-2 text-tangerine-primary" />
            Available Pools ({filteredPools.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-tangerine-primary mx-auto mb-4"></div>
              <p className="text-gray-300">Loading pools...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="border-tangerine-primary/20">
                    <TableHead className="text-gray-300 font-semibold">Pool</TableHead>
                    <TableHead className="text-gray-300 font-semibold">Fee Tier</TableHead>
                    <TableHead className="text-gray-300 font-semibold">TVL</TableHead>
                    <TableHead className="text-gray-300 font-semibold">APR</TableHead>
                    <TableHead className="text-gray-300 font-semibold">1D Volume</TableHead>
                    <TableHead className="text-gray-300 font-semibold">30D Volume</TableHead>
                    <TableHead className="text-gray-300 font-semibold">Vol/TVL</TableHead>
                    <TableHead className="text-gray-300 font-semibold">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredPools.map((pool) => (
                    <TableRow key={pool.address} className="border-tangerine-primary/10 hover:bg-tangerine-primary/5 transition-colors">
                      <TableCell className="text-white">
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 bg-gradient-to-r from-tangerine-primary to-tangerine-purple rounded-full flex items-center justify-center shadow-sm animate-glow">
                            <span className="text-white font-bold text-xs">
                              {pool.token0[0]}{pool.token1[0]}
                            </span>
                          </div>
                          <div>
                            <div className="font-medium">{pool.name}</div>
                            <a 
                              href={`https://basescan.org/address/${pool.address}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-tangerine-primary hover:text-tangerine-dark underline"
                            >
                              {pool.address.slice(0, 6)}...{pool.address.slice(-4)}
                            </a>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary" className="glass-effect text-white border-tangerine-primary/30">
                          {(pool.fee_tier / 10000).toFixed(2)}%
                        </Badge>
                      </TableCell>
                      <TableCell className="text-white">
                        <div className="flex items-center">
                          <DollarSign className="w-4 h-4 mr-1 text-tangerine-green" />
                          {formatNumber(pool.tvl)}
                        </div>
                      </TableCell>
                      <TableCell className="text-white">
                        <div className="flex items-center">
                          <TrendingUp className="w-4 h-4 mr-1 text-tangerine-primary" />
                          {formatPercentage(pool.apr)}
                        </div>
                      </TableCell>
                      <TableCell className="text-gray-300">
                        {formatNumber(pool.volume_1d)}
                      </TableCell>
                      <TableCell className="text-gray-300">
                        {formatNumber(pool.volume_30d)}
                      </TableCell>
                      <TableCell className="text-gray-300">
                        {pool.vol_tvl_ratio.toFixed(2)}
                      </TableCell>
                      <TableCell>
                        <Button
                          onClick={() => onPoolSelect(pool)}
                          className="bg-gradient-to-r from-tangerine-primary to-tangerine-purple hover:from-tangerine-dark hover:to-tangerine-primary text-white font-semibold shadow-sm neon-border"
                        >
                          Select Pool
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}





