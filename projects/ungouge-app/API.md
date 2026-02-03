# Ungouge.ai API Documentation

> **Backend API Reference** - Complete endpoint documentation with examples

**Base URL (Dev):** `http://localhost:8000`  
**Base URL (Prod):** `https://api.ungouge.ai` *(when deployed)*

**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI)  
**OpenAPI Schema:** `http://localhost:8000/openapi.json`

---

## Table of Contents

- [Authentication](#authentication)
- [Health Checks](#health-checks)
- [User Management](#user-management)
- [Quote Analysis](#quote-analysis)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Rate Limits](#rate-limits)

---

## Authentication

All authenticated endpoints require a JWT token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

### Register User

**Endpoint:** `POST /api/auth/register`

**Description:** Create a new user account

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

**Validation:**
- Email must be valid format
- Password: min 8 characters, 1 uppercase, 1 lowercase, 1 number
- Full name: optional, max 255 chars

**Response (201):**
```json
{
  "message": "User registered successfully. Please check your email to verify your account.",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_verified": false,
    "created_at": "2024-02-02T10:30:00Z"
  }
}
```

**Errors:**
- `400 Bad Request` - Invalid input (validation error)
- `409 Conflict` - Email already registered

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

---

### Login

**Endpoint:** `POST /api/auth/login`

**Description:** Authenticate and receive JWT token

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_verified": true
  }
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - Email not verified

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'SecurePass123!'
  })
});
const data = await response.json();
localStorage.setItem('token', data.access_token);
```

---

### Logout

**Endpoint:** `POST /api/auth/logout`

**Description:** Invalidate JWT token (adds to blacklist)

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Get Current User

**Endpoint:** `GET /api/auth/me`

**Description:** Get currently authenticated user's profile

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_verified": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### Request Password Reset

**Endpoint:** `POST /api/auth/password-reset-request`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "If an account with that email exists, a password reset link has been sent."
}
```

**Notes:**
- Always returns 200 (security: don't reveal if email exists)
- Email contains reset link valid for 1 hour

---

### Reset Password

**Endpoint:** `POST /api/auth/password-reset`

**Request Body:**
```json
{
  "token": "abc123def456...",
  "new_password": "NewSecurePass123!"
}
```

**Response (200):**
```json
{
  "message": "Password reset successfully"
}
```

**Errors:**
- `400 Bad Request` - Invalid or expired token

---

## Health Checks

### Basic Health Check

**Endpoint:** `GET /health`

**Description:** Quick liveness check

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-02-02T10:30:00Z"
}
```

---

### Readiness Check

**Endpoint:** `GET /health/ready`

**Description:** Check if service is ready to accept requests (includes DB check)

**Response (200):**
```json
{
  "status": "ready",
  "database": "connected",
  "timestamp": "2024-02-02T10:30:00Z"
}
```

**Response (503) - Not Ready:**
```json
{
  "status": "not_ready",
  "database": "disconnected",
  "timestamp": "2024-02-02T10:30:00Z"
}
```

---

### Liveness Check

**Endpoint:** `GET /health/live`

**Description:** Check if service is alive (for container orchestration)

**Response (200):**
```json
{
  "status": "alive"
}
```

---

## Quote Analysis

### Upload Quote

**Endpoint:** `POST /api/quotes/upload`

**Description:** Upload contractor quote for analysis (PDF or image)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request (multipart/form-data):**
- `file` - Quote file (PDF, PNG, JPG, JPEG)
- Max size: 10MB

**Response (200):**
```json
{
  "message": "Quote uploaded successfully",
  "quote_id": "abc123-def456-...",
  "status": "processing"
}
```

**Errors:**
- `400 Bad Request` - Invalid file type or size
- `401 Unauthorized` - Missing or invalid token
- `429 Too Many Requests` - Rate limit exceeded

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/quotes/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/quote.pdf"
```

**Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8000/api/quotes/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

---

### Submit Quote (Parsed Data)

**Endpoint:** `POST /api/quotes`

