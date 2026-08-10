import smtplib
from email.message import EmailMessage
import logging

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Email"])

class VerificationRequest(BaseModel):
    email: str
    code: str

def send_email_sync(recipient: str, code: str):
    """Synchronous function to send email via SMTP."""
    if not settings.smtp_email or not settings.smtp_password:
        logger.error("SMTP_EMAIL or SMTP_PASSWORD not configured.")
        raise ValueError("Email service is not configured.")

    msg = EmailMessage()
    msg["Subject"] = "Your GameHub Verification Code"
    msg["From"] = f"GameHub <{settings.smtp_email}>"
    msg["To"] = recipient

    # HTML Email Template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 40px; margin: 0; }}
            .container {{ max-width: 500px; margin: 0 auto; background-color: #1e293b; padding: 40px; border-radius: 16px; border: 1px solid #334155; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
            .logo {{ width: 64px; height: 64px; margin-bottom: 20px; }}
            h1 {{ color: #38bdf8; font-size: 24px; margin-bottom: 10px; font-weight: 700; letter-spacing: 0.5px; }}
            p {{ color: #94a3b8; font-size: 15px; line-height: 1.6; margin-bottom: 30px; }}
            .code-box {{ background-color: #0f172a; border: 2px dashed #38bdf8; border-radius: 12px; padding: 24px; margin-bottom: 30px; }}
            .code {{ font-size: 42px; font-weight: 800; color: #f8fafc; letter-spacing: 8px; font-family: monospace; text-shadow: 0 0 15px rgba(56, 189, 248, 0.4); }}
            .footer {{ font-size: 13px; color: #64748b; margin-top: 30px; border-top: 1px solid #334155; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Using a standard gamepad emoji as fallback logo -->
            <div style="font-size: 48px; margin-bottom: 15px;">🎮</div>
            <h1>Security Verification</h1>
            <p>You requested a verification code to proceed with your checkout on GameHub. Please enter the code below to securely complete your purchase.</p>
            
            <div class="code-box">
                <div class="code">{code}</div>
            </div>
            
            <p style="margin-bottom: 0;">This code will expire in 10 minutes.<br>If you did not request this, please ignore this email.</p>
            
            <div class="footer">
                &copy; 2026 GameHub. All rights reserved.<br>
                Secure Checkout System
            </div>
        </div>
    </body>
    </html>
    """

    msg.add_alternative(html_content, subtype='html')

    try:
        # Standard Gmail SMTP connection
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.smtp_email, settings.smtp_password)
            server.send_message(msg)
            logger.info(f"Verification email sent to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e}")
        raise e

@router.post("/email/send-verification", summary="Send verification code via email")
def send_verification(request: VerificationRequest, background_tasks: BackgroundTasks):
    """
    Sends a 4-digit verification code to the user's email address.
    Uses BackgroundTasks so the API responds immediately without waiting for SMTP.
    """
    if not settings.smtp_email or not settings.smtp_password:
        # Return 503 so the frontend knows the service isn't set up
        raise HTTPException(status_code=503, detail="Email service is not configured on the server.")

    # Queue the email sending in the background
    background_tasks.add_task(send_email_sync, request.email, request.code)
    
    return {"message": "Verification email queued successfully"}
