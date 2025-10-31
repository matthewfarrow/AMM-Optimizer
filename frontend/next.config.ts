import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  /* config options here */
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Production optimizations
  output: 'standalone',
  // Environment variables for production
  env: {
    NEXT_PUBLIC_ALCHEMY_API_KEY: process.env.NEXT_PUBLIC_ALCHEMY_API_KEY,
    NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID: process.env.NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID,
    NEXT_PUBLIC_ALCHEMY_RPC_URL: process.env.NEXT_PUBLIC_ALCHEMY_RPC_URL,
  },
  // When using builds array in vercel.json, Vercel runs from repo root
  // But the build command runs from frontend/ directory
  // We need to resolve paths relative to where next.config.ts is located
  webpack: (config) => {
    // __dirname points to the frontend directory (where next.config.ts is)
    // But when Vercel uses builds array, it might run from root
    // So we need to detect: if src exists relative to cwd, use that, otherwise use __dirname
    let rootDir = process.cwd();
    
    // Check if we're in the repo root (src doesn't exist) vs frontend dir (src exists)
    const fs = require('fs');
    if (!fs.existsSync(path.join(rootDir, 'src'))) {
      // We're in repo root, need to go to frontend/
      rootDir = path.join(rootDir, 'frontend');
    }
    
    const srcPath = path.resolve(rootDir, 'src');
    
    // Ensure path alias is set
    config.resolve = config.resolve || {};
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': srcPath,
    };
    
    return config;
  },
};

export default nextConfig;
