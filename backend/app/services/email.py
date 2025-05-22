from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from ..config import settings
import os

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@nazzelandrian.site"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TIMEOUT=30
)

async def send_verification_email(email: str, token: str, background_tasks: BackgroundTasks):
    """Send email verification link."""
    message = MessageSchema(
        subject="Verify Your Email",
        recipients=[email],
        body=f"Click the link to verify your email: {settings.VITE_API_BASE_URL}/auth/verify/{token}",
        subtype="html",
        headers={"Reply-To": "noreply@nazzelandrian.site"}
    )
    
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)

async def send_password_reset_email(email: str, token: str, background_tasks: BackgroundTasks):
    """Send password reset link."""
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        body=f"Click the link to reset your password: {settings.VITE_API_BASE_URL}/auth/reset-password/{token}",
        subtype="html",
        headers={"Reply-To": "noreply@nazzelandrian.site"}
    )
    
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)

async def send_verification_email(email: str, token: str, background_tasks: BackgroundTasks):
    """Send email verification link."""
    message = MessageSchema(
        subject="Verify Your Email",
        recipients=[email],
        body=f"Click the link to verify your email: {settings.VITE_API_BASE_URL}/auth/verify/{token}",
        subtype="html",
    )
    
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)

async def send_password_reset_email(email: str, token: str, background_tasks: BackgroundTasks):
    """Send password reset link."""
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        body=f"Click the link to reset your password: {settings.VITE_API_BASE_URL}/auth/reset-password/{token}",
        subtype="html",
    )
    
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
