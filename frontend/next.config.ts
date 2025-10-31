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
  webpack: (config, { defaultLoaders }) => {
    // When rootDirectory is set in vercel.json, process.cwd() will be the frontend directory
    // We need to ensure the alias points to the src directory within frontend
    const rootDir = process.cwd();
    const srcPath = path.join(rootDir, 'src');
    
    // Set up path aliases - this must match tsconfig.json paths
    if (!config.resolve) {
      config.resolve = {};
    }
    if (!config.resolve.alias) {
      config.resolve.alias = {};
    }
    
    config.resolve.alias['@'] = srcPath;
    
    // Also ensure webpack can find node_modules
    if (!config.resolve.modules) {
      config.resolve.modules = [];
    }
    config.resolve.modules.push(path.join(rootDir, 'node_modules'));
    
    return config;
  },
};

export default nextConfig;
