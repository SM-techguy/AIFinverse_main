from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import boto3
from botocore.exceptions import ClientError
import requests
import json
import random
import pandas as pd
from io import StringIO
import pytz
import numpy as np

app = FastAPI(title="AIFinverse Backend API", version="1.1")

# -------------------- CONFIG --------------------
SMTP_SERVER = "smtp.hostinger.com"
SMTP_PORT = 587
EMAIL_SENDER = "info@aifinverse.com"
EMAIL_PASSWORD = "$AIfin123" 

AWS_ACCESS_KEY_ID = "AKIA3NUGFTNOMHFO4X4A"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION = "us-east-1"
S3_BUCKET_NAME = "aifinverse"
S3_USERS_FILE_KEY = "users.json"
S3_REALTIME_ALERTS_CSV_KEY = "52_WH/realtime_alerts.csv"  # same directory as before

TAVILY_API_KEY = "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"
TAVILY_SEARCH_URL = "https://api.tavily.com/search"

TELEGRAM_BOT_TOKEN_US = "8515387318:AAEKWrh35aAG1vIhQe4Nde7pmRLvcNGggxY"
TELEGRAM_BOT_TOKEN_INDIA = "8461838689:AAH9SUFHliFXSOf5A1Yx5PhnBZ3uthQuZ_s"
TELEGRAM_BOT_TOKEN_WATCHLIST = "8236210636:AAH9n64cvol61iGhKOuw4tl17ita0YIfuVk"

# -------------------- MIDDLEWARE --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- MODELS --------------------
class RegisterUser(BaseModel):
    # Step 1 fields
    first_name: str
    last_name: str
    email: EmailStr
    country: str
    password: str
    confirm_password: str
    
    # Step 2 fields (optional with defaults)
    selected_market: Optional[str] = "India"  # India, US, or Both
    selected_strategies: Optional[List[str]] = []  # List of strategies

class MarketPreferenceUpdate(BaseModel):
    email: EmailStr
    market: str  
    strategy: str
    action: str

class StrategyEnum(str, Enum):
    Momentum = "Momentum Riders (52-week High/Low, All-Time High/Low)"
    Breakout = "Cycle Count Reversal"
    Reversal = "Mean Reversion"
    ContrabetsDTDB = "Double Top - Double Bottom (Contrabets)"
    ContrabetsCandle = "Topping Candle - Bottoming Candle (Contrabets)"
    ChartPatterns = "Pattern Formation"
    Picks = "Fundamental Picks (Earnings Season focused)"

class LoginUser(BaseModel):
    email: EmailStr
    password: str

class ContactUs(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class SubscribeRequest(BaseModel):
    email: EmailStr

class WatchlistRequest(BaseModel):
    user_id: str
    companies: List[str]  # company_name list

class WatchlistModifyRequest(BaseModel):
    user_id: str
    companies: List[str]  # company_name list
    action: str  # "add" or "remove"

# -------------------- S3 HELPERS --------------------
s3_client = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION)

def load_users():
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_USERS_FILE_KEY)
        return json.loads(response["Body"].read().decode("utf-8"))
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return []
        raise HTTPException(status_code=500, detail="S3 Load Error")

def save_users(users):
    s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=S3_USERS_FILE_KEY, Body=json.dumps(users, indent=4), ContentType="application/json")

def verify_password(plain, stored):
    return plain == stored

#--------------------------------------------------------------------------------------
def send_welcome_email(to_email: str, first_name: str):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email
        msg["Subject"] = "Welcome to AIFinverse 🚀"

        body = f"""
Hi {first_name},

Welcome to AIFinverse! 🎉
You have successfully registered with us.

🔹 Smart AI-powered trading insights
🔹 Personalized strategies
🔹 Market intelligence made simple

If you didn't register, please ignore this email.

Regards,
Team AIFinverse
info@aifinverse.com
"""
        msg.attach(MIMEText(body, "plain"))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Email sending failed:", e)

# def load_telegram_users():
#     try:
#         obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=TELEGRAM_USERS_KEY)
#         return json.loads(obj["Body"].read().decode())
#     except ClientError:
#         return []

# def save_telegram_users(users):
#     s3_client.put_object(
#         Bucket=S3_BUCKET_NAME,
#         Key=TELEGRAM_USERS_KEY,
#         Body=json.dumps(users, indent=4),
#         ContentType="application/json"
#     )

def store_telegram_chat_in_user(
    chat_id: int,
    telegram_username: str,
    first_name: str,
    bot: str
):
    users = load_users()
    updated = False

    for user in users:
        # Match by Telegram username
        if user.get("telegram", {}).get("username") == telegram_username:
            user.setdefault("telegram", {})
            user["telegram"]["username"] = telegram_username

            if bot == "India":
                user["telegram"]["india_chat_id"] = chat_id
            else:
                user["telegram"]["us_chat_id"] = chat_id

            user["telegram"]["subscribed_at"] = datetime.utcnow().isoformat()
            updated = True
            break

    if not updated:
        print(f"⚠️ Telegram user @{telegram_username} not found in users.json")

    save_users(users)

