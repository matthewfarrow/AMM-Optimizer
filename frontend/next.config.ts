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
    // When rootDirectory is set in vercel.json, the build runs from that directory
    // So __dirname in next.config.ts will be the frontend directory
    const configDir = __dirname;
    const srcPath = path.resolve(configDir, 'src');
    
    // Set up path aliases - this must match tsconfig.json paths
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': srcPath,
    };
    
    return config;
  },
};

export default nextConfig;
