'use client';

import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useAccount } from 'wagmi';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, Zap, BarChart3, Target, Sparkles } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';

export default function LandingPage() {
  const { isConnected, address } = useAccount();
  const router = useRouter();

  // Redirect connected users to the app
  useEffect(() => {
    if (isConnected) {
      router.push('/app?tab=pools');
    }
  }, [isConnected, router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-tangerine-cream via-orange-50 to-tangerine-cream">
      {/* Header */}
      <header className="border-b border-tangerine-primary/20 bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <Image
              src="/tangerine-logo.svg"
              alt="Tangerine.trading"
              width={32}
              height={32}
              className="w-8 h-8"
            />
            <span className="text-xl font-bold text-tangerine-black">Tangerine.trading</span>
          </div>
          <ConnectButton />
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-tangerine-primary text-white border-tangerine-primary">
            <Sparkles className="w-4 h-4 mr-1" />
            The Citrus Swap Revolution
          </Badge>
          
          <h1 className="text-6xl font-bold text-tangerine-black mb-6">
            Squeeze Maximum
            <br />
            <span className="bg-gradient-to-r from-tangerine-primary to-tangerine-accent bg-clip-text text-transparent">
              Yields
            </span>
          </h1>
          
          <p className="text-xl text-tangerine-black/80 mb-8 max-w-3xl mx-auto">
            Tangerine.trading optimizes your concentrated liquidity positions on Uniswap V3 
            for Base Network. Peel back inefficiencies and segment your liquidity like tangerine wedges.
          </p>

          {isConnected ? (
            <div className="space-y-4">
              <p className="text-tangerine-green font-medium">
                ✅ Wallet Connected: {address?.slice(0, 6)}...{address?.slice(-4)}
              </p>
              <Link href="/app?tab=pools">
                <Button size="lg" className="bg-gradient-to-r from-tangerine-primary to-tangerine-accent hover:from-tangerine-dark hover:to-tangerine-primary text-white font-semibold">
                  Launch App
                </Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-tangerine-black/60">Connect your wallet to get started</p>
              <ConnectButton />
            </div>
          )}
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <Card className="bg-white/80 border-tangerine-primary/20 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader>
              <div className="w-12 h-12 bg-gradient-to-r from-tangerine-primary to-tangerine-accent rounded-lg flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <CardTitle className="text-tangerine-black">🍊 Peel Back Inefficiencies</CardTitle>
              <CardDescription className="text-tangerine-black/70">
                Automated rebalancing when price moves out of range, 
                maximizing your fee earnings with concentrated citrus power.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-white/80 border-tangerine-primary/20 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader>
              <div className="w-12 h-12 bg-gradient-to-r from-tangerine-primary to-tangerine-accent rounded-lg flex items-center justify-center mb-4">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <CardTitle className="text-tangerine-black">📊 Segment Your Liquidity</CardTitle>
              <CardDescription className="text-tangerine-black/70">
                Advanced volatility analysis and out-of-range probability 
                calculations to optimize your tangerine wedges.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-white/80 border-tangerine-primary/20 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader>
              <div className="w-12 h-12 bg-gradient-to-r from-tangerine-primary to-tangerine-accent rounded-lg flex items-center justify-center mb-4">
                <Target className="w-6 h-6 text-white" />
              </div>
              <CardTitle className="text-tangerine-black">⚡ Zest for Optimization</CardTitle>
              <CardDescription className="text-tangerine-black/70">
                Built-in risk controls and profitability checks ensure 
                your positions remain juicy and profitable.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Beta Warning */}
        <Card className="bg-tangerine-accent/10 border-tangerine-accent/30 mb-8">
          <CardHeader>
            <CardTitle className="text-tangerine-accent flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2" />
              Fresh from the Grove - Beta Testing
            </CardTitle>
            <CardDescription className="text-tangerine-black/70">
              This application is freshly squeezed and in beta testing phase. Please use only test funds 
              that you are willing to lose. The application is largely untested, 
              unaudited, and is an MVP for a hackathon. Use extreme caution.
            </CardDescription>
          </CardHeader>
        </Card>

        {/* How it Works */}
        <div className="text-center">
          <h2 className="text-4xl font-bold text-tangerine-black mb-8">How It Works</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="w-16 h-16 bg-gradient-to-r from-tangerine-primary to-tangerine-accent rounded-full flex items-center justify-center mx-auto shadow-lg">
                <span className="text-white font-bold text-xl">1</span>
              </div>
              <h3 className="text-xl font-semibold text-tangerine-black">Connect Wallet</h3>
              <p className="text-tangerine-black/70">
                Connect your wallet to access the juiciest liquidity pools on Base Network.
              </p>
            </div>
            
            <div className="space-y-4">
              <div className="w-16 h-16 bg-gradient-to-r from-tangerine-primary to-tangerine-accent rounded-full flex items-center justify-center mx-auto shadow-lg">
                <span className="text-white font-bold text-xl">2</span>
              </div>
              <h3 className="text-xl font-semibold text-tangerine-black">Select Pool</h3>
              <p className="text-tangerine-black/70">
                Choose from available Uniswap V3 pools with real-time TVL, APR, and volume data.
              </p>
            </div>
            
            <div className="space-y-4">
              <div className="w-16 h-16 bg-gradient-to-r from-tangerine-primary to-tangerine-accent rounded-full flex items-center justify-center mx-auto shadow-lg">
                <span className="text-white font-bold text-xl">3</span>
              </div>
              <h3 className="text-xl font-semibold text-tangerine-black">Set Range</h3>
              <p className="text-tangerine-black/70">
                Configure your tick range and analyze volatility to optimize your tangerine wedges.
              </p>
            </div>
            
            <div className="space-y-4">
              <div className="w-16 h-16 bg-gradient-to-r from-tangerine-primary to-tangerine-accent rounded-full flex items-center justify-center mx-auto shadow-lg">
                <span className="text-white font-bold text-xl">4</span>
              </div>
              <h3 className="text-xl font-semibold text-tangerine-black">Squeeze Profits</h3>
              <p className="text-tangerine-black/70">
                Deploy your position and let our system automatically monitor and rebalance as needed.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-tangerine-primary/20 mt-16 bg-white/50">
        <div className="container mx-auto px-4 py-8 text-center text-tangerine-black/60">
          <p>&copy; 2024 Tangerine.trading - The Citrus Swap Revolution. Built for Base Hackathon.</p>
        </div>
      </footer>
    </div>
  );
}