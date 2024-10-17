import pickle
import random
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from models import schemas
from utilities import utils
from utilities.key_generator import generator
from utilities.settings import setting
from models.users_model import UsersModel
from utilities.api_limiter import ApiLimitDependency


def generate_otp(length=6):
    return "".join([str(random.randint(0, 9)) for _ in range(length)])


def send_otp_via_email(sender_email, sender_password, recipient_email, otp, User):
    subject = "Your ChatNet OTP for 2-Step Verification"
    message = (
        """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .header {
            background-color: #4CAF50;
            padding: 10px;
            text-align: center;
            color: white;
            border-radius: 8px 8px 0 0;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
        }
        .body {
            padding: 20px;
        }
        .body p {
            font-size: 16px;
            color: #333;
        }
        .otp-box {
            font-size: 22px;
            font-weight: bold;
            background-color: #f0f0f0;
            padding: 15px;
            text-align: center;
            letter-spacing: 5px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .footer {
            text-align: center;
            font-size: 14px;
            color: #777;
            padding: 10px;
        }
        .footer p {
            margin: 0;
        }
        a {
            color: #4CAF50;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ChatNet</h1>
        </div>
        <div class="body">
            <p>Dear """
        + User
        + """,</p>
            <p>Thank you for using ChatNet! To complete your login, please use the One-Time Password (OTP) below for two-step verification:</p>
            <div class="otp-box">"""
        + str(otp)
        + """</div>
            <p>This OTP is valid for the next 5 minutes. Please do not share it with anyone.</p>
            <p>If you did not request this OTP, you can safely ignore this email.</p>
            <p>Best regards,<br>The ChatNet Team</p>
        </div>
        <div class="footer">
            <p>© """
        + str(datetime.now().year)
        + """ ChatNet. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
    )

    # Create email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject

    # Attach the message
    msg.attach(MIMEText(message, "html"))

    # Setup the server
    server = smtplib.SMTP(
        "smtp.gmail.com", 587
    )  # Use Gmail's SMTP server (or your preferred one)
    server.starttls()
    server.login(sender_email, sender_password)

    # Send the email
    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()


router = APIRouter(prefix="/OTP", tags=["OTP"])

send_otp_api_limit = ApiLimitDependency(req_count=1, time_frame_in_sec=15)


@router.post("/send-otp")
def send_otp(
    secret_string: schemas.OtpSecretKey,
    background_tasks: BackgroundTasks,
    rds: utils.rds_dependency,
    limit: Annotated[ApiLimitDependency, Depends(send_otp_api_limit)],
):
    cache = rds.get(secret_string.secret_key)
    if not cache:
        raise HTTPException(status_code=403, detail="invalid secret key")

    otp_verification_secret_key = generator(64)

    rds.delete(secret_string.secret_key)
    OTP = generate_otp()
    final_OTP_key = str(OTP) + otp_verification_secret_key
    rds.setex(final_OTP_key, 5 * 60, cache)

    data = pickle.loads(cache)
    recipient_email = data["email"]
    user = data["user_name"]

    background_tasks.add_task(
        send_otp_via_email,
        setting.otp_email,
        setting.otp_password,
        recipient_email,
        OTP,
        User=user,
    )

    return {
        "message": "OTP has been sent",
        "otp_verification_secret_key": otp_verification_secret_key,
    }


verify_otp_api_limit = ApiLimitDependency(req_count=5, time_frame_in_sec=10)


@router.post("/verify-otp", response_model=schemas.UserOut)
def verify_otp(
    data: schemas.VerifyOtp,
    rds: utils.rds_dependency,
    db: utils.db_dependency,
    request: Request,
    limit: Annotated[ApiLimitDependency, Depends(verify_otp_api_limit)],
):
    final_OTP_key = str(data.OTP) + data.secret_key
    cache = rds.get(final_OTP_key)
    if not cache:
        raise HTTPException(status_code=403, detail="invalid credentials")

    return UsersModel.create_user_after_otp(pickle.loads(cache), db, request)
