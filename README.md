# HOMIGO Authentication API

Production-ready authentication system for the HOMIGO rental & flatmate marketplace platform.

## 🚀 Features

- ✅ User Signup with validation
- ✅ User Login with JWT authentication
- ✅ CAPTCHA protection (generate & verify)
- ✅ Password hashing with bcrypt
- ✅ MongoDB integration
- ✅ Input validation & sanitization
- ✅ Standard error handling
- ✅ CORS configuration
- ✅ Environment-based configuration
- ✅ API documentation (Swagger/ReDoc)

## 📋 Prerequisites

- Python 3.9+
- MongoDB 4.4+
- pip (Python package manager)

## 🛠️ Installation

### 1. Clone or create the project

```bash
mkdir HOMIGO
cd HOMIGO
```

### 2. Create virtual environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and update the values:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=homigo_db

# JWT Configuration (CHANGE IN PRODUCTION!)
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-characters-long
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application Configuration
APP_NAME=HOMIGO
APP_VERSION=1.0.0
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# CAPTCHA Configuration
CAPTCHA_EXPIRY_SECONDS=300
```

### 5. Start MongoDB

Make sure MongoDB is running on your system:

```bash
# On Windows (if installed as service)
net start MongoDB

# On macOS (with Homebrew)
brew services start mongodb-community

# On Linux
sudo systemctl start mongod
```

## 🏃 Running the Application

### Development mode

```bash
uvicorn app.main:app --reload --port 8000
```

### Production mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

Once the server is running, access the interactive documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## 🔌 API Endpoints

### 1. Generate CAPTCHA

**GET** `/api/auth/captcha`

**Response:**
```json
{
  "captcha_id": "123e4567-e89b-12d3-a456-426614174000",
  "captcha_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

### 2. User Signup

**POST** `/api/auth/signup`

**Request Body:**
```json
{
  "first_name": "Ram",
  "last_name": "Harish",
  "email": "ram@homigo.com",
  "phone_number": "9876543210",
  "password": "SecurePass@123",
  "captcha_id": "123e4567-e89b-12d3-a456-426614174000",
  "captcha_answer": "ABC123"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Account created successfully",
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "first_name": "Ram",
    "last_name": "Harish",
    "email": "ram@homigo.com",
    "phone_number": "9876543210",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-12-02T10:30:00"
  }
}
```

### 3. User Login

**POST** `/api/auth/login`

**Request Body:**
```json
{
  "email": "ram@homigo.com",
  "password": "SecurePass@123",
  "captcha_id": "123e4567-e89b-12d3-a456-426614174000",
  "captcha_answer": "ABC123"
}
```

**Success Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "first_name": "Ram",
    "last_name": "Harish",
    "email": "ram@homigo.com",
    "phone_number": "9876543210",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-12-02T10:30:00"
  },
  "token": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

### 4. Health Check

**GET** `/api/auth/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "HOMIGO Authentication API",
  "active_captchas": 3
}
```

## 🔐 Using the JWT Token

Include the token in subsequent API requests:

```bash
curl -H "Authorization: Bearer <access_token>" http://localhost:8000/api/protected-endpoint
```

Frontend example (JavaScript):
```javascript
fetch('http://localhost:8000/api/protected-endpoint', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
})
```

## 🧪 Testing with cURL

### 1. Generate CAPTCHA
```bash
curl -X GET http://localhost:8000/api/auth/captcha
```

### 2. Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Ram",
    "last_name": "Harish",
    "email": "ram@homigo.com",
    "phone_number": "9876543210",
    "password": "SecurePass@123",
    "captcha_id": "YOUR_CAPTCHA_ID",
    "captcha_answer": "YOUR_CAPTCHA_ANSWER"
  }'
```

### 3. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ram@homigo.com",
    "password": "SecurePass@123",
    "captcha_id": "YOUR_CAPTCHA_ID",
    "captcha_answer": "YOUR_CAPTCHA_ANSWER"
  }'
```

