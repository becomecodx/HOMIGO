# HOMIGO - ENTITY RELATIONSHIP DIAGRAM (ERD)

## Core Entity Relationships - Mermaid Diagram

```mermaid
erDiagram
    USERS ||--o| USER_VERIFICATIONS : has
    USERS ||--o| TENANT_PROFILES : "has (optional)"
    USERS ||--o| HOST_PROFILES : "has (optional)"
    USERS ||--o{ PAYMENTS : makes
    USERS ||--o{ SUBSCRIPTIONS : subscribes
    USERS ||--o{ NOTIFICATIONS : receives
    USERS ||--o{ MESSAGES : sends
    USERS ||--o{ RATINGS : "gives/receives"
    USERS ||--o{ REPORTS : "files/receives"
    USERS ||--o{ BLOCKED_USERS : "blocks/is_blocked"
    
    TENANT_PROFILES ||--o| TENANT_PRIORITIES : has
    TENANT_PROFILES ||--o{ TENANT_REQUIREMENTS : posts
    
    HOST_PROFILES ||--o| HOST_PREFERENCES : has
    HOST_PROFILES ||--o{ PROPERTY_LISTINGS : posts
    
    PROPERTY_LISTINGS ||--o{ PROPERTY_PHOTOS : has
    PROPERTY_LISTINGS ||--o{ LISTING_VIEWS : "is_viewed_by"
    PROPERTY_LISTINGS ||--o{ SWIPE_ACTIONS : "receives"
    
    TENANT_REQUIREMENTS ||--o{ REQUIREMENT_VIEWS : "is_viewed_by"
    TENANT_REQUIREMENTS ||--o{ SWIPE_ACTIONS : "receives"
    
    SWIPE_ACTIONS }o--|| MATCHES : "creates (mutual)"
    
    MATCHES ||--|| CONVERSATIONS : has
    MATCHES ||--o{ SERVICE_REQUESTS : generates
    
    CONVERSATIONS ||--o{ MESSAGES : contains
    
    PAYMENTS }o--o| PROPERTY_LISTINGS : "for"
    PAYMENTS }o--o| TENANT_REQUIREMENTS : "for"
    PAYMENTS }o--o| SUBSCRIPTIONS : "for"
    
    PARTNER_SERVICES ||--o{ SERVICE_REQUESTS : provides

    USERS {
        uuid user_id PK
        varchar full_name
        varchar email UK
        varchar phone UK
        date date_of_birth
        varchar gender
        varchar user_type
        varchar account_status
        timestamp created_at
    }
    
    USER_VERIFICATIONS {
        uuid verification_id PK
        uuid user_id FK
        boolean phone_verified
        boolean email_verified
        boolean aadhaar_verified
        boolean face_id_verified
        boolean is_fully_verified
    }
    
    TENANT_PROFILES {
        uuid tenant_profile_id PK
        uuid user_id FK UK
        varchar occupation_type
        varchar smoking
        varchar drinking
        varchar food_preference
        text lifestyle_notes
        int profile_completeness
    }
    
    TENANT_REQUIREMENTS {
        uuid requirement_id PK
        uuid user_id FK
        varchar title
        decimal budget_min
        decimal budget_max
        jsonb preferred_localities
        geography preferred_coordinates
        varchar occupancy
        varchar property_type
        date possession_date
        varchar status
        boolean is_premium
        date expires_at
    }
    
    HOST_PROFILES {
        uuid host_profile_id PK
        uuid user_id FK UK
        varchar host_category
        varchar company_name
        decimal avg_rating
        int total_properties_listed
        boolean is_premium
    }
    
    PROPERTY_LISTINGS {
        uuid listing_id PK
        uuid host_id FK
        varchar title
        varchar locality
        geography coordinates
        varchar property_type
        varchar configuration
        decimal rent_monthly
        decimal deposit_amount
        varchar furnishing
        date possession_date
        varchar status
        boolean is_premium
        boolean is_featured
        date expires_at
    }
    
    PROPERTY_PHOTOS {
        uuid photo_id PK
        uuid listing_id FK
        text photo_url
        varchar photo_type
        int sequence_order
        boolean is_primary
        boolean is_verified
    }
    
    SWIPE_ACTIONS {
        uuid swipe_id PK
        uuid swiper_id FK
        varchar swiper_type
        uuid swiped_listing_id FK
        uuid swiped_requirement_id FK
        uuid swiped_user_id FK
        varchar action
        decimal compatibility_score
        timestamp created_at
    }
    
    MATCHES {
        uuid match_id PK
        uuid tenant_id FK
        uuid host_id FK
        uuid requirement_id FK
        uuid listing_id FK
        decimal compatibility_score
        varchar match_status
        boolean contact_shared
        boolean deal_closed
        timestamp matched_at
    }
    
    CONVERSATIONS {
        uuid conversation_id PK
        uuid match_id FK UK
        uuid tenant_id FK
        uuid host_id FK
        timestamp last_message_at
        boolean is_active
    }
    
    MESSAGES {
        uuid message_id PK
        uuid conversation_id FK
        uuid sender_id FK
        text message_text
        varchar message_type
        boolean is_read
        timestamp sent_at
    }
    
    NOTIFICATIONS {
        uuid notification_id PK
        uuid user_id FK
        varchar notification_type
        varchar title
        text body
        boolean sent_via_whatsapp
        boolean is_read
        timestamp created_at
    }
    
    PAYMENTS {
        uuid payment_id PK
        uuid user_id FK
        varchar payment_for
        decimal amount
        varchar payment_method
        varchar status
        timestamp initiated_at
        timestamp completed_at
    }
    
    SUBSCRIPTIONS {
        uuid subscription_id PK
        uuid user_id FK
        varchar subscription_type
        int duration_months
        decimal final_amount
        varchar status
        date starts_at
        date expires_at
    }
    
    RATINGS {
        uuid rating_id PK
        uuid rater_id FK
        uuid rated_user_id FK
        uuid match_id FK
        decimal rating_value
        text review_text
        boolean is_verified
    }
```

