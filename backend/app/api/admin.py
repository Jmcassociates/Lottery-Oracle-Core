import os
import logging
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.models import User, DrawRecord, SyncLog
from app.api.auth import get_current_admin_user
from app.core.config import GAMES

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stats")
def get_admin_stats(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    JMc - [2026-03-28] - Dashboard metrics for the War Room.
    """
    logger.info("Oracle - Admin API - Fetching Global Pulse metrics...")
    
    total_users = db.query(User).count()
    pro_tier = db.query(User).filter(User.tier == "pro").count()
    free_tier = db.query(User).filter(User.tier == "free").count()
    
    # Simple check for sync activity in the last 10 minutes
    from datetime import datetime, timedelta
    ten_mins_ago = datetime.utcnow() - timedelta(minutes=10)
    sync_active = db.query(SyncLog).filter(SyncLog.status == "IMPORTING", SyncLog.executed_at >= ten_mins_ago).count() > 0
    
    # 24h acquisition
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    new_users = db.query(User).filter(User.created_at >= one_day_ago).count()

    # Engine status
    sync_health = {}
    for game in GAMES.keys():
        last_log = db.query(SyncLog).filter(SyncLog.game_name == game).order_by(SyncLog.executed_at.desc()).first()
        sync_health[game] = {
            "status": last_log.status if last_log else "Needs Sync",
            "last_sync": last_log.executed_at.strftime("%Y-%m-%d") if last_log else "Never"
        }

    return {
        "status": "online",
        "sync_active": sync_active,
        "syndicate_metrics": {
            "total_users": total_users,
            "pro_tier": pro_tier,
            "free_tier": free_tier,
            "acquisition_24h": new_users
        },
        "sync_health": sync_health
    }

@router.get("/users")
def get_users_ledger(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    JMc - [2026-03-28] - Fetches the user ledger for manual review.
    """
    logger.info("Oracle - Admin API - Fetching Syndicate Ledger...")
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
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
async def update_user_tier(user_id: int, payload: dict, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    JMc - [2026-03-31] - Manual override for user tiers with GHL Pipeline signaling.
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

    # JMc - Signal GHL Pipeline via Inbound Webhook
    ghl_webhook_url = os.getenv("GHL_TIER_UPDATE_WEBHOOK")
    if ghl_webhook_url:
        try:
            requests.post(ghl_webhook_url, json={
                "email": user.email,
                "tier": new_tier,
                "status": "active" if user.is_active else "inactive",
                "source": "oracle_war_room",
                "admin": current_admin.email
            }, timeout=5)
        except Exception as e:
            logger.error(f"Oracle - GHL Signal - Failed for {user.email}: {e}")

    return {"status": "success", "user": user.email, "new_tier": user.tier}

@router.post("/users/{user_id}/active")
async def update_user_status(user_id: int, payload: dict, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    JMc - [2026-04-03] - Compliance Killswitch. 
    Toggles a user's active status and signals GHL to move the card to the 'Banned/Inactive' stage.
    """
    is_active = payload.get("is_active")
    if is_active is None:
        raise HTTPException(status_code=400, detail="Status required")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_active = 1 if is_active else 0
    db.commit()
    
    status_str = "active" if user.is_active else "inactive"
    logger.info(f"Admin {current_admin.email} set {user.email} status to {status_str}.")

    # JMc - Signal GHL of the Compliance Action
    ghl_webhook_url = os.getenv("GHL_TIER_UPDATE_WEBHOOK")
    if ghl_webhook_url:
        try:
            requests.post(ghl_webhook_url, json={
                "email": user.email,
                "tier": user.tier,
                "status": status_str,
                "source": "oracle_compliance_killswitch",
                "admin": current_admin.email
            }, timeout=5)
        except Exception as e:
            logger.error(f"Oracle - GHL Compliance Signal - Failed for {user.email}: {e}")

    return {"status": "success", "user": user.email, "is_active": bool(user.is_active)}

@router.get("/logs")
def get_sync_logs(limit: int = 20, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    JMc - [2026-03-28] - Audit trail for sync operations.
    """
    logger.info("Oracle - Admin API - Fetching Sync History audit trail...")
    logs = db.query(SyncLog).order_by(SyncLog.executed_at.desc()).limit(limit).all()
    return logs
