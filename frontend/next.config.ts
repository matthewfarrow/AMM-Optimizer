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
  // Explicitly configure webpack to resolve path aliases
  // This ensures path aliases work in Vercel's build environment
  webpack: (config) => {
    // Use process.cwd() which will be the frontend directory when Vercel runs npm run build
    // This works because vercel.json points to frontend/package.json, so build runs from frontend/
    const rootDir = process.cwd();
    const srcPath = path.resolve(rootDir, 'src');
    
    // Set up path aliases - this must match tsconfig.json paths
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': srcPath,
    };
    
    return config;
  },
};

export default nextConfig;
