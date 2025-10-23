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
      const data = await apiClient.getPools({
        sort_by: sortBy,
        sort_order: sortOrder,
        limit: 50,
      });
      setPools(data);
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
        <h1 className="text-3xl font-bold text-slate-200 mb-2">Select a Pool</h1>
        <p className="text-slate-400">
          Choose a Uniswap V3 pool to provide liquidity to
        </p>
      </div>

      {/* Filters */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                <Input
                  placeholder="Search pools by token name..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-slate-700 border-slate-600 text-slate-200"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-40 bg-slate-700 border-slate-600">
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
                className="bg-slate-700 border-slate-600"
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Pools Table */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-slate-200 flex items-center">
            <Activity className="w-5 h-5 mr-2" />
            Available Pools ({filteredPools.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500 mx-auto mb-4"></div>
              <p className="text-slate-400">Loading pools...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="border-slate-700">
                    <TableHead className="text-slate-300">Pool</TableHead>
                    <TableHead className="text-slate-300">Fee Tier</TableHead>
                    <TableHead className="text-slate-300">TVL</TableHead>
                    <TableHead className="text-slate-300">APR</TableHead>
                    <TableHead className="text-slate-300">1D Volume</TableHead>
                    <TableHead className="text-slate-300">30D Volume</TableHead>
                    <TableHead className="text-slate-300">Vol/TVL</TableHead>
                    <TableHead className="text-slate-300">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredPools.map((pool) => (
                    <TableRow key={pool.address} className="border-slate-700 hover:bg-slate-700/50">
                      <TableCell className="text-slate-200">
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center">
                            <span className="text-slate-200 font-bold text-xs">
                              {pool.token0[0]}{pool.token1[0]}
                            </span>
                          </div>
                          <div>
                            <div className="font-medium">{pool.name}</div>
                            <a 
                              href={`https://basescan.org/address/${pool.address}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-blue-400 hover:text-blue-300 underline"
                            >
                              {pool.address.slice(0, 6)}...{pool.address.slice(-4)}
                            </a>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary">
                          {(pool.fee_tier / 10000).toFixed(2)}%
                        </Badge>
                      </TableCell>
                      <TableCell className="text-slate-200">
                        <div className="flex items-center">
                          <DollarSign className="w-4 h-4 mr-1 text-green-400" />
                          {formatNumber(pool.tvl)}
                        </div>
                      </TableCell>
                      <TableCell className="text-slate-200">
                        <div className="flex items-center">
                          <TrendingUp className="w-4 h-4 mr-1 text-orange-400" />
                          {formatPercentage(pool.apr)}
                        </div>
                      </TableCell>
                      <TableCell className="text-slate-300">
                        {formatNumber(pool.volume_1d)}
                      </TableCell>
                      <TableCell className="text-slate-300">
                        {formatNumber(pool.volume_30d)}
                      </TableCell>
                      <TableCell className="text-slate-300">
                        {pool.vol_tvl_ratio.toFixed(2)}
                      </TableCell>
                      <TableCell>
                        <Button
                          onClick={() => onPoolSelect(pool)}
                          className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600"
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





