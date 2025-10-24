'use client';

import { useState, useEffect, Suspense } from 'react';
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
  // Whitelist feature removed - all users can access the app

  // Get tab from URL params
  const urlTab = searchParams.get('tab') as Tab || 'pools';

  useEffect(() => {
    setActiveTab(urlTab);
  }, [urlTab]);

  // Redirect if not connected
  if (!isConnected) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-tangerine-cream via-orange-50 to-tangerine-cream flex items-center justify-center">
        <Card className="w-full max-w-md bg-white/80 border-tangerine-primary/20">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-tangerine-black">Wallet Required</CardTitle>
            <p className="text-tangerine-black/70">Please connect your wallet to access the app</p>
          </CardHeader>
          <CardContent className="text-center">
            <ConnectButton />
            <Link href="/" className="block mt-4">
              <Button variant="outline" className="w-full border-tangerine-primary text-tangerine-black hover:bg-tangerine-primary/10">
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
    setSelectedPool(pool);
    setActiveTab('strategy');
    router.push('/app?tab=strategy');
  };

  const handleStrategyComplete = () => {
    setActiveTab('monitor');
    router.push('/app?tab=monitor');
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'pools':
        return <PoolSelector onPoolSelect={handlePoolSelect} />;
      case 'strategy':
        return (
          <StrategyConfig 
            pool={selectedPool} 
            onComplete={handleStrategyComplete}
            onBack={() => {
              setActiveTab('pools');
              router.push('/app?tab=pools');
            }}
          />
        );
      case 'monitor':
        return (
          <PositionMonitor 
            onBack={() => {
              setActiveTab('pools');
              router.push('/app?tab=pools');
            }}
          />
        );
      default:
        return <PoolSelector onPoolSelect={handlePoolSelect} />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900">
      {/* Header */}
      <header className="border-b border-tangerine-primary/30 glass-effect sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center space-x-3">
                <Image 
                  src="/tangerine-logo.svg" 
                  alt="Tangerine.trading" 
                  width={32} 
                  height={32}
                  className="w-8 h-8 animate-glow"
                />
                <span className="text-xl font-bold text-white gradient-text">Tangerine.trading</span>
              </Link>
              
              {/* Tab Navigation */}
              <nav className="hidden md:flex space-x-1">
                <Button
                  variant={activeTab === 'pools' ? 'default' : 'ghost'}
                  onClick={() => {
                    setActiveTab('pools');
                    router.push('/app?tab=pools');
                  }}
                  className={activeTab === 'pools' 
                    ? "bg-tangerine-primary text-white hover:bg-tangerine-dark neon-border" 
                    : "text-white hover:text-tangerine-primary hover:bg-tangerine-primary/10 glass-effect"
                  }
                >
                  Select Pool
                </Button>
                <Button
                  variant={activeTab === 'strategy' ? 'default' : 'ghost'}
                  onClick={() => {
                    setActiveTab('strategy');
                    router.push('/app?tab=strategy');
                  }}
                  disabled={!selectedPool}
                  className={activeTab === 'strategy' 
                    ? "bg-tangerine-primary text-white hover:bg-tangerine-dark neon-border" 
                    : "text-white hover:text-tangerine-primary hover:bg-tangerine-primary/10 glass-effect"
                  }
                >
                  Configure Strategy
                </Button>
                <Button
                  variant={activeTab === 'monitor' ? 'default' : 'ghost'}
                  onClick={() => {
                    setActiveTab('monitor');
                    router.push('/app?tab=monitor');
                  }}
                  className={activeTab === 'monitor' 
                    ? "bg-tangerine-primary text-white hover:bg-tangerine-dark neon-border" 
                    : "text-white hover:text-tangerine-primary hover:bg-tangerine-primary/10 glass-effect"
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
                  <SelectTrigger className="w-40 glass-effect border-tangerine-primary/30 text-white">
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
              <Badge variant="secondary" className="hidden sm:inline-flex glass-effect text-white border-tangerine-primary/30">
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





