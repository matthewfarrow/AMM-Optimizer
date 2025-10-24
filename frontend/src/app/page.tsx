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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900">
      {/* Header */}
      <header className="border-b border-tangerine-primary/30 glass-effect">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <Image
              src="/tangerine-logo.svg"
              alt="Tangerine.trading"
              width={32}
              height={32}
              className="w-8 h-8 animate-glow"
            />
            <span className="text-xl font-bold text-white gradient-text">Tangerine.trading</span>
          </div>
          <ConnectButton />
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-tangerine-primary/20 text-tangerine-primary border-tangerine-primary/50 neon-border">
            <Sparkles className="w-4 h-4 mr-1" />
            The Future of DeFi Trading
          </Badge>
          
          <h1 className="text-6xl font-bold text-white mb-6 animate-fade-in">
            Optimize Maximum
            <br />
            <span className="gradient-text animate-pulse">
              Yields
            </span>
          </h1>
          
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Tangerine.trading leverages advanced AI to optimize your concentrated liquidity positions on Uniswap V3 
            for Base Network. Experience the next generation of automated yield farming.
          </p>

          {isConnected ? (
            <div className="space-y-4">
              <p className="text-tangerine-green font-medium">
                ✅ Wallet Connected: {address?.slice(0, 6)}...{address?.slice(-4)}
              </p>
              <Link href="/app?tab=pools">
                <Button size="lg" className="bg-gradient-to-r from-tangerine-primary to-tangerine-purple hover:from-tangerine-dark hover:to-tangerine-primary text-white font-semibold neon-border animate-glow">
                  Launch App
                </Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-gray-400">Connect your wallet to get started</p>
              <ConnectButton />
            </div>
          )}
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <Card className="glass-effect border-tangerine-primary/30 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 hover:border-tangerine-primary/60 neon-border">
            <CardHeader>
              <div className="w-12 h-12 bg-gradient-to-r from-tangerine-primary to-tangerine-purple rounded-lg flex items-center justify-center mb-4 shadow-sm animate-glow">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <CardTitle className="text-white">⚡ AI-Powered Rebalancing</CardTitle>
              <CardDescription className="text-gray-300">
                Advanced machine learning algorithms automatically rebalance when price moves out of range, 
                maximizing your fee earnings with intelligent optimization.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="glass-effect border-tangerine-primary/30 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 hover:border-tangerine-primary/60 neon-border">
            <CardHeader>
              <div className="w-12 h-12 bg-gradient-to-r from-tangerine-primary to-tangerine-purple rounded-lg flex items-center justify-center mb-4 shadow-sm animate-glow">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <CardTitle className="text-white">📊 Smart Liquidity Segmentation</CardTitle>
              <CardDescription className="text-gray-300">
                Real-time volatility analysis and predictive modeling 
                to optimize your liquidity distribution across multiple ranges.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="glass-effect border-tangerine-primary/30 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 hover:border-tangerine-primary/60 neon-border">
            <CardHeader>
              <div className="w-12 h-12 bg-gradient-to-r from-tangerine-primary to-tangerine-purple rounded-lg flex items-center justify-center mb-4 shadow-sm animate-glow">
                <Target className="w-6 h-6 text-white" />
              </div>
              <CardTitle className="text-white">🎯 Risk-Optimized Strategies</CardTitle>
              <CardDescription className="text-gray-300">
                Built-in risk controls and profitability algorithms ensure 
                your positions remain optimized and profitable in all market conditions.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Beta Warning */}
        <Card className="glass-effect border-orange-500/30 mb-8 shadow-lg neon-border">
          <CardHeader>
            <CardTitle className="text-orange-400 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2" />
              Beta Testing Phase
            </CardTitle>
            <CardDescription className="text-gray-300">
              This application is in beta testing phase. Please use only test funds 
              that you are willing to lose. The application is largely untested, 
              unaudited, and is an MVP for a hackathon. Use extreme caution.
            </CardDescription>
          </CardHeader>
        </Card>

        {/* How it Works */}
        <div className="text-center">
          <h2 className="text-4xl font-bold text-white mb-8 gradient-text">How It Works</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="space-y-4 hover:scale-105 transition-transform duration-300">
              <div className="w-16 h-16 bg-gradient-to-r from-tangerine-primary to-tangerine-purple rounded-full flex items-center justify-center mx-auto shadow-lg animate-glow">
                <span className="text-white font-bold text-xl">1</span>
              </div>
              <h3 className="text-xl font-semibold text-white">Connect Wallet</h3>
              <p className="text-gray-300">
                Connect your wallet to access the most advanced liquidity pools on Base Network.
              </p>
            </div>
            
            <div className="space-y-4 hover:scale-105 transition-transform duration-300">
              <div className="w-16 h-16 bg-gradient-to-r from-tangerine-primary to-tangerine-purple rounded-full flex items-center justify-center mx-auto shadow-lg animate-glow">
                <span className="text-white font-bold text-xl">2</span>
              </div>
              <h3 className="text-xl font-semibold text-white">Select Pool</h3>
              <p className="text-gray-300">
                Choose from available Uniswap V3 pools with real-time TVL, APR, and volume data.
              </p>
            </div>
            
            <div className="space-y-4 hover:scale-105 transition-transform duration-300">
              <div className="w-16 h-16 bg-gradient-to-r from-tangerine-primary to-tangerine-purple rounded-full flex items-center justify-center mx-auto shadow-lg animate-glow">
                <span className="text-white font-bold text-xl">3</span>
              </div>
              <h3 className="text-xl font-semibold text-white">Configure Strategy</h3>
              <p className="text-gray-300">
                Set your parameters and let AI analyze volatility to optimize your position ranges.
              </p>
            </div>
            
            <div className="space-y-4 hover:scale-105 transition-transform duration-300">
              <div className="w-16 h-16 bg-gradient-to-r from-tangerine-primary to-tangerine-purple rounded-full flex items-center justify-center mx-auto shadow-lg animate-glow">
                <span className="text-white font-bold text-xl">4</span>
              </div>
              <h3 className="text-xl font-semibold text-white">Deploy & Monitor</h3>
              <p className="text-gray-300">
                Deploy your position and let our AI system automatically monitor and rebalance as needed.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-tangerine-primary/30 mt-16 glass-effect">
        <div className="container mx-auto px-4 py-12">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <Image
                  src="/tangerine-logo.svg"
                  alt="Tangerine.trading"
                  width={24}
                  height={24}
                  className="w-6 h-6 animate-glow"
                />
                <span className="text-lg font-bold text-white gradient-text">Tangerine.trading</span>
              </div>
              <p className="text-gray-300 text-sm">
                The Future of DeFi Trading - AI-powered optimization for concentrated liquidity positions on Uniswap V3 for Base Network.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-4">Features</h4>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>• AI-Powered Rebalancing</li>
                <li>• Predictive Analytics</li>
                <li>• Risk Management</li>
                <li>• Real-time Monitoring</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-4">Network</h4>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>• Built on Base Network</li>
                <li>• Uniswap V3 Integration</li>
                <li>• Ethereum Compatible</li>
                <li>• Low Gas Fees</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-tangerine-primary/30 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Tangerine.trading - The Future of DeFi Trading. Built for Base Hackathon.</p>
            <p className="text-xs mt-2">⚠️ Beta Software - Use at your own risk</p>
          </div>
        </div>
      </footer>
    </div>
  );
}