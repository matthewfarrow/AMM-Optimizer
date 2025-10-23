#!/usr/bin/env python3
"""
REAL-TIME DEBUGGER FOR HACKATHON
Monitors app performance and logs in real-time
"""

import requests
import time
import json
import subprocess
import os
from datetime import datetime

class RealTimeDebugger:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_address = "0x8a679aCf39c06682072C4a2A833eb437A0CC0bdb"
        self.pool_address = "0x72ab388e2e2f6facef59e3c3fa2c4e29011c2d38"
        self.start_time = datetime.now()
        self.log_file = "debug_log.txt"
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        
        # Also write to log file
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")
    
    def check_backend_health(self):
        """Check backend health every 30 seconds"""
        try:
            response = requests.get(f"{self.base_url}/api/pools/?limit=4", timeout=5)
            if response.status_code == 200:
                return True
            else:
                self.log(f"Backend health check failed: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Backend health check error: {e}", "ERROR")
            return False
    
    def check_price_data(self):
        """Check price data freshness"""
        try:
            response = requests.get(f"{self.base_url}/api/analytics/{self.pool_address}/price-data?timeframe=1d", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    latest_price = data['data'][-1]['price']
                    timestamp = data['data'][-1].get('timestamp', 'unknown')
                    self.log(f"Price data fresh: ${latest_price:,.2f} at {timestamp}")
                    return latest_price
            return None
        except Exception as e:
            self.log(f"Price data check error: {e}", "ERROR")
            return None
    
    def check_whitelist_status(self):
        """Check whitelist status"""
        try:
            response = requests.get(f"{self.base_url}/api/whitelist/status/{self.test_address}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                whitelisted = data.get('whitelisted', False)
                if whitelisted:
                    return True
                else:
                    self.log("User NOT whitelisted!", "ERROR")
                    return False
            return False
        except Exception as e:
            self.log(f"Whitelist check error: {e}", "ERROR")
            return False
    
    def monitor_transaction_logs(self):
        """Monitor for transaction-related logs"""
        # This would monitor browser console logs in a real implementation
        # For now, we'll check backend logs
        try:
            # Check if there are any recent error logs
            if os.path.exists("logs/optimizer.log"):
                with open("logs/optimizer.log", "r") as f:
                    lines = f.readlines()
                    recent_lines = lines[-10:]  # Last 10 lines
                    for line in recent_lines:
                        if "ERROR" in line or "FAILED" in line:
                            self.log(f"Backend error detected: {line.strip()}", "ERROR")
        except Exception as e:
            self.log(f"Error monitoring logs: {e}", "ERROR")
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring"""
        self.log("🔍 Starting Real-Time Debugging Monitor...")
        self.log("=" * 60)
        self.log("Monitoring app performance for hackathon...")
        self.log("Press Ctrl+C to stop")
        self.log("=" * 60)
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                self.log(f"🔄 Monitoring cycle #{cycle_count}")
                
                # Check backend health
                if not self.check_backend_health():
                    self.log("❌ Backend health check failed!", "ERROR")
                
                # Check price data
                price = self.check_price_data()
                if price:
                    self.log(f"✅ Price data OK: ${price:,.2f}")
                else:
                    self.log("❌ Price data check failed!", "ERROR")
                
                # Check whitelist
                if self.check_whitelist_status():
                    self.log("✅ User whitelisted")
                else:
                    self.log("❌ User not whitelisted!", "ERROR")
                
                # Monitor logs
                self.monitor_transaction_logs()
                
                # Wait 30 seconds before next check
                self.log("⏳ Waiting 30 seconds for next check...")
                time.sleep(30)
                
        except KeyboardInterrupt:
            self.log("🛑 Monitoring stopped by user")
            self.log("=" * 60)
            self.log("📊 FINAL SUMMARY:")
            self.log(f"Monitoring duration: {datetime.now() - self.start_time}")
            self.log(f"Total cycles: {cycle_count}")
            self.log("Check debug_log.txt for full log history")
            self.log("=" * 60)

def main():
    print("🔍 REAL-TIME DEBUGGER FOR HACKATHON")
    print("=" * 60)
    print("This will monitor your app in real-time during testing")
    print("=" * 60)
    
    debugger = RealTimeDebugger()
    debugger.run_continuous_monitoring()

if __name__ == "__main__":
    main()
