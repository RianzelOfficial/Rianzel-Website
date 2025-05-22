from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.database import get_db, engine
from app.models import Base
from app.schemas.user import UserResponse, UserCreate, UserLogin
from app.schemas.post import PostResponse, PostCreate
from app.schemas.forum import Category, Comment, CommentCreate, Like, LikeCreate
from app.schemas.notification import Notification
from app.models import User as UserModel
from app.crud import create_user
from app.services import security, auth

app = FastAPI(title="Rianzel Official Website API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Welcome to Rianzel Official Website API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Authentication endpoints
@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.post("/api/auth/login", response_model=UserResponse)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    return security.authenticate_user(db, user.username, user.password)

# User endpoints
@app.get("/api/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserModel = Depends(security.get_current_user)):
    return current_user

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user(db, user_id)

# Post endpoints
@app.post("/api/posts", response_model=PostResponse)
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    return crud.create_post(db=db, post=post)

@app.get("/api/posts", response_model=List[PostResponse])
async def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_posts(db, skip=skip, limit=limit)

@app.get("/api/posts/{post_id}", response_model=PostResponse)
async def read_post(post_id: int, db: Session = Depends(get_db)):
    return crud.get_post(db, post_id)

# Category endpoints
@app.get("/api/categories", response_model=List[Category])
async def read_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)

# Comment endpoints
@app.post("/api/comments", response_model=Comment)
async def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    return crud.create_comment(db=db, comment=comment)

# Like endpoints
@app.post("/api/likes", response_model=Like)
async def create_like(like: LikeCreate, db: Session = Depends(get_db)):
    return crud.create_like(db=db, like=like)

# Notification endpoints
@app.get("/api/notifications", response_model=List[Notification])
async def read_notifications(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(security.get_current_user)
):
    return crud.get_notifications(db, current_user.id, skip, limit)

# Maintenance mode endpoint
@app.get("/api/maintenance")
async def get_maintenance_status():
    return {"is_maintenance": os.environ.get("MAINTENANCE_MODE", "false") == "true"}
