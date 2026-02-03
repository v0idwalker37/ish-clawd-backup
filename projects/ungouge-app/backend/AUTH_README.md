# Authentication System Documentation

## Overview

The authentication system provides user registration, login, and profile management for the Ungouge.ai backend.

## Features

✅ User registration with email, password, and name  
✅ JWT-based authentication (access + refresh tokens)  
✅ Password hashing with bcrypt  
✅ Protected routes with Bearer token authentication  
✅ User profile management  
✅ Optional authentication for quote submission  
✅ User-specific quote history  

## API Endpoints

### Authentication

#### POST /api/auth/register
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST /api/auth/login
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST /api/auth/refresh
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET /api/auth/me
Get current user's profile (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

#### PUT /api/auth/me
Update current user's profile (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "name": "Jane Doe",
  "email": "newemail@example.com"
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "newemail@example.com",
  "name": "Jane Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T13:00:00"
}
```

#### POST /api/auth/forgot-password
Request password reset (stub implementation).

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "If the email exists, a password reset link has been sent"
}
```

### Quotes (Updated)

#### POST /api/quotes
Submit a quote for analysis (optionally authenticated).

- If user is logged in (provides Bearer token), quote is linked to their account
- If not logged in, quote is created without user association

**Headers (optional):**
```
Authorization: Bearer <access_token>
```

#### GET /api/quotes/my
Get current user's quotes (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (default: 0) - Pagination offset
- `limit` (default: 10) - Number of results

**Response:**
```json
{
  "quotes": [
    {
      "id": "quote-uuid",
      "project_type": "Kitchen Remodel",
      "location": "Denver, CO",
      "contractor_name": "ABC Contracting",
      "created_at": "2024-01-01T12:00:00",
      "report_url": "/api/quotes/quote-uuid/report"
    }
  ],
  "total": 1
}
```

#### GET /api/quotes/{quote_id}/report
Get full analysis report for a quote.

**Response:** Same as GET /api/quotes/{quote_id}

## Token Management

### Access Token
- **Expiry:** 30 minutes
- **Type:** "access"
- **Usage:** Include in Authorization header for protected routes

### Refresh Token
- **Expiry:** 7 days
- **Type:** "refresh"
- **Usage:** Use to obtain new access/refresh token pair

## Environment Variables

Add to your `.env` file:

```env
JWT_SECRET_KEY=your-secret-key-change-in-production-use-openssl-rand-hex-32
```

Generate a secure key:
```bash
openssl rand -hex 32
```

## Database Changes

The `User` model has been updated with the following fields:

```python
class User(Base):
    id: str                    # UUID
    email: str                 # Unique, indexed
    password_hash: str         # Bcrypt hashed
    name: str                  # User's full name
    is_active: bool            # Account status
    is_verified: bool          # Email verification status
    created_at: datetime       # Account creation
    updated_at: datetime       # Last update
    quotes: List[Quote]        # User's quotes
```

## Testing with cURL

### 1. Register a user
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "name": "Test User"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

Save the `access_token` from the response.

### 3. Get profile
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### 4. Update profile
```bash
curl -X PUT http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name"
  }'
```

### 5. Submit a quote (authenticated)
```bash
curl -X POST http://localhost:8000/api/quotes \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "project_type": "Kitchen Remodel",
    "location": "Denver, CO",
    "contractor_name": "Test Contractor",
    "line_items": [
      {
        "item_name": "Cabinet Installation",
        "description": "Install cabinets",
        "quoted_price": 4500.00,
        "quantity": 1,
        "unit": "job"
      }
    ]
  }'
```

### 6. Get my quotes
```bash
curl -X GET http://localhost:8000/api/auth/quotes/my \
  -H "Authorization: Bearer <access_token>"
```

## Security Notes

1. **JWT Secret:** Change the default secret key in production
2. **HTTPS:** Always use HTTPS in production
3. **Password Requirements:** Currently minimum 8 characters (can be enhanced)
4. **Token Storage:** Store tokens securely on the client (httpOnly cookies recommended)
5. **CORS:** Configure allowed origins appropriately

## Future Enhancements

- Email verification
- Password reset functionality (currently stub)
- OAuth integration (Google, GitHub, etc.)
- Rate limiting
- Account lockout after failed login attempts
- Two-factor authentication (2FA)
- Session management
