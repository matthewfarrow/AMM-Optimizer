"""
Position management endpoints
Handles user position creation, monitoring, and management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from database import get_db, UserPosition, create_user_position, get_user_positions, is_whitelisted

# Import the lazy initialization dependency
from dependencies import ensure_db_initialized

router = APIRouter()

class CreatePositionRequest(BaseModel):
    user_address: str
    pool_address: str
    tick_lower: int
    tick_upper: int
    amount0: float
    amount1: float
    check_interval: int = 60

class PositionResponse(BaseModel):
    id: int
    user_address: str
    token_id: Optional[int]
    pool_address: str
    tick_lower: int
    tick_upper: int
    amount0: float
    amount1: float
    check_interval: int
    active: bool
    created_at: str
    updated_at: str

@router.post("/create")
async def create_position(
    request: CreatePositionRequest,
    db: Session = Depends(get_db),
    _: None = Depends(ensure_db_initialized)
):
    """Create a new position for a user"""
    
    # Check if user is whitelisted
    if not is_whitelisted(db, request.user_address):
        raise HTTPException(
            status_code=403,
            detail="User not whitelisted. Please sign up for beta access."
        )
    
    # Validate tick range
    if request.tick_lower >= request.tick_upper:
        raise HTTPException(
            status_code=400,
            detail="Invalid tick range: lower must be less than upper"
        )
    
    # Validate amounts
    if request.amount0 <= 0 or request.amount1 <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amounts must be positive"
        )
    
    # Create position
    position = create_user_position(
        db=db,
        user_address=request.user_address,
        pool_address=request.pool_address,
        tick_lower=request.tick_lower,
        tick_upper=request.tick_upper,
        amount0=request.amount0,
        amount1=request.amount1,
        check_interval=request.check_interval
    )
    
    return {
        "message": "Position created successfully",
        "position_id": position.id,
        "user_address": position.user_address,
        "pool_address": position.pool_address,
        "tick_range": f"{position.tick_lower} to {position.tick_upper}",
        "amounts": {
            "token0": position.amount0,
            "token1": position.amount1
        },
        "check_interval": position.check_interval
    }

@router.get("/user/{user_address}")
async def get_user_positions_endpoint(
    user_address: str,
    db: Session = Depends(get_db),
    _: None = Depends(ensure_db_initialized)
):
    """Get all positions for a user"""
    
    # Check if user is whitelisted
    if not is_whitelisted(db, user_address):
        raise HTTPException(
            status_code=403,
            detail="User not whitelisted"
        )
    
    positions = get_user_positions(db, user_address)
    
    return [
        PositionResponse(
            id=pos.id,
            user_address=pos.user_address,
            token_id=pos.token_id,
            pool_address=pos.pool_address,
            tick_lower=pos.tick_lower,
            tick_upper=pos.tick_upper,
            amount0=pos.amount0,
            amount1=pos.amount1,
            check_interval=pos.check_interval,
            active=pos.active,
            created_at=pos.created_at.isoformat(),
            updated_at=pos.updated_at.isoformat()
        )
        for pos in positions
    ]

@router.get("/{position_id}")
async def get_position_details(
    position_id: int,
    db: Session = Depends(get_db)
):
    """Get details of a specific position"""
    
    position = db.query(UserPosition).filter(UserPosition.id == position_id).first()
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    return PositionResponse(
        id=position.id,
        user_address=position.user_address,
        token_id=position.token_id,
        pool_address=position.pool_address,
        tick_lower=position.tick_lower,
        tick_upper=position.tick_upper,
        amount0=position.amount0,
        amount1=position.amount1,
        check_interval=position.check_interval,
        active=position.active,
        created_at=position.created_at.isoformat(),
        updated_at=position.updated_at.isoformat()
    )

@router.post("/{position_id}/pause")
async def pause_position(
    position_id: int,
    db: Session = Depends(get_db)
):
    """Pause monitoring for a position"""
    
    position = db.query(UserPosition).filter(UserPosition.id == position_id).first()
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    position.active = False
    position.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Position monitoring paused",
        "position_id": position_id,
        "active": False
    }

@router.post("/{position_id}/resume")
async def resume_position(
    position_id: int,
    db: Session = Depends(get_db)
):
    """Resume monitoring for a position"""
    
    position = db.query(UserPosition).filter(UserPosition.id == position_id).first()
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    position.active = True
    position.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Position monitoring resumed",
        "position_id": position_id,
        "active": True
    }

@router.post("/{position_id}/update-token-id")
async def update_token_id(
    position_id: int,
    token_id: int,
    db: Session = Depends(get_db)
):
    """Update the NFT token ID for a position (called after on-chain creation)"""
    
    position = db.query(UserPosition).filter(UserPosition.id == position_id).first()
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    position.token_id = token_id
    position.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Token ID updated successfully",
        "position_id": position_id,
        "token_id": token_id
    }

@router.delete("/{position_id}")
async def delete_position(
    position_id: int,
    db: Session = Depends(get_db)
):
    """Delete a position (soft delete by setting active=False)"""
    
    position = db.query(UserPosition).filter(UserPosition.id == position_id).first()
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    position.active = False
    position.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Position deleted successfully",
        "position_id": position_id
    }

@router.get("/active/all")
async def get_all_active_positions(db: Session = Depends(get_db)):
    """Get all active positions (for monitoring service)"""
    
    active_positions = db.query(UserPosition).filter(
        UserPosition.active == True
    ).all()
    
    return [
        {
            "id": pos.id,
            "user_address": pos.user_address,
            "token_id": pos.token_id,
            "pool_address": pos.pool_address,
            "tick_lower": pos.tick_lower,
            "tick_upper": pos.tick_upper,
            "amount0": pos.amount0,
            "amount1": pos.amount1,
            "check_interval": pos.check_interval,
            "created_at": pos.created_at.isoformat(),
            "updated_at": pos.updated_at.isoformat()
        }
        for pos in active_positions
    ]

@router.get("/stats/overview")
async def get_positions_overview(db: Session = Depends(get_db)):
    """Get overview statistics of all positions"""
    
    total_positions = db.query(UserPosition).count()
    active_positions = db.query(UserPosition).filter(UserPosition.active == True).count()
    paused_positions = total_positions - active_positions
    
    # Get unique users
    unique_users = db.query(UserPosition.user_address).distinct().count()
    
    return {
        "total_positions": total_positions,
        "active_positions": active_positions,
        "paused_positions": paused_positions,
        "unique_users": unique_users,
        "monitoring_status": "active" if active_positions > 0 else "idle"
    }
