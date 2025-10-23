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
      // In a real app, you'd get the user address from the wallet
      const mockAddress = '0x1234567890123456789012345678901234567890';
      const data = await apiClient.getUserPositions(mockAddress);
      setPositions(data);
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
            <h1 className="text-3xl font-bold text-white">Deploy & Monitor</h1>
            <p className="text-slate-400">Manage your active liquidity positions</p>
          </div>
        </div>
        <Button 
          onClick={fetchPositions}
          variant="outline"
          className="bg-slate-700 border-slate-600"
        >
          Refresh
        </Button>
      </div>

      {/* Positions Overview */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Positions</p>
                <p className="text-2xl font-bold text-white">{positions.length}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Active</p>
                <p className="text-2xl font-bold text-green-400">
                  {positions.filter(p => p.active).length}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Paused</p>
                <p className="text-2xl font-bold text-yellow-400">
                  {positions.filter(p => !p.active).length}
                </p>
              </div>
              <Pause className="w-8 h-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Value</p>
                <p className="text-2xl font-bold text-white">
                  ${positions.reduce((sum, p) => sum + p.amount0 + p.amount1, 0).toFixed(0)}
                </p>
              </div>
              <AlertCircle className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Positions List */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Your Positions</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500 mx-auto mb-4"></div>
              <p className="text-slate-400">Loading positions...</p>
            </div>
          ) : positions.length === 0 ? (
            <div className="text-center py-8">
              <AlertCircle className="w-12 h-12 text-slate-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">No Positions Found</h3>
              <p className="text-slate-400 mb-4">
                You don't have any active positions yet. Create your first position to get started.
              </p>
              <Button onClick={onBack} className="bg-gradient-to-r from-orange-500 to-red-500">
                Create Position
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {positions.map((position) => {
                const statusInfo = getPositionStatus(position);
                const StatusIcon = statusInfo.icon;
                
                return (
                  <Card key={position.id} className="bg-slate-700/50 border-slate-600">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center">
                            <span className="text-white font-bold">
                              {position.pool_address.slice(0, 2).toUpperCase()}
                            </span>
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-white">
                              Position #{position.id}
                            </h3>
                            <p className="text-sm text-slate-400">
                              Pool: {position.pool_address.slice(0, 6)}...{position.pool_address.slice(-4)}
                            </p>
                            <p className="text-sm text-slate-400">
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
                            <p className="text-sm text-slate-400">
                              Created: {formatDate(position.created_at)}
                            </p>
                            <p className="text-sm text-slate-400">
                              Amount: {position.amount0.toFixed(4)} / {position.amount1.toFixed(2)}
                            </p>
                          </div>
                          
                          <div className="flex space-x-2">
                            {position.active ? (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handlePausePosition(position.id)}
                                className="bg-slate-600 border-slate-500"
                              >
                                <Pause className="w-4 h-4 mr-1" />
                                Pause
                              </Button>
                            ) : (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleResumePosition(position.id)}
                                className="bg-slate-600 border-slate-500"
                              >
                                <Play className="w-4 h-4 mr-1" />
                                Resume
                              </Button>
                            )}
                            
                            <Button
                              variant="outline"
                              size="sm"
                              className="bg-red-600 border-red-500 text-white hover:bg-red-700"
                            >
                              Withdraw
                            </Button>
                          </div>
                        </div>
                      </div>
                      
                      {/* Position Details */}
                      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-600">
                        <div>
                          <p className="text-sm text-slate-400">Check Interval</p>
                          <p className="text-white font-medium">{position.check_interval}s</p>
                        </div>
                        <div>
                          <p className="text-sm text-slate-400">Last Updated</p>
                          <p className="text-white font-medium">{formatDate(position.updated_at)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-slate-400">Token ID</p>
                          <p className="text-white font-medium">
                            {position.token_id ? `#${position.token_id}` : 'Not deployed'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-slate-400">Status</p>
                          <p className="text-white font-medium">
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





