"""
Database configuration and models for AMM Optimizer
Uses SQLite for MVP, can be upgraded to PostgreSQL later
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# Database URL (SQLite for MVP, PostgreSQL for production)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Handle PostgreSQL scheme compatibility (SQLAlchemy v2 requirement)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"🔧 Using database: {DATABASE_URL}")

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Models
class WhitelistUser(Base):
    __tablename__ = "whitelist_users"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(42), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=True)
    reason = Column(Text, nullable=True)
    whitelisted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Pool(Base):
    __tablename__ = "pools"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(42), unique=True, index=True, nullable=False)
    name = Column(String(50), nullable=False)
    token0 = Column(String(10), nullable=False)
    token1 = Column(String(10), nullable=False)
    token0_address = Column(String(42), nullable=False)
    token1_address = Column(String(42), nullable=False)
    fee_tier = Column(Integer, nullable=False)
    tvl = Column(Float, default=0.0)
    apr = Column(Float, default=0.0)
    volume_1d = Column(Float, default=0.0)
    volume_30d = Column(Float, default=0.0)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserPosition(Base):
    __tablename__ = "user_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_address = Column(String(42), index=True, nullable=False)
    token_id = Column(Integer, nullable=True)  # NFT token ID
    pool_address = Column(String(42), nullable=False)
    tick_lower = Column(Integer, nullable=False)
    tick_upper = Column(Integer, nullable=False)
    amount0 = Column(Float, nullable=False)
    amount1 = Column(Float, nullable=False)
    check_interval = Column(Integer, default=60)  # seconds
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PriceData(Base):
    __tablename__ = "price_data"
    
    id = Column(Integer, primary_key=True, index=True)
    pool_address = Column(String(42), index=True, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

# Database functions
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")

def add_whitelist_user(db, address: str, email: str = None, reason: str = None):
    """Add user to whitelist"""
    user = WhitelistUser(
        address=address.lower(),
        email=email,
        reason=reason,
        whitelisted=True
    )
    db.add(user)
    db.commit()
    return user

def is_whitelisted(db, address: str) -> bool:
    """Check if user is whitelisted"""
    user = db.query(WhitelistUser).filter(
        WhitelistUser.address == address.lower(),
        WhitelistUser.whitelisted == True
    ).first()
    return user is not None

def get_user_positions(db, address: str):
    """Get user's active positions"""
    return db.query(UserPosition).filter(
        UserPosition.user_address == address.lower(),
        UserPosition.active == True
    ).all()

def create_user_position(db, user_address: str, pool_address: str, tick_lower: int, 
                        tick_upper: int, amount0: float, amount1: float, check_interval: int = 60):
    """Create new user position"""
    position = UserPosition(
        user_address=user_address.lower(),
        pool_address=pool_address,
        tick_lower=tick_lower,
        tick_upper=tick_upper,
        amount0=amount0,
        amount1=amount1,
        check_interval=check_interval
    )
    db.add(position)
    db.commit()
    return position















