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
    <div className="min-h-screen bg-black cyber-grid relative overflow-hidden">
      {/* Cyber Grid Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-black via-gray-900 to-black opacity-90"></div>
      
      {/* Animated Data Streams */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-orange-500 to-transparent animate-pulse"></div>
        <div className="absolute top-1/2 right-0 w-px h-full bg-gradient-to-b from-transparent via-orange-500 to-transparent animate-pulse"></div>
        <div className="absolute bottom-1/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-orange-500 to-transparent animate-pulse"></div>
      </div>
      
      {/* Header */}
      <header className="relative z-10 border-b border-orange-500/30 glass-effect">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg animate-glow flex items-center justify-center">
              <span className="text-white font-bold text-sm">T</span>
            </div>
            <span className="text-xl font-bold text-white gradient-text">Tangerine.trading</span>
          </div>
          <ConnectButton />
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16 relative z-10">
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-orange-500/20 text-orange-400 border-orange-500/30 animate-pulse">
            <Sparkles className="w-3 h-3 mr-1" />
            CUTTING EDGE DEFI
          </Badge>
          
          <h1 className="text-7xl font-black text-white mb-6 animate-fade-in leading-tight">
            SQUEEZE MAXIMUM
            <br />
            <span className="gradient-text animate-glow">
              YIELDS
            </span>
          </h1>
          
          <p className="text-2xl text-gray-300 mb-8 max-w-3xl mx-auto font-light">
            <span className="text-orange-400 font-semibold">Next-generation AMM optimization</span> for Uniswap V3 on Base Network. 
            <span className="text-orange-400 font-semibold">Automated rebalancing</span> meets 
            <span className="text-orange-400 font-semibold"> cutting-edge algorithms</span>.
          </p>

          {isConnected ? (
            <div className="space-y-6">
              <div className="inline-flex items-center px-4 py-2 bg-green-500/20 border border-green-500/30 rounded-full">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse mr-2"></div>
                <span className="text-green-400 font-medium">
                  WALLET CONNECTED: {address?.slice(0, 6)}...{address?.slice(-4)}
                </span>
              </div>
              <Link href="/app?tab=pools">
                <Button size="lg" className="cyber-button text-black font-bold px-8 py-4 text-xl">
                  <Zap className="w-6 h-6 mr-3" />
                  LAUNCH TRADING SUITE
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
          <Card className="glass-effect border-orange-500/30 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 hover:border-orange-500/60 neon-border data-stream">
            <CardHeader>
              <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl flex items-center justify-center mb-4 shadow-lg animate-glow">
                <Zap className="w-8 h-8 text-white" />
              </div>
              <CardTitle className="text-white text-xl font-bold">⚡ AI-POWERED REBALANCING</CardTitle>
              <CardDescription className="text-gray-300 text-base">
                <span className="text-orange-400 font-semibold">Advanced ML algorithms</span> automatically rebalance when price moves out of range, 
                maximizing your fee earnings with <span className="text-orange-400 font-semibold">intelligent optimization</span>.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="glass-effect border-orange-500/30 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 hover:border-orange-500/60 neon-border data-stream">
            <CardHeader>
              <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl flex items-center justify-center mb-4 shadow-lg animate-glow">
                <BarChart3 className="w-8 h-8 text-white" />
              </div>
              <CardTitle className="text-white text-xl font-bold">📊 SMART LIQUIDITY SEGMENTATION</CardTitle>
              <CardDescription className="text-gray-300 text-base">
                <span className="text-orange-400 font-semibold">Real-time volatility analysis</span> and predictive modeling 
                to optimize your liquidity distribution across <span className="text-orange-400 font-semibold">multiple ranges</span>.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="glass-effect border-orange-500/30 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 hover:border-orange-500/60 neon-border data-stream">
            <CardHeader>
              <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl flex items-center justify-center mb-4 shadow-lg animate-glow">
                <Target className="w-8 h-8 text-white" />
              </div>
              <CardTitle className="text-white text-xl font-bold">🎯 RISK-OPTIMIZED STRATEGIES</CardTitle>
              <CardDescription className="text-gray-300 text-base">
                Built-in <span className="text-orange-400 font-semibold">risk controls</span> and profitability algorithms ensure 
                your positions remain optimized and profitable in <span className="text-orange-400 font-semibold">all market conditions</span>.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Beta Warning */}
        <Card className="glass-effect border-red-500/30 mb-8 shadow-lg neon-border">
          <CardHeader>
            <CardTitle className="text-red-400 flex items-center text-xl font-bold">
              <AlertTriangle className="w-6 h-6 mr-3 animate-pulse" />
              ⚠️ BETA TESTING PHASE ⚠️
            </CardTitle>
            <CardDescription className="text-gray-300 text-lg">
              <span className="text-red-400 font-semibold">WARNING:</span> This application is in beta testing phase. 
              Please use only <span className="text-red-400 font-semibold">test funds</span> that you are willing to lose. 
              The application is largely untested, unaudited, and is an MVP for a hackathon. 
              <span className="text-red-400 font-semibold">Use extreme caution.</span>
            </CardDescription>
          </CardHeader>
        </Card>

        {/* How it Works */}
        <div className="text-center">
          <h2 className="text-5xl font-black text-white mb-12 gradient-text animate-glow">HOW IT WORKS</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="space-y-6 hover:scale-105 transition-transform duration-300">
              <div className="w-20 h-20 bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl flex items-center justify-center mx-auto shadow-lg animate-glow">
                <span className="text-white font-black text-2xl">1</span>
              </div>
              <h3 className="text-2xl font-bold text-white">CONNECT WALLET</h3>
              <p className="text-gray-300 text-lg">
                Connect your wallet to access the most <span className="text-orange-400 font-semibold">advanced liquidity pools</span> on Base Network.
              </p>
            </div>
            
            <div className="space-y-6 hover:scale-105 transition-transform duration-300">
              <div className="w-20 h-20 bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl flex items-center justify-center mx-auto shadow-lg animate-glow">
                <span className="text-white font-black text-2xl">2</span>
              </div>
              <h3 className="text-2xl font-bold text-white">SELECT POOL</h3>
              <p className="text-gray-300 text-lg">
                Choose from available Uniswap V3 pools with <span className="text-orange-400 font-semibold">real-time TVL, APR, and volume data</span>.
              </p>
            </div>
            
            <div className="space-y-6 hover:scale-105 transition-transform duration-300">
              <div className="w-20 h-20 bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl flex items-center justify-center mx-auto shadow-lg animate-glow">
                <span className="text-white font-black text-2xl">3</span>
              </div>
              <h3 className="text-2xl font-bold text-white">CONFIGURE STRATEGY</h3>
              <p className="text-gray-300 text-lg">
                Set your parameters and let <span className="text-orange-400 font-semibold">AI analyze volatility</span> to optimize your position ranges.
              </p>
            </div>
            
            <div className="space-y-6 hover:scale-105 transition-transform duration-300">
              <div className="w-20 h-20 bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl flex items-center justify-center mx-auto shadow-lg animate-glow">
                <span className="text-white font-black text-2xl">4</span>
              </div>
              <h3 className="text-2xl font-bold text-white">DEPLOY & MONITOR</h3>
              <p className="text-gray-300 text-lg">
                Deploy your position and let our <span className="text-orange-400 font-semibold">AI system automatically monitor and rebalance</span> as needed.
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