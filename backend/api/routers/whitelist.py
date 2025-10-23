"""
Whitelist management endpoints
Handles beta tester signup and whitelist status checking
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import re

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from database import get_db, WhitelistUser, add_whitelist_user, is_whitelisted

router = APIRouter()

class WhitelistSignupRequest(BaseModel):
    address: str
    email: Optional[str] = None
    reason: Optional[str] = None

class WhitelistStatusResponse(BaseModel):
    address: str
    whitelisted: bool
    email: Optional[str] = None
    created_at: Optional[str] = None

def validate_ethereum_address(address: str) -> bool:
    """Validate Ethereum address format"""
    pattern = r"^0x[a-fA-F0-9]{40}$"
    return bool(re.match(pattern, address))

@router.post("/signup")
async def signup_for_whitelist(
    request: WhitelistSignupRequest,
    db: Session = Depends(get_db)
):
    """Sign up for beta testing whitelist"""
    
    # Validate address format
    if not validate_ethereum_address(request.address):
        raise HTTPException(
            status_code=400,
            detail="Invalid Ethereum address format"
        )
    
    # Check if already exists
    existing_user = db.query(WhitelistUser).filter(
        WhitelistUser.address == request.address.lower()
    ).first()
    
    if existing_user:
        if existing_user.whitelisted:
            return {
                "message": "Address already whitelisted",
                "address": request.address,
                "whitelisted": True
            }
        else:
            # Update existing signup
            existing_user.email = request.email
            existing_user.reason = request.reason
            existing_user.whitelisted = False  # Admin needs to approve
            db.commit()
            
            return {
                "message": "Signup updated, pending admin approval",
                "address": request.address,
                "whitelisted": False
            }
    
    # Create new signup
    user = add_whitelist_user(
        db=db,
        address=request.address,
        email=request.email,
        reason=request.reason
    )
    
    # For MVP, auto-whitelist (in production, admin approval required)
    user.whitelisted = True
    db.commit()
    
    return {
        "message": "Successfully added to whitelist",
        "address": request.address,
        "whitelisted": True
    }

@router.get("/status/{address}")
async def check_whitelist_status(
    address: str,
    db: Session = Depends(get_db)
):
    """Check if an address is whitelisted"""
    
    if not validate_ethereum_address(address):
        raise HTTPException(
            status_code=400,
            detail="Invalid Ethereum address format"
        )
    
    user = db.query(WhitelistUser).filter(
        WhitelistUser.address == address.lower()
    ).first()
    
    if not user:
        return WhitelistStatusResponse(
            address=address,
            whitelisted=False
        )
    
    return WhitelistStatusResponse(
        address=address,
        whitelisted=user.whitelisted,
        email=user.email,
        created_at=user.created_at.isoformat() if user.created_at else None
    )

@router.get("/pending")
async def get_pending_signups(
    db: Session = Depends(get_db)
):
    """Get pending whitelist signups (admin only)"""
    
    pending_users = db.query(WhitelistUser).filter(
        WhitelistUser.whitelisted == False
    ).all()
    
    return [
        {
            "id": user.id,
            "address": user.address,
            "email": user.email,
            "reason": user.reason,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        for user in pending_users
    ]

@router.post("/approve/{user_id}")
async def approve_whitelist_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Approve a whitelist user (admin only)"""
    
    user = db.query(WhitelistUser).filter(WhitelistUser.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.whitelisted = True
    db.commit()
    
    return {
        "message": f"User {user.address} approved for whitelist",
        "address": user.address,
        "whitelisted": True
    }

@router.post("/reject/{user_id}")
async def reject_whitelist_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Reject a whitelist user (admin only)"""
    
    user = db.query(WhitelistUser).filter(WhitelistUser.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {
        "message": f"User {user.address} rejected from whitelist",
        "address": user.address
    }

@router.get("/all")
async def get_all_whitelisted_users(
    db: Session = Depends(get_db)
):
    """Get all whitelisted users (admin only)"""
    
    whitelisted_users = db.query(WhitelistUser).filter(
        WhitelistUser.whitelisted == True
    ).all()
    
    return [
        {
            "id": user.id,
            "address": user.address,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        for user in whitelisted_users
    ]

@router.get("/stats")
async def get_whitelist_stats(db: Session = Depends(get_db)):
    """Get whitelist statistics"""
    
    total_users = db.query(WhitelistUser).count()
    whitelisted_users = db.query(WhitelistUser).filter(
        WhitelistUser.whitelisted == True
    ).count()
    pending_users = db.query(WhitelistUser).filter(
        WhitelistUser.whitelisted == False
    ).count()
    
    return {
        "total_signups": total_users,
        "whitelisted_users": whitelisted_users,
        "pending_users": pending_users,
        "approval_rate": (whitelisted_users / total_users * 100) if total_users > 0 else 0
    }