**Description:** Submit already-parsed quote data for analysis

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "contractor_name": "ABC Roofing Co",
  "project_type": "roof_replacement",
  "location": "Austin, TX 78701",
  "line_items": [
    {
      "item_name": "Asphalt shingles - Architectural",
      "description": "GAF Timberline HDZ, 30-year warranty",
      "quoted_price": 175.00,
      "quantity": 20,
      "unit": "square"
    },
    {
      "item_name": "Ice & water shield",
      "description": "Underlayment",
      "quoted_price": 450.00,
      "quantity": 3,
      "unit": "roll"
    }
  ]
}
```

**Response (202 Accepted):**
```json
{
  "message": "Quote submitted for analysis",
  "quote_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing"
}
```

**Errors:**
- `400 Bad Request` - Invalid data format
- `401 Unauthorized` - Missing or invalid token

---

### Get Quote Analysis

**Endpoint:** `GET /api/quotes/{quote_id}`

**Description:** Retrieve analysis results for a quote

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "quote_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "contractor_name": "ABC Roofing Co",
  "project_type": "roof_replacement",
  "location": "Austin, TX 78701",
  "total_quoted": 8500.00,
  "total_fair_price": 6200.00,
  "potential_savings": 2300.00,
  "savings_percentage": 27.06,
  "overall_rating": "high",
  "line_items": [
    {
      "item_name": "Asphalt shingles - Architectural",
      "description": "GAF Timberline HDZ, 30-year warranty",
      "quoted_price": 175.00,
      "quantity": 20,
      "unit": "square",
      "total_quoted": 3500.00,
      "fair_price": 140.00,
      "total_fair_price": 2800.00,
      "difference": 700.00,
      "percentage_markup": 25.00,
      "rating": "fair",
      "notes": "Within industry-standard markup range. Price includes 30-year warranty shingles."
    },
    {
      "item_name": "Ice & water shield",
      "description": "Underlayment",
      "quoted_price": 450.00,
      "quantity": 3,
      "unit": "roll",
      "total_quoted": 1350.00,
      "fair_price": 350.00,
      "total_fair_price": 1050.00,
      "difference": 300.00,
      "percentage_markup": 28.57,
      "rating": "fair",
      "notes": "Slightly above average but acceptable for quality material."
    }
  ],
  "summary": "Overall, this quote is on the high side but within acceptable ranges for quality materials. Consider negotiating the total down by 10-15%.",
  "red_flags": [],
  "created_at": "2024-02-02T10:30:00Z",
  "completed_at": "2024-02-02T10:32:15Z"
}
```

**Rating values:**
- `fair` - 0-15% markup (green)
- `high` - 15-30% markup (yellow)
- `gouged` - 30%+ markup (red)

**Errors:**
- `404 Not Found` - Quote ID doesn't exist
- `403 Forbidden` - Quote belongs to another user

---

### List User Quotes

**Endpoint:** `GET /api/quotes`

**Description:** Get all quotes for the authenticated user

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (optional) - Results per page (default: 10, max: 100)
- `offset` (optional) - Pagination offset (default: 0)
- `status` (optional) - Filter by status: `processing`, `completed`, `failed`

**Response (200):**
```json
{
  "quotes": [
    {
      "quote_id": "550e8400-e29b-41d4-a716-446655440000",
      "contractor_name": "ABC Roofing Co",
      "project_type": "roof_replacement",
      "total_quoted": 8500.00,
      "total_fair_price": 6200.00,
      "potential_savings": 2300.00,
      "status": "completed",
      "overall_rating": "high",
      "created_at": "2024-02-02T10:30:00Z"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

**Example (curl):**
```bash
curl -X GET "http://localhost:8000/api/quotes?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Delete Quote

**Endpoint:** `DELETE /api/quotes/{quote_id}`

