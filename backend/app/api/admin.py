from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.models import User, DrawRecord, SyncLog
from app.core.config import GAMES
from app.core.security import get_current_user
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """
    JMc - [2026-03-28] - Verifies the 'is_admin' flag is set to 1 in the DB.
    """
    if not current_user.is_admin:
        logger.warning(f"Unauthorized admin access attempt by {current_user.email}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Technician clearance required.")
    return current_user

@router.get("/stats")
def get_admin_stats(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    JMc - [2026-03-28] - The War Room Global Pulse.
    """
    logger.info("Oracle - Admin API - Fetching Global Pulse metrics...")
    total_users = db.query(func.count(User.id)).scalar()
    pro_users = db.query(func.count(User.id)).filter(User.tier == "pro").scalar()
    free_users = db.query(func.count(User.id)).filter(User.tier == "free").scalar()
    
    # 24-hour acquisition velocity
    yesterday = datetime.utcnow() - timedelta(days=1)
    new_users_24h = db.query(func.count(User.id)).filter(User.created_at >= yesterday).scalar()

    # Dynamic Sync Health tracking
    sync_health = {}
    for game_name, config in GAMES.items():
        # Query the latest draw date for this specific game (handles Day/Night variants)
        latest_draw = db.query(DrawRecord.draw_date).filter(DrawRecord.game_name.like(f"{game_name}%")).order_by(DrawRecord.draw_date.desc()).first()
        
        if latest_draw:
            # Check if sync is "stale" (older than 24h for daily games)
            # For simplicity, we just show the last date found.
            last_date_str = latest_draw[0].strftime("%Y-%m-%d")
            status = "Up to date"
        else:
            last_date_str = "No records"
            status = "Needs Sync"
            
        sync_health[game_name] = {"status": status, "last_sync": last_date_str}

    return {
        "status": "online",
        "syndicate_metrics": {
            "total_users": total_users,
            "pro_tier": pro_users,
            "free_tier": free_users,
            "acquisition_24h": new_users_24h
        },
        "sync_health": sync_health
    }

@router.get("/users")
def get_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    JMc - [2026-03-28] - Fetches the user ledger for manual review.
    """
    logger.info("Oracle - Admin API - Fetching Syndicate Ledger...")
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    # Clean the payload before sending it to the React frontend
    return [
        {
            "id": u.id,
            "email": u.email,
            "tier": u.tier,
            "is_active": bool(u.is_active),
            "is_admin": bool(u.is_admin),
            "created_at": u.created_at
        } for u in users
    ]

@router.post("/users/{user_id}/tier")
def update_user_tier(user_id: int, payload: dict, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    JMc - [2026-03-28] - Manual override for user tiers.
    """
    new_tier = payload.get("tier")
    if new_tier not in ["free", "pro"]:
        raise HTTPException(status_code=400, detail="Invalid tier")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.tier = new_tier
    db.commit()
    logger.info(f"Admin {current_admin.email} manually updated {user.email} to tier {new_tier}.")
    return {"status": "success", "user": user.email, "new_tier": user.tier}

@router.get("/logs")
def get_sync_logs(limit: int = 20, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    JMc - [2026-03-28] - Returns the audit trail for the last N sync operations.
    """
    logger.info("Oracle - Admin API - Fetching Sync History audit trail...")
    logs = db.query(SyncLog).order_by(SyncLog.executed_at.desc()).limit(limit).all()
    return logs
