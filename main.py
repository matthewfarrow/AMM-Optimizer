#!/usr/bin/env python3
"""
Railway deployment entry point for AMM Optimizer Backend
"""

import sys
import os
from pathlib import Path

try:
    # Add backend to Python path
    backend_path = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_path))

    # Add backend/api to Python path for router imports
    api_path = backend_path / "api"
    sys.path.insert(0, str(api_path))

    print(f"🔧 Python path: {sys.path[:3]}")
    print(f"🔧 Backend path: {backend_path}")
    print(f"🔧 API path: {api_path}")

    # Import the FastAPI app
    from api.main import app
    print("✅ FastAPI app imported successfully")

    if __name__ == "__main__":
        import uvicorn
        port = int(os.environ.get("PORT", 8000))
        print(f"🚀 Starting AMM Optimizer API on port {port}")
        print(f"🔧 Environment: PORT={os.environ.get('PORT', '8000')}")
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

except Exception as e:
    print(f"❌ Error starting application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
