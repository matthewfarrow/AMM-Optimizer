'use client';

import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useAccount } from 'wagmi';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, TrendingUp, Shield, Zap } from 'lucide-react';
import Link from 'next/link';

export default function LandingPage() {
  const { isConnected, address } = useAccount();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-800">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-500 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">AMM Optimizer</span>
          </div>
          <ConnectButton />
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <Badge variant="destructive" className="mb-4">
            <AlertTriangle className="w-4 h-4 mr-1" />
            BETA - Use test funds only
          </Badge>
          
          <h1 className="text-5xl font-bold text-white mb-6">
            Automated Uniswap V3
            <br />
            <span className="bg-gradient-to-r from-orange-500 to-red-500 bg-clip-text text-transparent">
              Liquidity Management
            </span>
          </h1>
          
          <p className="text-xl text-slate-300 mb-8 max-w-3xl mx-auto">
            Optimize your Uniswap V3 positions with automated rebalancing, 
            volatility analysis, and smart risk management on Base Network.
          </p>

          {isConnected ? (
            <div className="space-y-4">
              <p className="text-green-400 font-medium">
                ✅ Wallet Connected: {address?.slice(0, 6)}...{address?.slice(-4)}
              </p>
              <Link href="/app">
                <Button size="lg" className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600">
                  Launch App
                </Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-slate-400">Connect your wallet to get started</p>
              <ConnectButton />
            </div>
          )}
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <Zap className="w-8 h-8 text-orange-500 mb-2" />
              <CardTitle className="text-white">Automated Rebalancing</CardTitle>
              <CardDescription className="text-slate-300">
                Positions automatically rebalance when price moves out of range, 
                maximizing your fee earnings.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <TrendingUp className="w-8 h-8 text-orange-500 mb-2" />
              <CardTitle className="text-white">Smart Analytics</CardTitle>
              <CardDescription className="text-slate-300">
                Advanced volatility analysis and liquidation probability 
                calculations to optimize your strategy.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <Shield className="w-8 h-8 text-orange-500 mb-2" />
              <CardTitle className="text-white">Risk Management</CardTitle>
              <CardDescription className="text-slate-300">
                Built-in risk controls and profitability checks ensure 
                your positions remain profitable.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Beta Warning */}
        <Card className="bg-red-900/20 border-red-800 mb-8">
          <CardHeader>
            <CardTitle className="text-red-400 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2" />
              Beta Testing Notice
            </CardTitle>
            <CardDescription className="text-red-300">
              This application is in beta testing phase. Please use only test funds 
              that you are willing to lose. The application is largely untested, 
              unaudited, and is an MVP for a hackathon. Use extreme caution.
            </CardDescription>
          </CardHeader>
        </Card>

        {/* How it Works */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white mb-8">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="space-y-4">
              <div className="w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center mx-auto">
                <span className="text-white font-bold">1</span>
              </div>
              <h3 className="text-xl font-semibold text-white">Select Pool</h3>
              <p className="text-slate-300">
                Choose from available Uniswap V3 pools with real-time TVL, APR, and volume data.
              </p>
            </div>
            
            <div className="space-y-4">
              <div className="w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center mx-auto">
                <span className="text-white font-bold">2</span>
              </div>
              <h3 className="text-xl font-semibold text-white">Configure Strategy</h3>
              <p className="text-slate-300">
                Set your tick range, check frequency, and analyze volatility to optimize your position.
              </p>
            </div>
            
            <div className="space-y-4">
              <div className="w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center mx-auto">
                <span className="text-white font-bold">3</span>
              </div>
              <h3 className="text-xl font-semibold text-white">Deploy & Monitor</h3>
              <p className="text-slate-300">
                Deploy your position and let our system automatically monitor and rebalance as needed.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 mt-16">
        <div className="container mx-auto px-4 py-8 text-center text-slate-400">
          <p>&copy; 2024 AMM Liquidity Optimizer. Built for Base Hackathon.</p>
        </div>
      </footer>
    </div>
  );
}