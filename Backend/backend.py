from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
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
S3_REALTIME_ALERTS_INDIA_JSON_KEY = "52_WH/realtime_alerts_INDIA.json"  # India alerts JSON file
S3_REALTIME_ALERTS_US_JSON_KEY = "52_WH/realtime_alerts_US.json"  # US alerts JSON file

TAVILY_API_KEY = "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"
TAVILY_SEARCH_URL = "https://api.tavily.com/search"

TELEGRAM_BOT_TOKEN_US = "8515387318:AAEKWrh35aAG1vIhQe4Nde7pmRLvcNGggxY"
TELEGRAM_BOT_TOKEN_INDIA = "8461838689:AAH9SUFHliFXSOf5A1Yx5PhnBZ3uthQuZ_s"
TELEGRAM_BOT_TOKEN_WATCHLIST = "8236210636:AAH9n64cvol61iGhKOuw4tl17ita0YIfuVk"

S3_POSTS_FILE_KEY = "posts/posts.json"
S3_POST_IMAGES_KEY = "posts/images/"
S3_COMMENTS_FILE_KEY = "posts/comments.json"
S3_NEWSLETTERS_FILE_KEY = "posts/newsletters.json"

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
    ContrabetsDTDB = "Swing Trade"
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

class PostCreate(BaseModel):
    title: str
    subtitle: Optional[str] = None
    content: str  # HTML content from rich text editor
    excerpt: Optional[str] = None
    featured_image_url: Optional[str] = None
    status: str = "published"  # draft, published
    category: Optional[str] = None
    tags: List[str] = []
    meta_description: Optional[str] = None
    is_featured: bool = False

class PostUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    featured_image_url: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    meta_description: Optional[str] = None
    is_featured: Optional[bool] = None

class PostResponse(BaseModel):
    id: str
    title: str
    subtitle: Optional[str] = None
    content: str
    excerpt: Optional[str] = None
    featured_image_url: Optional[str] = None
    author: Dict[str, str]
    status: str
    category: Optional[str] = None
    tags: List[str]
    meta_description: Optional[str] = None
    is_featured: bool
    read_time: int
    views: int
    likes: int
    created_at: str
    updated_at: str
    published_at: Optional[str] = None

class PostListResponse(BaseModel):
    id: str
    title: str
    subtitle: Optional[str] = None
    excerpt: Optional[str] = None
    featured_image_url: Optional[str] = None
    author_name: str
    category: Optional[str] = None
    tags: List[str]
    read_time: int
    views: int
    likes: int
    created_at: str
    published_at: Optional[str] = None

class CommentCreate(BaseModel):
    post_id: str
    author_name: str
    author_email: EmailStr
    content: str
    parent_id: Optional[str] = None

class CommentResponse(BaseModel):
    id: str
    post_id: str
    author_name: str
    author_email: str
    content: str
    parent_id: Optional[str] = None
    likes: int
    created_at: str
    replies: List['CommentResponse'] = []

class NewsletterSend(BaseModel):
    post_id: str
    subject: Optional[str] = None
    custom_message: Optional[str] = None


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
    
# Add these two new functions to load India and US alerts separately
def load_realtime_alerts_india_json():
    try:
        response = s3_client.get_object(
            Bucket=S3_BUCKET_NAME,
            Key=S3_REALTIME_ALERTS_INDIA_JSON_KEY
        )

        json_data = json.loads(response["Body"].read().decode("utf-8"))

        all_records = []

        # ✅ Handle dictionary format: { "2026-02-23": [ {...}, {...} ] }
        if isinstance(json_data, dict):
            for date_key, alerts_list in json_data.items():
                if isinstance(alerts_list, list):
                    for alert in alerts_list:
                        alert["date"] = date_key  # ensure date consistency
                        all_records.append(alert)

        # ✅ Handle list format (fallback safety)
        elif isinstance(json_data, list):
            all_records = json_data

        # Convert to DataFrame
        df = pd.DataFrame(all_records)

        # Convert date column to datetime.date
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date

        # Replace NaN with None
        df = df.replace({np.nan: None})

        return df

    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            print(f"⚠️ India JSON file not found at {S3_REALTIME_ALERTS_INDIA_JSON_KEY}")
            return pd.DataFrame()
        raise HTTPException(status_code=500, detail=f"Failed to load India alerts JSON: {str(e)}")

    except Exception as e:
        print(f"❌ Unexpected error loading India JSON: {e}")
        return pd.DataFrame()