## 📱 Frontend Integration Guide

### React/Next.js Example

```javascript
// 1. Generate CAPTCHA
const getCaptcha = async () => {
  const response = await fetch('http://localhost:8000/api/auth/captcha');
  const data = await response.json();
  return data; // { captcha_id, captcha_image }
};

// 2. Signup
const signup = async (formData) => {
  const response = await fetch('http://localhost:8000/api/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      first_name: formData.firstName,
      last_name: formData.lastName,
      email: formData.email,
      phone_number: formData.phone,
      password: formData.password,
      captcha_id: formData.captchaId,
      captcha_answer: formData.captchaAnswer
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }
  
  return await response.json();
};

// 3. Login
const login = async (email, password, captchaId, captchaAnswer) => {
  const response = await fetch('http://localhost:8000/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, captcha_id: captchaId, captcha_answer: captchaAnswer })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }
  
  const data = await response.json();
  
  // Store token
  localStorage.setItem('access_token', data.token.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  
  return data;
};

// 4. Use token in authenticated requests
const makeAuthenticatedRequest = async (url) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  return await response.json();
};
```

## ⚠️ Error Handling

All errors follow this format:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": {}
}
```

**Common Error Codes:**
- `INVALID_CAPTCHA` - CAPTCHA verification failed
- `USER_EXISTS` - Email or phone already registered
- `INVALID_CREDENTIALS` - Wrong email/password
- `INTERNAL_ERROR` - Server error

**HTTP Status Codes:**
- `200` - Success
- `201` - Created (signup)
- `400` - Bad Request (invalid CAPTCHA)
- `401` - Unauthorized (wrong credentials)
- `409` - Conflict (user exists)
- `422` - Validation Error
- `500` - Internal Server Error

## 🔒 Security Features

1. **Password Requirements:**
   - Minimum 8 characters
   - At least one uppercase letter
   - At least one lowercase letter
   - At least one digit
   - At least one special character

2. **CAPTCHA Protection:**
   - 6-character alphanumeric
   - 5-minute expiry
   - One-time use only

3. **JWT Tokens:**
   - 24-hour expiry (configurable)
   - HS256 algorithm
   - Includes user metadata

4. **Password Security:**
   - Bcrypt hashing
   - Never stored in plain text
   - Hash verification on login

## 📁 Project Structure Explained

```
app/
├── config/          # Configuration and settings
├── models/          # Database models (Pydantic)
├── schemas/         # Request/Response schemas
├── routes/          # API endpoints
├── services/        # Business logic
├── database/        # Database connection
└── utils/           # Helper functions
```

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] Change `JWT_SECRET_KEY` to a strong random string (min 32 characters)
- [ ] Set `DEBUG=False`
- [ ] Update `ALLOWED_ORIGINS` to your frontend domain
- [ ] Use a production MongoDB instance (MongoDB Atlas recommended)
- [ ] Set up proper logging
- [ ] Configure HTTPS
- [ ] Set up monitoring
- [ ] Use environment variables (never commit `.env`)
- [ ] Consider rate limiting
- [ ] Set up backup for MongoDB

## 🐛 Troubleshooting

### MongoDB Connection Error
```
Error: Database not initialized
```
**Solution:** Ensure MongoDB is running and `MONGODB_URL` is correct.

### CAPTCHA Not Working
```
Error: Invalid or expired CAPTCHA
```
**Solution:** Ensure you're using the correct `captcha_id` and answer within 5 minutes.

### Import Errors
```
ModuleNotFoundError: No module named 'app'
```
**Solution:** Run the app from the project root: `uvicorn app.main:app`

## 📞 Support

For issues or questions, contact the development team or create an issue in the project repository.

## 📄 License

Proprietary - HOMIGO Platform © 2024

---

**Built with ❤️ for HOMIGO - Find the place you deserve**

