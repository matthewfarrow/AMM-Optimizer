'use client';

import { useState, useEffect, useRef, Suspense } from 'react';
import { useAccount } from 'wagmi';
import { useRouter, useSearchParams } from 'next/navigation';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import { PoolSelector } from '@/components/PoolSelector';
import { StrategyConfig } from '@/components/StrategyConfig';
import { PositionMonitor } from '@/components/PositionMonitor';

type Tab = 'pools' | 'strategy' | 'monitor';

function AppPageContent() {
  const { isConnected, address } = useAccount();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [activeTab, setActiveTab] = useState<Tab>('pools');
  const [selectedPool, setSelectedPool] = useState<any>(null);
  const selectedPoolRef = useRef<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isNavigating, setIsNavigating] = useState(false);
  
  // Load selectedPool from localStorage on mount
  useEffect(() => {
    const savedPool = localStorage.getItem('selectedPool');
    if (savedPool) {
      try {
        const parsedPool = JSON.parse(savedPool);
        console.log('🔄 Loading selectedPool from localStorage:', parsedPool);
        setSelectedPool(parsedPool);
        selectedPoolRef.current = parsedPool;
      } catch (e) {
        console.error('Failed to parse saved pool:', e);
        localStorage.removeItem('selectedPool');
      }
    }
    setIsLoading(false);
  }, []);
  
  // Persist selectedPool to localStorage and ref
  useEffect(() => {
    selectedPoolRef.current = selectedPool;
    
    // Save to localStorage
    if (selectedPool) {
      localStorage.setItem('selectedPool', JSON.stringify(selectedPool));
    } else {
      localStorage.removeItem('selectedPool');
    }
  }, [selectedPool]);
  // Whitelist feature removed - all users can access the app

  // Get tab from URL params
  const urlTab = searchParams.get('tab') as Tab || 'pools';

  useEffect(() => {
    // Only update activeTab from URL if we don't have a selected pool
    // This prevents the redirect loop when a pool is selected
    if (!selectedPool) {
      setActiveTab(urlTab);
    }
  }, [urlTab]);

  // Show loading while checking localStorage
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <Card className="w-full max-w-md bg-white/10 border-orange-500/30 glass-effect">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-white">Loading...</CardTitle>
            <p className="text-gray-300">Initializing application</p>
          </CardHeader>
        </Card>
      </div>
    );
  }

  // Redirect if not connected (only after loading is complete)
  // Skip wallet requirement if we have a saved pool (user was already using the app)
  // Also skip wallet requirement during navigation to prevent flashing
  if (!isConnected && !selectedPool && !isNavigating && isLoading === false) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <Card className="w-full max-w-md bg-white/10 border-orange-500/30 glass-effect">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-white">Wallet Required</CardTitle>
            <p className="text-gray-300">Please connect your wallet to access the app</p>
          </CardHeader>
          <CardContent className="text-center">
            <ConnectButton />
            <Link href="/" className="block mt-4">
              <Button variant="outline" className="w-full border-tangerine-border text-tangerine-text-secondary bg-tangerine-surface hover:bg-tangerine-gray hover:text-white">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Home
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Whitelist restrictions removed - proceed directly to app

  const handlePoolSelect = (pool: any) => {
    // Set navigating state to show loading on current page
    setIsNavigating(true);
    
    // Set both the pool and active tab immediately
    setSelectedPool(pool);
    setActiveTab('strategy');
    
    // Use setTimeout to delay URL update, allowing the new tab to render first
    setTimeout(() => {
      router.push('/app?tab=strategy');
      setIsNavigating(false);
    }, 100);
  };

  const handleStrategyComplete = () => {
    setIsNavigating(true);
    setActiveTab('monitor');
    setTimeout(() => {
      router.push('/app?tab=monitor');
      setIsNavigating(false);
    }, 100);
  };

  const handleBackToPools = () => {
    setIsNavigating(true);
    setActiveTab('pools');
    
    setTimeout(() => {
      router.push('/app?tab=pools');
      setIsNavigating(false);
    }, 100);
  };

  const handleStartOver = () => {
    setSelectedPool(null);
    setActiveTab('pools');
    router.push('/app?tab=pools');
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'pools':
        return (
          <PoolSelector 
            onPoolSelect={handlePoolSelect} 
            onStartOver={handleStartOver}
            hasSelectedPool={!!selectedPool}
          />
        );
      case 'strategy':
        // Use ref and localStorage as fallbacks if state is null
        let poolToUse = selectedPool || selectedPoolRef.current;
        
        // If still null, try localStorage
        if (!poolToUse) {
          try {
            const savedPool = localStorage.getItem('selectedPool');
            if (savedPool) {
              poolToUse = JSON.parse(savedPool);
            }
          } catch (e) {
            console.error('Failed to parse localStorage pool:', e);
          }
        }
        
        if (!poolToUse || !poolToUse.address || !poolToUse.token0 || !poolToUse.token1) {
          // Redirect to pools if no valid pool is selected
          setActiveTab('pools');
          router.push('/app?tab=pools');
          return <PoolSelector onPoolSelect={handlePoolSelect} />;
        }
        return (
          <StrategyConfig 
            pool={poolToUse} 
            onComplete={handleStrategyComplete}
            onBack={handleBackToPools}
          />
        );
      case 'monitor':
        return (
          <PositionMonitor 
            onBack={handleBackToPools}
          />
        );
      default:
        return <PoolSelector onPoolSelect={handlePoolSelect} />;
    }
  };

  return (
    <div className="min-h-screen bg-tangerine-black fruit-pattern relative">
      {/* Navigation Loading Overlay */}
      {isNavigating && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-orange-500/30">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-orange-500"></div>
              <span className="text-white">Loading...</span>
            </div>
          </div>
        </div>
      )}
      
      {/* Header */}
      <header className="border-b border-tangerine-border sticky top-0 z-50 glass-effect">
        <div className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center space-x-3">
                <div className="w-8 h-8 tangerine-gradient rounded-lg flex items-center justify-center citrus-glow">
                  <span className="text-white font-bold text-sm">🍊</span>
                </div>
                <span className="text-xl font-semibold text-white">Tangerine.trading</span>
              </Link>
              
              {/* Tab Navigation */}
              <nav className="hidden md:flex space-x-2">
                <Button
                  variant={activeTab === 'pools' ? 'default' : 'ghost'}
                  onClick={handleBackToPools}
                  className={activeTab === 'pools' 
                    ? "bg-tangerine-primary text-white hover:bg-tangerine-dark" 
                    : "text-tangerine-text-secondary hover:text-white hover:bg-tangerine-surface"
                  }
                >
                  Select Pool
                </Button>
                <Button
                  variant={activeTab === 'strategy' ? 'default' : 'ghost'}
                  onClick={() => {
                    if (selectedPool) {
                      setIsNavigating(true);
                      setActiveTab('strategy');
                      setTimeout(() => {
                        router.push('/app?tab=strategy');
                        setIsNavigating(false);
                      }, 100);
                    }
                  }}
                  disabled={!selectedPool}
                  className={activeTab === 'strategy' 
                    ? "bg-tangerine-primary text-white hover:bg-tangerine-dark" 
                    : "text-tangerine-text-secondary hover:text-white hover:bg-tangerine-surface"
                  }
                >
                  Configure Strategy
                </Button>
                <Button
                  variant={activeTab === 'monitor' ? 'default' : 'ghost'}
                  onClick={() => {
                    setIsNavigating(true);
                    setActiveTab('monitor');
                    setTimeout(() => {
                      router.push('/app?tab=monitor');
                      setIsNavigating(false);
                    }, 100);
                  }}
                  className={activeTab === 'monitor' 
                    ? "bg-tangerine-primary text-white hover:bg-tangerine-dark" 
                    : "text-tangerine-text-secondary hover:text-white hover:bg-tangerine-surface"
                  }
                >
                  Deploy & Monitor
                </Button>
              </nav>
              
              {/* Mobile Navigation */}
              <div className="md:hidden">
                <Select value={activeTab} onValueChange={(value) => {
                  setActiveTab(value as Tab);
                  router.push(`/app?tab=${value}`);
                }}>
                  <SelectTrigger className="w-40 bg-tangerine-surface border-tangerine-border text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pools">Select Pool</SelectItem>
                    <SelectItem value="strategy" disabled={!selectedPool}>Configure Strategy</SelectItem>
                    <SelectItem value="monitor">Deploy & Monitor</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="hidden sm:inline-flex bg-tangerine-surface text-tangerine-text-secondary border-tangerine-border">
                {address?.slice(0, 6)}...{address?.slice(-4)}
              </Badge>
              <ConnectButton />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {renderTabContent()}
      </main>
    </div>
  );
}

export default function AppPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-tangerine-primary to-tangerine-purple rounded-full flex items-center justify-center mx-auto mb-4 animate-glow">
            <span className="text-white font-bold text-xl">⚡</span>
          </div>
          <p className="text-gray-300 text-lg">Loading Tangerine.trading...</p>
        </div>
      </div>
    }>
      <AppPageContent />
    </Suspense>
  );
}





