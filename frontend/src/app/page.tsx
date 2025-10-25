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
  
  // Force Vercel deployment - UI update

  // Note: Removed automatic redirect to allow users to stay on home page

  return (
    <div className="min-h-screen bg-tangerine-black cyber-grid relative overflow-hidden">
      {/* Sophisticated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-tangerine-black via-tangerine-gray to-tangerine-black opacity-95"></div>
      
      {/* Elegant Data Streams */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-tangerine-primary to-transparent animate-pulse opacity-60"></div>
        <div className="absolute top-1/2 right-0 w-px h-full bg-gradient-to-b from-transparent via-tangerine-blue to-transparent animate-pulse opacity-60"></div>
        <div className="absolute bottom-1/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-tangerine-accent to-transparent animate-pulse opacity-60"></div>
        <div className="absolute top-1/3 left-1/4 w-px h-1/3 bg-gradient-to-b from-transparent via-tangerine-primary to-transparent animate-pulse opacity-40"></div>
        <div className="absolute bottom-1/3 right-1/4 w-px h-1/3 bg-gradient-to-b from-transparent via-tangerine-blue to-transparent animate-pulse opacity-40"></div>
      </div>
      
      {/* Header */}
      <header className="relative z-10 border-b border-tangerine-primary/20 glass-effect">
        <div className="container mx-auto px-4 py-6 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-gradient-to-br from-tangerine-primary to-tangerine-blue rounded-xl animate-glow flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-lg">T</span>
            </div>
            <span className="text-2xl font-bold text-white gradient-text">Tangerine.trading</span>
          </div>
          <ConnectButton />
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16 relative z-10">
        <div className="text-center mb-16">
          <Badge className="mb-6 bg-tangerine-primary/20 text-tangerine-primary border-tangerine-primary/30 animate-pulse px-4 py-2">
            <Sparkles className="w-4 h-4 mr-2" />
            SOPHISTICATED DEFI PLATFORM
          </Badge>
          
          <h1 className="text-6xl font-black text-white mb-8 animate-fade-in leading-tight">
            MAXIMIZE
            <br />
            <span className="gradient-text animate-glow">
              LIQUIDITY YIELDS
            </span>
          </h1>
          
          <p className="text-xl text-tangerine-cream mb-10 max-w-4xl mx-auto font-light leading-relaxed">
            <span className="orange-accent font-semibold">Professional-grade AMM optimization</span> for Uniswap V3 on Base Network. 
            <span className="blue-accent font-semibold">Intelligent rebalancing</span> powered by 
            <span className="orange-accent font-semibold"> advanced algorithms</span> and 
            <span className="blue-accent font-semibold"> real-time market analysis</span>.
          </p>

          {isConnected ? (
            <div className="space-y-8">
              <div className="inline-flex items-center px-6 py-3 bg-tangerine-green/20 border border-tangerine-green/30 rounded-full">
                <div className="w-3 h-3 bg-tangerine-green rounded-full animate-pulse mr-3"></div>
                <span className="text-tangerine-green font-semibold text-lg">
                  WALLET CONNECTED: {address?.slice(0, 6)}...{address?.slice(-4)}
                </span>
              </div>
              <Link href="/app?tab=pools">
                <Button size="lg" className="cyber-button text-white font-bold px-10 py-5 text-xl rounded-xl">
                  <Zap className="w-6 h-6 mr-3" />
                  LAUNCH TRADING PLATFORM
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
        <div className="grid md:grid-cols-3 gap-8 mb-20">
          <Card className="sophisticated-card data-stream">
            <CardHeader className="p-8">
              <div className="w-20 h-20 bg-gradient-to-br from-tangerine-primary to-tangerine-blue rounded-2xl flex items-center justify-center mb-6 shadow-lg animate-glow">
                <Zap className="w-10 h-10 text-white" />
              </div>
              <CardTitle className="text-white text-2xl font-bold mb-4">⚡ AI-POWERED REBALANCING</CardTitle>
              <CardDescription className="text-tangerine-cream text-lg leading-relaxed">
                <span className="orange-accent font-semibold">Advanced ML algorithms</span> automatically rebalance when price moves out of range, 
                maximizing your fee earnings with <span className="blue-accent font-semibold">intelligent optimization</span>.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="sophisticated-card data-stream">
            <CardHeader className="p-8">
              <div className="w-20 h-20 bg-gradient-to-br from-tangerine-blue to-tangerine-primary rounded-2xl flex items-center justify-center mb-6 shadow-lg animate-glow">
                <BarChart3 className="w-10 h-10 text-white" />
              </div>
              <CardTitle className="text-white text-2xl font-bold mb-4">📊 SMART LIQUIDITY SEGMENTATION</CardTitle>
              <CardDescription className="text-tangerine-cream text-lg leading-relaxed">
                <span className="blue-accent font-semibold">Real-time volatility analysis</span> and predictive modeling 
                to optimize your liquidity distribution across <span className="orange-accent font-semibold">multiple ranges</span>.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="sophisticated-card data-stream">
            <CardHeader className="p-8">
              <div className="w-20 h-20 bg-gradient-to-br from-tangerine-accent to-tangerine-blue rounded-2xl flex items-center justify-center mb-6 shadow-lg animate-glow">
                <Target className="w-10 h-10 text-white" />
              </div>
              <CardTitle className="text-white text-2xl font-bold mb-4">🎯 RISK-OPTIMIZED STRATEGIES</CardTitle>
              <CardDescription className="text-tangerine-cream text-lg leading-relaxed">
                Built-in <span className="orange-accent font-semibold">risk controls</span> and profitability algorithms ensure 
                your positions remain optimized and profitable in <span className="blue-accent font-semibold">all market conditions</span>.
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
          <h2 className="text-5xl font-black text-white mb-16 gradient-text animate-glow">HOW IT WORKS</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-10">
            <div className="space-y-8 hover:scale-105 transition-transform duration-300">
              <div className="w-24 h-24 bg-gradient-to-br from-tangerine-primary to-tangerine-blue rounded-3xl flex items-center justify-center mx-auto shadow-lg animate-glow">
                <span className="text-white font-black text-3xl">1</span>
              </div>
              <h3 className="text-2xl font-bold text-white">CONNECT WALLET</h3>
              <p className="text-tangerine-cream text-lg leading-relaxed">
                Connect your wallet to access the most <span className="orange-accent font-semibold">advanced liquidity pools</span> on Base Network.
              </p>
            </div>
            
            <div className="space-y-8 hover:scale-105 transition-transform duration-300">
              <div className="w-24 h-24 bg-gradient-to-br from-tangerine-blue to-tangerine-primary rounded-3xl flex items-center justify-center mx-auto shadow-lg animate-glow">
                <span className="text-white font-black text-3xl">2</span>
              </div>
              <h3 className="text-2xl font-bold text-white">SELECT POOL</h3>
              <p className="text-tangerine-cream text-lg leading-relaxed">
                Choose from available Uniswap V3 pools with <span className="blue-accent font-semibold">real-time TVL, APR, and volume data</span>.
              </p>
            </div>
            
            <div className="space-y-8 hover:scale-105 transition-transform duration-300">
              <div className="w-24 h-24 bg-gradient-to-br from-tangerine-accent to-tangerine-blue rounded-3xl flex items-center justify-center mx-auto shadow-lg animate-glow">
                <span className="text-white font-black text-3xl">3</span>
              </div>
              <h3 className="text-2xl font-bold text-white">CONFIGURE STRATEGY</h3>
              <p className="text-tangerine-cream text-lg leading-relaxed">
                Set your parameters and let <span className="orange-accent font-semibold">AI analyze volatility</span> to optimize your position ranges.
              </p>
            </div>
            
            <div className="space-y-8 hover:scale-105 transition-transform duration-300">
              <div className="w-24 h-24 bg-gradient-to-br from-tangerine-blue to-tangerine-accent rounded-3xl flex items-center justify-center mx-auto shadow-lg animate-glow">
                <span className="text-white font-black text-3xl">4</span>
              </div>
              <h3 className="text-2xl font-bold text-white">DEPLOY & MONITOR</h3>
              <p className="text-tangerine-cream text-lg leading-relaxed">
                Deploy your position and let our <span className="blue-accent font-semibold">AI system automatically monitor and rebalance</span> as needed.
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