def load_realtime_alerts_us_json():
    try:
        response = s3_client.get_object(
            Bucket=S3_BUCKET_NAME,
            Key=S3_REALTIME_ALERTS_US_JSON_KEY
        )

        json_data = json.loads(response["Body"].read().decode("utf-8"))

        all_records = []

        # ✅ Handle dictionary format: { "2026-02-23": [ {...}, {...} ] }
        if isinstance(json_data, dict):
            for date_key, alerts_list in json_data.items():
                if isinstance(alerts_list, list):
                    for alert in alerts_list:
                        alert["date"] = date_key  # ensure date consistency
                        all_records.append(alert)

        # Convert to DataFrame
        df = pd.DataFrame(all_records)

        # Convert date column to datetime.date
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date

        df = df.replace({np.nan: None})

        return df

    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            print(f"⚠️ US JSON file not found at {S3_REALTIME_ALERTS_US_JSON_KEY}")
            return pd.DataFrame()
        raise HTTPException(status_code=500, detail=f"Failed to load US alerts JSON: {str(e)}")

    except Exception as e:
        print(f"❌ Unexpected error loading US JSON: {e}")
        return pd.DataFrame()


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

def load_posts():
    """Load all posts from S3"""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_POSTS_FILE_KEY)
        return json.loads(response["Body"].read().decode("utf-8"))
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return []
        raise HTTPException(status_code=500, detail="Failed to load posts")

def save_posts(posts):
    """Save all posts to S3"""
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=S3_POSTS_FILE_KEY,
        Body=json.dumps(posts, indent=4, default=str),
        ContentType="application/json"
    )

def load_comments():
    """Load all comments from S3"""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_COMMENTS_FILE_KEY)
        return json.loads(response["Body"].read().decode("utf-8"))
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return []
        raise HTTPException(status_code=500, detail="Failed to load comments")

def save_comments(comments):
    """Save all comments to S3"""
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=S3_COMMENTS_FILE_KEY,
        Body=json.dumps(comments, indent=4, default=str),
        ContentType="application/json"
    )

def load_newsletters():
    """Load newsletter sending history from S3"""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_NEWSLETTERS_FILE_KEY)
        return json.loads(response["Body"].read().decode("utf-8"))
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return []
        raise HTTPException(status_code=500, detail="Failed to load newsletters")

def save_newsletters(newsletters):
    """Save newsletter history to S3"""
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=S3_NEWSLETTERS_FILE_KEY,
        Body=json.dumps(newsletters, indent=4, default=str),
        ContentType="application/json"
    )

def calculate_read_time(content: str) -> int:
    """Calculate read time in minutes based on content length"""
    words_per_minute = 200
    word_count = len(content.split())
    read_time = max(1, round(word_count / words_per_minute))
    return read_time

def process_post_image(image_data: bytes, filename: str) -> str:
    """Process and upload post image to S3"""
    try:
        # Generate unique filename
        ext = filename.split('.')[-1].lower()
        unique_filename = f"{uuid4()}.{ext}"
        s3_key = f"{S3_POST_IMAGES_KEY}{unique_filename}"
        
        # Optional: Resize/optimize image
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Resize if too large (max width 1200px)
        if img.width > 1200:
            ratio = 1200 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((1200, new_height), Image.Resampling.LANCZOS)
        
        # Save to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
        img_byte_arr = img_byte_arr.getvalue()
        
        # Upload to S3
        content_type = f"image/{ext}" if ext != 'jpg' else "image/jpeg"
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=img_byte_arr,
            ContentType=content_type,
            CacheControl="max-age=31536000"
        )
        
        # Return public URL
        return f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")

def send_newsletter_email(post_title: str, post_excerpt: str, post_url: str, subscriber_email: str, custom_message: Optional[str] = None):
    """Send newsletter email to subscriber"""
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = subscriber_email
        msg["Subject"] = f"📬 New Post: {post_title} - AIFinverse"

        body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white;">
        <h1 style="margin: 0;">AIFinverse</h1>
        <p style="margin: 10px 0 0; opacity: 0.9;">Market Insights & Analysis</p>
    </div>
    
    <div style="padding: 30px;">
        <h2 style="color: #333; margin-top: 0;">{post_title}</h2>
        
        {f'<p style="color: #666; font-style: italic;">{post_excerpt}</p>' if post_excerpt else ''}
        
        {f'<div style="background: #f5f5f5; padding: 15px; border-left: 4px solid #667eea; margin: 20px 0;">{custom_message}</div>' if custom_message else ''}
        
        <p>We've just published a new market insight. Click the button below to read the full post:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{post_url}" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Read Full Post →</a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <p style="color: #999; font-size: 12px; text-align: center;">
            You're receiving this because you subscribed to AIFinverse newsletter.<br>
            <a href="https://aifinverse.com/unsubscribe?email={subscriber_email}" style="color: #667eea;">Unsubscribe</a>
        </p>
    </div>