---

## Simplified Visual Representation

### Main User Journey Flow

```
┌──────────────────────────────────────────────────────────────┐
│                        USER REGISTRATION                      │
│  Phone OTP → Email OTP → Aadhaar OTP → Face ID → VERIFIED   │
└──────────────────────────────────────────────────────────────┘
                            ↓
                   ┌────────┴────────┐
                   │                 │
              ┌────▼────┐      ┌────▼────┐
              │ TENANT  │      │  HOST   │
              │ PROFILE │      │ PROFILE │
              └────┬────┘      └────┬────┘
                   │                 │
              ┌────▼────────┐  ┌────▼──────────┐
              │  POST       │  │  POST          │
              │ REQUIREMENT │  │  PROPERTY      │
              │             │  │  LISTING       │
              └────┬────────┘  └────┬───────────┘
                   │                 │
                   └────────┬────────┘
                            ↓
                   ┌────────────────┐
                   │  FEED/BROWSE   │
                   │  (with filters)│
                   └────────┬───────┘
                            ↓
                   ┌────────────────┐
                   │  SWIPE ACTION  │
                   │  (Like/Dislike)│
                   └────────┬───────┘
                            ↓
                    ┌───────────────┐
                    │ Mutual Like?  │
                    └───┬───────┬───┘
                        │ Yes   │ No
                        ↓       └─→ Continue Browsing
                    ┌───────┐
                    │ MATCH │
                    └───┬───┘
                        ↓
              ┌─────────────────────┐
              │ WhatsApp Notification│
              └─────────┬────────────┘
                        ↓
              ┌─────────────────────┐
              │ Contact Revealed    │
              │ Chat Enabled        │
              └─────────┬───────────┘
                        ↓
              ┌─────────────────────┐
              │ Schedule Visit      │
              └─────────┬───────────┘
                        ↓
              ┌─────────────────────┐
              │ Close Deal          │
              └─────────┬───────────┘
                        ↓
              ┌─────────────────────┐
              │ Rate & Review       │
              └─────────────────────┘
```

### Database Module Structure

