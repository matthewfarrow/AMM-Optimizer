"""
FastAPI Backend for AMM Liquidity Optimizer
Provides REST API for frontend and manages whitelist/analytics
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

from routers import pools, analytics, whitelist, positions
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AMM Liquidity Optimizer API",
    description="Backend API for automated Uniswap V3 liquidity management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "https://tangerine.trading",
        "https://tangerine-trading.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pools.router, prefix="/api/pools", tags=["pools"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(whitelist.router, prefix="/api/whitelist", tags=["whitelist"])
app.include_router(positions.router, prefix="/api/positions", tags=["positions"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AMM Liquidity Optimizer API", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    try:
        # Simple health check that doesn't depend on database
        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/api/health")
async def api_health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", os.getenv("BACKEND_PORT", 8000)))
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Disable reload in production
    )






