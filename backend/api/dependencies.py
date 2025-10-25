"""
Dependencies for FastAPI routes
"""

from fastapi import HTTPException
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from database import init_db

# Global flag to track database initialization
_db_initialized = False

def ensure_db_initialized():
    """Lazy initialize database on first request"""
    global _db_initialized
    if not _db_initialized:
        try:
            init_db()
            _db_initialized = True
        except Exception as e:
            print(f"Database initialization failed: {e}")
            raise HTTPException(status_code=503, detail="Database unavailable")