def store_telegram_chat_in_user(
    chat_id: int,
    telegram_username: str,
    first_name: str,
    bot: str
):
    users = load_users()
    updated = False

    for user in users:
        # Match by Telegram username
        if user.get("telegram", {}).get("username") == telegram_username:
            user.setdefault("telegram", {})
            user["telegram"]["username"] = telegram_username

            if bot == "India":
                user["telegram"]["india_chat_id"] = chat_id
            else:
                user["telegram"]["us_chat_id"] = chat_id

            user["telegram"]["subscribed_at"] = datetime.utcnow().isoformat()
            updated = True
            break

    if not updated:
        print(f"⚠️ Telegram user @{telegram_username} not found in users.json")

    save_users(users)

def link_telegram_to_user_by_email(
    email: str,
    chat_id: int,
    telegram_username: str,
    bot: str
):
    users = load_users()
    for user in users:
        if user["email"].lower() == email.lower():
            user.setdefault("telegram", {})
            user["telegram"]["username"] = telegram_username

            if bot == "India":
                user["telegram"]["india_chat_id"] = chat_id
            else:
                user["telegram"]["us_chat_id"] = chat_id

            user["telegram"]["linked_at"] = datetime.utcnow().isoformat()
            save_users(users)
            return True
    return False


# def store_telegram_chat(chat_id, username, first_name, bot: str):
#     users = load_telegram_users()
#     if any(u.get("chat_id") == chat_id and u.get("bot") == bot for u in users):
#         return
#     users.append({
#         "chat_id": chat_id,
#         "username": username,
#         "first_name": first_name,
#         "bot": bot,
#         "subscribed_at": datetime.utcnow().isoformat()
#     })
#     save_telegram_users(users)

def send_telegram_response(chat_id: int, text: str, bot_type: str = "India"):
    """Send message back via Telegram Bot API"""
    try:
        if bot_type == "India":
            token = TELEGRAM_BOT_TOKEN_INDIA
        else:
            token = TELEGRAM_BOT_TOKEN_US
            
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=5)
        print(f"📤 Telegram response sent: {response.status_code}")
        return response.json()
    except Exception as e:
        print(f"⚠️ Failed to send Telegram response: {e}")
        return None

#-------------------------------------------------------------------------------------

def send_contact_emails(name: str, email: str, subject: str, message: str):
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)

        # Email to user
        user_msg = MIMEMultipart()
        user_msg["From"] = EMAIL_SENDER
        user_msg["To"] = email
        user_msg["Subject"] = "Thanks for contacting AIFinverse"
        user_body = f"""
Hi {name},

Thank you for reaching out to AIFinverse.

We have received your message regarding:
"{subject}"

One of our team members will get back to you shortly.

Regards,
Team AIFinverse
info@aifinverse.com
"""
        user_msg.attach(MIMEText(user_body, "plain"))
        server.send_message(user_msg)

        # Email to admin
        admin_msg = MIMEMultipart()
        admin_msg["From"] = EMAIL_SENDER
        admin_msg["To"] = "soumyadeepmondal2372001@gmail.com"
        admin_msg["Subject"] = f"New Contact Request: {subject}"
        admin_body = f"""
New contact request received.

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
AIFinverse System
"""
        admin_msg.attach(MIMEText(admin_body, "plain"))
        server.send_message(admin_msg)
        server.quit()
    except Exception as e:
        print("Contact email sending failed:", e)
        raise HTTPException(status_code=500, detail="Failed to send contact emails")
    
import random
from datetime import timedelta

RESET_BASE_URL = "https://aifinverse.com/reset-password"

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email: str, otp: str):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = email
    msg["Subject"] = "AIFinverse Password Reset OTP"

    body = f"""
Your OTP for password reset is:

🔐 OTP: {otp}

This OTP is valid for 10 minutes.
If you did not request this, please ignore this email.

Regards,
Team AIFinverse
"""
    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

def send_reset_link_email(email: str, link: str):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = email
    msg["Subject"] = "Reset Your AIFinverse Password"

    body = f"""
Click the link below to reset your password:

{link}

This link is valid for 15 minutes.
If you did not request this, please ignore this email.

Regards,
Team AIFinverse
"""
    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

def send_subscription_email(email: str):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = email
        msg["Subject"] = "You’re now subscribed to AIFinverse 📈"

        body = f"""
Hi,

👋 Welcome to AIFinverse!

You have successfully subscribed to our market insights 📊  
You will be the **first to receive a notification whenever a new edition is published**.

🚀 What you can expect:
• Timely market insights  
• Strategy-driven analysis  
• Important updates straight to your inbox  

We’re excited to have you with us and look forward to helping you stay ahead in the markets.

If you did not subscribe to this service, you can safely ignore this email.

Warm regards,  
Team AIFinverse  
info@aifinverse.com
"""
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

    except Exception as e:
        print("❌ Subscription email failed:", e)
        raise HTTPException(status_code=500, detail="Failed to send subscription email")
    
