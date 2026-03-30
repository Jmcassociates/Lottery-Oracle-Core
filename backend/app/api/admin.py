from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.models import User
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
    total_users = db.query(func.count(User.id)).scalar()
    pro_users = db.query(func.count(User.id)).filter(User.tier == "pro").scalar()
    free_users = db.query(func.count(User.id)).filter(User.tier == "free").scalar()
    
    # 24-hour acquisition velocity
    yesterday = datetime.utcnow() - timedelta(days=1)
    new_users_24h = db.query(func.count(User.id)).filter(User.created_at >= yesterday).scalar()

    return {
        "status": "online",
        "syndicate_metrics": {
            "total_users": total_users,
            "pro_tier": pro_users,
            "free_tier": free_users,
            "acquisition_24h": new_users_24h
        },
        "sync_health": {
            # Mocking the sync health for now until we wire it to the APScheduler logs
            "VA_Cash5": {"status": "Up to date", "last_sync": "03:00 AM EST"},
            "TX_Cash5": {"status": "Up to date", "last_sync": "03:00 AM EST"},
            "NY_Lotto": {"status": "Up to date", "last_sync": "03:00 AM EST"},
            "National": {"status": "Up to date", "last_sync": "03:00 AM EST"}
        }
    }

@router.get("/users")
def get_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    JMc - [2026-03-28] - Fetches the user ledger for manual review.
    """
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
