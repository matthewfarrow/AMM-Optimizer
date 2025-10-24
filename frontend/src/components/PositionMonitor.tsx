'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, TrendingUp, AlertCircle, CheckCircle, Pause, Play } from 'lucide-react';
import { apiClient } from '@/lib/api';

interface Position {
  id: number;
  user_address: string;
  token_id?: number;
  pool_address: string;
  tick_lower: number;
  tick_upper: number;
  amount0: number;
  amount1: number;
  check_interval: number;
  active: boolean;
  created_at: string;
  updated_at: string;
}

interface PositionMonitorProps {
  onBack: () => void;
}

export function PositionMonitor({ onBack }: PositionMonitorProps) {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPosition, setSelectedPosition] = useState<Position | null>(null);

  useEffect(() => {
    fetchPositions();
    // Set up polling for real-time updates
    const interval = setInterval(fetchPositions, 30000); // Poll every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchPositions = async () => {
    try {
      // Try API first
      try {
        const mockAddress = '0x1234567890123456789012345678901234567890';
        const data = await apiClient.getUserPositions(mockAddress);
        setPositions(data as any);
        return;
      } catch (apiError) {
        console.log('API not available, using mock data:', apiError);
      }
      
      // Mock data for positions
      const mockPositions = [
        {
          id: 1,
          user_address: '0x1234567890123456789012345678901234567890',
          token_id: 12345,
          pool_address: '0xd0b53D9277642d899DF5C87A3966A349A798F224',
          tick_lower: -200,
          tick_upper: 200,
          amount0: 1.5,
          amount1: 3750.0,
          check_interval: 60,
          active: true,
          created_at: new Date(Date.now() - 86400000).toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 2,
          user_address: '0x1234567890123456789012345678901234567890',
          token_id: 12346,
          pool_address: '0x6c561B446416E1A00E8E93E221854d6eA4171372',
          tick_lower: -100,
          tick_upper: 100,
          amount0: 0.8,
          amount1: 2000.0,
          check_interval: 30,
          active: false,
          created_at: new Date(Date.now() - 172800000).toISOString(),
          updated_at: new Date(Date.now() - 3600000).toISOString()
        }
      ];
      
      setPositions(mockPositions);
    } catch (error) {
      console.error('Error fetching positions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePausePosition = async (positionId: number) => {
    try {
      await apiClient.pausePosition(positionId);
      await fetchPositions();
    } catch (error) {
      console.error('Error pausing position:', error);
    }
  };

  const handleResumePosition = async (positionId: number) => {
    try {
      await apiClient.resumePosition(positionId);
      await fetchPositions();
    } catch (error) {
      console.error('Error resuming position:', error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getPositionStatus = (position: Position) => {
    if (!position.active) {
      return { status: 'paused', color: 'yellow', icon: Pause };
    }
    // In a real app, you'd check the actual position status
    return { status: 'active', color: 'green', icon: CheckCircle };
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
            <h1 className="text-3xl font-bold text-tangerine-black">Deploy & Monitor</h1>
            <p className="text-tangerine-black/70">Manage your active liquidity positions</p>
          </div>
        </div>
        <Button 
          onClick={fetchPositions}
          variant="outline"
          className="bg-white border-tangerine-primary/30 text-tangerine-black hover:bg-tangerine-primary/10 hover:border-tangerine-primary"
        >
          Refresh
        </Button>
      </div>

      {/* Positions Overview */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card className="bg-white/90 border-tangerine-primary/20 shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-tangerine-black/70 text-sm">Total Positions</p>
                <p className="text-2xl font-bold text-tangerine-black">{positions.length}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-tangerine-primary" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/90 border-tangerine-primary/20 shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-tangerine-black/70 text-sm">Active</p>
                <p className="text-2xl font-bold text-tangerine-green">
                  {positions.filter(p => p.active).length}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-tangerine-green" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/90 border-tangerine-primary/20 shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-tangerine-black/70 text-sm">Paused</p>
                <p className="text-2xl font-bold text-tangerine-accent">
                  {positions.filter(p => !p.active).length}
                </p>
              </div>
              <Pause className="w-8 h-8 text-tangerine-accent" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/90 border-tangerine-primary/20 shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-tangerine-black/70 text-sm">Total Value</p>
                <p className="text-2xl font-bold text-tangerine-black">
                  ${positions.reduce((sum, p) => sum + p.amount0 + p.amount1, 0).toFixed(0)}
                </p>
              </div>
              <AlertCircle className="w-8 h-8 text-tangerine-primary" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Positions List */}
      <Card className="bg-white/90 border-tangerine-primary/20 shadow-lg">
        <CardHeader>
          <CardTitle className="text-tangerine-black">Your Positions</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-tangerine-primary mx-auto mb-4"></div>
              <p className="text-tangerine-black/70">Loading positions...</p>
            </div>
          ) : positions.length === 0 ? (
            <div className="text-center py-8">
              <AlertCircle className="w-12 h-12 text-tangerine-black/70 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-tangerine-black mb-2">No Positions Found</h3>
              <p className="text-tangerine-black/70 mb-4">
                You don&apos;t have any active positions yet. Create your first position to get started.
              </p>
              <Button onClick={onBack} className="bg-gradient-to-r from-tangerine-primary to-tangerine-accent hover:from-tangerine-dark hover:to-tangerine-primary text-white font-semibold">
                Create Position
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {positions.map((position) => {
                const statusInfo = getPositionStatus(position);
                const StatusIcon = statusInfo.icon;
                
                return (
                  <Card key={position.id} className="bg-tangerine-cream/30 border-tangerine-primary/20 shadow-sm">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-gradient-to-r from-tangerine-primary to-tangerine-accent rounded-full flex items-center justify-center shadow-sm">
                            <span className="text-white font-bold">
                              {position.pool_address.slice(0, 2).toUpperCase()}
                            </span>
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-tangerine-black">
                              Position #{position.id}
                            </h3>
                            <p className="text-sm text-tangerine-black/70">
                              Pool: {position.pool_address.slice(0, 6)}...{position.pool_address.slice(-4)}
                            </p>
                            <p className="text-sm text-tangerine-black/70">
                              Range: {position.tick_lower} to {position.tick_upper}
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                          <div className="text-right">
                            <div className="flex items-center space-x-2 mb-1">
                              <StatusIcon className={`w-4 h-4 text-${statusInfo.color}-400`} />
                              <Badge variant={statusInfo.color === 'green' ? 'default' : 'secondary'}>
                                {statusInfo.status}
                              </Badge>
                            </div>
                            <p className="text-sm text-tangerine-black/70">
                              Created: {formatDate(position.created_at)}
                            </p>
                            <p className="text-sm text-tangerine-black/70">
                              Amount: {position.amount0.toFixed(4)} / {position.amount1.toFixed(2)}
                            </p>
                          </div>
                          
                          <div className="flex space-x-2">
                            {position.active ? (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handlePausePosition(position.id)}
                                className="bg-white border-tangerine-primary/30 text-tangerine-black hover:bg-tangerine-primary/10 hover:border-tangerine-primary"
                              >
                                <Pause className="w-4 h-4 mr-1" />
                                Pause
                              </Button>
                            ) : (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleResumePosition(position.id)}
                                className="bg-white border-tangerine-primary/30 text-tangerine-black hover:bg-tangerine-primary/10 hover:border-tangerine-primary"
                              >
                                <Play className="w-4 h-4 mr-1" />
                                Resume
                              </Button>
                            )}
                            
                            <Button
                              variant="outline"
                              size="sm"
                              className="bg-white border-red-500/30 text-red-600 hover:bg-red-50 hover:border-red-500"
                            >
                              Withdraw
                            </Button>
                          </div>
                        </div>
                      </div>
                      
                      {/* Position Details */}
                      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-tangerine-primary/20">
                        <div>
                          <p className="text-sm text-tangerine-black/70">Check Interval</p>
                          <p className="text-tangerine-black font-medium">{position.check_interval}s</p>
                        </div>
                        <div>
                          <p className="text-sm text-tangerine-black/70">Last Updated</p>
                          <p className="text-tangerine-black font-medium">{formatDate(position.updated_at)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-tangerine-black/70">Token ID</p>
                          <p className="text-tangerine-black font-medium">
                            {position.token_id ? `#${position.token_id}` : 'Not deployed'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-tangerine-black/70">Status</p>
                          <p className="text-tangerine-black font-medium">
                            {position.active ? 'Monitoring' : 'Paused'}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}