def fetch_live_news():
    try:
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": "latest important stock market and financial news",
            "search_depth": "advanced",
            "max_results": 3,
            "include_answer": False,
            "include_raw_content": False
        }
        response = requests.post(TAVILY_SEARCH_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        news_list = []
        for item in data.get("results", []):
            news_list.append({
                "title": item.get("title"),
                "source": item.get("url"),
                "summary": item.get("content")
            })
        return news_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch live news: {str(e)}")


S3_EMAILS_FILE_KEY = "emails.json"

def load_subscribed_emails():
    try:
        response = s3_client.get_object(
            Bucket=S3_BUCKET_NAME,
            Key=S3_EMAILS_FILE_KEY
        )
        return json.loads(response["Body"].read().decode("utf-8"))
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return []
        raise HTTPException(status_code=500, detail="Failed to load emails.json")

def save_subscribed_emails(emails):
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=S3_EMAILS_FILE_KEY,
        Body=json.dumps(emails, indent=4),
        ContentType="application/json"
    )

S3_COMPANIES_FILE_KEY = "stock_universe_with_company_names.csv"

def load_companies_from_s3():
    try:
        response = s3_client.get_object(
            Bucket=S3_BUCKET_NAME,
            Key=S3_COMPANIES_FILE_KEY
        )
        csv_data = response["Body"].read().decode("utf-8")
        df = pd.read_csv(StringIO(csv_data))
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load companies CSV: {str(e)}")
    
def load_realtime_alerts_csv():
    try:
        response = s3_client.get_object(
            Bucket=S3_BUCKET_NAME,
            Key=S3_REALTIME_ALERTS_CSV_KEY
        )

        csv_data = response["Body"].read().decode("utf-8")

        df = pd.read_csv(StringIO(csv_data))

        # ✅ Convert date column properly
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date

        # ✅ Replace ALL NaN with None (JSON safe)
        df = df.replace({np.nan: None})

        return df

    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return pd.DataFrame()
        raise HTTPException(status_code=500, detail="Failed to load realtime alerts CSV")


def get_ist_today():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%Y-%m-%d")

def link_watchlist_bot_to_user(email: str):
    users = load_users()
    for user in users:
        if user["email"].lower() == email.lower():
            user["watchlist_linked"] = "yes"
            user["watchlist_linked_at"] = datetime.utcnow().isoformat()
            save_users(users)
            return True
    return False

def send_watchlist_telegram_response(chat_id: int, text: str):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN_WATCHLIST}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=5)
        return response.json()
    except Exception as e:
        print("Watchlist bot send error:", e)
        return None


# -------------------- AUTH ENDPOINTS --------------------

# -------------------- REGISTRATION ENDPOINT --------------------

