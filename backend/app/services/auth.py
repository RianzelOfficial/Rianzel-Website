import random
import string
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import EmailStr, validator
import re
from app.models import User, LoginAttempt, OTP
from app.schemas.user import UserCreate, UserLogin
from app.schemas.user import PasswordReset
from app.schemas.user import Token
from app.schemas.user import TokenData
from app.services.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    generate_otp,
    verify_otp,
    validate_password_strength
)
from app.services.email import send_verification_email, send_password_reset_email
from app.database import get_db
from app.config import settings
from app.utils.recaptcha import verify_recaptcha
from app.utils.rate_limiter import rate_limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Helper functions for login attempts

async def get_failed_login_attempts(db: AsyncSession, username: str, ip_address: str) -> int:
    """Get the number of failed login attempts for a username/IP."""
    # Check both username and IP based attempts
    query = select(LoginAttempt).where(
        (LoginAttempt.username == username) | 
        (LoginAttempt.ip_address == ip_address),
        LoginAttempt.created_at > datetime.utcnow() - timedelta(hours=1)  # Last hour
    )
    result = await db.execute(query)
    return len(result.scalars().all())

@router.post("/forgot-password", response_model=Dict[str, Any])
async def forgot_password(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Send password reset email to user."""
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalar_one_or_none()
    
    if user:  # Only generate token if user exists
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        
        # Store reset token in database
        reset_token_hash = get_password_hash(reset_token)
        user.reset_token = reset_token_hash
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)  # Token valid for 24 hours
        db.add(user)
        await db.commit()
        
        # Send password reset email
        background_tasks.add_task(
            send_password_reset_email,
            email=user.email,
            reset_token=reset_token
        )
    
    # Always return success to prevent email enumeration
    return {"message": "If your email is registered, you will receive a password reset link."}

@router.post("/reset-password", response_model=Dict[str, Any])
async def reset_password(
    reset_token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db)
):
    """Reset user password using reset token."""
    user = await db.execute(select(User).where(User.reset_token != None))
    user = user.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Verify token hasn't expired
    if user.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Verify token matches
    if not verify_password(reset_token, user.reset_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    # Validate password strength
    if not validate_password_strength(new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet requirements"
        )
    
    # Update password and clear reset token
    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    user.is_active = True  # Re-enable account if it was disabled
    db.add(user)
    await db.commit()
    
    return {"message": "Password reset successful"}

async def record_failed_login_attempt(
    db: AsyncSession, 
    username: str, 
    ip_address: str,
    reason: str = "Invalid credentials"
) -> None:
    """Record a failed login attempt."""
    attempt = LoginAttempt(
        username=username,
        ip_address=ip_address,
        reason=reason,
        user_agent=request.headers.get("user-agent", "unknown")
    )
    db.add(attempt)
    
    # Also update user's failed login count
    if username:
        user = await db.execute(select(User).where(User.username == username))
        user = user.scalar_one_or_none()
        if user:
            user.failed_login_attempts += 1
            user.last_failed_login = datetime.utcnow()
            db.add(user)
    
    await db.commit()

async def reset_failed_login_attempts(db: AsyncSession, username: str) -> None:
    """Reset failed login attempts counter for a user."""
    user = await db.execute(select(User).where(User.username == username))
    user = user.scalar_one_or_none()
    if user:
        user.failed_login_attempts = 0
        user.last_failed_login = None
        db.add(user)
        await db.commit()

# Helper function to validate OTP
async def validate_otp(db: AsyncSession, user_id: int, otp_code: str) -> bool:
    """Validate OTP code for a user."""
    query = select(OTP).where(
        OTP.user_id == user_id,
        OTP.code == otp_code,
        OTP.used == False,
        OTP.expires_at > datetime.utcnow()
    )
    result = await db.execute(query)
    otp = result.scalar_one_or_none()
    
    if not otp:
        return False
    
    # Mark OTP as used
    otp.used = True
    otp.used_at = datetime.utcnow()
    db.add(otp)
    await db.commit()
    
    return True

@router.post("/register", response_model=Dict[str, Any])
@rate_limiter(max_requests=5, time_window=60)  # 5 requests per minute
async def register(
    request: Request,
    background_tasks: BackgroundTasks,
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user with email verification and additional security checks.
    """
    # Verify reCAPTCHA
    if settings.RECAPTCHA_ENABLED:
        recaptcha_token = request.headers.get("recaptcha-token")
        if not recaptcha_token or not await verify_recaptcha(recaptcha_token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="reCAPTCHA verification failed"
            )
    
    # Check if username already exists
    query = select(User).where(User.username == user.username)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    query = select(User).where(User.email == user.email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    if not validate_password_strength(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet requirements"
        )
    
    # Validate date of birth (must be at least 15 years old)
    min_age_date = datetime.utcnow() - timedelta(days=365.25 * 15)
    if user.date_of_birth and user.date_of_birth > min_age_date.date():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must be at least 15 years old to register"
        )
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create user with default role
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        date_of_birth=user.date_of_birth,
        country=user.country,
        is_active=False,  # User needs to verify email first
        role=UserRole.USER  # Default role
    )
    
    db.add(db_user)
    await db.flush()  # Get the user ID for OTP
    
    # Generate and store OTP
    otp_code = generate_otp()
    otp = OTP(
        user_id=db_user.id,
        code=otp_code,
        expires_at=datetime.utcnow() + timedelta(minutes=15)  # OTP valid for 15 minutes
    )
    db.add(otp)
    
    # Send verification email with OTP
    background_tasks.add_task(
        send_verification_email,
        email=user.email,
        username=user.username,
        otp_code=otp_code
    )
    
    await db.commit()
    
    return {
        "message": "Registration successful. Please check your email to verify your account.",
        "user_id": db_user.id,
        "email": db_user.email,
        "requires_verification": True
    }

