import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
from jose import JWTError

from ..models import User, OTP, LoginAttempt, UserRole
from ..schemas import (
    UserCreate, UserLogin, Token, UserResponse, EmailVerifyRequest,
    OTPVerifyRequest, ResetPasswordRequest, UserUpdate, ChangePasswordRequest
)
from ..services.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, validate_password_strength, get_password_hash,
    generate_otp, verify_otp, get_current_user, get_current_active_user
)
from ..services.email import send_verification_email, send_password_reset_email, send_otp_email
from ..database import get_db
from ..config import settings
from ..utils.recaptcha import verify_recaptcha
from ..utils.rate_limiter import rate_limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Helper functions for login attempts

async def get_failed_login_attempts(db: AsyncSession, username: str, ip_address: str) -> int:
    """Get the number of failed login attempts for a username/IP."""
    query = select(LoginAttempt).where(
        (LoginAttempt.username == username) | 
        (LoginAttempt.ip_address == ip_address),
        LoginAttempt.created_at > datetime.utcnow() - timedelta(hours=1)
    )
    result = await db.execute(query)
    return len(result.scalars().all())

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
        user_agent="unknown"  # We'll set this from the request when needed
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
@rate_limiter(max_requests=5, time_window=60)
async def register(
    request: Request,
    background_tasks: BackgroundTasks,
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user with email verification."""
    # Verify reCAPTCHA if enabled
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
        role=UserRole.USER,
        two_factor_enabled=user.two_factor_enabled or False
    )
    
    db.add(db_user)
    await db.flush()
    
    # Generate and store OTP
    otp_code = generate_otp()
    otp = OTP(
        user_id=db_user.id,
        code=otp_code,
        expires_at=datetime.utcnow() + timedelta(minutes=15)
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
@rate_limiter(max_requests=5, time_window=60)
async def login(
    request: Request,
    background_tasks: BackgroundTasks,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """User login with email/username and password."""
    client_ip = request.client.host if request.client else "unknown"
    
    # Verify reCAPTCHA if enabled and failed attempts > 3
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
            expires_at=datetime.utcnow() + timedelta(minutes=5)
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

@router.post("/verify-otp", response_model=Dict[str, Any])
async def verify_otp_endpoint(
    otp_data: OTPVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify OTP code for 2FA or email verification."""
    # Validate OTP
    is_valid = await validate_otp(db, otp_data.user_id, otp_data.otp_code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP code"
        )
    
    # Get user
    user = await db.get(User, otp_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Activate user if this was an email verification
    if not user.is_active:
        user.is_active = True
        user.email_verified_at = datetime.utcnow()
        db.add(user)
    
    # Generate tokens
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username}
    )
    
    # Store refresh token in database
    user.refresh_token = refresh_token
    await db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "two_factor_enabled": user.two_factor_enabled
        }
    }

@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    email_data: EmailVerifyRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Resend email verification OTP."""
    # Get user by email
    query = select(User).where(User.email == email_data.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email"
        )
    
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already verified"
        )
    
    # Generate and store new OTP
    otp_code = generate_otp()
    otp = OTP(
        user_id=user.id,
        code=otp_code,
        expires_at=datetime.utcnow() + timedelta(minutes=15)
    )
    db.add(otp)
    await db.commit()
    
    # Send verification email
    background_tasks.add_task(
        send_verification_email,
        email=user.email,
        username=user.username,
        otp_code=otp_code
    )
    
    return {"message": "Verification email sent successfully"}

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    email_data: EmailVerifyRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Initiate password reset process."""
    # Get user by email
    query = select(User).where(User.email == email_data.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        # Don't reveal that the email doesn't exist
        return {"message": "If an account exists with this email, a password reset link has been sent"}
    
    # Generate and store reset token
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
    db.add(user)
    await db.commit()
    
    # Send password reset email
    background_tasks.add_task(
        send_password_reset_email,
        email=user.email,
        username=user.username,
        reset_token=reset_token
    )
    
    return {"message": "Password reset email sent successfully"}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Reset user password using the reset token."""
    # Find user by reset token
    query = select(User).where(
        User.reset_token == reset_data.reset_token,
        User.reset_token_expires > datetime.utcnow()
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Validate new password
    if not validate_password_strength(reset_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet requirements"
        )
    
    # Update password and clear reset token
    user.hashed_password = get_password_hash(reset_data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    user.failed_login_attempts = 0  # Reset failed attempts
    db.add(user)
    await db.commit()
    
    return {"message": "Password reset successful"}

@router.post("/refresh-token", response_model=Dict[str, Any])
async def refresh_token(
    refresh_token: str = Cookie(None, alias="refresh_token"),
    db: AsyncSession = Depends(get_db)
):
    """Get a new access token using a refresh token."""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing"
        )
    
    # Find user by refresh token
    query = select(User).where(User.refresh_token == refresh_token)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify refresh token
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username != user.username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Generate new access token
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout user by invalidating the refresh token."""
    # Clear refresh token from database
    current_user.refresh_token = None
    db.add(current_user)
    await db.commit()
    
    # Clear cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information."""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user information."""
    # Update only the provided fields
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return current_user

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Change current user's password."""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    if not validate_password_strength(password_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password does not meet requirements"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.add(current_user)
    await db.commit()
    
    return {"message": "Password updated successfully"}

@router.post("/enable-2fa", status_code=status.HTTP_200_OK)
async def enable_two_factor_auth(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Enable two-factor authentication for the current user."""
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication is already enabled"
        )
    
    # Generate and store OTP
    otp_code = generate_otp()
    otp = OTP(
        user_id=current_user.id,
        code=otp_code,
        expires_at=datetime.utcnow() + timedelta(minutes=15)
    )
    db.add(otp)
    
    # Enable 2FA after OTP verification
    current_user.two_factor_enabled = True
    db.add(current_user)
    await db.commit()
    
    # Send OTP via email
    background_tasks.add_task(
        send_otp_email,
        email=current_user.email,
        username=current_user.username,
        otp_code=otp_code
    )
    
    return {"message": "Two-factor authentication enabled. Please verify with the OTP sent to your email."}

@router.post("/disable-2fa", status_code=status.HTTP_200_OK)
async def disable_two_factor_auth(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Disable two-factor authentication for the current user."""
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication is not enabled"
        )
    
    # Disable 2FA
    current_user.two_factor_enabled = False
    db.add(current_user)
    await db.commit()
    
    return {"message": "Two-factor authentication disabled"}
