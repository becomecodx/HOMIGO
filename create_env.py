"""
Helper script to create .env file for HOMIGO Authentication API
Run this script: python create_env.py
"""

import secrets
import os

# Generate a strong JWT secret key
jwt_secret = secrets.token_urlsafe(32)

# .env file content
env_content = f"""# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=homigo_db

# JWT Configuration
JWT_SECRET_KEY={jwt_secret}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application Configuration
APP_NAME=HOMIGO
APP_VERSION=1.0.0
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# CAPTCHA Configuration
CAPTCHA_EXPIRY_SECONDS=300
"""

# Check if .env already exists
if os.path.exists('.env'):
    response = input('.env file already exists. Overwrite? (y/n): ')
    if response.lower() != 'y':
        print('Cancelled. .env file not modified.')
        exit(0)

# Write .env file
try:
    with open('.env', 'w') as f:
        f.write(env_content)
    print('[SUCCESS] .env file created successfully!')
    print(f'[SUCCESS] JWT Secret Key generated: {jwt_secret[:20]}...')
    print('\nNext steps:')
    print('1. Review the .env file and update MONGODB_URL if needed')
    print('2. Update ALLOWED_ORIGINS with your frontend URLs')
    print('3. Run: pip install -r requirements.txt')
    print('4. Run: uvicorn app.main:app --reload --port 8000')
except Exception as e:
    print(f'[ERROR] Error creating .env file: {e}')

