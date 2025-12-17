# HOMIGO DATABASE SCHEMA DESIGN DOCUMENTATION
**Rental & Flatmate Marketplace Platform**

---

## Table of Contents
1. [Schema Overview](#schema-overview)
2. [Entity Relationship Summary](#entity-relationship-summary)
3. [Core Modules](#core-modules)
4. [Key Design Decisions](#key-design-decisions)
5. [API Integration Points](#api-integration-points)
6. [Matching Algorithm Data Flow](#matching-algorithm-data-flow)
7. [Performance Optimization](#performance-optimization)

---

## Schema Overview

The Homigo database schema consists of **40+ interconnected tables** organized into 10 major modules:

### Module Breakdown

| Module | Tables | Purpose |
|--------|--------|---------|
| **User Management** | 3 | Core user accounts, profiles, authentication |
| **Verification** | 2 | Multi-layer verification (OTP, Aadhaar, FaceID) |
| **Tenant System** | 3 | Tenant profiles, requirements, priorities |
| **Host System** | 4 | Host profiles, property listings, photos, preferences |
| **Matching Engine** | 3 | Swipes, matches, saved items |
| **Communication** | 4 | Conversations, messages, notifications, WhatsApp logs |
| **Payments** | 2 | Transactions, subscriptions |
| **Trust & Safety** | 3 | Ratings, reports, blocked users |
| **Analytics** | 4 | Activity logs, views tracking |
| **Admin & Services** | 5 | Admin controls, partner services, system settings |

---

## Entity Relationship Summary

### Core Relationships

```
USER (Central Entity)
├── has one → USER_VERIFICATION
├── has one → TENANT_PROFILE (if tenant)
│   └── has many → TENANT_REQUIREMENTS
│       └── has many → SWIPE_ACTIONS
│           └── creates → MATCHES
├── has one → HOST_PROFILE (if host)
│   └── has many → PROPERTY_LISTINGS
│       ├── has many → PROPERTY_PHOTOS
│       └── has many → SWIPE_ACTIONS
│           └── creates → MATCHES
├── has many → PAYMENTS
├── has many → SUBSCRIPTIONS
├── has many → MESSAGES
├── has many → NOTIFICATIONS
├── has many → RATINGS (given and received)
└── has many → REPORTS (filed and received)
```

### Key Relationships Explained

**1. User → Verification (1:1)**
- Every user has exactly one verification record
- Tracks 4 verification types: Phone, Email, Aadhaar, FaceID
- Computed field `is_fully_verified` ensures all checks pass

**2. User → Tenant Profile (1:1 optional)**
- Only exists if user_type includes 'tenant'
- Stores lifestyle preferences and occupation details
- Links to tenant_requirements (1:many)

**3. User → Host Profile (1:1 optional)**
- Only exists if user_type includes 'host'
- Stores host category and business details
- Links to property_listings (1:many)

**4. Tenant Requirements ← → Property Listings (many:many via swipe_actions)**
- Swipe actions create the connection
- Mutual likes create a match
- Matches enable communication

**5. Match → Conversation (1:1)**
- Each match has exactly one conversation
- Conversation contains multiple messages
- Messages can include visit scheduling

---

## Core Modules

### 1. USER MANAGEMENT MODULE

**Tables:**
- `users` - Base user account
- `tenant_profiles` - Extended tenant information
- `host_profiles` - Extended host information

**Key Features:**
- Dual role support (user can be both tenant and host)
- Profile completeness tracking
- Account status management
- Device token storage for push notifications

**Critical Fields:**
```sql
users.user_type: 'tenant' | 'host' | 'both'
users.account_status: 'active' | 'suspended' | 'deleted' | 'pending'
tenant_profiles.profile_completeness: 0-100 percentage
host_profiles.host_category: 'owner' | 'broker' | 'company' | ...
```

---

### 2. VERIFICATION MODULE

**Tables:**
- `user_verifications` - Verification status tracking
- `otp_logs` - OTP generation and validation history

**Verification Levels:**

| Level | Type | Method | Badge |
|-------|------|--------|-------|
| 1 | Phone | OTP via SMS | ✓ Phone Verified |
| 2 | Email | OTP via Email | ✓ Email Verified |
| 3 | Aadhaar | Government OTP | ✓ Aadhaar Verified |
| 4 | Face ID | Biometric Selfie | ✓ Face Verified |

**Verification Flow:**
1. User initiates verification
2. OTP generated and stored in `otp_logs`
3. User submits OTP
4. System validates and updates `user_verifications`
5. Badge displayed on profile

**Security Features:**
- OTP expiry (5-10 minutes)
- Attempt limiting (max 3-5 attempts)
- Aadhaar data encrypted/masked
- Face verification score threshold

---

### 3. TENANT SYSTEM MODULE

**Tables:**
- `tenant_profiles` - Personal info and lifestyle
- `tenant_requirements` - Property search postings
- `tenant_priorities` - Matching preference weights

**Tenant Requirement Posting:**

Required Fields:
- Budget range (min/max)
- Location preferences (JSONB array + geo point)
- Occupancy type
- Move-in date
- Gender preference
- Property type

Optional Fields:
- Lifestyle requirements (non-smoker, non-drinker, etc.)
- Furnishing preference
- Other preferences (free text)

**Priority System:**
Tenants rank 8 factors (1=highest priority):
1. Budget
2. Occupancy
3. Location
4. Possession date
5. Gender preference
6. Property type
7. Lifestyle compatibility
8. Furnishing

**Status Lifecycle:**
```
draft → active → [paused/expired/fulfilled] → deleted
```

---

### 4. HOST SYSTEM MODULE

**Tables:**
- `host_profiles` - Host identity and category
- `property_listings` - Rental property details (30+ fields)
- `property_photos` - Ordered photo sequence
- `host_preferences` - Desired tenant attributes

**Property Listing Structure:**

**Location Data:**
- Full address
- Geo coordinates (PostGIS GEOGRAPHY type)
- Locality/neighborhood
- City, state, pincode

**Property Details (30 mandatory fields):**
- Configuration (1BHK, 2BHK, etc.)
- Total area and rentable area
- Furnishing level
- Amenities (WiFi, AC, washing machine, etc.)
- Parking availability
- Bathroom type
- Water supply details
- Property age

**Distance Metrics (auto-calculated if possible):**
- Metro/train station
- Bus stop, airport
- Hospital, gym
- Grocery, mall, theater

**Financial Breakdown:**
- Monthly rent
- Deposit amount
- Brokerage fees
- One-time charges
- Recurring charges (maintenance, electricity, WiFi)

**Rules & Restrictions:**
- Pets allowed?
- Non-veg cooking allowed?
- Drinking/partying allowed?
- Guest policy

**Photo Sequence Enforcement:**
Mandatory order:
1. **Room** (primary - must be first)
2. Kitchen
3. Bathroom (WC)
4. Hall/Living room
5. Balcony
6. Building exterior
7. Street view

System enforces this order and prevents publishing without proper sequence.

---

### 5. MATCHING ENGINE MODULE

**Tables:**
- `swipe_actions` - Tinder-style like/dislike
- `matches` - Mutual interest connections
- `saved_items` - Bookmarked listings/requirements

**Swipe Action Flow:**

```
Tenant views Listing
    ↓
Right swipe (LIKE)
    ↓
System records in swipe_actions
    ↓
Host receives WhatsApp notification
    ↓
Host views Tenant requirement
    ↓
Host right swipes (LIKE)
    ↓
MUTUAL MATCH created
    ↓
Contact details revealed
    ↓
Chat enabled
```

**Compatibility Scoring:**

The system calculates a compatibility score (0-100) based on:

**For Tenant viewing Listing:**
- Budget match (30%)
- Location proximity (25%)
- Lifestyle compatibility (20%)
- Property type match (15%)
- Furnishing match (10%)

**For Host viewing Requirement:**
- Tenant occupation match (30%)
- Budget alignment (25%)
- Lifestyle preferences (25%)
- Possession date alignment (20%)

**Weighted by Priority Rankings:**
The tenant's priority settings adjust these weights. If location is priority #1, its weight increases.

**Match Status Lifecycle:**
```
active → visit_scheduled → deal_closed
    ↓
[tenant_unmatched / host_unmatched / both_unmatched / deal_failed]
```

---

### 6. COMMUNICATION MODULE

**Tables:**
- `conversations` - Chat threads between matches
- `messages` - Individual messages
- `notifications` - In-app alerts
- `whatsapp_notifications` - WhatsApp message log

**Notification Types:**

| Type | Trigger | Channels |
|------|---------|----------|
| `like_received` | Someone swipes right | App, WhatsApp |
| `match_made` | Mutual like | App, Email, WhatsApp |
| `message_received` | New chat message | App, Push |
| `visit_scheduled` | Visit booked | App, Email, SMS |
| `visit_reminder` | 24hrs before visit | App, WhatsApp |
| `listing_expiring` | 3 days before expiry | App, Email |
| `payment_reminder` | Subscription renewal | App, Email |

**WhatsApp Integration:**
- Instant notification on right-swipe
- Includes tenant summary (without contact details)
- Template-based messaging
- Delivery tracking
- Status updates (sent/delivered/read/failed)

**Message Types:**
- text
- image
- document
- system (auto-generated)
- visit_request
- visit_confirmation

---

### 7. PAYMENTS & SUBSCRIPTIONS MODULE

**Tables:**
- `payments` - Transaction records
- `subscriptions` - Recurring plans

**Pricing Structure:**

| Item | Price | Validity |
|------|-------|----------|
| Tenant Listing | ₹250 | 30 days |
| Host Listing | ₹499 | 30 days |
| Premium Listing | ₹999 | 45 days (top placement) |
| Tenant Subscription | ₹999/month | Monthly |
| Host Subscription | ₹1499/month | Monthly |

**Payment Gateway Integration:**
- Razorpay (primary)
- Paytm (secondary)
- Supports: UPI, Cards, Net Banking, Wallets

**Payment Flow:**
1. User initiates payment
2. Record created with status='pending'
3. Redirect to gateway
4. Gateway callback updates status
5. On success: activate listing/subscription
6. Generate invoice/receipt

**Subscription Benefits:**

**Tenant Premium:**
- Unlimited requirement postings
- Priority in host feeds
- Advanced filters
- Visit scheduling priority

**Host Premium:**
- Unlimited property listings
- Top placement in search results
- Verified badge
- Analytics dashboard
- Priority customer support

---

### 8. TRUST & SAFETY MODULE

**Tables:**
- `ratings` - 5-star reviews
- `reports` - User/content flagging
- `blocked_users` - User blocking

**Rating System:**

Overall rating + 3 sub-ratings:
- Communication (1-5 stars)
- Accuracy (listing vs reality)
- Responsiveness (reply speed)

**Average rating calculation:**
```sql
AVG(rating_value) across all ratings for a user
Stored in: host_profiles.avg_rating
```

**Report Types:**
- Fake profile
- Fake listing
- Inappropriate content
- Harassment
- Scam
- Spam
- Misleading information
- Safety concern

**Report Handling:**
1. User files report
2. Status: 'pending'
3. Assigned to moderator
4. Investigation: 'under_review'
5. Action taken or dismissed
6. Status: 'resolved' or 'action_taken'

**Possible Actions:**
- Warning to user
- Temporary suspension
- Permanent ban
- Content removal
- Account deletion

---

### 9. ANALYTICS MODULE

**Tables:**
- `user_activity_logs` - User actions tracking
- `listing_views` - Property listing views
- `requirement_views` - Tenant requirement views

**Tracked Activities:**
- Login/Logout
- Profile updates
- Listing creation/editing
- Search queries
- Filter usage
- Swipe actions
- Message sending
- Payment initiation

**Metrics Captured:**
- View duration
- Photos viewed
- IP address
- Device type
- App version
- User agent

**Analytics Use Cases:**
1. User engagement scoring
2. Listing performance metrics
3. Conversion funnel analysis
4. A/B testing data
5. Recommendation engine training

---

### 10. ADMIN & SERVICES MODULE

**Tables:**
- `admin_users` - Platform administrators
- `system_settings` - Configuration
- `partner_services` - Third-party services
- `service_requests` - Service bookings

**Admin Roles:**

| Role | Permissions |
|------|-------------|
| super_admin | Full system access |
| moderator | Content review, user suspension |
| support | User queries, basic support |
| finance | Payment reconciliation, refunds |

**Partner Services:**
- Packers & Movers
- Furniture Rental
- Cleaning Services
- Internet Installation
- Property Verification
- Legal Assistance
- Painting/Repairs

**Commission Model:**
- Service fee: 10-20% commission
- Tracked in `service_requests`
- Auto-calculated on completion

---

## Key Design Decisions

### 1. PostgreSQL with PostGIS

**Why:**
- Geospatial queries for location-based matching
- JSONB for flexible schema fields
- Strong ACID compliance
- Excellent performance with proper indexing

**PostGIS Usage:**
```sql
-- Store coordinates
coordinates GEOGRAPHY(POINT)

-- Find listings within 5km
SELECT * FROM property_listings
WHERE ST_DWithin(
    coordinates,
    ST_GeogFromText('POINT(72.8777 19.0760)'),
    5000
);
```

### 2. UUID Primary Keys

**Why:**
- Distributed system friendly
- No collision risk
- Obfuscates record count
- Better for public-facing APIs

### 3. JSONB for Dynamic Data

**Used in:**
- `preferred_localities` (tenant requirements)
- `permissions` (admin users)
- `metadata` (payments)
- `request_details` (service requests)

**Benefits:**
- Flexible schema
- Indexable with GIN indexes
- Query with JSON operators

### 4. Separate Verification Table

Instead of verification flags in `users` table, we use `user_verifications`:

**Benefits:**
- Cleaner separation of concerns
- Easier to audit verification history
- Can store verification metadata
- Computed `is_fully_verified` field

### 5. Photo Sequence Enforcement

`property_photos` table with `sequence_order`:
- Enforces mandatory photo order
- Prevents listing publishing without proper sequence
- First photo must be the rentable space

**Implementation:**
```sql
CHECK constraint: 
  sequence_order=1 AND photo_type='room'
  (for single room listings)
```

### 6. Dual Listing System

Both tenants and hosts can create postings:
- **Tenants**: Create requirements
- **Hosts**: Create property listings
- Both can swipe on each other
- Symmetrical matching

### 7. Match Privacy Model

Contact details revealed only after mutual match:
- Before match: Limited info visible
- After match: Full contact + chat enabled
- User can set: `contact_visibility` preference

### 8. Status-Based Lifecycle

Every entity has a status field:
- Draft → Active → Paused/Expired/Completed → Deleted
- Enables soft deletes
- Audit trail preservation
- Can reactivate archived items

---

## API Integration Points

### Authentication & Authorization

```
POST /api/v1/auth/signup
POST /api/v1/auth/login
POST /api/v1/auth/verify-otp
POST /api/v1/auth/verify-aadhaar
POST /api/v1/auth/verify-faceid
POST /api/v1/auth/logout
```

### User Profile

```
GET    /api/v1/users/me
PUT    /api/v1/users/me
GET    /api/v1/users/{user_id}
POST   /api/v1/users/me/tenant-profile
PUT    /api/v1/users/me/tenant-profile
POST   /api/v1/users/me/host-profile
PUT    /api/v1/users/me/host-profile
```

### Tenant Requirements

```
GET    /api/v1/requirements
POST   /api/v1/requirements
GET    /api/v1/requirements/{requirement_id}
PUT    /api/v1/requirements/{requirement_id}
DELETE /api/v1/requirements/{requirement_id}
GET    /api/v1/requirements/my
```

### Property Listings

```
GET    /api/v1/listings
POST   /api/v1/listings
GET    /api/v1/listings/{listing_id}
PUT    /api/v1/listings/{listing_id}
DELETE /api/v1/listings/{listing_id}
GET    /api/v1/listings/my
POST   /api/v1/listings/{listing_id}/photos
DELETE /api/v1/listings/{listing_id}/photos/{photo_id}
```

### Matching & Swiping

```
GET    /api/v1/feed/listings
GET    /api/v1/feed/requirements
POST   /api/v1/swipe
GET    /api/v1/matches
GET    /api/v1/matches/{match_id}
DELETE /api/v1/matches/{match_id}
```

### Communication

```
GET    /api/v1/conversations
GET    /api/v1/conversations/{conversation_id}
POST   /api/v1/conversations/{conversation_id}/messages
GET    /api/v1/notifications
PUT    /api/v1/notifications/{notification_id}/read
```

### Payments

```
POST   /api/v1/payments/initiate
POST   /api/v1/payments/callback
GET    /api/v1/payments/{payment_id}
GET    /api/v1/subscriptions
POST   /api/v1/subscriptions/purchase
```

### Trust & Safety

```
POST   /api/v1/ratings
POST   /api/v1/reports
POST   /api/v1/users/{user_id}/block
DELETE /api/v1/users/{user_id}/block
```

---

## Matching Algorithm Data Flow

### Step 1: User Browses Feed

**Query for Tenant:**
```sql
SELECT pl.*, 
       hp.host_category,
       u.full_name,
       v.is_fully_verified,
       COALESCE(pp.photo_count, 0) as photo_count,
       -- Calculate compatibility score
       calculate_compatibility_score(
           tr.tenant_priorities,
           pl.listing_attributes
       ) as compatibility_score
FROM property_listings pl
JOIN users u ON pl.host_id = u.user_id
JOIN host_profiles hp ON u.user_id = hp.user_id
JOIN user_verifications v ON u.user_id = v.user_id
LEFT JOIN (
    SELECT listing_id, COUNT(*) as photo_count
    FROM property_photos
    GROUP BY listing_id
) pp ON pl.listing_id = pp.listing_id
LEFT JOIN tenant_requirements tr ON tr.user_id = $current_user_id
WHERE pl.status = 'active'
  AND pl.rent_monthly BETWEEN tr.budget_min AND tr.budget_max
  AND ST_DWithin(
      pl.coordinates,
      tr.preferred_coordinates,
      10000  -- 10km radius
  )
  AND pl.listing_id NOT IN (
      SELECT swiped_listing_id 
      FROM swipe_actions 
      WHERE swiper_id = $current_user_id
  )
ORDER BY 
  pl.is_premium DESC,
  compatibility_score DESC,
  pl.created_at DESC
LIMIT 20;
```

### Step 2: Compatibility Scoring

**Pseudo-code:**
```python
def calculate_compatibility_score(tenant_req, property_listing):
    score = 0
    weights = get_tenant_priority_weights(tenant_req.user_id)
    
    # Budget match (0-30 points)
    if listing.rent <= tenant_req.budget_max:
        budget_diff = (tenant_req.budget_max - listing.rent) / tenant_req.budget_max
        score += budget_diff * 30 * weights['budget']
    
    # Location proximity (0-25 points)
    distance = calculate_distance(tenant_req.location, listing.location)
    if distance <= 5km:
        location_score = (5 - distance) / 5 * 25
        score += location_score * weights['location']
    
    # Lifestyle match (0-20 points)
    lifestyle_matches = count_lifestyle_matches(tenant_req, listing)
    score += (lifestyle_matches / total_lifestyle_factors) * 20 * weights['lifestyle']
    
    # Property type match (0-15 points)
    if tenant_req.property_type == listing.property_type:
        score += 15 * weights['property_type']
    
    # Furnishing match (0-10 points)
    if tenant_req.furnishing == listing.furnishing:
        score += 10 * weights['furnishing']
    
    # Verification bonus (+5 points)
    if listing.host.is_fully_verified and listing.photos_verified:
        score += 5
    
    return min(score, 100)  # Cap at 100
```

### Step 3: Swipe Action

**On Right Swipe:**
1. Insert into `swipe_actions`
2. Increment `likes_count` (via trigger)
3. Check for mutual match
4. If mutual:
   - Create record in `matches`
   - Create `conversation`
   - Send notifications (app + WhatsApp + email)
   - Reveal contact details

**SQL for Match Check:**
```sql
-- Check if host also swiped right on this tenant
SELECT sa.*
FROM swipe_actions sa
WHERE sa.swiper_id = $host_id
  AND sa.swiped_user_id = $tenant_id
  AND sa.action IN ('like', 'super_like')
  AND EXISTS (
      SELECT 1 FROM swipe_actions
      WHERE swiper_id = $tenant_id
        AND swiped_user_id = $host_id
        AND action IN ('like', 'super_like')
  );
```

### Step 4: Match Creation

**Transaction:**
```sql
BEGIN;

-- Create match
INSERT INTO matches (
    tenant_id,
    host_id,
    listing_id,
    requirement_id,
    compatibility_score,
    match_status
) VALUES (
    $tenant_id,
    $host_id,
    $listing_id,
    $requirement_id,
    $compatibility_score,
    'active'
) RETURNING match_id;

-- Create conversation
INSERT INTO conversations (
    match_id,
    tenant_id,
    host_id
) VALUES (
    $match_id,
    $tenant_id,
    $host_id
);

-- Send notifications
INSERT INTO notifications (
    user_id,
    notification_type,
    title,
    body,
    related_match_id,
    sent_via_app,
    sent_via_whatsapp
) VALUES
($tenant_id, 'match_made', 'It's a Match!', 
 'You and [host_name] matched! Start chatting now.', 
 $match_id, true, true),
($host_id, 'match_made', 'It's a Match!', 
 'You and [tenant_name] matched! Start chatting now.', 
 $match_id, true, true);

COMMIT;
```

---

## Performance Optimization

### 1. Indexing Strategy

**Spatial Indexes:**
```sql
CREATE INDEX idx_listings_location 
    ON property_listings USING GIST(coordinates);

CREATE INDEX idx_requirements_location 
    ON tenant_requirements USING GIST(preferred_coordinates);
```

**Composite Indexes:**
```sql
CREATE INDEX idx_listings_active_search 
    ON property_listings(status, rent_monthly, created_at DESC)
    WHERE status = 'active';

CREATE INDEX idx_requirements_active_search 
    ON tenant_requirements(status, budget_min, budget_max, created_at DESC)
    WHERE status = 'active';
```

**Text Search Indexes:**
```sql
CREATE INDEX idx_listings_fulltext 
    ON property_listings 
    USING GIN(to_tsvector('english', 
        title || ' ' || description || ' ' || locality));
```

### 2. Query Optimization

**Avoid N+1 Queries:**
- Use JOINs for related data
- Batch load related entities
- Use eager loading in ORMs

**Pagination:**
- Use OFFSET/LIMIT with caution
- Better: cursor-based pagination using `created_at` + `id`

```sql
-- Instead of OFFSET 1000 LIMIT 20
SELECT * FROM property_listings
WHERE created_at < $last_seen_timestamp
ORDER BY created_at DESC
LIMIT 20;
```

### 3. Caching Strategy

**Redis Cache:**
- User sessions (1 hour TTL)
- Verification OTPs (10 min TTL)
- Feed results (5 min TTL)
- User profiles (30 min TTL)
- Compatibility scores (15 min TTL)

**Cache Invalidation:**
- On profile update → clear user cache
- On swipe action → clear feed cache for both users
- On listing update → clear listing cache

### 4. Database Partitioning

**Partition Large Tables:**

```sql
-- Partition messages by created_at (monthly)
CREATE TABLE messages_2025_01 PARTITION OF messages
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE messages_2025_02 PARTITION OF messages
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

**Benefits:**
- Faster queries on recent data
- Easy archival of old data
- Better index performance

### 5. Read Replicas

**Architecture:**
```
Master DB (Write)
    ↓
Replica 1 (Read) - API queries
Replica 2 (Read) - Analytics
Replica 3 (Read) - Admin panel
```

**Query Routing:**
- Writes → Master
- User-facing reads → Replica 1
- Analytics queries → Replica 2
- Admin queries → Replica 3

### 6. Connection Pooling

**PgBouncer Configuration:**
```ini
[databases]
homigo = host=localhost dbname=homigo

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
reserve_pool_size = 5
```

---

## Implementation Checklist

### Phase 1: Foundation (Week 1-2)
- [ ] Setup PostgreSQL with PostGIS
- [ ] Create user management tables
- [ ] Implement authentication system
- [ ] Setup verification tables
- [ ] Create OTP system
- [ ] Implement basic user CRUD APIs

### Phase 2: Core Features (Week 3-4)
- [ ] Create tenant profile & requirement tables
- [ ] Create host profile & listing tables
- [ ] Implement photo upload system
- [ ] Create swipe action tables
- [ ] Implement matching logic
- [ ] Setup notification system

### Phase 3: Communication (Week 5-6)
- [ ] Create conversation & message tables
- [ ] Implement real-time chat (WebSockets)
- [ ] Setup WhatsApp integration
- [ ] Create email notification system
- [ ] Implement push notifications

### Phase 4: Payments (Week 7)
- [ ] Setup payment gateway integration
- [ ] Create payment tables
- [ ] Implement subscription system
- [ ] Create invoice generation
- [ ] Setup webhook handlers

### Phase 5: Safety & Analytics (Week 8)
- [ ] Create ratings & reviews system
- [ ] Implement report & moderation
- [ ] Setup analytics tracking
- [ ] Create admin dashboard
- [ ] Implement blocking system

### Phase 6: Optimization (Week 9-10)
- [ ] Add indexes
- [ ] Setup caching layer
- [ ] Implement search optimization
- [ ] Create database backups
- [ ] Performance testing
- [ ] Load testing

---

## Monitoring & Maintenance

### Database Metrics to Monitor

1. **Connection Pool:**
   - Active connections
   - Wait time for connection
   - Pool saturation

2. **Query Performance:**
   - Slow query log (>1s)
   - Most frequent queries
   - Query plan analysis

3. **Table Growth:**
   - Table sizes
   - Index sizes
   - Bloat percentage

4. **Replication Lag:**
   - Master-replica delay
   - Replication errors

### Regular Maintenance Tasks

**Daily:**
- Monitor error logs
- Check backup completion
- Review slow queries

**Weekly:**
- Vacuum analyze large tables
- Review and optimize new slow queries
- Check index usage

**Monthly:**
- Reindex heavily updated tables
- Archive old data
- Review and prune unused indexes
- Security audit

---

## Conclusion

This schema design provides a solid foundation for the Homigo platform with:

✅ **Scalability**: Designed for growth with partitioning, indexing, and caching
✅ **Security**: Multi-layer verification, encrypted data, audit trails
✅ **Performance**: Optimized queries, proper indexing, spatial search
✅ **Flexibility**: JSONB fields for extensibility, status-based lifecycles
✅ **Maintainability**: Clear relationships, comprehensive documentation
✅ **Business Logic**: Built-in matching algorithm, priority system, monetization

The schema supports all requirements from the business plan including:
- Tinder-style swipe matching
- Dual role support (tenant/host)
- Multi-layer verification
- Photo sequence enforcement
- WhatsApp notifications
- Payment & subscription management
- Partner services integration
- Trust & safety features
- Comprehensive analytics

**Next Steps:**
1. Review schema with development team
2. Set up development database
3. Create database migration scripts
4. Build seed data for testing
5. Implement API endpoints
6. Begin frontend integration
