#!/usr/bin/env python3
"""
Startup script for the AMM Optimizer backend
Runs both the FastAPI server and the monitoring service
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def run_fastapi():
    """Run the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    
    # Change to the api directory
    api_dir = backend_dir / "api"
    os.chdir(api_dir)
    
    # Start the FastAPI server
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ])
    
    return process

async def run_monitor():
    """Run the position monitoring service"""
    print("📊 Starting position monitoring service...")
    
    # Import and run the monitor
    from monitor.position_monitor import main as monitor_main
    await monitor_main()

async def main():
    """Main function to run both services"""
    print("🎯 Starting AMM Optimizer Backend Services")
    print("=" * 50)
    
    # Start FastAPI server
    api_process = await run_fastapi()
    
    # Wait a moment for the server to start
    await asyncio.sleep(3)
    
    try:
        # Start monitoring service
        await run_monitor()
    except KeyboardInterrupt:
        print("\n⛔ Shutting down services...")
    finally:
        # Terminate the API process
        if api_process:
            api_process.terminate()
            api_process.wait()
        print("✅ All services stopped")

if __name__ == "__main__":
    asyncio.run(main())







