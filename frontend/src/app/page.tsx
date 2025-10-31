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
    <div className="min-h-screen bg-tangerine-black fruit-pattern">
      {/* Header */}
      <header className="border-b border-tangerine-border glass-effect">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 tangerine-gradient rounded-lg flex items-center justify-center citrus-glow">
              <span className="text-white font-bold text-sm">🍊</span>
            </div>
            <span className="text-xl font-semibold text-white">Tangerine.trading</span>
          </div>
          <ConnectButton />
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-6 py-20">
        <div className="text-center mb-20">
          <h1 className="text-6xl font-bold text-tangerine-text-secondary mb-6 leading-tight">
            <span className="tangerine-accent">Squeeze Maximum Yields</span>
            <br />
            <span className="gradient-text">from Your Liquidity</span>
          </h1>
          
          <p className="text-xl text-tangerine-text-secondary mb-12 max-w-3xl mx-auto leading-relaxed">
            Automated liquidity management for Uniswap V3 on Base Network with 
            <span className="tangerine-accent"> intelligent rebalancing</span> and 
            <span className="teal-accent"> real-time market analysis</span>.
          </p>

          {isConnected ? (
            <div className="space-y-8">
              <div className="inline-flex items-center px-6 py-3 bg-success-green/20 border border-success-green/30 rounded-full">
                <div className="w-3 h-3 bg-success-green rounded-full animate-pulse mr-3"></div>
                <span className="text-success-green font-medium">
                  WALLET CONNECTED: {address?.slice(0, 6)}...{address?.slice(-4)}
                </span>
              </div>
              <Link href="/app?tab=pools">
                <Button size="lg" className="cyber-button text-white font-semibold px-8 py-4 text-lg rounded-lg">
                  <Zap className="w-5 h-5 mr-3" />
                  Enter App
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
          <div className="organic-shape p-8 hover:citrus-glow transition-all duration-300">
            <div className="w-12 h-12 tangerine-gradient rounded-lg flex items-center justify-center mb-6">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-white text-xl font-semibold mb-4">Automated Position Management</h3>
            <p className="text-white leading-relaxed">
              Advanced strategies can be configured to automatically rebalance your position when price moves out of range, 
              maximizing your fee earnings with <span className="tangerine-accent">intelligent optimization</span>.
            </p>
          </div>

          <div className="organic-shape p-8 hover:citrus-glow transition-all duration-300">
            <div className="w-12 h-12 tangerine-gradient rounded-lg flex items-center justify-center mb-6">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-white text-xl font-semibold mb-4">Smart Liquidity Segmentation</h3>
            <p className="text-white leading-relaxed">
              Real-time volatility analysis and predictive modeling 
              to optimize your liquidity distribution across <span className="teal-accent">multiple ranges</span>.
            </p>
          </div>

          <div className="organic-shape p-8 hover:citrus-glow transition-all duration-300">
            <div className="w-12 h-12 tangerine-gradient rounded-lg flex items-center justify-center mb-6">
              <Target className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-white text-xl font-semibold mb-4">Risk-Optimized Strategies</h3>
            <p className="text-white leading-relaxed">
              Built-in risk controls and profitability algorithms ensure 
              your positions remain optimized and profitable in <span className="tangerine-accent">all market conditions</span>.
            </p>
          </div>
        </div>

        {/* Beta Warning */}
        <div className="bg-error-red/10 border border-error-red/30 rounded-lg p-6 mb-8">
          <div className="flex items-center mb-4">
            <AlertTriangle className="w-6 h-6 text-error-red mr-3" />
            <h3 className="text-error-red font-semibold text-lg">Beta Testing Phase</h3>
          </div>
          <p className="text-tangerine-text-secondary">
            <span className="text-error-red font-semibold">WARNING:</span> This application is in beta testing phase. 
            Please use only <span className="text-error-red font-semibold">test funds</span> that you are willing to lose. 
            The application is largely untested, unaudited, and is an MVP for a hackathon. 
            <span className="text-error-red font-semibold">Use extreme caution.</span> None / Not all features listed above are active or implemented yet, this website serves as a MVP.
          </p>
        </div>

        {/* How it Works */}
        <div className="text-center">
          <h2 className="text-4xl font-bold text-white mb-16"><span className="tangerine-accent">How it Works</span></h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="space-y-6">
              <div className="w-16 h-16 tangerine-gradient rounded-lg flex items-center justify-center mx-auto citrus-glow">
                <span className="text-white font-bold text-xl">1</span>
              </div>
              <h3 className="text-xl font-semibold text-white"><span className="tangerine-accent">Connect Wallet</span></h3>
              <p className="text-tangerine-text-secondary leading-relaxed">
                Connect your wallet to access the most <span className="tangerine-accent">advanced liquidity pools</span> on Base Network.
              </p>
            </div>
            
            <div className="space-y-6">
              <div className="w-16 h-16 tangerine-gradient rounded-lg flex items-center justify-center mx-auto citrus-glow">
                <span className="text-white font-bold text-xl">2</span>
              </div>
              <h3 className="text-xl font-semibold text-white"><span className="tangerine-accent">Select Pool</span></h3>
              <p className="text-tangerine-text-secondary leading-relaxed">
                Choose from available Uniswap V3 pools with <span className="teal-accent">real-time TVL, APR, and volume data</span>.
              </p>
            </div>
            
            <div className="space-y-6">
              <div className="w-16 h-16 tangerine-gradient rounded-lg flex items-center justify-center mx-auto citrus-glow">
                <span className="text-white font-bold text-xl">3</span>
              </div>
              <h3 className="text-xl font-semibold text-white"><span className="tangerine-accent">Configure Strategy</span></h3>
              <p className="text-tangerine-text-secondary leading-relaxed">
                Set your parameters and let <span className="tangerine-accent">AI analyze volatility</span> to optimize your position ranges.
              </p>
            </div>
            
            <div className="space-y-6">
              <div className="w-16 h-16 tangerine-gradient rounded-lg flex items-center justify-center mx-auto citrus-glow">
                <span className="text-white font-bold text-xl">4</span>
              </div>
              <h3 className="text-xl font-semibold text-white"><span className="tangerine-accent">Deploy & Monitor</span></h3>
              <p className="text-tangerine-text-secondary leading-relaxed">
                Deploy your position and let our <span className="teal-accent">AI system automatically monitor and rebalance</span> as needed.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-tangerine-border mt-16">
        <div className="container mx-auto px-6 py-12">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-6 h-6 tangerine-gradient rounded flex items-center justify-center">
                  <span className="text-white font-bold text-xs">🍊</span>
                </div>
                <span className="text-lg font-semibold text-white"><span className="tangerine-accent">Tangerine.trading</span></span>
              </div>
              <p className="text-tangerine-text-secondary text-sm">
                Modern citrus-powered DeFi optimization. Automated liquidity management for Uniswap V3 on Base Network.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-4"><span className="tangerine-accent">Features</span></h4>
              <ul className="space-y-2 text-sm text-tangerine-text-secondary">
                <li>• AI-Powered Rebalancing</li>
                <li>• Predictive Analytics</li>
                <li>• Risk Management</li>
                <li>• Real-time Monitoring</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-4"><span className="tangerine-accent">Network</span></h4>
              <ul className="space-y-2 text-sm text-tangerine-text-secondary">
                <li>• Built on Base Network</li>
                <li>• Uniswap V3 Integration</li>
                <li>• Ethereum Compatible</li>
                <li>• Low Gas Fees</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-tangerine-border pt-8 text-center text-tangerine-text-secondary">
            <p>&copy; 2025 Tangerine.trading</p>
            <p className="text-xs mt-2">⚠️ Beta version - Use at your own risk</p>
          </div>
        </div>
      </footer>
    </div>
  );
}