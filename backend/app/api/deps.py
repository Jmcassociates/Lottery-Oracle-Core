import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.core.models import User
from app.core.security import SECRET_KEY, ALGORITHM

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    JMc - [2026-04-04] - Standard user dependency. Validates JWT and returns the user object.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Oracle - Auth - Token payload missing 'sub' claim.")
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"Oracle - Auth - JWT Decode Error: {e}")
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        logger.warning(f"Oracle - Auth - User {email} not found in database.")
        raise credentials_exception
        
    # Killswitch check
    if not user.is_active:
        logger.error(f"Oracle - Auth - Blocked access for deactivated account: {email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ACCOUNT DEACTIVATED: Protocol access revoked by administrator."
        )
        
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """
    JMc - [2026-04-04] - Admin-only dependency.
    """
    if not current_user.is_admin:
        logger.error(f"Oracle - Auth - Administrative clearance rejected for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Technician clearance rejected: Administrative privileges required."
        )
    return current_user
