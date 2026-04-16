import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
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
from app.api.deps import get_current_user
from app.services.email import EmailService

logger = logging.getLogger(__name__)
router = APIRouter()

# JMc - [2026-03-31] - Secrets for secure webhook ingestion
GHL_WEBHOOK_SECRET = os.getenv("GHL_WEBHOOK_SECRET")
if not GHL_WEBHOOK_SECRET:
    raise RuntimeError("CRITICAL SECRETS MISSING: GHL_WEBHOOK_SECRET environment variable is not set. Halting boot sequence.")
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
    
    # JMc - [2026-04-05] - Telemetry Dispatch: Signal GHL that a Free Tier user has entered the Vault.
    ghl_webhook_url = os.getenv("GHL_TIER_UPDATE_WEBHOOK")
    if ghl_webhook_url:
        import requests
        try:
            requests.post(ghl_webhook_url, json={
                "email": new_user.email,
                "tier": "free",
                "status": "active",
                "source": "oracle_registration"
            }, timeout=5)
            logger.info(f"Oracle Telemetry: GHL signaled for new Vault User {new_user.email}")
        except Exception as e:
            logger.error(f"Oracle Telemetry: GHL Signal failed for registration {new_user.email}: {e}")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "tier": new_user.tier, "is_admin": bool(new_user.is_admin)}

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
@limiter.limit("5/minute")
def request_magic_link(request: Request, req: MagicLinkRequest, db: Session = Depends(get_db)):
    """
    JMc - [2026-03-18] - Forged on demand. 
    Allows existing users to login without a password.
    """
    logger.info(f"Oracle - Auth - Magic Link Request initiated for {req.email}")
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        logger.info(f"Oracle - Auth - Identity {req.email} not found. Silent success triggered.")
        # JMc - Silent failure for security (prevents user enumeration)
        return {"status": "success", "message": "If you are in the system, a link has been dispatched."}
    
    logger.info(f"Oracle - Auth - Forging token for {user.email}...")
    token = create_magic_link_token(user.email)
    
    logger.info(f"Oracle - Auth - Token forged. Handing off to EmailService...")
    EmailService.send_magic_link(user.email, token)
    
    logger.info(f"Oracle - Auth - Dispatch sequence complete for {user.email}")
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


    # JMc - [2026-04-03] - Compliance Killswitch Check
    if not user.is_active:
        logger.warning(f"Protocol access DENIED for deactivated account: {email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ACCOUNT DEACTIVATED: Protocol access terminated by administration."
        )

    # Update last login
    from sqlalchemy import update
    db.execute(update(User).where(User.id == user.id).values(last_login=datetime.utcnow()))
    db.commit()

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "tier": user.tier, "is_admin": bool(user.is_admin)}

@router.post("/webhook/ghl-provision")
async def ghl_webhook_provision(request: Request, db: Session = Depends(get_db)):
    """
    JMc - [2026-03-31] - Consolidated, secure webhook receiver for GoHighLevel.
    Triggered when a user successfully purchases the Pro Tier via Stripe in the GHL Funnel.
    Creates or upgrades the user and dispatches a Magic Link via SMTP.
    """
    # 1. Security Check (Header-based)
    token = request.headers.get("X-GHL-Verify")
    if token != GHL_WEBHOOK_SECRET:
        logger.warning(f"Unauthorized webhook attempt blocked. Invalid token: {token}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook secret")
        
    request_data = await request.json()
    
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

@router.post("/webhook/ghl-cancel")
async def ghl_webhook_cancel(request: Request, db: Session = Depends(get_db)):
    """
    JMc - [2026-04-16] - The Stripe Proxy. 
    Receives cancellation signal from GHL and securely terminates the Stripe subscription
    without relying on GHL's premium actions or hallucinated merge tags.
    """
    # 1. Security Check
    token = request.headers.get("X-GHL-Verify")
    if token != GHL_WEBHOOK_SECRET:
        logger.warning(f"Unauthorized cancel webhook attempt blocked. Invalid token: {token}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook secret")
        
    request_data = await request.json()
    
    # 2. Extract Email Payload
    def extract_email(data):
        if isinstance(data, dict):
            if "email" in data and isinstance(data["email"], str) and "@" in data["email"]:
                return data["email"]
            if "emailLowerCase" in data and isinstance(data["emailLowerCase"], str) and "@" in data["emailLowerCase"]:
                return data["emailLowerCase"]
            for key, value in data.items():
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
        logger.error(f"Cancel Webhook missing email. Payload: {request_data}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")
        
    email = email.lower().strip()
    
    # 3. Connect to Stripe API
    import requests
    stripe_key = os.getenv("STRIPE_SECRET_KEY")
    if not stripe_key:
        logger.error("Oracle Billing: STRIPE_SECRET_KEY is missing from environment. Cannot proxy cancellation.")
        return {"status": "failed", "reason": "server_misconfiguration"}
        
    headers = {
        "Authorization": f"Bearer {stripe_key}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # 3a. Look up customer by email
    cust_res = requests.get(f"https://api.stripe.com/v1/customers?email={email}", headers=headers)
    if cust_res.status_code != 200:
        logger.error(f"Oracle Billing: Stripe API error fetching customer for {email}: {cust_res.text}")
        return {"status": "failed", "reason": "stripe_api_error"}
        
    customers = cust_res.json().get("data", [])
    if not customers:
        logger.warning(f"Oracle Billing: No Stripe customer found for {email}.")
        return {"status": "skipped", "reason": "no_customer"}
        
    cust_id = customers[0]["id"]
    
    # 3b. Look up active subscription
    sub_res = requests.get(f"https://api.stripe.com/v1/subscriptions?customer={cust_id}&status=active", headers=headers)
    subs = sub_res.json().get("data", [])
    
    if not subs:
        logger.info(f"Oracle Billing: No active subscriptions to cancel for {email}.")
        return {"status": "skipped", "reason": "no_active_subscriptions"}
        
    sub_id = subs[0]["id"]
    
    # 3c. Execute Deferred Cancellation
    update_res = requests.post(
        f"https://api.stripe.com/v1/subscriptions/{sub_id}",
        headers=headers,
        data={"cancel_at_period_end": "true"}
    )
    
    if update_res.status_code == 200:
        logger.info(f"Oracle Billing: Successfully scheduled termination for {email} (Sub: {sub_id}).")
        return {"status": "success"}
    else:
        logger.error(f"Oracle Billing: Failed to cancel {sub_id}: {update_res.text}")
        return {"status": "failed", "reason": "stripe_update_error"}
