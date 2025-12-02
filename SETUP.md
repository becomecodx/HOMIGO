# HOMIGO Authentication API - Quick Setup Guide

## 🚀 Quick Start Steps

### Step 1: Create Virtual Environment

```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Create `.env` File

Create a file named `.env` in the root directory (`HOMIGO/.env`) with the following content:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=homigo_db

# JWT Configuration (IMPORTANT: Change JWT_SECRET_KEY in production!)
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-characters-long-change-in-production
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

**⚠️ IMPORTANT NOTES:**
- Replace `JWT_SECRET_KEY` with a strong random string (minimum 32 characters) before production use
- Update `MONGODB_URL` if your MongoDB is running on a different host/port
- Update `ALLOWED_ORIGINS` to include your frontend URLs

### Step 4: Start MongoDB

Make sure MongoDB is running:

```bash
# Windows
net start MongoDB

# macOS (Homebrew)
brew services start mongodb-community

# Linux
sudo systemctl start mongod
```

### Step 5: Run the Application

```bash
uvicorn app.main:app --reload --port 8000
```

### Step 6: Test the API

Open your browser and go to:
- **API Documentation**: http://localhost:8000/api/docs
- **Alternative Docs**: http://localhost:8000/api/redoc

## ✅ Verification

To verify everything is working:

1. **Check health endpoint:**
   ```bash
   curl http://localhost:8000/api/auth/health
   ```

2. **Generate CAPTCHA:**
   ```bash
   curl http://localhost:8000/api/auth/captcha
   ```

If both commands return JSON responses, you're good to go! 🎉

## 🆘 Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Verify MongoDB is running: `mongosh` or `mongo`
- Check logs for error messages
- Ensure all dependencies are installed: `pip list`

## 🔐 Generating a Strong JWT Secret Key

For production, generate a strong JWT secret key:

**Using Python:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

**Using OpenSSL:**
```bash
openssl rand -base64 32
```

Copy the generated string and use it as your `JWT_SECRET_KEY` in the `.env` file.

---

**Happy coding! 🚀**

