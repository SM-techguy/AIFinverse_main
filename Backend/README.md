# AIFinverse Backend API - Complete Functionality Guide

## 📋 Table of Contents
1. [Authentication APIs](#authentication-apis)
2. [User Management APIs](#user-management-apis)
3. [Market Preferences APIs](#market-preferences-apis)
4. [Watchlist Management APIs](#watchlist-management-apis)
5. [Alerts & Market Data APIs](#alerts--market-data-apis)
6. [Telegram Bot Integration APIs](#telegram-bot-integration-apis)
7. [Company Data APIs](#company-data-apis)
8. [Communication APIs](#communication-apis)
9. [Admin APIs](#admin-apis)

---

## 🔐 Authentication APIs

### 1. POST `/register`
**Purpose**: Complete user registration with two-step process

**Functionality**:
- Validates password confirmation match
- Checks for existing email in `users.json` (S3)
- Creates user with unique UUID
- Stores registration info including country, selected market, and strategies
- Initializes market preferences based on selection (India/US/Both)
- Sends welcome email via SMTP
- Returns user details with preferences

**Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "country": "USA",
  "password": "secure123",
  "confirm_password": "secure123",
  "selected_market": "Both",
  "selected_strategies": ["Momentum", "Breakout"]
}
```

**Response**: User ID, email, and complete market preferences

---

### 2. POST `/login`
**Purpose**: Authenticate existing users

**Functionality**:
- Validates email and password (plain text comparison - needs improvement)
- Loads user data from S3
- Returns user profile and market preferences on success
- Throws 401 for invalid credentials

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "secure123"
}
```

**Response**: User ID, profile info, and current preferences

---

### 3. POST `/forgot-password`
**Purpose**: Initiate password reset process

**Functionality**:
- Verifies email exists in system
- Generates 6-digit OTP
- Stores OTP with 10-minute expiry in user record
- Sends OTP via email
- Returns success message

**Request Body**:
```json
{
  "email": "john@example.com"
}
```

---

### 4. POST `/verify-otp`
**Purpose**: Verify OTP and send reset link

**Functionality**:
- Validates OTP matches stored value
- Checks OTP expiration (10 minutes)
- Generates unique reset token with 15-minute expiry
- Creates password reset link
- Sends reset link via email
- Returns confirmation

**Request Body**:
```json
{
  "email": "john@example.com",
  "otp": "123456"
}
```

---

### 5. POST `/reset-password`
**Purpose**: Complete password reset with token

**Functionality**:
- Validates token exists and not expired
- Confirms password match
- Updates user password
- Clears all reset-related fields
- Returns success message

**Request Body**:
```json
{
  "token": "uuid-token",
  "new_password": "newpass123",
  "confirm_password": "newpass123"
}
```

---

## 👤 User Management APIs

### 6. GET `/users/{user_id}`
**Purpose**: Retrieve complete user details

**Functionality**:
- Fetches user by UUID
- Returns registration data, market preferences, and watchlist
- Calculates watchlist summary counts
- Sanitizes sensitive data

**Response**:
```json
{
  "registration_data": {...},
  "india_alerts": {"strategies": [...]},
  "us_alerts": {"strategies": [...]},
  "watchlist": {"India": [...], "US": [...]},
  "watchlist_summary": {"india_count": 5, "us_count": 3, "total": 8}
}
```

---

## 🎯 Market Preferences APIs

### 7. POST `/register/preferences`
**Purpose**: Save initial market preferences after registration

**Functionality**:
- Updates user's market selections
- Activates selected markets (India/US)
- Adds chosen strategies to each market
- Persists to S3

**Request Body**:
```json
{
  "email": "john@example.com",
  "markets": ["India", "US"],
  "strategies": ["Momentum", "Breakout"]
}
```

---

### 8. PUT `/update/preferences`
**Purpose**: Modify existing market preferences

**Functionality**:
- Adds or removes markets
- Adds or removes strategies per market
- Auto-deactivates market when no strategies remain
- Returns updated market strategies

**Request Body**:
```json
{
  "email": "john@example.com",
  "market": "India",
  "strategy": "Momentum",
  "action": "add"  // or "remove"
}
```

---

## 📊 Watchlist Management APIs

### 9. POST `/watchlist/update`
**Purpose**: Bulk update user watchlist

**Functionality**:
- Validates companies against master CSV
- Enforces 20-company limit per market
- Prevents duplicates
- Organizes by market (India/US)
- Returns complete watchlist with counts

**Request Body**:
```json
{
  "user_id": "uuid",
  "companies": ["Reliance Industries", "TCS", "HDFC Bank"]
}
```

**Limit**: Max 20 companies per market (India and US)

---

### 10. POST `/watchlist/modify/india`
**Purpose**: Modify India-specific watchlist

**Functionality**:
- Validates all companies are India market stocks
- Enforces total 20-company limit across both markets
- Supports add/remove operations
- Maintains market separation
- Returns updated India watchlist

**Request Body**:
```json
{
  "user_id": "uuid",
  "companies": ["Reliance Industries", "Infosys"],
  "action": "add"  // or "remove"
}
```

---

### 11. POST `/watchlist/modify/us`
**Purpose**: Modify US-specific watchlist

**Functionality**:
- Same as India endpoint but for US stocks
- Validates against US market in master CSV
- Enforces total limit across markets
- Returns updated US watchlist

**Request Body**:
```json
{
  "user_id": "uuid",
  "companies": ["Apple Inc", "Microsoft Corp"],
  "action": "add"  // or "remove"
}
```

---

## 📈 Alerts & Market Data APIs

### 12. GET `/alerts/live/india`
**Purpose**: Fetch today's India market alerts

**Functionality**:
- Loads realtime_alerts.csv from S3
- Filters for today's date (IST timezone)
- Filters for India market only
- Sorts by timestamp descending
- Returns formatted alerts with counts

**Response**: List of today's alerts with company, strategy, signal type

---

### 13. GET `/alerts/live/us`
**Purpose**: Fetch today's US market alerts

**Functionality**:
- Same as India endpoint but for US market
- Uses IST date for consistency
- Returns US-specific alerts

---

### 14. GET `/alerts/history/india`
**Purpose**: Get last 7 days of India alerts

**Functionality**:
- Calculates date range (today - 7 days)
- Filters alerts within range
- Sorts by date and timestamp
- Returns historical alert data

---

### 15. GET `/alerts/history/us`
**Purpose**: Get last 7 days of US alerts

**Functionality**:
- Same as India history endpoint
- Provides 7-day historical view
- Useful for trend analysis

---

## 🤖 Telegram Bot Integration APIs

### 16. POST `/telegram/webhook`
**Purpose**: Webhook for US market Telegram bot

**Functionality**:
- Processes incoming Telegram messages
- Handles `/start` command with welcome message
- Links user email to Telegram chat ID
- Stores India/US chat IDs separately in user profile
- Sends confirmation messages

**Bot Flow**:
1. User sends `/start`
2. Bot asks for registered email
3. User replies with email
4. System links email to chat_id
5. Confirmation sent

---

### 17. POST `/telegram/webhook/india`
**Purpose**: Webhook for India market Telegram bot

**Functionality**:
- Same as US webhook but for India market
- Detailed logging for debugging
- Links to India-specific chat_id field
- Sends India market alerts confirmation

---

### 18. POST `/telegram/webhook/watchlist`
**Purpose**: Webhook for Watchlist-specific Telegram bot

**Functionality**:
- Dedicated bot for watchlist notifications
- Links user email specifically for watchlist
- Sets `watchlist_linked` flag in user profile
- Will send watchlist alerts (future functionality)

---

## 🏢 Company Data APIs

### 19. GET `/companies/india`
**Purpose**: Get all India companies from master CSV

**Functionality**:
- Loads stock_universe_with_company_names.csv
- Filters for India market
- Returns company name and base symbol
- Handles null values gracefully

**Response**: List of India companies with count

---

### 20. GET `/companies/us`
**Purpose**: Get all US companies from master CSV

**Functionality**:
- Same as India endpoint
- Filters for US market
- Returns company details

---

## 📧 Communication APIs

### 21. POST `/contact-us`
**Purpose**: Handle contact form submissions

**Functionality**:
- Sends confirmation email to user
- Sends notification email to admin (soumyadeepmondal2372001@gmail.com)
- Includes all form details
- Returns success message

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Query about services",
  "message": "I would like to know more..."
}
```

---

### 22. POST `/subscribe`
**Purpose**: Newsletter subscription

**Functionality**:
- Loads existing subscribers from emails.json (S3)
- Prevents duplicate subscriptions
- Stores email with timestamp
- Sends subscription confirmation email
- Returns success message

**Request Body**:
```json
{
  "email": "john@example.com"
}
```

---

### 23. GET `/news/live`
**Purpose**: Fetch latest market news

**Functionality**:
- Calls Tavily Search API with stock market query
- Returns top 3 financial news articles
- Includes title, source URL, and summary
- Returns with timestamp

---

### 24. GET `/whatsapp/redirect`
**Purpose**: Generate WhatsApp contact link

**Functionality**:
- Creates pre-filled WhatsApp message
- Uses predefined phone number (+971545964747)
- URL-encodes message
- Returns ready-to-use WhatsApp URL

---

## 👑 Admin APIs

### 25. GET `/admin/users`
**Purpose**: List all registered users (admin only)

**Functionality**:
- Loads all users from S3
- Removes sensitive data (passwords, reset tokens)
- Returns sanitized user list with count
- Includes fetch timestamp

**Security Note**: Should be restricted in production

---

## 🛠 Helper Functions

### Internal Functions (Not APIs)

#### `load_users()` / `save_users()`
- S3 CRUD operations for users.json
- Handles NoSuchKey errors
- JSON serialization/deserialization

#### `load_subscribed_emails()` / `save_subscribed_emails()`
- Manages newsletter subscribers list
- Stores in emails.json on S3

#### `load_companies_from_s3()`
- Loads master company CSV
- Returns pandas DataFrame
- Used by watchlist and company endpoints

#### `load_realtime_alerts_csv()`
- Loads alert data from S3
- Handles date conversion
- Replaces NaN with None for JSON

#### Email Functions
- `send_welcome_email()`: New user registration
- `send_otp_email()`: Password reset OTP
- `send_reset_link_email()`: Password reset link
- `send_contact_emails()`: Contact form (user + admin)
- `send_subscription_email()`: Newsletter confirmation

#### Telegram Helper Functions
- `link_telegram_to_user_by_email()`: Links email to chat_id
- `send_telegram_response()`: Sends messages via Telegram API
- `send_watchlist_telegram_response()`: Watchlist bot messaging

#### Utility Functions
- `generate_otp()`: 6-digit random OTP
- `get_ist_today()`: Current date in IST timezone
- `verify_password()`: Plain text comparison (needs improvement)

---

## 📊 Data Models

### User Schema (users.json)
```json
{
  "user_id": "uuid",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "password": "string",
  "registration_info": {
    "country": "string",
    "selected_market": "string",
    "selected_strategies": [],
    "registered_at": "ISO datetime"
  },
  "market_preferences": {
    "India": {"is_active": boolean, "strategies": []},
    "US": {"is_active": boolean, "strategies": []}
  },
  "telegram": {
    "username": "string",
    "india_chat_id": "integer",
    "us_chat_id": "integer"
  },
  "watchlist": {
    "India": [{"company_name": "string", "base_symbol": "string"}],
    "US": [{"company_name": "string", "base_symbol": "string"}]
  }
}
```

---

## 🔄 API Flow Examples

### Complete User Journey
1. **Register** → `/register`
2. **Login** → `/login`
3. **Set Preferences** → `/register/preferences`
4. **Add to Watchlist** → `/watchlist/modify/india`
5. **Link Telegram** → Interact with Telegram bot
6. **View Alerts** → `/alerts/live/india`
7. **Update Preferences** → `/update/preferences`

### Password Reset Flow
1. Request reset → `/forgot-password`
2. Verify OTP → `/verify-otp` (gets reset link)
3. Set new password → `/reset-password`

---

## ⚠️ Error Handling

All APIs return appropriate HTTP status codes:
- **200**: Success
- **400**: Bad request (validation failed)
- **401**: Unauthorized (invalid credentials)
- **404**: Resource not found
- **500**: Server error (with details)

---

This comprehensive guide covers all 25+ API endpoints and their complete functionality in the AIFinverse backend system.