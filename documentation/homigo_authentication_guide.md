# HOMIGO AUTHENTICATION IMPLEMENTATION GUIDE
**Hybrid Approach: Firebase + Custom JWT**

---

## Table of Contents
1. [Authentication Strategy Overview](#authentication-strategy-overview)
2. [Firebase Setup](#firebase-setup)
3. [Custom JWT Implementation](#custom-jwt-implementation)
4. [Complete Authentication Flow](#complete-authentication-flow)
5. [Code Examples](#code-examples)
6. [Security Considerations](#security-considerations)

---

## Authentication Strategy Overview

### Why Hybrid Approach?

**Firebase for:**
- ✅ Phone OTP verification (reliable delivery)
- ✅ Email OTP verification
- ✅ Social logins (Google, Apple) - future
- ✅ Handles SMS/Email delivery infrastructure
- ✅ Proven reliability at scale

**Custom JWT for:**
- ✅ Session management
- ✅ Role-based access control (RBAC)
- ✅ Fine-grained permissions
- ✅ API authorization
- ✅ Custom claims (user_type, verification_status)
- ✅ No vendor lock-in for core business logic

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      MOBILE/WEB APP                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ↓
    ┌──────────────────────────────────────────┐
    │   1. Send Phone Number                   │
    └──────────────┬───────────────────────────┘
                   ↓
    ┌──────────────────────────────────────────┐
    │   FIREBASE AUTHENTICATION                │
    │   - Sends OTP via SMS                    │
    │   - Returns verification_id              │
    └──────────────┬───────────────────────────┘
                   ↓
    ┌──────────────────────────────────────────┐
    │   2. User enters OTP                     │
    │   3. Client verifies with Firebase       │
    └──────────────┬───────────────────────────┘
                   ↓
    ┌──────────────────────────────────────────┐
    │   4. Firebase returns ID Token           │
    └──────────────┬───────────────────────────┘
                   ↓
    ┌──────────────────────────────────────────┐
    │   5. Send Firebase Token to Backend      │
    └──────────────┬───────────────────────────┘
                   ↓
    ┌──────────────────────────────────────────┐
    │   HOMIGO BACKEND SERVER                  │
    │                                           │
    │   6. Verify Firebase Token               │
    │   7. Check/Create user in DB             │
    │   8. Generate Custom JWT                 │
    │   9. Return JWT + User Data              │
    └──────────────┬───────────────────────────┘
                   ↓
    ┌──────────────────────────────────────────┐
    │   10. Client stores JWT                  │
    │   11. Use JWT for all API calls          │
    └──────────────────────────────────────────┘
```

---

## Firebase Setup

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create new project: "Homigo"
3. Enable Google Analytics (optional)
4. Get your configuration

### 2. Enable Authentication Methods

```
Firebase Console → Authentication → Sign-in method
```

Enable:
- ✅ Phone (for OTP)
- ✅ Email/Password (for email verification)
- ✅ Google (for future social login)
- ✅ Apple (for future social login)

### 3. Configure Phone Authentication

**Enable Phone Providers:**
- Select phone authentication
- Enable "Phone number sign-in"
- Add test phone numbers (for development)

**Test Phone Numbers (Development):**
```
Phone: +91 9999999999
Code: 123456
```

### 4. Get Firebase Configuration

**For Web:**
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "homigo.firebaseapp.com",
  projectId: "homigo",
  storageBucket: "homigo.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef123456"
};
```

**For Android:**
Download `google-services.json`

**For iOS:**
Download `GoogleService-Info.plist`

### 5. Get Service Account Key (Backend)

```
Firebase Console → Project Settings → Service Accounts → Generate New Private Key
```

Download JSON file: `homigo-firebase-adminsdk.json`

**⚠️ CRITICAL:** Never commit this file to git! Store securely.

---

## Custom JWT Implementation

### JWT Structure

```javascript
{
  // Header
  "alg": "HS256",
  "typ": "JWT"
  
  // Payload
  "user_id": "uuid-here",
  "phone": "+919876543210",
  "email": "user@example.com",
  "user_type": "tenant",  // or "host" or "both"
  "verification_status": {
    "is_fully_verified": true,
    "phone_verified": true,
    "email_verified": true,
    "aadhaar_verified": true,
    "face_id_verified": true
  },
  "is_premium": false,
  "role": "user",  // or "admin"
  "iat": 1642234567,  // Issued at
  "exp": 1642839367   // Expires at (7 days)
  
  // Signature
  "signature": "..."
}
```

### JWT Secret Management

```bash
# Generate strong secret (256-bit)
openssl rand -base64 32

# Store in environment variable
export JWT_SECRET="your_generated_secret_here"
export JWT_REFRESH_SECRET="another_secret_for_refresh_tokens"
```

---

## Complete Authentication Flow

### Flow 1: Phone OTP Signup/Login

#### Client-Side (React Native / React Web)

```javascript
// Step 1: Initialize Firebase
import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  RecaptchaVerifier,
  signInWithPhoneNumber 
} from 'firebase/auth';

const firebaseConfig = { /* your config */ };
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Step 2: Setup reCAPTCHA (for web)
const setupRecaptcha = () => {
  window.recaptchaVerifier = new RecaptchaVerifier(
    'recaptcha-container',
    {
      'size': 'invisible',
      'callback': (response) => {
        // reCAPTCHA solved
      }
    },
    auth
  );
};

// Step 3: Send OTP
const sendOTP = async (phoneNumber) => {
  try {
    setupRecaptcha();
    const appVerifier = window.recaptchaVerifier;
    
    const confirmationResult = await signInWithPhoneNumber(
      auth,
      phoneNumber,  // e.g., "+919876543210"
      appVerifier
    );
    
    // Store confirmation result for verification
    window.confirmationResult = confirmationResult;
    
    return {
      success: true,
      message: "OTP sent successfully"
    };
  } catch (error) {
    console.error("Error sending OTP:", error);
    return {
      success: false,
      error: error.message
    };
  }
};

// Step 4: Verify OTP
const verifyOTP = async (otp) => {
  try {
    const result = await window.confirmationResult.confirm(otp);
    
    // User signed in with Firebase
    const firebaseUser = result.user;
    const firebaseToken = await firebaseUser.getIdToken();
    
    // Send to your backend
    const response = await fetch('https://api.homigo.com/v1/auth/verify-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        firebase_token: firebaseToken,
        phone: firebaseUser.phoneNumber,
        device_id: getDeviceId(),
        fcm_token: getFCMToken()
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Store your custom JWT
      localStorage.setItem('access_token', data.data.token.access_token);
      localStorage.setItem('refresh_token', data.data.token.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.data.user));
      
      return {
        success: true,
        user: data.data.user
      };
    }
  } catch (error) {
    console.error("Error verifying OTP:", error);
    return {
      success: false,
      error: error.message
    };
  }
};
```

#### Backend (Node.js + Express Example)

```javascript
const admin = require('firebase-admin');
const jwt = require('jsonwebtoken');
const { Pool } = require('pg');

// Initialize Firebase Admin
const serviceAccount = require('./homigo-firebase-adminsdk.json');
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

// Database pool
const pool = new Pool({
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  port: 6432  // PgBouncer port
});

// Verify OTP endpoint
app.post('/auth/verify-otp', async (req, res) => {
  try {
    const { firebase_token, phone, device_id, fcm_token } = req.body;
    
    // Step 1: Verify Firebase token
    const decodedToken = await admin.auth().verifyIdToken(firebase_token);
    const firebaseUid = decodedToken.uid;
    const phoneFromToken = decodedToken.phone_number;
    
    // Verify phone matches
    if (phoneFromToken !== phone) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'PHONE_MISMATCH',
          message: 'Phone number does not match token'
        }
      });
    }
    
    // Step 2: Check if user exists in our database
    let user = await getUserByPhone(phone);
    let isNewUser = false;
    
    if (!user) {
      // Create new user
      user = await createUser({
        phone: phone,
        firebase_uid: firebaseUid,
        device_id: device_id,
        fcm_token: fcm_token
      });
      isNewUser = true;
      
      // Create verification record with phone verified
      await createUserVerification(user.user_id, {
        phone_verified: true
      });
    } else {
      // Update existing user
      await updateUser(user.user_id, {
        firebase_uid: firebaseUid,
        device_id: device_id,
        fcm_token: fcm_token,
        last_login_at: new Date()
      });
    }
    
    // Step 3: Get user's verification status
    const verification = await getUserVerification(user.user_id);
    
    // Step 4: Generate custom JWT
    const accessToken = jwt.sign(
      {
        user_id: user.user_id,
        phone: user.phone,
        email: user.email,
        user_type: user.user_type,
        verification_status: {
          is_fully_verified: verification.is_fully_verified,
          phone_verified: verification.phone_verified,
          email_verified: verification.email_verified,
          aadhaar_verified: verification.aadhaar_verified,
          face_id_verified: verification.face_id_verified
        },
        role: 'user'
      },
      process.env.JWT_SECRET,
      {
        expiresIn: '7d',  // 7 days
        issuer: 'homigo-api',
        audience: 'homigo-app'
      }
    );
    
    // Generate refresh token
    const refreshToken = jwt.sign(
      {
        user_id: user.user_id,
        type: 'refresh'
      },
      process.env.JWT_REFRESH_SECRET,
      {
        expiresIn: '30d'  // 30 days
      }
    );
    
    // Step 5: Return response
    return res.status(200).json({
      success: true,
      message: 'Authentication successful',
      data: {
        user: {
          user_id: user.user_id,
          phone: user.phone,
          email: user.email,
          full_name: user.full_name,
          user_type: user.user_type,
          is_new_user: isNewUser,
          profile_completed: user.profile_completeness > 80,
          verification_status: verification
        },
        token: {
          access_token: accessToken,
          token_type: 'Bearer',
          expires_in: 604800,  // 7 days in seconds
          refresh_token: refreshToken
        }
      }
    });
    
  } catch (error) {
    console.error('Auth error:', error);
    
    if (error.code === 'auth/id-token-expired') {
      return res.status(401).json({
        success: false,
        error: {
          code: 'TOKEN_EXPIRED',
          message: 'Firebase token expired'
        }
      });
    }
    
    return res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Authentication failed'
      }
    });
  }
});

// Helper functions
async function getUserByPhone(phone) {
  const result = await pool.query(
    'SELECT * FROM users WHERE phone = $1',
    [phone]
  );
  return result.rows[0];
}

async function createUser(data) {
  const result = await pool.query(
    `INSERT INTO users (phone, user_type, device_token, fcm_token, account_status)
     VALUES ($1, 'tenant', $2, $3, 'active')
     RETURNING *`,
    [data.phone, data.device_id, data.fcm_token]
  );
  return result.rows[0];
}

async function createUserVerification(userId, verification) {
  await pool.query(
    `INSERT INTO user_verifications (user_id, phone_verified, phone_verified_at)
     VALUES ($1, $2, NOW())`,
    [userId, verification.phone_verified]
  );
}

async function getUserVerification(userId) {
  const result = await pool.query(
    'SELECT * FROM user_verifications WHERE user_id = $1',
    [userId]
  );
  return result.rows[0];
}

async function updateUser(userId, data) {
  await pool.query(
    `UPDATE users 
     SET device_token = $2, fcm_token = $3, last_login_at = $4
     WHERE user_id = $1`,
    [userId, data.device_id, data.fcm_token, data.last_login_at]
  );
}
```

---

### Flow 2: Email OTP Verification

#### Client-Side

```javascript
// Send email OTP
const sendEmailOTP = async (email) => {
  try {
    const response = await fetch('https://api.homigo.com/v1/auth/send-email-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAccessToken()}`
      },
      body: JSON.stringify({ email })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
};

// Verify email OTP
const verifyEmailOTP = async (email, otp, sessionId) => {
  try {
    const response = await fetch('https://api.homigo.com/v1/auth/verify-email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAccessToken()}`
      },
      body: JSON.stringify({
        email,
        otp,
        session_id: sessionId
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
};
```

#### Backend

```javascript
// Send Email OTP endpoint
app.post('/auth/send-email-otp', authenticateJWT, async (req, res) => {
  try {
    const { email } = req.body;
    const userId = req.user.user_id;
    
    // Generate 6-digit OTP
    const otp = Math.floor(100000 + Math.random() * 900000).toString();
    const otpHash = await bcrypt.hash(otp, 10);
    const sessionId = uuidv4();
    
    // Store OTP in database
    await pool.query(
      `INSERT INTO otp_logs (user_id, contact_method, contact_value, otp_code, otp_hash, purpose, expires_at)
       VALUES ($1, 'email', $2, $3, $4, 'verification', NOW() + INTERVAL '10 minutes')`,
      [userId, email, otp, otpHash]
    );
    
    // Send email
    await sendEmailWithOTP(email, otp);
    
    res.json({
      success: true,
      message: 'OTP sent to email',
      data: {
        session_id: sessionId,
        expires_in: 600
      }
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({
      success: false,
      error: { message: 'Failed to send OTP' }
    });
  }
});

// Verify Email OTP endpoint
app.post('/auth/verify-email', authenticateJWT, async (req, res) => {
  try {
    const { email, otp, session_id } = req.body;
    const userId = req.user.user_id;
    
    // Get OTP from database
    const otpRecord = await pool.query(
      `SELECT * FROM otp_logs 
       WHERE user_id = $1 AND contact_value = $2 AND contact_method = 'email'
       AND expires_at > NOW() AND is_verified = false
       ORDER BY created_at DESC LIMIT 1`,
      [userId, email]
    );
    
    if (otpRecord.rows.length === 0) {
      return res.status(400).json({
        success: false,
        error: { message: 'OTP expired or not found' }
      });
    }
    
    const record = otpRecord.rows[0];
    
    // Verify OTP
    const isValid = await bcrypt.compare(otp, record.otp_hash);
    
    if (!isValid) {
      // Increment attempts
      await pool.query(
        'UPDATE otp_logs SET attempts = attempts + 1 WHERE otp_id = $1',
        [record.otp_id]
      );
      
      return res.status(400).json({
        success: false,
        error: { message: 'Invalid OTP' }
      });
    }
    
    // Mark OTP as verified
    await pool.query(
      'UPDATE otp_logs SET is_verified = true, verified_at = NOW() WHERE otp_id = $1',
      [record.otp_id]
    );
    
    // Update user email and verification
    await pool.query(
      'UPDATE users SET email = $1 WHERE user_id = $2',
      [email, userId]
    );
    
    await pool.query(
      `UPDATE user_verifications 
       SET email_verified = true, email_verified_at = NOW()
       WHERE user_id = $1`,
      [userId]
    );
    
    res.json({
      success: true,
      message: 'Email verified successfully',
      data: {
        email_verified: true
      }
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({
      success: false,
      error: { message: 'Verification failed' }
    });
  }
});

// Email sending function (using NodeMailer)
const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransporter({
  host: process.env.SMTP_HOST,
  port: process.env.SMTP_PORT,
  secure: false,
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASSWORD
  }
});

async function sendEmailWithOTP(email, otp) {
  const mailOptions = {
    from: 'Homigo <noreply@homigo.com>',
    to: email,
    subject: 'Verify your email - Homigo',
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Verify Your Email</h2>
        <p>Your OTP for email verification is:</p>
        <h1 style="color: #00A86B; font-size: 32px; letter-spacing: 5px;">${otp}</h1>
        <p>This OTP will expire in 10 minutes.</p>
        <p>If you didn't request this, please ignore this email.</p>
        <hr>
        <p style="color: #666; font-size: 12px;">Homigo - Find Your Perfect Home</p>
      </div>
    `
  };
  
  await transporter.sendMail(mailOptions);
}
```

---

### JWT Middleware for Protected Routes

```javascript
const jwt = require('jsonwebtoken');

// Middleware to authenticate JWT
const authenticateJWT = (req, res, next) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader) {
    return res.status(401).json({
      success: false,
      error: {
        code: 'UNAUTHORIZED',
        message: 'No token provided'
      }
    });
  }
  
  const token = authHeader.split(' ')[1];  // Bearer <token>
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET, {
      issuer: 'homigo-api',
      audience: 'homigo-app'
    });
    
    // Attach user info to request
    req.user = decoded;
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        error: {
          code: 'TOKEN_EXPIRED',
          message: 'Token has expired'
        }
      });
    }
    
    return res.status(403).json({
      success: false,
      error: {
        code: 'INVALID_TOKEN',
        message: 'Invalid token'
      }
    });
  }
};

// Middleware to check verification status
const requireVerified = (req, res, next) => {
  if (!req.user.verification_status.is_fully_verified) {
    return res.status(403).json({
      success: false,
      error: {
        code: 'VERIFICATION_REQUIRED',
        message: 'Please complete all verifications'
      }
    });
  }
  next();
};

// Middleware to check user type
const requireUserType = (...types) => {
  return (req, res, next) => {
    if (!types.includes(req.user.user_type)) {
      return res.status(403).json({
        success: false,
        error: {
          code: 'FORBIDDEN',
          message: 'Insufficient permissions'
        }
      });
    }
    next();
  };
};

// Usage in routes
app.get('/tenant/profile', 
  authenticateJWT, 
  requireUserType('tenant', 'both'), 
  async (req, res) => {
    // Handler code
  }
);

app.post('/listings', 
  authenticateJWT, 
  requireVerified,
  requireUserType('host', 'both'), 
  async (req, res) => {
    // Handler code
  }
);
```

---

### Refresh Token Implementation

```javascript
// Refresh token endpoint
app.post('/auth/refresh-token', async (req, res) => {
  try {
    const { refresh_token } = req.body;
    
    if (!refresh_token) {
      return res.status(401).json({
        success: false,
        error: { message: 'Refresh token required' }
      });
    }
    
    // Verify refresh token
    const decoded = jwt.verify(refresh_token, process.env.JWT_REFRESH_SECRET);
    
    if (decoded.type !== 'refresh') {
      return res.status(403).json({
        success: false,
        error: { message: 'Invalid token type' }
      });
    }
    
    // Get fresh user data
    const user = await getUserById(decoded.user_id);
    if (!user) {
      return res.status(404).json({
        success: false,
        error: { message: 'User not found' }
      });
    }
    
    const verification = await getUserVerification(user.user_id);
    
    // Generate new access token
    const newAccessToken = jwt.sign(
      {
        user_id: user.user_id,
        phone: user.phone,
        email: user.email,
        user_type: user.user_type,
        verification_status: verification,
        role: 'user'
      },
      process.env.JWT_SECRET,
      {
        expiresIn: '7d',
        issuer: 'homigo-api',
        audience: 'homigo-app'
      }
    );
    
    res.json({
      success: true,
      data: {
        access_token: newAccessToken,
        expires_in: 604800
      }
    });
  } catch (error) {
    console.error('Refresh token error:', error);
    return res.status(401).json({
      success: false,
      error: {
        code: 'INVALID_REFRESH_TOKEN',
        message: 'Refresh token is invalid or expired'
      }
    });
  }
});
```

---

## Security Considerations

### 1. Token Storage

**Mobile (React Native):**
```javascript
import * as SecureStore from 'expo-secure-store';

// Store tokens securely
await SecureStore.setItemAsync('access_token', token);
await SecureStore.setItemAsync('refresh_token', refreshToken);

// Retrieve
const token = await SecureStore.getItemAsync('access_token');
```

**Web:**
```javascript
// Option 1: Secure httpOnly cookies (RECOMMENDED)
res.cookie('access_token', token, {
  httpOnly: true,
  secure: true,  // HTTPS only
  sameSite: 'strict',
  maxAge: 7 * 24 * 60 * 60 * 1000  // 7 days
});

// Option 2: localStorage (less secure, but simpler)
localStorage.setItem('access_token', token);
```

### 2. Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 5,  // 5 requests per window
  message: {
    success: false,
    error: {
      code: 'RATE_LIMIT_EXCEEDED',
      message: 'Too many authentication attempts'
    }
  }
});

app.post('/auth/send-otp', authLimiter, async (req, res) => {
  // Handler
});
```

### 3. OTP Security

```javascript
// Generate cryptographically secure OTP
const crypto = require('crypto');

function generateSecureOTP(length = 6) {
  const digits = '0123456789';
  let otp = '';
  const randomBytes = crypto.randomBytes(length);
  
  for (let i = 0; i < length; i++) {
    otp += digits[randomBytes[i] % 10];
  }
  
  return otp;
}
```

### 4. Token Blacklisting (Optional)

For logout and token revocation:

```javascript
const Redis = require('redis');
const client = Redis.createClient();

// Logout endpoint
app.post('/auth/logout', authenticateJWT, async (req, res) => {
  try {
    const token = req.headers.authorization.split(' ')[1];
    const decoded = jwt.decode(token);
    
    // Calculate remaining TTL
    const exp = decoded.exp;
    const now = Math.floor(Date.now() / 1000);
    const ttl = exp - now;
    
    if (ttl > 0) {
      // Add token to blacklist with TTL
      await client.setex(`blacklist:${token}`, ttl, 'true');
    }
    
    res.json({
      success: true,
      message: 'Logged out successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: { message: 'Logout failed' }
    });
  }
});

// Updated JWT middleware to check blacklist
const authenticateJWT = async (req, res, next) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader) {
    return res.status(401).json({
      success: false,
      error: { code: 'UNAUTHORIZED', message: 'No token provided' }
    });
  }
  
  const token = authHeader.split(' ')[1];
  
  // Check if token is blacklisted
  const isBlacklisted = await client.get(`blacklist:${token}`);
  if (isBlacklisted) {
    return res.status(401).json({
      success: false,
      error: { code: 'TOKEN_REVOKED', message: 'Token has been revoked' }
    });
  }
  
  // Continue with normal verification...
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    // Error handling...
  }
};
```

---

## Environment Variables

```bash
# .env file

# Firebase
FIREBASE_PROJECT_ID=homigo
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@homigo.iam.gserviceaccount.com

# JWT
JWT_SECRET=your_256_bit_secret_key_here
JWT_REFRESH_SECRET=your_refresh_token_secret_here
JWT_EXPIRY=7d
JWT_REFRESH_EXPIRY=30d

# Database
DB_HOST=localhost
DB_PORT=6432
DB_NAME=homigo
DB_USER=homigo_user
DB_PASSWORD=your_db_password

# Redis (for token blacklisting)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@homigo.com
SMTP_PASSWORD=your_smtp_app_password
```

---

## Summary

### ✅ Implementation Checklist

**Phase 1: Firebase Setup**
- [ ] Create Firebase project
- [ ] Enable Phone authentication
- [ ] Enable Email authentication
- [ ] Download service account key
- [ ] Configure Firebase in client app

**Phase 2: Backend Setup**
- [ ] Install dependencies (firebase-admin, jsonwebtoken)
- [ ] Initialize Firebase Admin SDK
- [ ] Create JWT secret keys
- [ ] Implement token generation logic
- [ ] Create authentication endpoints

**Phase 3: Client Setup**
- [ ] Initialize Firebase in client
- [ ] Implement OTP sending flow
- [ ] Implement OTP verification
- [ ] Store JWT tokens securely
- [ ] Implement token refresh logic

**Phase 4: Security**
- [ ] Implement rate limiting
- [ ] Add token blacklisting (optional)
- [ ] Setup HTTPS
- [ ] Configure CORS properly
- [ ] Add request validation

**Phase 5: Testing**
- [ ] Test phone OTP flow
- [ ] Test email OTP flow
- [ ] Test token refresh
- [ ] Test logout
- [ ] Load testing

---

This hybrid approach gives you the best of both worlds - Firebase's reliability for OTP delivery and your own control over session management and authorization!
