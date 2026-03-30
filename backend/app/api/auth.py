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
    is_admin: bool

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
    
    return {"access_token": access_token, "token_type": "bearer", "tier": user.tier, "is_admin": bool(user.is_admin)}

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
    EmailService.send_magic_link(user.email, token)
    
    return {"status": "success", "message": "Link dispatched to the vault."}

@router.post("/verify-magic-link", response_model=Token)
def verify_magic_link(req: MagicLinkVerify, db: Session = Depends(get_db)):
    """
    JMc - [2026-03-18] - Redempton logic. 
    Exchanges a 15-minute magic token for a standard 7-day session token.
    """
    try:
        # JMc - [2026-03-28] - Added 60s leeway to account for server clock drift in Cloud Run environment.
        payload = jwt.decode(req.token, SECRET_KEY, algorithms=[ALGORITHM], options={"leeway": 60})
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if email is None or token_type != "magic_link":
            raise HTTPException(status_code=400, detail="Invalid token architecture.")
            
    except JWTError as e:
        logger.error(f"Magic Link Verification Failure: {str(e)}")
        raise HTTPException(status_code=400, detail="Token has expired or has been corrupted.")
        
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Identity not found in the database.")

    # JMc - [2026-03-28] - Failsafe Master Admin Promotion. 
    # Ensures the lead architect is always provisioned with War Room clearance.
    if email == 'james@moderncyph3r.com':
        user.is_admin = 1
        user.tier = 'pro'
        db.commit()


    # Update last login
    from sqlalchemy import update
    db.execute(update(User).where(User.id == user.id).values(last_login=datetime.utcnow()))
    db.commit()

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "tier": user.tier, "is_admin": bool(user.is_admin)}

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
    EmailService.send_magic_link(user.email, magic_token)
    
    return {"status": "success", "message": f"User {email} provisioned and link dispatched."}


@router.post("/webhook/ghl-provision")
def ghl_webhook_provision(request_data: dict, token: str = None, db: Session = Depends(get_db)):
    """
    JMc - [2026-03-26] - Secure webhook receiver for GoHighLevel.
    Triggered when a user successfully purchases the Pro Tier via Stripe in the GHL Funnel.
    Creates or upgrades the user and dispatches a Magic Link via SMTP.
    """
    # 1. Security Check (Token must match environment variable)
    if token != GHL_WEBHOOK_SECRET:
        logger.warning(f"Unauthorized webhook attempt blocked. Invalid token: {token}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook secret")
        
    # 2. Extract Payload (Robust Recursive Search for GHL)
    email = None
    first_name = "Technician"

    # GHL Webhooks are notoriously nested (e.g., payload["contact"]["email"] or payload["email"])
    # We will recursively search the entire JSON dictionary for the first valid email address.
    def extract_email(data):
        if isinstance(data, dict):
            # Check common top-level keys first
            if "email" in data and isinstance(data["email"], str) and "@" in data["email"]:
                return data["email"]
            if "emailLowerCase" in data and isinstance(data["emailLowerCase"], str) and "@" in data["emailLowerCase"]:
                return data["emailLowerCase"]
                
            for key, value in data.items():
                # Grab first name if we see it while hunting for the email
                nonlocal first_name
                if key in ["firstName", "first_name", "name"] and isinstance(value, str):
                    first_name = value.split()[0]
                
                result = extract_email(value)
                if result:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = extract_email(item)
                if result:
                    return result
        return None

    email = extract_email(request_data)
    
    if not email:
        logger.error(f"Webhook payload missing email address. Payload received: {request_data}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")
        
    # Normalize email
    email = email.lower().strip()
    
    # 3. Database Operations
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        # In-App Upgrade Path: User already exists from the free tier PDF opt-in
        user.tier = "pro"
        logger.info(f"Oracle Provisioning: Upgraded existing user {email} to PRO tier.")
    else:
        # Direct Funnel Purchase: User is brand new
        user = User(email=email, tier="pro")
        db.add(user)
        logger.info(f"Oracle Provisioning: Created new PRO user {email}.")
        
    db.commit()
    
    # 4. Generate Magic Link and Dispatch Email
    magic_token = create_magic_link_token(email)
    success = EmailService.send_magic_link(email=email, token=magic_token)
    
    if not success:
        logger.error(f"Oracle Provisioning: User {email} upgraded, but SMTP dispatch failed.")
        # We don't return a 500 to GHL, because the provisioning worked. Just log it.
        return {"status": "success", "user": email, "email_dispatched": False}
        
    return {"status": "success", "user": email, "email_dispatched": True}
