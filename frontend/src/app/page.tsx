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
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="border-b border-slate-800">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">A</span>
            </div>
            <span className="text-xl font-semibold text-white">Arrakis Finance</span>
          </div>
          <ConnectButton />
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-6 py-20">
        <div className="text-center mb-20">
          <h1 className="text-5xl font-bold text-white mb-6 leading-tight">
            We Make Onchain Markets
            <br />
            <span className="text-blue-400">Liquid and Efficient</span>
          </h1>
          
          <p className="text-xl text-slate-300 mb-12 max-w-3xl mx-auto leading-relaxed">
            Onchain market making for token issuers. Automated liquidity management 
            for Uniswap V3 on Base Network with intelligent rebalancing and 
            real-time market analysis.
          </p>

          {isConnected ? (
            <div className="space-y-8">
              <div className="inline-flex items-center px-6 py-3 bg-green-500/20 border border-green-500/30 rounded-full">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse mr-3"></div>
                <span className="text-green-400 font-medium">
                  WALLET CONNECTED: {address?.slice(0, 6)}...{address?.slice(-4)}
                </span>
              </div>
              <Link href="/app?tab=pools">
                <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-4 text-lg rounded-lg transition-colors">
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
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-6">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-white text-xl font-semibold mb-4">AI-Powered Rebalancing</h3>
            <p className="text-slate-300 leading-relaxed">
              Advanced ML algorithms automatically rebalance when price moves out of range, 
              maximizing your fee earnings with intelligent optimization.
            </p>
          </div>

          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-6">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-white text-xl font-semibold mb-4">Smart Liquidity Segmentation</h3>
            <p className="text-slate-300 leading-relaxed">
              Real-time volatility analysis and predictive modeling 
              to optimize your liquidity distribution across multiple ranges.
            </p>
          </div>

          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-6">
              <Target className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-white text-xl font-semibold mb-4">Risk-Optimized Strategies</h3>
            <p className="text-slate-300 leading-relaxed">
              Built-in risk controls and profitability algorithms ensure 
              your positions remain optimized and profitable in all market conditions.
            </p>
          </div>
        </div>

        {/* Beta Warning */}
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6 mb-8">
          <div className="flex items-center mb-4">
            <AlertTriangle className="w-6 h-6 text-red-400 mr-3" />
            <h3 className="text-red-400 font-semibold text-lg">Beta Testing Phase</h3>
          </div>
          <p className="text-slate-300">
            <span className="text-red-400 font-semibold">WARNING:</span> This application is in beta testing phase. 
            Please use only <span className="text-red-400 font-semibold">test funds</span> that you are willing to lose. 
            The application is largely untested, unaudited, and is an MVP for a hackathon. 
            <span className="text-red-400 font-semibold">Use extreme caution.</span>
          </p>
        </div>

        {/* How it Works */}
        <div className="text-center">
          <h2 className="text-4xl font-bold text-white mb-16">How it Works</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="space-y-6">
              <div className="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center mx-auto">
                <span className="text-white font-bold text-xl">1</span>
              </div>
              <h3 className="text-xl font-semibold text-white">Connect Wallet</h3>
              <p className="text-slate-300 leading-relaxed">
                Connect your wallet to access the most advanced liquidity pools on Base Network.
              </p>
            </div>
            
            <div className="space-y-6">
              <div className="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center mx-auto">
                <span className="text-white font-bold text-xl">2</span>
              </div>
              <h3 className="text-xl font-semibold text-white">Select Pool</h3>
              <p className="text-slate-300 leading-relaxed">
                Choose from available Uniswap V3 pools with real-time TVL, APR, and volume data.
              </p>
            </div>
            
            <div className="space-y-6">
              <div className="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center mx-auto">
                <span className="text-white font-bold text-xl">3</span>
              </div>
              <h3 className="text-xl font-semibold text-white">Configure Strategy</h3>
              <p className="text-slate-300 leading-relaxed">
                Set your parameters and let AI analyze volatility to optimize your position ranges.
              </p>
            </div>
            
            <div className="space-y-6">
              <div className="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center mx-auto">
                <span className="text-white font-bold text-xl">4</span>
              </div>
              <h3 className="text-xl font-semibold text-white">Deploy & Monitor</h3>
              <p className="text-slate-300 leading-relaxed">
                Deploy your position and let our AI system automatically monitor and rebalance as needed.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 mt-16">
        <div className="container mx-auto px-6 py-12">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center">
                  <span className="text-white font-bold text-xs">A</span>
                </div>
                <span className="text-lg font-semibold text-white">Arrakis Finance</span>
              </div>
              <p className="text-slate-300 text-sm">
                Onchain market making for token issuers. Automated liquidity management for Uniswap V3 on Base Network.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-4">Features</h4>
              <ul className="space-y-2 text-sm text-slate-300">
                <li>• AI-Powered Rebalancing</li>
                <li>• Predictive Analytics</li>
                <li>• Risk Management</li>
                <li>• Real-time Monitoring</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-4">Network</h4>
              <ul className="space-y-2 text-sm text-slate-300">
                <li>• Built on Base Network</li>
                <li>• Uniswap V3 Integration</li>
                <li>• Ethereum Compatible</li>
                <li>• Low Gas Fees</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-slate-800 pt-8 text-center text-slate-400">
            <p>&copy; 2024 Arrakis Finance - Onchain Market Making. Built for Base Hackathon.</p>
            <p className="text-xs mt-2">⚠️ Beta Software - Use at your own risk</p>
          </div>
        </div>
      </footer>
    </div>
  );
}