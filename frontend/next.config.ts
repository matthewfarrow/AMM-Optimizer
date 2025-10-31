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
  // Next.js should automatically read path aliases from tsconfig.json/jsconfig.json
  // But we add explicit webpack config as fallback for Vercel builds
  webpack: (config) => {
    const rootDir = process.cwd();
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
