#!/usr/bin/env python3
"""
Complete startup script for AMM Optimizer
Runs both the FastAPI backend and monitoring service
"""

import asyncio
import subprocess
import sys
import os
import signal
import time
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_api_server(self):
        """Start the FastAPI server"""
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
        
        self.processes.append(("API Server", process))
        return process
    
    async def start_monitoring_service(self):
        """Start the monitoring service"""
        print("📊 Starting position monitoring service...")
        
        # Import and run the monitor
        from monitor.position_monitor import main as monitor_main
        await monitor_main()
    
    def stop_all_services(self):
        """Stop all running services"""
        print("\n⛔ Shutting down all services...")
        
        for name, process in self.processes:
            if process and process.poll() is None:
                print(f"Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"Force killing {name}...")
                    process.kill()
        
        self.running = False
        print("✅ All services stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}")
        self.stop_all_services()
        sys.exit(0)
    
    async def run(self):
        """Main function to run all services"""
        print("🎯 Starting AMM Optimizer - Complete System")
        print("=" * 60)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Start API server
            api_process = self.start_api_server()
            
            # Wait for API server to start
            print("⏳ Waiting for API server to start...")
            await asyncio.sleep(3)
            
            # Check if API server is running
            try:
                import requests
                response = requests.get("http://localhost:8000/api/health", timeout=5)
                if response.status_code == 200:
                    print("✅ API server is running")
                else:
                    print("❌ API server health check failed")
            except Exception as e:
                print(f"⚠️  API server health check failed: {e}")
            
            # Start monitoring service
            print("📊 Starting monitoring service...")
            await self.start_monitoring_service()
            
        except KeyboardInterrupt:
            print("\n⛔ Shutdown requested by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.stop_all_services()

async def main():
    """Main entry point"""
    manager = ServiceManager()
    await manager.run()

if __name__ == "__main__":
    asyncio.run(main())







