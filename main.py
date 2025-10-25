#!/usr/bin/env python3
"""
Railway deployment entry point for AMM Optimizer Backend
"""

import sys
import os
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Add backend/api to Python path for router imports
api_path = backend_path / "api"
sys.path.insert(0, str(api_path))

# Import the FastAPI app
from api.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting AMM Optimizer API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