</body>
</html>
"""
        msg.attach(MIMEText(body, "html"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
    except Exception as e:
        print(f"❌ Newsletter email failed for {subscriber_email}: {e}")
        # Don't raise exception - continue with other subscribers


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

# Update the live alerts endpoints
@app.get("/alerts/live/india")
def get_today_india_alerts():
    df = load_realtime_alerts_india_json()

    if df.empty:
        return {
            "market": "India",
            "date": get_ist_today(),
            "timezone": "Asia/Kolkata",
            "count": 0,
            "alerts": []
        }

    # Get today's date in IST
    ist = pytz.timezone("Asia/Kolkata")
    today_ist = datetime.now(ist).date()
    
    print(f"📅 Today's IST date: {today_ist}")
    print(f"📊 Total records in India JSON: {len(df)}")
    
    # Filter by today (IST date) - No need to filter by market since it's India-specific file
    india_df = df[df["date"] == today_ist]

    print(f"✅ Found {len(india_df)} India alerts for today")

    # Sort by timestamp descending if available
    if "timestamp" in india_df.columns and not india_df.empty:
        india_df = india_df.sort_values(by="timestamp", ascending=False)

    # Convert to records
    alerts = india_df.to_dict(orient="records")

    return {
        "market": "India",
        "date": today_ist.strftime("%Y-%m-%d"),
        "timezone": "Asia/Kolkata",
        "count": len(alerts),
        "alerts": alerts
    }

@app.get("/alerts/live/us")
def get_today_us_alerts():
    df = load_realtime_alerts_us_json()

    if df.empty:
        return {
            "market": "US",
            "date": datetime.now(pytz.UTC).strftime("%Y-%m-%d"),
            "timezone": "UTC",
            "count": 0,
            "alerts": []
        }

    # Get today's date in UTC (since US data is stored in UTC)
    utc_now = datetime.now(pytz.UTC)
    today_utc = utc_now.date()
    
    print(f"📅 Today's UTC date: {today_utc}")
    print(f"📊 Total records in US JSON: {len(df)}")

    # Filter by today (UTC date) - No need to filter by market since it's US-specific file
    us_df = df[df["date"] == today_utc]

    print(f"✅ Found {len(us_df)} US alerts for today")

    # Sort by timestamp descending if available
    if "timestamp" in us_df.columns and not us_df.empty:
        us_df = us_df.sort_values(by="timestamp", ascending=False)

    # Convert to records
    alerts = us_df.to_dict(orient="records")

    return {
        "market": "US",
        "date": today_utc.strftime("%Y-%m-%d"),
        "timezone": "UTC",
        "count": len(alerts),
        "alerts": alerts
    }

# Update the history endpoints
@app.get("/alerts/history/india")
def get_india_alert_history():
    df = load_realtime_alerts_india_json()

    if df.empty or "date" not in df.columns:
        return {
            "market": "India",
            "timezone": "Asia/Kolkata",
            "count": 0,
            "alerts": []
        }

    ist = pytz.timezone("Asia/Kolkata")
    today = datetime.now(ist).date()
    seven_days_ago = today - timedelta(days=7)

    from_date = seven_days_ago
    to_date = today - timedelta(days=1)  # exclude today

    print(f"📅 India history range: {from_date} to {to_date}")

    india_df = df[
        (df["date"] >= from_date) &
        (df["date"] <= to_date)
    ]

    # Sort safely
    if not india_df.empty:
        if "timestamp" in india_df.columns:
            india_df = india_df.sort_values(
                by=["date", "timestamp"],
                ascending=[False, False]
            )
        else:
            india_df = india_df.sort_values(
                by="date",
                ascending=False
            )

    alerts = india_df.to_dict(orient="records")

    return {
        "market": "India",
        "timezone": "Asia/Kolkata",
        "from_date": str(from_date),
        "to_date": str(to_date),
        "count": len(alerts),
        "alerts": alerts
    }


@app.get("/alerts/history/us")
def get_us_alert_history():
    df = load_realtime_alerts_us_json()

    if df.empty or "date" not in df.columns:
        return {
            "market": "US",
            "timezone": "UTC",
            "count": 0,
            "alerts": []
        }

    utc_now = datetime.now(pytz.UTC)
    today = utc_now.date()
    seven_days_ago = today - timedelta(days=7)

    from_date = seven_days_ago
    to_date = today - timedelta(days=1)  # exclude today

    print(f"📅 US history range: {from_date} to {to_date}")

    us_df = df[
        (df["date"] >= from_date) &
        (df["date"] <= to_date)
    ]

    # Sort safely
    if not us_df.empty:
        if "timestamp" in us_df.columns:
            us_df = us_df.sort_values(
                by=["date", "timestamp"],
                ascending=[False, False]
            )
        else:
            us_df = us_df.sort_values(
                by="date",
                ascending=False
            )

    alerts = us_df.to_dict(orient="records")

    return {
        "market": "US",
        "timezone": "UTC",
        "from_date": str(from_date),
        "to_date": str(to_date),
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
            users = load_users()
            linked = False

            for user in users:
                if user["email"].lower() == text.lower():
                    # ✅ Save watchlist chat id inside same user
                    user["watchlist_chat_id"] = chat_id
                    user["watchlist_linked"] = "yes"
                    user["watchlist_linked_at"] = datetime.utcnow().isoformat()

                    linked = True
                    break

            if linked:
                save_users(users)

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

# -------------------- POST ENDPOINTS --------------------

@app.post("/admin/posts/create", response_model=PostResponse)
def create_post(post: PostCreate):
    """Create a new post (Admin only - protected by admin key in production)"""
    # In production, add proper authentication middleware
    
    posts = load_posts()
    
    # Get admin user (first admin or create system user)
    users = load_users()
    admin_user = next((u for u in users if u.get("is_admin", False)), None)
    
    if not admin_user:
        # Create system admin if none exists
        admin_user = {
            "user_id": "system",
            "first_name": "AIFinverse",
            "last_name": "Admin",
            "email": "admin@aifinverse.com"
        }
    
    now = datetime.utcnow().isoformat() + "Z"
    
    new_post = {
        "id": str(uuid4()),
        "title": post.title,
        "subtitle": post.subtitle,
        "content": post.content,
        "excerpt": post.excerpt or post.content[:200] + "..." if len(post.content) > 200 else post.content,
        "featured_image_url": post.featured_image_url,
        "author": {
            "id": admin_user["user_id"],
            "name": f"{admin_user['first_name']} {admin_user['last_name']}",
            "email": admin_user["email"]
        },
        "status": post.status,
        "category": post.category,
        "tags": post.tags,
        "meta_description": post.meta_description or post.excerpt or post.content[:160],
        "is_featured": post.is_featured,
        "read_time": calculate_read_time(post.content),
        "views": 0,
        "likes": 0,
        "created_at": now,
        "updated_at": now,
        "published_at": now if post.status == "published" else None
    }
    
    posts.append(new_post)
    save_posts(posts)
    
    return new_post

@app.post("/admin/posts/{post_id}/images/upload")
async def upload_post_image(post_id: str, file: UploadFile = File(...)):
    """Upload an image for a specific post"""
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, GIF and WebP images are allowed")
    
    # Read file
    contents = await file.read()
    
    # Process and upload
    image_url = process_post_image(contents, file.filename)
    
    # Update post to include image reference
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    
    if post:
        # Add to post's images list
        post.setdefault("images", [])
        if image_url not in post["images"]:
            post["images"].append(image_url)
        save_posts(posts)
    
    return {
        "url": image_url,
        "filename": file.filename,
        "post_id": post_id
    }

@app.post("/admin/posts/images/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image for use in posts (returns URL for embedding)"""
    
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, GIF and WebP images are allowed")
    
    contents = await file.read()
    image_url = process_post_image(contents, file.filename)
    
    return {
        "url": image_url,
        "filename": file.filename
    }

