#!/usr/bin/env python3
"""
Production startup script for the AMM Optimizer monitoring service
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from monitor.position_monitor import main as monitor_main

async def main():
    """Main function to run the monitoring service"""
    print("🎯 Starting AMM Optimizer Monitoring Service")
    print("=" * 50)
    
    # Get configuration from environment
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    contract_address = os.getenv("CONTRACT_ADDRESS")
    
    if not contract_address:
        print("⚠️  WARNING: No CONTRACT_ADDRESS provided - running in simulation mode")
        print("   Set CONTRACT_ADDRESS environment variable for production")
    
    print(f"Backend URL: {backend_url}")
    print(f"Contract Address: {contract_address or 'Not set (simulation mode)'}")
    print("=" * 50)
    
    try:
        # Start monitoring
        await monitor_main()
    except KeyboardInterrupt:
        print("\n⛔ Monitoring service stopped by user")
    except Exception as e:
        print(f"\n❌ Error in monitoring service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())