```
┌─────────────────────────────────────────────────────────────┐
│                     HOMIGO DATABASE                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │ USER MANAGEMENT│  │  VERIFICATION  │  │   TENANT     │ │
│  │   - users      │  │  - user_verif. │  │   SYSTEM     │ │
│  │   - tenant_pro │  │  - otp_logs    │  │ - profiles   │ │
│  │   - host_pro   │  └────────────────┘  │ - requirements│ │
│  └────────────────┘                       │ - priorities │ │
│                                            └──────────────┘ │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │  HOST SYSTEM   │  │    MATCHING    │  │ COMMUNICATION│ │
│  │  - profiles    │  │  - swipe_act.  │  │ - conversat. │ │
│  │  - listings    │  │  - matches     │  │ - messages   │ │
│  │  - photos      │  │  - saved_items │  │ - notificat. │ │
│  │  - preferences │  └────────────────┘  │ - whatsapp   │ │
│  └────────────────┘                       └──────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │   PAYMENTS     │  │  TRUST/SAFETY  │  │  ANALYTICS   │ │
│  │  - payments    │  │  - ratings     │  │ - activity   │ │
│  │  - subscript.  │  │  - reports     │  │ - views      │ │
│  └────────────────┘  │  - blocked     │  └──────────────┘ │
│                       └────────────────┘                    │
│  ┌────────────────┐  ┌────────────────┐                    │
│  │  ADMIN/SYSTEM  │  │    SERVICES    │                    │
│  │  - admin_users │  │  - partners    │                    │
│  │  - settings    │  │  - requests    │                    │
│  └────────────────┘  └────────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Setup Guide

### Prerequisites

```bash
# Install PostgreSQL 15+
sudo apt update
sudo apt install postgresql-15 postgresql-contrib-15

# Install PostGIS
sudo apt install postgresql-15-postgis-3

# Install pgAdmin (optional, for GUI)
sudo apt install pgadmin4
```

### Step 1: Create Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database
CREATE DATABASE homigo;

# Create user
CREATE USER homigo_user WITH ENCRYPTED PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE homigo TO homigo_user;

# Enable PostGIS extension
\c homigo
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For text search

# Exit
\q
```

### Step 2: Run Schema Script

```bash
# Copy the schema file to server
scp homigo_schema_design.sql user@server:/tmp/

# Connect and run
psql -U homigo_user -d homigo -f /tmp/homigo_schema_design.sql
```

### Step 3: Verify Installation

```sql
-- Check tables
\dt

-- Check PostGIS
SELECT PostGIS_Version();

-- Check UUID extension
SELECT uuid_generate_v4();

-- Verify key tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

### Step 4: Create Initial Admin User

```sql
-- Insert admin user
INSERT INTO users (full_name, email, phone, user_type, account_status)
VALUES ('Admin User', 'admin@homigo.com', '9999999999', 'both', 'active')
RETURNING user_id;

-- Use the returned user_id in next query
INSERT INTO admin_users (user_id, role, is_active)
VALUES ('<user_id_from_above>', 'super_admin', true);

-- Mark as verified
INSERT INTO user_verifications (
    user_id, 
    phone_verified, 
    email_verified, 
    aadhaar_verified, 
    face_id_verified
) VALUES (
    '<user_id_from_above>', 
    true, 
    true, 
    true, 
    true
);
```

### Step 5: Configure Connection Pooling (PgBouncer)

```bash
# Install PgBouncer
sudo apt install pgbouncer

# Edit config
sudo nano /etc/pgbouncer/pgbouncer.ini
```

Add configuration:
```ini
[databases]
homigo = host=localhost port=5432 dbname=homigo

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 5
max_db_connections = 50
max_user_connections = 50
```

Start PgBouncer:
```bash
sudo systemctl enable pgbouncer
sudo systemctl start pgbouncer
```

### Step 6: Setup Backups

```bash
# Create backup directory
sudo mkdir -p /var/backups/postgresql

# Create backup script
sudo nano /usr/local/bin/backup_homigo.sh
```

Backup script:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/postgresql"
DB_NAME="homigo"
DB_USER="homigo_user"

# Create backup
pg_dump -U $DB_USER -d $DB_NAME -F c -f $BACKUP_DIR/homigo_$DATE.backup

# Keep only last 7 days
find $BACKUP_DIR -name "homigo_*.backup" -mtime +7 -delete

# Upload to S3 (optional)
# aws s3 cp $BACKUP_DIR/homigo_$DATE.backup s3://your-bucket/backups/
```

Make executable and schedule:
```bash
sudo chmod +x /usr/local/bin/backup_homigo.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add line:
# 0 2 * * * /usr/local/bin/backup_homigo.sh
```