@app.put("/admin/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: str, post_update: PostUpdate):
    """Update an existing post"""
    
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Update fields
    update_data = post_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if value is not None:
            post[field] = value
    
    # Recalculate excerpt if content changed
    if "content" in update_data:
        post["excerpt"] = post.get("excerpt") or post["content"][:200] + "..." if len(post["content"]) > 200 else post["content"]
        post["read_time"] = calculate_read_time(post["content"])
    
    # Update timestamps
    post["updated_at"] = datetime.utcnow().isoformat() + "Z"
    if post["status"] == "published" and not post.get("published_at"):
        post["published_at"] = post["updated_at"]
    
    save_posts(posts)
    return post

@app.delete("/admin/posts/{post_id}")
def delete_post(post_id: str):
    """Delete a post"""
    
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    posts = [p for p in posts if p["id"] != post_id]
    save_posts(posts)
    
    return {"message": "Post deleted successfully"}

@app.get("/admin/posts/drafts")
def get_drafts():
    """Get all draft posts (Admin only)"""
    posts = load_posts()
    drafts = [p for p in posts if p["status"] == "draft"]
    
    # Sort by updated_at descending
    drafts.sort(key=lambda x: x["updated_at"], reverse=True)
    
    return {
        "count": len(drafts),
        "drafts": drafts
    }

@app.post("/admin/posts/{post_id}/publish")
def publish_post(post_id: str):
    """Publish a draft post"""
    
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    now = datetime.utcnow().isoformat() + "Z"
    post["status"] = "published"
    post["published_at"] = now
    post["updated_at"] = now
    
    save_posts(posts)
    
    return {"message": "Post published successfully", "post": post}

@app.post("/admin/posts/{post_id}/send-newsletter")
def send_post_newsletter(post_id: str, newsletter: NewsletterSend):
    """Send post as newsletter to all subscribers"""
    
    # Load post
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post["status"] != "published":
        raise HTTPException(status_code=400, detail="Only published posts can be sent as newsletters")
    
    # Load subscribers
    subscribers = load_subscribed_emails()
    
    if not subscribers:
        return {"message": "No subscribers found", "sent_count": 0}
    
    # Prepare email data
    post_url = f"https://aifinverse.com/posts/{post_id}"
    subject = newsletter.subject or f"New Post: {post['title']}"
    
    # Send to all subscribers
    sent_count = 0
    failed_count = 0
    
    for subscriber in subscribers:
        try:
            send_newsletter_email(
                post_title=post['title'],
                post_excerpt=post.get('excerpt', ''),
                post_url=post_url,
                subscriber_email=subscriber['email'],
                custom_message=newsletter.custom_message
            )
            sent_count += 1
        except Exception as e:
            print(f"Failed to send to {subscriber['email']}: {e}")
            failed_count += 1
    
    # Log newsletter send
    newsletters = load_newsletters()
    newsletters.append({
        "id": str(uuid4()),
        "post_id": post_id,
        "post_title": post['title'],
        "subject": subject,
        "sent_at": datetime.utcnow().isoformat() + "Z",
        "sent_count": sent_count,
        "failed_count": failed_count
    })
    save_newsletters(newsletters)
    
    return {
        "message": "Newsletter sent successfully",
        "post_id": post_id,
        "post_title": post['title'],
        "sent_count": sent_count,
        "failed_count": failed_count,
        "total_subscribers": len(subscribers)
    }

# -------------------- PUBLIC POST ENDPOINTS --------------------

@app.get("/posts", response_model=List[PostListResponse])
def get_posts(
    page: int = 1,
    limit: int = 10,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    featured: bool = False
):
    """Get published posts with pagination and filtering"""
    
    posts = load_posts()
    
    # Filter published posts
    published_posts = [p for p in posts if p["status"] == "published"]
    
    # Apply filters
    if category:
        published_posts = [p for p in published_posts if p.get("category") == category]
    
    if tag:
        published_posts = [p for p in published_posts if tag in p.get("tags", [])]
    
    if featured:
        published_posts = [p for p in published_posts if p.get("is_featured", False)]
    
    # Sort by published date (newest first)
    published_posts.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    
    # Paginate
    start = (page - 1) * limit
    end = start + limit
    paginated_posts = published_posts[start:end]
    
    # Format response
    result = []
    for post in paginated_posts:
        result.append({
            "id": post["id"],
            "title": post["title"],
            "subtitle": post.get("subtitle"),
            "excerpt": post.get("excerpt"),
            "featured_image_url": post.get("featured_image_url"),
            "author_name": post["author"]["name"],
            "category": post.get("category"),
            "tags": post.get("tags", []),
            "read_time": post.get("read_time", 1),
            "views": post.get("views", 0),
            "likes": post.get("likes", 0),
            "created_at": post["created_at"],
            "published_at": post.get("published_at")
        })
    
    return result

@app.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: str):
    """Get a single post by ID"""
    
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    
    if not post or post["status"] != "published":
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment view count
    post["views"] = post.get("views", 0) + 1
    save_posts(posts)
    
    return post

