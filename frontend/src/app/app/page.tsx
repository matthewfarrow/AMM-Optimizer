'use client';

import { useState, useEffect } from 'react';
import { useAccount } from 'wagmi';
import { useRouter, useSearchParams } from 'next/navigation';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import { PoolSelector } from '@/components/PoolSelector';
import { StrategyConfig } from '@/components/StrategyConfig';
import { PositionMonitor } from '@/components/PositionMonitor';
import { apiClient } from '@/lib/api';

type Tab = 'pools' | 'strategy' | 'monitor';

export default function AppPage() {
  const { isConnected, address } = useAccount();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [activeTab, setActiveTab] = useState<Tab>('pools');
  const [selectedPool, setSelectedPool] = useState<any>(null);
  const [isWhitelisted, setIsWhitelisted] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  // Check whitelist status on mount
  useEffect(() => {
    if (address) {
      checkWhitelistStatus();
    } else {
      setLoading(false);
    }
  }, [address]);

  const checkWhitelistStatus = async () => {
    try {
      const status = await apiClient.checkWhitelistStatus(address!);
      setIsWhitelisted(status.whitelisted);
    } catch (error) {
      console.error('Error checking whitelist status:', error);
      setIsWhitelisted(false);
    } finally {
      setLoading(false);
    }
  };

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

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-tangerine-cream via-orange-50 to-tangerine-cream flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-tangerine-primary mx-auto mb-4"></div>
          <p className="text-tangerine-black/70">Checking whitelist status...</p>
        </div>
      </div>
    );
  }

  // Show not whitelisted message
  if (!isWhitelisted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-tangerine-cream via-orange-50 to-tangerine-cream flex items-center justify-center">
        <Card className="w-full max-w-md bg-white/80 border-tangerine-primary/20">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-tangerine-accent">Access Restricted</CardTitle>
            <p className="text-tangerine-black/70">Your wallet is not whitelisted for beta testing</p>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <Badge className="w-full justify-center bg-tangerine-accent/10 text-tangerine-accent border-tangerine-accent/30">
              <AlertTriangle className="w-4 h-4 mr-1" />
              Beta Access Required
            </Badge>
            <p className="text-sm text-tangerine-black/60">
              This app is currently in beta testing. Please sign up for whitelist access.
            </p>
            <div className="space-y-2">
              <Button 
                onClick={() => window.open('https://forms.gle/your-beta-signup-form', '_blank')}
                className="w-full bg-tangerine-primary hover:bg-tangerine-dark text-white"
              >
                Sign Up for Beta Access
              </Button>
              <Link href="/">
                <Button variant="outline" className="w-full border-tangerine-primary text-tangerine-black hover:bg-tangerine-primary/10">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Home
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Get tab from URL params
  const tab = searchParams.get('tab') as Tab || 'pools';

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
    <div className="min-h-screen bg-gradient-to-br from-tangerine-cream via-orange-50 to-tangerine-cream">
      {/* Header */}
      <header className="border-b border-tangerine-primary/20 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center space-x-3">
                <Image 
                  src="/tangerine-logo.svg" 
                  alt="Tangerine.trading" 
                  width={32} 
                  height={32}
                  className="w-8 h-8"
                />
                <span className="text-xl font-bold text-tangerine-black">Tangerine.trading</span>
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
                    ? "bg-tangerine-primary text-white hover:bg-tangerine-dark" 
                    : "text-tangerine-black hover:text-tangerine-primary hover:bg-tangerine-primary/10"
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
                    ? "bg-tangerine-primary text-white hover:bg-tangerine-dark" 
                    : "text-tangerine-black hover:text-tangerine-primary hover:bg-tangerine-primary/10"
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
                    ? "bg-tangerine-primary text-white hover:bg-tangerine-dark" 
                    : "text-tangerine-black hover:text-tangerine-primary hover:bg-tangerine-primary/10"
                  }
                >
                  Deploy & Monitor
                </Button>
              </nav>
            </div>
            
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="hidden sm:inline-flex bg-tangerine-primary/10 text-tangerine-black border-tangerine-primary/20">
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





