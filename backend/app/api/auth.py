import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.models import User
from app.core.security import (
    get_password_hash, verify_password, create_access_token, 
    create_magic_link_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
)
from app.services.email import EmailService

router = APIRouter()

# JMc - [2026-03-18] - Secrets for secure webhook ingestion
GHL_WEBHOOK_SECRET = os.getenv("GHL_WEBHOOK_SECRET", "moderncyph3r_debug_key")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://oracleapp.moderncyph3r.com")

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class MagicLinkRequest(BaseModel):
    email: EmailStr

class MagicLinkVerify(BaseModel):
    token: str

class Token(BaseModel):
    access_token: str
    token_type: str
    tier: str

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password, tier="free")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "tier": new_user.tier}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    # JMc - Passwordless users won't have a hashed_password, force them to use Magic Link.
    if not user or not user.hashed_password or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password. Passwordless users must use Magic Link.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "tier": user.tier}

@router.post("/request-magic-link")
def request_magic_link(req: MagicLinkRequest, db: Session = Depends(get_db)):
    """
    JMc - [2026-03-18] - Forged on demand. 
    Allows existing users to login without a password.
    """
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        # JMc - Silent failure for security (prevents user enumeration)
        return {"status": "success", "message": "If you are in the system, a link has been dispatched."}
    
    token = create_magic_link_token(user.email)
    magic_url = f"{FRONTEND_URL}/auth/verify?token={token}"
    
    EmailService.send_magic_link(user.email, magic_url)
    
    return {"status": "success", "message": "Link dispatched to the vault."}

@router.post("/verify-magic-link", response_model=Token)
def verify_magic_link(req: MagicLinkVerify, db: Session = Depends(get_db)):
    """
    JMc - [2026-03-18] - Redempton logic. 
    Exchanges a 15-minute magic token for a standard 7-day session token.
    """
    try:
        payload = jwt.decode(req.token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if email is None or token_type != "magic_link":
            raise HTTPException(status_code=400, detail="Invalid token architecture.")
            
    except JWTError:
        raise HTTPException(status_code=400, detail="Token has expired or been corrupted.")
        
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Identity not found in the database.")

    # Update last login
    from sqlalchemy import update
    db.execute(update(User).where(User.id == user.id).values(last_login=datetime.utcnow()))
    db.commit()

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "tier": user.tier}

@router.post("/ghl-webhook")
async def ghl_purchase_webhook(request: Request, db: Session = Depends(get_db)):
    """
    JMc - [2026-03-18] - The Paywall Breach. 
    Receives purchase confirmation from GoHighLevel, provisions user, and dispatches Magic Link.
    """
    # 1. Verify Webhook Secret
    token = request.headers.get("X-GHL-Verify")
    if token != GHL_WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized transmission.")
        
    data = await request.json()
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Missing payload identity (email).")
        
    # 2. Provision or Upgrade User
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, tier="pro", is_active=1)
        db.add(user)
    else:
        user.tier = "pro"
        user.is_active = 1
        
    db.commit()
    db.refresh(user)
    
    # 3. Dispatch Initial Magic Link
    magic_token = create_magic_link_token(user.email)
    magic_url = f"{FRONTEND_URL}/auth/verify?token={magic_token}"
    EmailService.send_magic_link(user.email, magic_url)
    
    return {"status": "success", "message": f"User {email} provisioned and link dispatched."}