@app.get("/posts/slug/{slug}", response_model=PostResponse)
def get_post_by_slug(slug: str):
    """Get a single post by slug (URL-friendly title)"""
    
    posts = load_posts()
    
    # Create slug from title (simplified - in production, store slug in post data)
    post = next((p for p in posts if p["status"] == "published"), None)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment view count
    post["views"] = post.get("views", 0) + 1
    save_posts(posts)
    
    return post

@app.get("/posts/featured/latest")
def get_latest_featured():
    """Get the latest featured post for homepage"""
    
    posts = load_posts()
    
    featured_posts = [
        p for p in posts 
        if p["status"] == "published" and p.get("is_featured", False)
    ]
    
    if not featured_posts:
        # Return most recent published post
        published_posts = [p for p in posts if p["status"] == "published"]
        if published_posts:
            published_posts.sort(key=lambda x: x.get("published_at", ""), reverse=True)
            return published_posts[0]
        return None
    
    featured_posts.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    return featured_posts[0]

# -------------------- COMMENTS ENDPOINTS --------------------

@app.post("/posts/{post_id}/comments")
def add_comment(post_id: str, comment: CommentCreate):
    """Add a comment to a post"""
    
    # Verify post exists
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id and p["status"] == "published"), None)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comments = load_comments()
    
    now = datetime.utcnow().isoformat() + "Z"
    
    new_comment = {
        "id": str(uuid4()),
        "post_id": post_id,
        "author_name": comment.author_name,
        "author_email": comment.author_email.lower(),
        "content": comment.content,
        "parent_id": comment.parent_id,
        "likes": 0,
        "created_at": now,
        "status": "approved"  # Auto-approve for now
    }
    
    comments.append(new_comment)
    save_comments(comments)
    
    return new_comment