@app.post("/register")
def register_user(user: RegisterUser):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    users = load_users()
    if any(u["email"].lower() == user.email.lower() for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")

    # FIXED: Initializing full structure with BOTH step 1 and step 2 data
    new_user = {
        "user_id": str(uuid4()),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email.lower(),
        "password": user.password,
        "registration_info": {
            "country": user.country,
            "selected_market": user.selected_market,  # Save market from step 2
            "selected_strategies": user.selected_strategies,  # Save strategies from step 2
            "registered_at": datetime.utcnow().isoformat(timespec='microseconds') + "Z"
        },
        "market_preferences": {
            "India": {"is_active": False, "strategies": []},
            "US": {"is_active": False, "strategies": []}
        },
        "telegram": {"username": None, "india_chat_id": None, "us_chat_id": None}
    }
    
    # ACTIVATE the selected market and add strategies
    if user.selected_market == "India":
        new_user["market_preferences"]["India"]["is_active"] = True
        new_user["market_preferences"]["India"]["strategies"] = user.selected_strategies
    elif user.selected_market == "US":
        new_user["market_preferences"]["US"]["is_active"] = True
        new_user["market_preferences"]["US"]["strategies"] = user.selected_strategies
    elif user.selected_market == "Both":
        # Activate both markets with selected strategies
        new_user["market_preferences"]["India"]["is_active"] = True
        new_user["market_preferences"]["India"]["strategies"] = user.selected_strategies
        new_user["market_preferences"]["US"]["is_active"] = True
        new_user["market_preferences"]["US"]["strategies"] = user.selected_strategies
    
    users.append(new_user)
    save_users(users)
    send_welcome_email(user.email, user.first_name)
    
    return {
        "message": "User registered successfully", 
        "user_id": new_user["user_id"], 
        "email": new_user["email"],
        "selected_market": user.selected_market,
        "selected_strategies": user.selected_strategies,
        "market_preferences": new_user["market_preferences"]
    }
    
#---------------------------------------------------------------------------------------------------------------------
@app.post("/login")
def login_user(login: LoginUser):
    users = load_users()
    for user in users:
        if user["email"] == login.email.lower() and user["password"] == login.password:
            return {
                "message": "Login successful",
                "user_id": user["user_id"],
                "email": user["email"],
                "profile": {
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "country": user["registration_info"]["country"]
                },
                "preferences": user["market_preferences"]
            }
    raise HTTPException(status_code=401, detail="Invalid Credentials")

# -------------------- PREFERENCE ENDPOINTS (For Alert Pages) --------------------

@app.post("/register/preferences")
def register_preferences(data: Dict[str, Any]):
    users = load_users()
    email = data.get("email", "").lower()
    selected_markets = data.get("markets", [])
    selected_strategies = data.get("strategies", [])

    for user in users:
        if user["email"] == email:
            for m in selected_markets:
                if m in user["market_preferences"]:
                    user["market_preferences"][m]["is_active"] = True
                    user["market_preferences"][m]["strategies"] = selected_strategies
            save_users(users)
            return {"message": "Preferences saved", "preferences": user["market_preferences"]}
    raise HTTPException(status_code=404, detail="User not found")

# -------------------- MODELS --------------------
# Update this model to match the specification
class UpdatePreferencesRequest(BaseModel):
    email: EmailStr
    add_markets: List[str] = []
    remove_markets: List[str] = []
    add_strategies: List[str] = []
    remove_strategies: List[str] = []

# Remove or update the old MarketPreferenceUpdate model if not used elsewhere
# class MarketPreferenceUpdate(BaseModel):  # Consider removing if not needed
#     email: EmailStr
#     market: str  
#     strategy: str

# -------------------- PREFERENCE ENDPOINTS --------------------

@app.put("/update/preferences")
def update_preferences(data: MarketPreferenceUpdate):
    users = load_users()
    
    for user in users:
        if user["email"].lower() == data.email.lower():
            market = data.market
            
            if market not in user["market_preferences"]:
                user["market_preferences"][market] = {"is_active": False, "strategies": []}
            
            # Handle ADD action
            if data.action == "add":
                user["market_preferences"][market]["is_active"] = True
                if data.strategy not in user["market_preferences"][market]["strategies"]:
                    user["market_preferences"][market]["strategies"].append(data.strategy)
            
            # Handle REMOVE action  
            elif data.action == "remove":
                if data.strategy in user["market_preferences"][market]["strategies"]:
                    user["market_preferences"][market]["strategies"].remove(data.strategy)
                
                # If no strategies left, deactivate market
                if len(user["market_preferences"][market]["strategies"]) == 0:
                    user["market_preferences"][market]["is_active"] = False
            
            save_users(users)
            return {
                "message": f"Strategy {data.action}ed successfully",
                "market": market,
                "strategies": user["market_preferences"][market]["strategies"]
            }
    
    raise HTTPException(status_code=404, detail="User not found")

#---------------------------------------------------------------------------------------

@app.get("/users/{user_id}")
def get_user_details(user_id: str):
    users = load_users()
    user = next((u for u in users if u.get("user_id") == user_id), None)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "registration_data": {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "country": user["registration_info"]["country"]
        },

        "india_alerts": user["market_preferences"].get("India", {"strategies": []}),
        "us_alerts": user["market_preferences"].get("US", {"strategies": []}),

        "registration_info": user.get("registration_info", {}),
        "market_preferences": user.get("market_preferences", {}),

        # ✅ NEW: Watchlist Data Added
        "watchlist": user.get("watchlist", {
            "India": [],
            "US": []
        }),

        # Optional: total count
        "watchlist_summary": {
            "india_count": len(user.get("watchlist", {}).get("India", [])),
            "us_count": len(user.get("watchlist", {}).get("US", [])),
            "total": len(user.get("watchlist", {}).get("India", [])) + len(user.get("watchlist", {}).get("US", []))
        }
    }


#----------------------------------------------------------------------
@app.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    users = load_users()
    for user in users:
        if user["email"] == data.email:
            otp = generate_otp()
            user["reset_otp"] = otp
            user["otp_expires_at"] = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
            save_users(users)

            send_otp_email(data.email, otp)
            return {"message": "OTP sent to your email"}

    raise HTTPException(status_code=404, detail="Email not registered")


@app.post("/verify-otp")
def verify_otp(data: VerifyOtpRequest):
    users = load_users()
    for user in users:
        if user["email"] == data.email:
            if user.get("reset_otp") != data.otp:
                raise HTTPException(status_code=400, detail="Invalid OTP")

            if datetime.utcnow() > datetime.fromisoformat(user["otp_expires_at"]):
                raise HTTPException(status_code=400, detail="OTP expired")

            token = str(uuid4())
            user["reset_token"] = token
            user["token_expires_at"] = (datetime.utcnow() + timedelta(minutes=15)).isoformat()
            save_users(users)

            reset_link = f"{RESET_BASE_URL}?token={token}"
            send_reset_link_email(data.email, reset_link)

            return {"message": "Password reset link sent"}

    raise HTTPException(status_code=404, detail="User not found")

@app.post("/reset-password")
def reset_password(data: ResetPasswordRequest):
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    users = load_users()
    for user in users:
        if user.get("reset_token") == data.token:
            if datetime.utcnow() > datetime.fromisoformat(user["token_expires_at"]):
                raise HTTPException(status_code=400, detail="Reset link expired")

            user["password"] = data.new_password
            user.pop("reset_otp", None)
            user.pop("otp_expires_at", None)
            user.pop("reset_token", None)
            user.pop("token_expires_at", None)

            save_users(users)
            return {"message": "Password reset successful"}

    raise HTTPException(status_code=400, detail="Invalid reset token")