**Description:** Delete a quote and all associated data

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Quote deleted successfully"
}
```

**Errors:**
- `404 Not Found` - Quote doesn't exist
- `403 Forbidden` - Quote belongs to another user

---

## Data Models

### QuoteSubmission

```typescript
{
  contractor_name: string;        // Required, max 255 chars
  project_type: string;           // Required, see Project Types
  location: string;               // Required, "City, State ZIP"
  line_items: LineItem[];         // Required, min 1 item
}
```

### LineItem

```typescript
{
  item_name: string;              // Required, max 255 chars
  description?: string;           // Optional, max 1000 chars
  quoted_price: number;           // Required, > 0
  quantity: number;               // Required, > 0
  unit: string;                   // Required, see Units
}
```

### Project Types

Valid `project_type` values:
- `roof_replacement`
- `kitchen_remodel`
- `bathroom_remodel`
- `deck_building`
- `fence_installation`
- `hvac_installation`
- `concrete_work`
- `painting_interior`
- `painting_exterior`
- `flooring`
- `siding`
- `windows_doors`
- `electrical`
- `plumbing`
- `landscaping`
- `other`

### Units

Common `unit` values:
- `square` - Roofing squares (100 sq ft)
- `sqft` - Square feet
- `linear_foot` - Linear feet
- `item` - Individual items
- `hour` - Labor hours
- `day` - Days of work
- `roll` - Material rolls
- `gallon` - Gallons (paint, etc.)
- `cubic_yard` - Concrete, etc.

### Report

See [Get Quote Analysis](#get-quote-analysis) response for full report structure.

---

## Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "detail": "Human-readable error message",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-02-02T10:30:00Z"
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `UNAUTHORIZED` | 401 | Missing or invalid auth token |
| `FORBIDDEN` | 403 | Token valid but access denied |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `CONFLICT` | 409 | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error (logged) |

### Validation Errors

**Example (400):**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Rate Limits

### Default Limits

- **Global:** 100 requests/minute per IP
- **Auth endpoints:** 10 requests/minute per IP
- **Upload:** 5 requests/minute per user

### Rate Limit Headers

All responses include:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1643798400
```

### Rate Limit Exceeded

**Response (429):**
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds.",
  "retry_after": 60
}
```

---

## Testing the API

### Using curl

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'

# Login
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}' \
  | jq -r '.access_token')

# Upload quote
curl -X POST http://localhost:8000/api/quotes/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@quote.pdf"

# Get quotes
curl -X GET http://localhost:8000/api/quotes \
  -H "Authorization: Bearer $TOKEN"
```

### Using Postman

1. Import OpenAPI schema from `http://localhost:8000/openapi.json`
2. Set up environment variables:
   - `base_url`: `http://localhost:8000`
   - `token`: (set after login)
3. Use collection runner for automated testing

### Using JavaScript (fetch)

```javascript
const API_URL = 'http://localhost:8000';

// Login
async function login(email, password) {
  const response = await fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  return data.access_token;
}

// Upload quote
async function uploadQuote(token, file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_URL}/api/quotes/upload`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });
  return response.json();
}

// Get analysis
async function getAnalysis(token, quoteId) {
  const response = await fetch(`${API_URL}/api/quotes/${quoteId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}
```

---

## Webhooks (Future)

### Stripe Webhooks

**Endpoint:** `POST /webhooks/stripe`

**Description:** Receive payment events from Stripe

**Events handled:**
- `payment_intent.succeeded`
- `payment_intent.failed`
- `customer.subscription.deleted`

*Full implementation pending.*

---

## Troubleshooting

### "401 Unauthorized"
- Check token is included in Authorization header
- Verify token hasn't expired (7 days)
- Try logging in again

### "403 Forbidden - Email not verified"
- Check spam folder for verification email
- Request new verification email via `/api/auth/resend-verification`

### "429 Rate Limit Exceeded"
- Wait for rate limit window to reset
- Check `X-RateLimit-Reset` header
- Consider upgrading to higher tier (future)

### "500 Internal Server Error"
- Check backend logs
- Verify database connection
- Check external service status (Gemini API, Stripe)

---

## Version History

**v1.0.0** (Current)
- Initial API release
- Authentication endpoints
- Quote upload & analysis
- User management

**v1.1.0** (Planned)
- Quote comparison
- Bulk uploads
- Advanced filtering

---

**Questions?** Contact: jasontrask@gmail.com

**Interactive Docs:** http://localhost:8000/docs