### Step 7: Monitoring Setup

```sql
-- Create monitoring view
CREATE VIEW db_health_check AS
SELECT
    'Database Size' as metric,
    pg_size_pretty(pg_database_size('homigo')) as value
UNION ALL
SELECT
    'Active Connections',
    count(*)::text
FROM pg_stat_activity
WHERE datname = 'homigo'
UNION ALL
SELECT
    'Slow Queries (>1s)',
    count(*)::text
FROM pg_stat_activity
WHERE datname = 'homigo'
  AND state = 'active'
  AND (now() - query_start) > interval '1 second';

-- Create slow query log
-- Add to postgresql.conf:
-- log_min_duration_statement = 1000  # Log queries > 1s
-- log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

---

## Environment Configuration

### .env File Template

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=6432  # PgBouncer port
DB_NAME=homigo
DB_USER=homigo_user
DB_PASSWORD=your_secure_password
DB_SSL=false
DB_POOL_MIN=5
DB_POOL_MAX=25

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# Application
APP_ENV=production
APP_PORT=3000
APP_SECRET_KEY=your_256_bit_secret_key
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRY=7d

# Verification Services
AADHAAR_API_KEY=your_aadhaar_api_key
FACE_VERIFICATION_API_KEY=your_face_api_key

# Messaging
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890

# WhatsApp (via Twilio or other)
WHATSAPP_API_KEY=your_whatsapp_api_key
WHATSAPP_PHONE_NUMBER=+1234567890

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@homigo.com
SMTP_PASSWORD=your_smtp_password

# Payment Gateways
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# File Storage
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=ap-south-1
S3_BUCKET_NAME=homigo-uploads

# Google Maps API
GOOGLE_MAPS_API_KEY=your_google_maps_key

# Firebase (for push notifications)
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY=your_private_key
FIREBASE_CLIENT_EMAIL=your_client_email

# Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=info
```

---

## Testing Data Generator

### Sample Script to Generate Test Data

```python
import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('en_IN')

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port=6432,
    database="homigo",
    user="homigo_user",
    password="your_secure_password"
)
cur = conn.cursor()

# Generate 100 test users (50 tenants, 50 hosts)
for i in range(100):
    user_type = 'tenant' if i < 50 else 'host'
    
    # Insert user
    cur.execute("""
        INSERT INTO users (full_name, email, phone, date_of_birth, gender, user_type)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING user_id
    """, (
        fake.name(),
        fake.email(),
        fake.phone_number()[:10],
        fake.date_of_birth(minimum_age=18, maximum_age=60),
        random.choice(['Male', 'Female']),
        user_type
    ))
    
    user_id = cur.fetchone()[0]
    
    # Insert verification
    cur.execute("""
        INSERT INTO user_verifications (
            user_id, phone_verified, email_verified, 
            aadhaar_verified, face_id_verified
        ) VALUES (%s, true, true, true, true)
    """, (user_id,))
    
    # Insert tenant profile and requirement
    if user_type == 'tenant':
        cur.execute("""
            INSERT INTO tenant_profiles (
                user_id, occupation_type, smoking, drinking, food_preference
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            random.choice(['working_professional', 'student']),
            random.choice(['yes', 'no']),
            random.choice(['yes', 'no', 'occasionally']),
            random.choice(['veg', 'non_veg', 'both'])
        ))
        
        cur.execute("""
            INSERT INTO tenant_requirements (
                user_id, title, budget_min, budget_max, occupancy,
                property_type, possession_date, status, expires_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'active', %s)
        """, (
            user_id,
            f"Looking for {random.choice(['1BHK', '2BHK', 'Room'])} in Mumbai",
            random.randint(8000, 15000),
            random.randint(15000, 30000),
            random.choice(['single', 'double']),
            random.choice(['flat', 'pg']),
            datetime.now() + timedelta(days=random.randint(7, 60)),
            datetime.now() + timedelta(days=30)
        ))
    
    # Insert host profile and listing
    else:
        cur.execute("""
            INSERT INTO host_profiles (
                user_id, host_category
            ) VALUES (%s, %s)
        """, (
            user_id,
            random.choice(['owner', 'broker'])
        ))
        
        cur.execute("""
            INSERT INTO property_listings (
                host_id, title, locality, city, state,
                property_type, configuration, rent_monthly,
                deposit_amount, possession_date, status, expires_at
            ) VALUES (%s, %s, %s, 'Mumbai', 'Maharashtra', %s, %s, %s, %s, %s, 'active', %s)
        """, (
            user_id,
            f"{random.choice(['1BHK', '2BHK', '2BHK'])} for Rent in {fake.city()}",
            fake.city(),
            random.choice(['apartment', 'house']),
            random.choice(['1bhk', '2bhk', '3bhk']),
            random.randint(10000, 40000),
            random.randint(20000, 80000),
            datetime.now() + timedelta(days=random.randint(7, 30)),
            datetime.now() + timedelta(days=30)
        ))

conn.commit()
cur.close()
conn.close()

print("✅ Generated 100 test users with profiles and postings!")
```