@app.get("/news/live")
def get_live_news():
    news = fetch_live_news()
    return {"count": len(news), "updated_at": datetime.utcnow().isoformat(), "news": news}

@app.get("/whatsapp/redirect")
def whatsapp_redirect():
    phone_number = "971545964747"
    message = "Hello AIFinverse, I want to connect with you."

    whatsapp_url = (
        f"https://wa.me/{phone_number}"
        f"?text={requests.utils.quote(message)}"
    )

    return {
        "whatsapp_url": whatsapp_url
    }

@app.post("/contact-us")
def contact_us(data: ContactUs):
    send_contact_emails(data.name, data.email, data.subject, data.message)
    return {"message": "Thank you for reaching out. Our team will contact you soon."}

# -------------------- TELEGRAM WEBHOOKS --------------------
@app.post("/telegram/webhook")
async def telegram_webhook_us(request: Request):
    try:
        data = await request.json()
        print("🔥 US webhook data:", data)
        message = data.get("message")
        if not message:
            return {"status": "ignored"}
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        username = chat.get("username")
        first_name = chat.get("first_name")
        text = message.get("text", "")

        # 1️⃣ Handle /start
        if text.startswith("/start"):
            send_telegram_response(
                chat_id,
                "👋 Welcome to AIFinverse US!\n\nPlease reply with your *registered email* to link your account.",
                "US"
            )
            return {"status": "awaiting_email"}


        # 2️⃣ Handle email reply
        if "@" in text and "." in text:
            linked = link_telegram_to_user_by_email(
                email=text,
                chat_id=chat_id,
                telegram_username=username,
                bot="US"
            )

            if linked:
                send_telegram_response(
                    chat_id,
                    "✅ Your Telegram is now linked successfully! You’ll receive US market alerts 🇺🇸",
                    "US"
                )
            else:
                send_telegram_response(
                    chat_id,
                    "❌ Email not found. Please register first on https://aifinverse.com",
                    "US"
                )
        # if text.startswith("/start") and chat_id:
        #     store_telegram_chat_in_user(
        #         chat_id=chat_id,
        #         telegram_username=username,
        #         first_name=first_name,
        #         bot="US"
        #     )

        #     # Send welcome message
        #     welcome_msg = f"Welcome {first_name}! You're now subscribed to AIFinverse US alerts 🇺🇸"
        #     send_telegram_response(chat_id, welcome_msg, "US")
        return {"status": "ok"}
    except Exception as e:
        print("❌ Error in US webhook:", e)
        return {"status": "error", "detail": str(e)}

@app.post("/telegram/webhook/india")
async def telegram_webhook_india(request: Request):
    print("\n" + "="*60)
    print("🔥 INDIA WEBHOOK TRIGGERED")
    
    try:
        # Method 1: Try to read as JSON directly first
        try:
            data = await request.json()
            print(f"✅ Method 1: Successfully parsed as JSON")
            print(f"📦 Data keys: {list(data.keys())}")
            
        except json.JSONDecodeError:
            print(f"⚠️ Method 1: JSON decode failed, trying raw body...")
            
            # Method 2: Read raw body
            body_bytes = await request.body()
            body_str = body_bytes.decode('utf-8', errors='ignore')
            
            print(f"📦 Raw body ({len(body_str)} chars): '{body_str[:200]}'")
            
            if not body_str.strip():
                print("⚠️ Empty body received")
                return {"status": "ok", "note": "empty_body"}
            
            try:
                data = json.loads(body_str)
                print(f"✅ Method 2: Successfully parsed raw body as JSON")
            except json.JSONDecodeError as e:
                print(f"❌ Could not parse as JSON: {e}")
                print(f"❌ Body content: {body_str}")
                return {"status": "ok", "note": "invalid_json", "body_preview": body_str[:100]}
        
        # If we get here, we have valid data
        print(f"✅ Full data received: {json.dumps(data, indent=2)[:500]}...")
        
        # Process Telegram update
        if "message" in data:
            message = data["message"]
            chat = message.get("chat", {})
            chat_id = chat.get("id")
            username = chat.get("username", "unknown")
            first_name = chat.get("first_name", "User")
            text = message.get("text", "")
            
            print(f"👤 From: {first_name} (@{username})")
            print(f"💬 Text: '{text}'")

            # 1️⃣ Handle /start command
            if text.strip().startswith("/start"):
                send_telegram_response(
                    chat_id,
                    "👋 Welcome to AIFinverse!\n\nPlease reply with your *registered email* to link your account.",
                    "India"
                )
                return {"status": "awaiting_email"}


            # 2️⃣ Handle email reply
            if "@" in text and "." in text:
                linked = link_telegram_to_user_by_email(
                    email=text.strip(),
                    chat_id=chat_id,
                    telegram_username=username,
                    bot="India"
                )

                if linked:
                    send_telegram_response(
                        chat_id,
                        "✅ Your Telegram is now linked successfully! You’ll receive India market alerts 🇮🇳",
                        "India"
                    )
                else:
                    send_telegram_response(
                        chat_id,
                        "❌ Email not found. Please register first on https://aifinverse.com",
                        "India"
                    )

            
            # if text and text.strip().startswith("/start"):
            #     print(f"🎯 /start command detected!")
            #     store_telegram_chat_in_user(
            #         chat_id=chat_id,
            #         telegram_username=username,
            #         first_name=first_name,
            #         bot="India"
            #     )

            #     print(f"💾 User stored in S3: {first_name}")
                
            #     # Send response back to Telegram
            #     try:
            #         welcome_msg = f"Welcome {first_name}! You're now subscribed to AIFinverse India alerts 🇮🇳"
            #         send_telegram_response(chat_id, welcome_msg, "India")
        
        elif "callback_query" in data:
            print(f"🔄 Callback query received")
        else:
            print(f"📨 Unknown update type: {list(data.keys())}")
        
        print("="*60)
        return {"status": "ok", "processed": True, "data_received": True}
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*60)
        return {"status": "ok", "error": str(e)}
    
