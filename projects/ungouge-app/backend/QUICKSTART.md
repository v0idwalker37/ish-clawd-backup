# 🚀 Quick Start Guide - Authentication System

## Prerequisites

- Python 3.9+
- Virtual environment activated
- Dependencies installed

## Setup (First Time)

### 1. Install Dependencies
```bash
cd /Users/moltbot/clawd/projects/ungouge-app/backend
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Generate a secure JWT secret
openssl rand -hex 32

# Edit .env and set JWT_SECRET_KEY to the generated value
```

### 3. Start the Server
```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

## Test the API

### Using the Interactive Docs

Visit `http://localhost:8000/docs` for Swagger UI with interactive testing.

### Using cURL

#### 1. Register a New User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123",
    "name": "Test User"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Save the `access_token` for the next requests.

#### 2. Get Your Profile
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 3. Submit a Quote (Authenticated)
```bash
curl -X POST http://localhost:8000/api/quotes \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_type": "Kitchen Remodel",
    "location": "Denver, CO",
    "contractor_name": "Test Contractor",
    "line_items": [
      {
        "item_name": "Cabinet Installation",
        "description": "Install kitchen cabinets",
        "quoted_price": 4500.00,
        "quantity": 1,
        "unit": "job"
      }
    ]
  }'
```

#### 4. Get Your Quotes
```bash
curl -X GET http://localhost:8000/api/quotes/my \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Run Automated Tests

```bash
python test_auth.py
```

Expected output:
```
🧪 Testing Authentication System

📦 Creating database tables...
   ✅ Database tables created

1️⃣ Testing password hashing...
   ✅ Password hashing and verification working

2️⃣ Testing JWT token creation...
   ✅ JWT tokens working correctly

3️⃣ Testing user creation in database...
   ✅ User created successfully

4️⃣ Testing quote creation linked to user...
   ✅ Quote linked to user successfully

5️⃣ Testing retrieval of user's quotes...
   ✅ Retrieved 1 quote(s) for user

6️⃣ Testing profile update...
   ✅ Profile updated successfully

🧹 Cleaning up test data...
   ✅ Test data cleaned up

✅ All tests passed!

🎉 Authentication system is working correctly!
```

## Common Tasks

### Login to Get a New Token
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123"
  }'
```

### Refresh Access Token
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### Update Profile
```bash
curl -X PUT http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name"
  }'
```

## Troubleshooting

### "JWT_SECRET_KEY not set" or weak security warning
- Set `JWT_SECRET_KEY` in your `.env` file
- Use a strong random key (generate with `openssl rand -hex 32`)

### "Email already registered"
- The email is already in use
- Try a different email or login instead

### "Could not validate credentials"
- Token is expired or invalid
- Get a new token by logging in or refreshing

### Database errors
- Delete `ungouge.db` and restart the server to recreate tables
- The app automatically creates tables on startup

## Next Steps

1. **Production Setup:**
   - Set strong `JWT_SECRET_KEY`
   - Use PostgreSQL instead of SQLite
   - Enable HTTPS
   - Configure CORS for your frontend domain

2. **Frontend Integration:**
   - Store tokens in httpOnly cookies or localStorage
   - Add Authorization header to all API requests
   - Implement token refresh logic

3. **Email Features:**
   - Configure email service (SendGrid, AWS SES)
   - Implement email verification
   - Complete password reset workflow

## Documentation

- `AUTH_README.md` - Complete API documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Support

For issues or questions, check the documentation files or the FastAPI interactive docs at `/docs`.