---

## Performance Benchmarks

### Expected Query Performance Targets

| Operation | Target Latency | Notes |
|-----------|----------------|-------|
| User Login | < 100ms | With cached verification |
| Feed Load (20 items) | < 300ms | With geospatial filtering |
| Swipe Action | < 50ms | Update + trigger |
| Match Creation | < 200ms | Transaction + notifications |
| Message Send | < 100ms | Insert + push notification |
| Search Query | < 500ms | Full-text + filters |
| Payment Init | < 200ms | Create record + redirect |
| Load Conversation | < 150ms | Last 50 messages |

### Load Testing Targets

- **Concurrent Users**: 10,000
- **Requests/Second**: 1,000
- **Database Connections**: 500 (via pooling)
- **Response Time P95**: < 500ms
- **Response Time P99**: < 1s

---

## Security Checklist

- [ ] All passwords hashed with bcrypt (cost factor 12)
- [ ] Aadhaar numbers encrypted at rest
- [ ] SQL injection prevention (parameterized queries)
- [ ] Rate limiting on APIs (100 req/min per user)
- [ ] HTTPS only (SSL/TLS)
- [ ] JWT token expiry (7 days)
- [ ] CORS configured properly
- [ ] Input validation on all endpoints
- [ ] File upload restrictions (type, size)
- [ ] Database backups encrypted
- [ ] Environment variables secured
- [ ] Database user has minimal required permissions
- [ ] Audit logging for sensitive operations
- [ ] Regular security updates
- [ ] Penetration testing before launch

---

## Launch Readiness Checklist

### Database
- [ ] Schema deployed to production
- [ ] Indexes created and verified
- [ ] Triggers tested
- [ ] Views created
- [ ] Backup system configured
- [ ] Monitoring setup
- [ ] Connection pooling configured
- [ ] Performance tested

### Application
- [ ] All APIs implemented
- [ ] Authentication working
- [ ] Payment integration tested
- [ ] WhatsApp integration working
- [ ] Email system configured
- [ ] Push notifications working
- [ ] File upload functional
- [ ] Error handling implemented

### Testing
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests
- [ ] Load testing completed
- [ ] Security audit done
- [ ] UAT completed
- [ ] Beta testing done

### Operations
- [ ] Server provisioned
- [ ] Domain configured
- [ ] SSL certificate installed
- [ ] CDN setup for static files
- [ ] Monitoring dashboards
- [ ] Alerting configured
- [ ] Documentation complete
- [ ] Team trained

---

## Support & Maintenance

### For Development Team

**Primary Contact**: Abhishek Yadav (CTO)
**Development Team Lead**: [To be assigned]
**Database Admin**: [To be assigned]

### Emergency Procedures

**Database Down:**
1. Check PostgreSQL service status
2. Check disk space
3. Review logs: `/var/log/postgresql/`
4. Restart if needed: `sudo systemctl restart postgresql`
5. If persists, restore from backup

**Performance Issues:**
1. Check active connections
2. Review slow query log
3. Check for locks: `SELECT * FROM pg_locks WHERE NOT granted;`
4. Analyze query plans
5. Add indexes if needed

**Data Corruption:**
1. Stop all writes
2. Create immediate backup
3. Restore from last known good backup
4. Investigate root cause
5. Implement fixes
6. Resume operations

---

This comprehensive setup guide should help the development team get started with implementing the Homigo database schema.