@app.post("/subscribe")
def subscribe_user(data: SubscribeRequest):
    # 🔹 Load existing subscribed emails from S3
    emails = load_subscribed_emails()

    # 🔹 Avoid duplicate subscriptions
    if any(e["email"].lower() == data.email.lower() for e in emails):
        return {
            "message": "Email already subscribed.",
            "email": data.email
        }

    # 🔹 Store email in emails.json (even if not registered)
    emails.append({
        "email": data.email.lower(),
        "subscribed_at": datetime.utcnow().isoformat()
    })
    save_subscribed_emails(emails)

    # 🔹 Send subscription confirmation email
    # (Already sent from info@aifinverse.com)
    send_subscription_email(data.email)

    return {
        "message": "Subscription successful. Please check your email.",
        "email": data.email,
        "subscribed_at": datetime.utcnow().isoformat()
    }

@app.get("/companies/india")
def get_india_companies():
    df = load_companies_from_s3()

    india_df = df[df["market"] == "India"]

    companies = [
        {
            "company_name": str(row["company_name"]),
            "base_symbol": str(row["base_symbol"])
        }
        for _, row in india_df.iterrows()
        if pd.notna(row["company_name"]) and pd.notna(row["base_symbol"])
    ]

    return {
        "market": "India",
        "count": len(companies),
        "companies": companies
    }

@app.get("/companies/us")
def get_us_companies():
    df = load_companies_from_s3()

    us_df = df[df["market"] == "US"]

    companies = [
        {
            "company_name": str(row["company_name"]),
            "base_symbol": str(row["base_symbol"])
        }
        for _, row in us_df.iterrows()
        if pd.notna(row["company_name"]) and pd.notna(row["base_symbol"])
    ]

    return {
        "market": "US",
        "count": len(companies),
        "companies": companies
    }