@app.get("/posts/{post_id}/comments")
def get_post_comments(post_id: str):
    """Get all comments for a post"""
    
    comments = load_comments()
    post_comments = [c for c in comments if c["post_id"] == post_id and c["status"] == "approved"]
    
    # Build comment tree
    comment_map = {}
    root_comments = []
    
    # First pass: create all comments
    for comment in post_comments:
        comment["replies"] = []
        comment_map[comment["id"]] = comment
    
    # Second pass: organize replies
    for comment in post_comments:
        if comment.get("parent_id") and comment["parent_id"] in comment_map:
            # This is a reply
            comment_map[comment["parent_id"]]["replies"].append(comment)
        elif not comment.get("parent_id"):
            # This is a root comment
            root_comments.append(comment)
    
    # Sort root comments by date (newest first)
    root_comments.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "post_id": post_id,
        "total_comments": len(post_comments),
        "comments": root_comments
    }

@app.post("/comments/{comment_id}/like")
def like_comment(comment_id: str):
    """Like a comment"""
    
    comments = load_comments()
    comment = next((c for c in comments if c["id"] == comment_id), None)
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    comment["likes"] = comment.get("likes", 0) + 1
    save_comments(comments)
    
    return {"likes": comment["likes"]}

# -------------------- ADMIN STATS ENDPOINTS --------------------

@app.get("/admin/stats/posts")
def get_post_stats():
    """Get post statistics for admin dashboard"""
    
    posts = load_posts()
    
    published_posts = [p for p in posts if p["status"] == "published"]
    draft_posts = [p for p in posts if p["status"] == "draft"]
    
    total_views = sum(p.get("views", 0) for p in posts)
    total_likes = sum(p.get("likes", 0) for p in posts)
    
    # Posts by category
    categories = {}
    for post in published_posts:
        category = post.get("category", "Uncategorized")
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    # Posts by month
    from collections import defaultdict
    monthly_posts = defaultdict(int)
    for post in published_posts:
        if post.get("published_at"):
            month = post["published_at"][:7]  # YYYY-MM
            monthly_posts[month] += 1
    
    return {
        "total_posts": len(posts),
        "published": len(published_posts),
        "drafts": len(draft_posts),
        "total_views": total_views,
        "total_likes": total_likes,
        "categories": categories,
        "monthly_posts": dict(monthly_posts)
    }

@app.get("/admin/newsletters/history")
def get_newsletter_history():
    """Get newsletter sending history"""
    
    newsletters = load_newsletters()
    
    # Sort by sent_at descending
    newsletters.sort(key=lambda x: x["sent_at"], reverse=True)
    
    return {
        "total_sent": len(newsletters),
        "history": newsletters
    }
