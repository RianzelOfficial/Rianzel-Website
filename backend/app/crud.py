from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import Optional
from .models import User
from .schemas.user import UserCreate
from app.services.security import get_password_hash

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Create a new user."""
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        date_of_birth=user.date_of_birth,
        country=user.country
    )
    
    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError:
        await db.rollback()
        raise ValueError("Username or email already exists")

async def get_user(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username."""
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email."""
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_user(db: AsyncSession, user_id: int, user_data: dict) -> Optional[User]:
    """Update user information."""
    user = await db.get(User, user_id)
    if user:
        for key, value in user_data.items():
            setattr(user, key, value)
        await db.commit()
        await db.refresh(user)
        return user
    return None

async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Delete user."""
    user = await db.get(User, user_id)
    if user:
        await db.delete(user)
        await db.commit()
        return True
    return False