@app.post("/watchlist/update")
def update_watchlist(data: WatchlistRequest):
    users = load_users()
    df = load_companies_from_s3()

    # Build lookup: company_name -> full row
    company_map = {}
    for _, row in df.iterrows():
        company_map[row["company_name"]] = {
            "market": row["market"],
            "base_symbol": row["base_symbol"],
            "yahoo_symbol": row["yahoo_symbol"],
            "exchange": row["exchange"],
            "marketCap": row["marketCap"],
            "asset_type": row["asset_type"]
        }

    # Find user
    user = next((u for u in users if u["user_id"] == data.user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Init watchlist structure if missing
    user.setdefault("watchlist", {
        "India": [],
        "US": []
    })

    # Current counts per market
    india_count = len(user["watchlist"]["India"])
    us_count = len(user["watchlist"]["US"])

    # Process selections
    for company_name in data.companies:
        if company_name not in company_map:
            raise HTTPException(
                status_code=400,
                detail=f"Company not found in master CSV: {company_name}"
            )

        info = company_map[company_name]
        market = info["market"]  # India / US

        # Enforce per-market limit (20 each)
        if market == "India" and india_count >= 20:
            raise HTTPException(
                status_code=400,
                detail="India watchlist limit exceeded. Max 20 companies allowed."
            )

        if market == "US" and us_count >= 20:
            raise HTTPException(
                status_code=400,
                detail="US watchlist limit exceeded. Max 20 companies allowed."
            )

        entry = {
            "company_name": company_name,
            "base_symbol": info["base_symbol"]
        }

        # Avoid duplicates
        existing_names = [c["company_name"] for c in user["watchlist"][market]]
        if company_name not in existing_names:
            user["watchlist"][market].append(entry)

            # Increment counter after adding
            if market == "India":
                india_count += 1
            else:
                us_count += 1

    save_users(users)

    return {
        "message": "Watchlist updated successfully",
        "user_id": data.user_id,
        "watchlist": user["watchlist"],
        "india_count": len(user["watchlist"]["India"]),
        "us_count": len(user["watchlist"]["US"]),
        "total_selected": len(user["watchlist"]["India"]) + len(user["watchlist"]["US"])
    }

# -------------------- STARTUP EVENT --------------------
@app.on_event("startup")
async def startup_event():
    print("\n" + "="*60)
    print("🔥 AIFinverse Backend STARTED")
    print(f"📅 {datetime.utcnow().isoformat()}")
    print("="*60)
    print("Registered Routes:")
    for route in app.routes:
        if hasattr(route, "methods"):
            methods = ', '.join(route.methods)
            print(f"  {methods:15} {route.path}")
    print("="*60 + "\n")

@app.post("/watchlist/modify/india")
def modify_watchlist_india(data: WatchlistModifyRequest):
    users = load_users()
    df = load_companies_from_s3()

    # Build company lookup
    company_map = {
        row["company_name"]: {
            "market": row["market"],
            "base_symbol": row["base_symbol"]
        }
        for _, row in df.iterrows()
    }

    # Find user
    user = next((u for u in users if u["user_id"] == data.user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Init watchlist
    user.setdefault("watchlist", {"India": [], "US": []})

    current_total = len(user["watchlist"]["India"]) + len(user["watchlist"]["US"])

    # ---------------- ADD MODE ----------------
    if data.action == "add":
        if current_total + len(data.companies) > 20:
            raise HTTPException(
                status_code=400,
                detail="Watchlist limit exceeded. Max 20 total companies."
            )

        for company_name in data.companies:
            if company_name not in company_map:
                raise HTTPException(status_code=400, detail=f"Company not found: {company_name}")

            info = company_map[company_name]

            # Ensure India market only
            if info["market"] != "India":
                raise HTTPException(status_code=400, detail=f"{company_name} is not an India stock")

            entry = {
                "company_name": company_name,
                "base_symbol": info["base_symbol"]
            }

            existing = [c["company_name"] for c in user["watchlist"]["India"]]
            if company_name not in existing:
                user["watchlist"]["India"].append(entry)

    # ---------------- REMOVE MODE ----------------
    elif data.action == "remove":
        user["watchlist"]["India"] = [
            c for c in user["watchlist"]["India"]
            if c["company_name"] not in data.companies
        ]

    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'add' or 'remove'")

    save_users(users)

    return {
        "message": f"India watchlist {data.action} successful",
        "market": "India",
        "user_id": data.user_id,
        "watchlist": user["watchlist"]["India"],
        "total_selected": len(user["watchlist"]["India"]) + len(user["watchlist"]["US"])
    }

@app.post("/watchlist/modify/us")
def modify_watchlist_us(data: WatchlistModifyRequest):
    users = load_users()
    df = load_companies_from_s3()

    company_map = {
        row["company_name"]: {
            "market": row["market"],
            "base_symbol": row["base_symbol"]
        }
        for _, row in df.iterrows()
    }

    user = next((u for u in users if u["user_id"] == data.user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.setdefault("watchlist", {"India": [], "US": []})

    current_total = len(user["watchlist"]["India"]) + len(user["watchlist"]["US"])

    # ---------------- ADD MODE ----------------
    if data.action == "add":
        if current_total + len(data.companies) > 20:
            raise HTTPException(
                status_code=400,
                detail="Watchlist limit exceeded. Max 20 total companies."
            )

        for company_name in data.companies:
            if company_name not in company_map:
                raise HTTPException(status_code=400, detail=f"Company not found: {company_name}")

            info = company_map[company_name]

            # Ensure US market only
            if info["market"] != "US":
                raise HTTPException(status_code=400, detail=f"{company_name} is not a US stock")

            entry = {
                "company_name": company_name,
                "base_symbol": info["base_symbol"]
            }

            existing = [c["company_name"] for c in user["watchlist"]["US"]]
            if company_name not in existing:
                user["watchlist"]["US"].append(entry)

    # ---------------- REMOVE MODE ----------------
    elif data.action == "remove":
        user["watchlist"]["US"] = [
            c for c in user["watchlist"]["US"]
            if c["company_name"] not in data.companies
        ]

    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'add' or 'remove'")

    save_users(users)

    return {
        "message": f"US watchlist {data.action} successful",
        "market": "US",
        "user_id": data.user_id,
        "watchlist": user["watchlist"]["US"],
        "total_selected": len(user["watchlist"]["India"]) + len(user["watchlist"]["US"])
    }

@app.get("/admin/users")
def get_all_users():
    users = load_users()

    if not users:
        return {
            "count": 0,
            "users": []
        }

    # OPTIONAL: Remove passwords before returning (recommended for security)
    sanitized_users = []
    for user in users:
        user_copy = user.copy()
        user_copy.pop("password", None)
        user_copy.pop("reset_otp", None)
        user_copy.pop("reset_token", None)
        sanitized_users.append(user_copy)

    return {
        "count": len(sanitized_users),
        "users": sanitized_users,
        "fetched_at": datetime.utcnow().isoformat()
    }

@app.get("/alerts/live/india")
def get_today_india_alerts():
    df = load_realtime_alerts_csv()

    if df.empty:
        return {
            "market": "India",
            "date": get_ist_today(),
            "timezone": "Asia/Kolkata",
            "count": 0,
            "alerts": []
        }

    today = get_ist_today()

    # Ensure date column is string
    df["date"] = df["date"].astype(str)

    # Filter by today (IST date) and India market
    india_df = df[
        (df["date"] == today) &
        (df["market"] == "India")
    ]

    # Sort by timestamp descending
    if "timestamp" in india_df.columns:
        india_df = india_df.sort_values(by="timestamp", ascending=False)

    alerts = india_df.to_dict(orient="records")

    return {
        "market": "India",
        "date": today,
        "timezone": "Asia/Kolkata",
        "count": len(alerts),
        "alerts": alerts
    }

@app.get("/alerts/live/us")
def get_today_us_alerts():
    df = load_realtime_alerts_csv()

    if df.empty:
        return {
            "market": "US",
            "date": get_ist_today(),
            "timezone": "Asia/Kolkata",
            "count": 0,
            "alerts": []
        }

    today = get_ist_today()

    df["date"] = df["date"].astype(str)

    # Filter by today and US market
    us_df = df[
        (df["date"] == today) &
        (df["market"] == "US")
    ]

    # Sort by timestamp descending
    if "timestamp" in us_df.columns:
        us_df = us_df.sort_values(by="timestamp", ascending=False)

    alerts = us_df.to_dict(orient="records")

    return {
        "market": "US",
        "date": today,
        "timezone": "Asia/Kolkata",
        "count": len(alerts),
        "alerts": alerts
    }

@app.get("/alerts/history/india")
def get_india_alert_history():
    df = load_realtime_alerts_csv()

    if df.empty:
        return {
            "market": "India",
            "timezone": "Asia/Kolkata",
            "count": 0,
            "alerts": []
        }

    ist = pytz.timezone("Asia/Kolkata")
    today = datetime.now(ist).date()
    seven_days_ago = today - timedelta(days=7)

    # Normalize market column
    df["market"] = df["market"].astype(str).str.upper().str.strip()

    india_df = df[
        (df["date"] >= seven_days_ago) &
        (df["date"] <= today) &
        (df["market"] == "INDIA")
    ]

    alerts = india_df.to_dict(orient="records")

    return {
        "market": "India",
        "timezone": "Asia/Kolkata",
        "from_date": str(seven_days_ago),
        "to_date": str(today),
        "count": len(alerts),
        "alerts": alerts
    }


@app.get("/alerts/history/us")
def get_us_alert_history():
    df = load_realtime_alerts_csv()

    if df.empty:
        return {
            "market": "US",
            "timezone": "Asia/Kolkata",
            "days": 7,
            "count": 0,
            "alerts": []
        }

    ist = pytz.timezone("Asia/Kolkata")
    today = datetime.now(ist).date()
    seven_days_ago = today - timedelta(days=7)

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date

    # Filter last 7 days and US market
    us_df = df[
        (df["date"] >= seven_days_ago) &
        (df["date"] <= today) &
        (df["market"] == "US")
    ]

    # Sort by date + timestamp (latest first)
    if "timestamp" in us_df.columns:
        us_df = us_df.sort_values(
            by=["date", "timestamp"],
            ascending=False
        )
    else:
        us_df = us_df.sort_values(by="date", ascending=False)

    alerts = us_df.to_dict(orient="records")

    return {
        "market": "US",
        "timezone": "Asia/Kolkata",
        "from_date": str(seven_days_ago),
        "to_date": str(today),
        "count": len(alerts),
        "alerts": alerts
    }

@app.post("/telegram/webhook/watchlist")
async def telegram_webhook_watchlist(request: Request):
    try:
        print("\n🔥 WATCHLIST WEBHOOK TRIGGERED")

        # ---- SAFE JSON PARSING ----
        try:
            body = await request.body()

            if not body:
                print("⚠️ Empty body received")
                return {"status": "ignored", "reason": "empty_body"}

            body_str = body.decode("utf-8", errors="ignore")

            if not body_str.strip():
                print("⚠️ Blank body received")
                return {"status": "ignored", "reason": "blank_body"}

            data = json.loads(body_str)

        except Exception as e:
            print("❌ JSON parsing failed:", e)
            print("Raw body:", body_str if 'body_str' in locals() else "None")
            return {"status": "ignored", "reason": "invalid_json"}

        # ---- PROCESS MESSAGE ----
        message = data.get("message")
        if not message:
            return {"status": "ignored", "reason": "no_message"}

        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = message.get("text", "").strip()

        # 1️⃣ Handle /start
        if text.startswith("/start"):
            send_watchlist_telegram_response(
                chat_id,
                "👋 Welcome to AIFinverse Watchlist Bot!\n\nPlease reply with your *registered email* to link your watchlist."
            )
            return {"status": "awaiting_email"}

        # 2️⃣ Handle Email Linking
        if "@" in text and "." in text:
            linked = link_watchlist_bot_to_user(text)

            if linked:
                send_watchlist_telegram_response(
                    chat_id,
                    "✅ Watchlist bot linked successfully!\n\nYou will now receive watchlist notifications 📊"
                )
            else:
                send_watchlist_telegram_response(
                    chat_id,
                    "❌ Email not found. Please register first on https://aifinverse.com"
                )

        return {"status": "ok"}

    except Exception as e:
        print("❌ Watchlist webhook unexpected error:", e)
        return {"status": "ok"}