@router.post("/login", response_model=Dict[str, Any])
@rate_limiter(max_requests=5, time_window=60)  # 5 requests per minute
async def login(
    request: Request,
    background_tasks: BackgroundTasks,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    User login with email/username and password.
    Requires OTP verification if enabled for the user.
    """
    # Verify reCAPTCHA if enabled and failed attempts > 3
    client_ip = request.client.host
    failed_attempts = await get_failed_login_attempts(db, form_data.username, client_ip)
    
    if failed_attempts >= 3 and settings.RECAPTCHA_ENABLED:
        recaptcha_token = request.headers.get("recaptcha-token")
        if not recaptcha_token or not await verify_recaptcha(recaptcha_token):
            await record_failed_login_attempt(db, form_data.username, client_ip, "reCAPTCHA failed")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="reCAPTCHA verification required"
            )
    
    # Get user by username or email
    query = select(User).where(
        (User.username == form_data.username) | (User.email == form_data.username)
    )
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()
    
    # Check if user exists and account is active
    if not db_user:
        await record_failed_login_attempt(db, form_data.username, client_ip, "User not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not activated. Please verify your email first."
        )
    
    # Check if account is locked
    if db_user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
        lock_time = db_user.last_failed_login + timedelta(minutes=settings.LOGIN_LOCKOUT_MINUTES)
        if datetime.utcnow() < lock_time:
            remaining_time = (lock_time - datetime.utcnow()).seconds // 60
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Account temporarily locked. Try again in {remaining_time} minutes."
            )
    
    # Verify password
    if not verify_password(form_data.password, db_user.hashed_password):
        await record_failed_login_attempt(db, db_user.username, client_ip, "Invalid password")
        remaining_attempts = settings.MAX_LOGIN_ATTEMPTS - (db_user.failed_login_attempts + 1)
        
        if remaining_attempts <= 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Account locked. Please try again in {settings.LOGIN_LOCKOUT_MINUTES} minutes."
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect password. {remaining_attempts} attempts remaining."
        )
    
    # Check if OTP is required (2FA)
    if db_user.two_factor_enabled:
        # Generate and send OTP
        otp_code = generate_otp()
        otp = OTP(
            user_id=db_user.id,
            code=otp_code,
            expires_at=datetime.utcnow() + timedelta(minutes=5)  # OTP valid for 5 minutes
        )
        db.add(otp)
        await db.commit()
        
        # Send OTP via email
        background_tasks.add_task(
            send_otp_email,
            email=db_user.email,
            username=db_user.username,
            otp_code=otp_code
        )
        
        return {
            "message": "OTP sent to your email",
            "otp_required": True,
            "user_id": db_user.id
        }
    
    # Reset failed login attempts on successful login
    await reset_failed_login_attempts(db, db_user.username)
    
    # Update last login time
    db_user.last_login = datetime.utcnow()
    await db.commit()
    
    # Generate tokens
    access_token = create_access_token(
        data={"sub": db_user.username, "user_id": db_user.id, "role": db_user.role}
    )
    refresh_token = create_refresh_token(
        data={"sub": db_user.username}
    )
    
    # Store refresh token in database
    db_user.refresh_token = refresh_token
    await db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "role": db_user.role,
            "is_active": db_user.is_active,
            "two_factor_enabled": db_user.two_factor_enabled
        }
    }
