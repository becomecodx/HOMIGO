# HOMIGO API DOCUMENTATION
**Version 1.0 | RESTful API Design**

---

## Table of Contents
1. [API Overview](#api-overview)
2. [Authentication Strategy](#authentication-strategy)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Formats](#requestresponse-formats)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Webhooks](#webhooks)

---

## API Overview

### Base URLs

```
Production:  https://api.homigo.com/v1
Staging:     https://staging-api.homigo.com/v1
Development: http://localhost:3000/api/v1
```

### API Design Principles

- **RESTful**: Standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- **JSON**: All requests and responses in JSON format
- **Versioned**: `/v1/` in URL for version control
- **Stateless**: Each request contains all necessary information
- **Paginated**: List endpoints support pagination
- **Filtered**: Search and filter capabilities on list endpoints

### Common Headers

```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token>
X-App-Version: 1.0.0
X-Device-ID: <unique_device_id>
X-Platform: ios|android|web
```

---

## Authentication Strategy

### Recommended Approach: Hybrid (Firebase + Custom JWT)

**Why Hybrid?**
- Firebase handles phone verification (OTP) reliably
- Custom JWT for session management and role-based access
- Best of both worlds: Firebase UX + Custom control

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                    CLIENT APP                        │
└───────────────────┬─────────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────────────────┐
│              AUTHENTICATION FLOW                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. Phone OTP (Firebase)                            │
│     ↓                                                │
│  2. Verify Firebase Token                           │
│     ↓                                                │
│  3. Create/Get User in Homigo DB                    │
│     ↓                                                │
│  4. Issue Custom JWT Token                          │
│     ↓                                                │
│  5. Client stores JWT                               │
│     ↓                                                │
│  6. JWT used for all API calls                      │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Implementation Strategy

#### Option 1: Firebase + Custom JWT (RECOMMENDED)

**Pros:**
- Firebase handles complex OTP delivery
- Reliable phone authentication
- Good developer experience
- Custom JWT for fine-grained control
- Can add social login later (Google, Apple)

**Cons:**
- Additional dependency
- Firebase SDK size

**Use Cases:**
- Phone/Email OTP verification
- Initial authentication
- Password reset

#### Option 2: Fully Custom (Alternative)

**Pros:**
- Complete control
- No external dependencies
- Lower costs at scale

**Cons:**
- Must handle OTP delivery (Twilio, AWS SNS)
- More development effort
- Edge cases to handle

**Recommendation:** Start with Firebase + Custom JWT for faster launch, can migrate later if needed.

---

## API Endpoints

### 1. AUTHENTICATION MODULE

#### 1.1 Send OTP (Phone)

```http
POST /auth/send-otp
```

**Request Body:**
```json
{
  "phone": "+919876543210",
  "type": "signup"  // or "login", "verification"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "data": {
    "session_id": "sess_abc123",
    "expires_in": 600,  // seconds
    "retry_after": 60   // seconds before can resend
  }
}
```

---

#### 1.2 Verify OTP & Authenticate

```http
POST /auth/verify-otp
```

**Request Body:**
```json
{
  "phone": "+919876543210",
  "otp": "123456",
  "session_id": "sess_abc123",
  "device_id": "device_xyz",
  "fcm_token": "fcm_token_here"  // For push notifications
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Authentication successful",
  "data": {
    "user": {
      "user_id": "uuid-here",
      "phone": "+919876543210",
      "email": null,
      "full_name": null,
      "user_type": "tenant",
      "is_new_user": true,
      "profile_completed": false,
      "verification_status": {
        "phone_verified": true,
        "email_verified": false,
        "aadhaar_verified": false,
        "face_id_verified": false,
        "is_fully_verified": false
      }
    },
    "token": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "Bearer",
      "expires_in": 604800,  // 7 days in seconds
      "refresh_token": "refresh_token_here"
    }
  }
}
```

---

#### 1.3 Refresh Token

```http
POST /auth/refresh-token
```

**Request Body:**
```json
{
  "refresh_token": "refresh_token_here"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "new_access_token",
    "expires_in": 604800
  }
}
```

---

#### 1.4 Logout

```http
POST /auth/logout
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

#### 1.5 Send Email OTP

```http
POST /auth/send-email-otp
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "OTP sent to email",
  "data": {
    "session_id": "sess_email_123",
    "expires_in": 600
  }
}
```

---

#### 1.6 Verify Email OTP

```http
POST /auth/verify-email
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456",
  "session_id": "sess_email_123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Email verified successfully",
  "data": {
    "email_verified": true
  }
}
```

---

### 2. USER PROFILE MODULE

#### 2.1 Get Current User Profile

```http
GET /users/me
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+919876543210",
    "date_of_birth": "1995-05-15",
    "age": 28,
    "gender": "Male",
    "user_type": "tenant",
    "profile_photo_url": "https://cdn.homigo.com/photos/user_123.jpg",
    "account_status": "active",
    "created_at": "2024-01-15T10:30:00Z",
    "verification_status": {
      "phone_verified": true,
      "email_verified": true,
      "aadhaar_verified": true,
      "face_id_verified": true,
      "is_fully_verified": true
    },
    "tenant_profile": {
      "occupation_type": "working_professional",
      "job_title": "Software Engineer",
      "company_name": "Tech Corp",
      "smoking": "no",
      "drinking": "occasionally",
      "food_preference": "veg",
      "lifestyle_notes": "Quiet person, prefers peaceful environment",
      "profile_completeness": 85
    },
    "subscription": {
      "is_premium": true,
      "expires_at": "2024-12-31"
    }
  }
}
```

---

#### 2.2 Update User Profile

```http
PUT /users/me
```

**Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "date_of_birth": "1995-05-15",
  "gender": "Male"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "user_id": "uuid",
    "full_name": "John Doe",
    "email": "john@example.com"
    // ... other fields
  }
}
```

---

#### 2.3 Upload Profile Photo

```http
POST /users/me/photo
```

**Content-Type:** `multipart/form-data`

**Form Data:**
```
photo: <file>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Photo uploaded successfully",
  "data": {
    "profile_photo_url": "https://cdn.homigo.com/photos/user_123.jpg"
  }
}
```

---

#### 2.4 Get User by ID (Public Profile)

```http
GET /users/{user_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "full_name": "John Doe",
    "profile_photo_url": "https://cdn.homigo.com/photos/user_123.jpg",
    "user_type": "tenant",
    "verification_status": {
      "is_fully_verified": true
    },
    "ratings": {
      "avg_rating": 4.5,
      "total_ratings": 12
    },
    "created_at": "2024-01-15T10:30:00Z"
    // Limited info for privacy
  }
}
```

---

### 3. VERIFICATION MODULE

#### 3.1 Send Aadhaar OTP

```http
POST /verification/aadhaar/send-otp
```

**Request Body:**
```json
{
  "aadhaar_number": "123456789012"  // Encrypted on client side
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "OTP sent to registered mobile",
  "data": {
    "reference_id": "ref_abc123",
    "expires_in": 600
  }
}
```

---

#### 3.2 Verify Aadhaar OTP

```http
POST /verification/aadhaar/verify-otp
```

**Request Body:**
```json
{
  "reference_id": "ref_abc123",
  "otp": "123456"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Aadhaar verified successfully",
  "data": {
    "aadhaar_verified": true,
    "last_4_digits": "9012",
    "verified_at": "2024-01-15T10:30:00Z"
  }
}
```

---

#### 3.3 Upload Face ID

```http
POST /verification/face-id
```

**Content-Type:** `multipart/form-data`

**Form Data:**
```
selfie: <image_file>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Face verification in progress",
  "data": {
    "verification_id": "face_verify_123",
    "status": "processing"  // or "verified", "failed"
  }
}
```

---

#### 3.4 Get Face ID Status

```http
GET /verification/face-id/{verification_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "verification_id": "face_verify_123",
    "status": "verified",  // "processing", "verified", "failed"
    "score": 95.5,
    "verified_at": "2024-01-15T10:35:00Z"
  }
}
```

---

#### 3.5 Get Verification Status

```http
GET /verification/status
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "phone_verified": true,
    "email_verified": true,
    "aadhaar_verified": true,
    "face_id_verified": true,
    "is_fully_verified": true,
    "verification_badges": [
      "phone_verified",
      "email_verified",
      "aadhaar_verified",
      "face_id_verified"
    ]
  }
}
```

---

### 4. TENANT PROFILE MODULE

#### 4.1 Create/Update Tenant Profile

```http
PUT /tenant/profile
```

**Request Body:**
```json
{
  "occupation_type": "working_professional",
  "job_title": "Software Engineer",
  "company_name": "Tech Corp",
  "smoking": "no",
  "drinking": "occasionally",
  "food_preference": "veg",
  "lifestyle_notes": "Quiet person, prefers peaceful environment",
  "bio": "Looking for a peaceful place near my office",
  "hobbies": "Reading, Gaming, Cooking",
  "languages_spoken": "English, Hindi, Marathi"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Tenant profile updated",
  "data": {
    "tenant_profile_id": "uuid",
    "profile_completeness": 85,
    // ... all profile fields
  }
}
```

---

#### 4.2 Set Tenant Priorities

```http
PUT /tenant/priorities
```

**Request Body:**
```json
{
  "budget_priority": 1,      // 1 = highest
  "location_priority": 2,
  "occupancy_priority": 3,
  "possession_priority": 4,
  "gender_priority": 5,
  "property_type_priority": 6,
  "lifestyle_priority": 7,
  "furnishing_priority": 8
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Priorities updated successfully",
  "data": {
    "budget_priority": 1,
    "location_priority": 2
    // ... all priorities
  }
}
```

---

### 5. TENANT REQUIREMENTS MODULE

#### 5.1 Create Tenant Requirement

```http
POST /requirements
```

**Request Body:**
```json
{
  "title": "Looking for 1BHK in Bandra",
  "description": "Need a peaceful 1BHK flat near Bandra station",
  "budget_min": 15000,
  "budget_max": 25000,
  "preferred_localities": ["Bandra West", "Bandra East", "Khar"],
  "location": {
    "latitude": 19.0596,
    "longitude": 72.8295
  },
  "occupancy": "single",
  "property_type": "flat",
  "furnishing": "semi_furnished",
  "possession_date": "2024-05-01",
  "lease_duration_months": 11,
  "gender_preference": "any",
  "flatmate_occupation_preference": "working_professional,student",
  "want_non_smoker": true,
  "want_non_drinker": false,
  "want_vegetarian": true,
  "want_non_party": true,
  "other_preferences": "Pet friendly preferred",
  "contact_visibility": "verified_hosts_only"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Requirement created successfully",
  "data": {
    "requirement_id": "uuid",
    "user_id": "uuid",
    "title": "Looking for 1BHK in Bandra",
    "status": "draft",  // Need to pay to activate
    "expires_at": "2024-02-15",
    "payment_required": true,
    "payment_amount": 250.00,
    "payment_link": "https://api.homigo.com/v1/payments/initiate/req_123"
  }
}
```

---

#### 5.2 Get My Requirements

```http
GET /requirements/my?status=active&page=1&limit=10
```

**Query Parameters:**
- `status` (optional): active, draft, paused, expired, fulfilled
- `page` (optional): default 1
- `limit` (optional): default 10, max 50

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "requirements": [
      {
        "requirement_id": "uuid",
        "title": "Looking for 1BHK in Bandra",
        "budget_min": 15000,
        "budget_max": 25000,
        "status": "active",
        "views_count": 125,
        "likes_count": 15,
        "expires_at": "2024-02-15",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 3,
      "total_items": 25,
      "items_per_page": 10
    }
  }
}
```

---

#### 5.3 Get Requirement by ID

```http
GET /requirements/{requirement_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "requirement_id": "uuid",
    "user": {
      "user_id": "uuid",
      "full_name": "John Doe",
      "profile_photo_url": "https://...",
      "is_verified": true,
      "occupation_type": "working_professional"
    },
    "title": "Looking for 1BHK in Bandra",
    "description": "Need a peaceful 1BHK flat",
    "budget_min": 15000,
    "budget_max": 25000,
    "preferred_localities": ["Bandra West", "Bandra East"],
    "occupancy": "single",
    "property_type": "flat",
    "furnishing": "semi_furnished",
    "possession_date": "2024-05-01",
    "preferences": {
      "want_non_smoker": true,
      "want_non_drinker": false,
      "want_vegetarian": true
    },
    "status": "active",
    "views_count": 125,
    "likes_count": 15,
    "is_premium": false,
    "created_at": "2024-01-15T10:30:00Z",
    "expires_at": "2024-02-15"
  }
}
```

---

#### 5.4 Update Requirement

```http
PUT /requirements/{requirement_id}
```

**Request Body:** Same as create

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Requirement updated successfully",
  "data": {
    // Updated requirement object
  }
}
```

---

#### 5.5 Delete Requirement

```http
DELETE /requirements/{requirement_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Requirement deleted successfully"
}
```

---

#### 5.6 Renew/Extend Requirement

```http
POST /requirements/{requirement_id}/renew
```

**Request Body:**
```json
{
  "duration_days": 30,  // 30 or 45 for premium
  "upgrade_to_premium": false
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Renewal initiated",
  "data": {
    "payment_required": true,
    "amount": 250.00,
    "new_expires_at": "2024-03-15",
    "payment_link": "https://..."
  }
}
```

---

### 6. HOST PROFILE MODULE

#### 6.1 Create/Update Host Profile

```http
PUT /host/profile
```

**Request Body:**
```json
{
  "host_category": "owner",  // owner, broker, company, etc.
  "company_name": "XYZ Properties",  // if company
  "company_registration_number": "REG123456",
  "gst_number": "GST123456",
  "bio": "Professional property dealer with 5 years experience",
  "response_time_expectation": "within_24_hours",
  "preferred_tenant_types": "working_professionals,students"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Host profile updated",
  "data": {
    "host_profile_id": "uuid",
    "host_category": "owner",
    "avg_rating": 4.5,
    "total_ratings": 25,
    "total_properties_listed": 5,
    "successful_matches": 12
    // ... all fields
  }
}
```

---

#### 6.2 Set Host Preferences

```http
PUT /host/preferences
```

**Request Body:**
```json
{
  "prefer_non_drinker": true,
  "prefer_non_smoker": true,
  "prefer_vegetarian": false,
  "prefer_working_professional": true,
  "prefer_student": false,
  "preferred_gender": "any",
  "preferred_age_min": 21,
  "preferred_age_max": 40,
  "other_preferences": "Prefer long-term tenants"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Preferences updated successfully"
}
```

---

### 7. PROPERTY LISTINGS MODULE

#### 7.1 Create Property Listing

```http
POST /listings
```

**Request Body:**
```json
{
  "title": "Spacious 2BHK in Bandra West",
  "description": "Beautiful apartment with modern amenities",
  "locality": "Bandra West",
  "tower_building_name": "Sea View Towers",
  "full_address": "123, Linking Road, Bandra West, Mumbai",
  "location": {
    "latitude": 19.0596,
    "longitude": 72.8295
  },
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400050",
  "property_type": "apartment",
  "configuration": "2bhk",
  "floor_number": 5,
  "total_floors": 12,
  "total_area_sqft": 1000,
  "rentable_area_type": "whole_flat",
  "furnishing": "semi_furnished",
  "amenities": {
    "has_wifi": true,
    "has_fridge": true,
    "has_ac": true,
    "has_fans": true,
    "has_washing_machine": false,
    "has_tv": false,
    "has_gas_connection": true
  },
  "parking_type": "bike",
  "wc_type": "separate",
  "total_bathrooms": 2,
  "water_supply_type": "Municipal",
  "water_supply_hours": "24/7",
  "property_age_years": 5,
  "restrictions": {
    "pets_allowed": false,
    "non_veg_allowed": true,
    "drinking_allowed": true,
    "partying_allowed": false,
    "guests_allowed": true
  },
  "suitable_for": "bachelors,couples",
  "open_for_gender": "any",
  "open_for_occupation": "working_professionals,students",
  "services": {
    "cook_available": false,
    "maid_available": true
  },
  "distances": {
    "distance_to_metro": 500,
    "distance_to_train": 1000,
    "distance_to_bus_stop": 200,
    "distance_to_hospital": 2000,
    "distance_to_grocery": 300
  },
  "current_flatmates_count": 0,
  "flatmates_info": "",
  "financial": {
    "rent_monthly": 35000,
    "deposit_amount": 70000,
    "brokerage_amount": 35000,
    "maintenance_monthly": 2000,
    "electricity_charges": "actual",
    "water_charges": "included",
    "wifi_charges": 0,
    "other_charges_onetime": 0,
    "other_charges_monthly": 0,
    "charges_notes": "Electricity as per meter reading"
  },
  "possession_date": "2024-04-01",
  "minimum_lease_months": 11,
  "other_highlights": "Near beach, quiet neighborhood, good connectivity"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Listing created successfully",
  "data": {
    "listing_id": "uuid",
    "status": "draft",  // Need to upload photos
    "payment_required": true,
    "payment_amount": 499.00,
    "next_steps": [
      "Upload minimum 3 photos in sequence",
      "Complete payment to publish"
    ]
  }
}
```

---

#### 7.2 Upload Property Photos

```http
POST /listings/{listing_id}/photos
```

**Content-Type:** `multipart/form-data`

**Form Data:**
```
photo: <file>
photo_type: "room"  // room, kitchen, bathroom, hall, balcony, building_exterior, street_view
sequence_order: 1
caption: "Master bedroom with attached bathroom"
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Photo uploaded successfully",
  "data": {
    "photo_id": "uuid",
    "photo_url": "https://cdn.homigo.com/listings/photo_123.jpg",
    "photo_type": "room",
    "sequence_order": 1,
    "is_primary": true,
    "total_photos": 1,
    "min_required": 3,
    "can_publish": false
  }
}
```

---

#### 7.3 Reorder Photos

```http
PUT /listings/{listing_id}/photos/reorder
```

**Request Body:**
```json
{
  "photo_sequence": [
    {
      "photo_id": "uuid1",
      "sequence_order": 1,
      "photo_type": "room"
    },
    {
      "photo_id": "uuid2",
      "sequence_order": 2,
      "photo_type": "kitchen"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Photo sequence updated"
}
```

---

#### 7.4 Delete Photo

```http
DELETE /listings/{listing_id}/photos/{photo_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Photo deleted successfully"
}
```

---

#### 7.5 Publish Listing

```http
POST /listings/{listing_id}/publish
```

**Validation:**
- Minimum 3 photos uploaded
- Photos in correct sequence (room first)
- All mandatory fields filled
- Payment completed

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Listing published successfully",
  "data": {
    "listing_id": "uuid",
    "status": "active",
    "published_at": "2024-01-15T10:30:00Z",
    "expires_at": "2024-02-15",
    "views_count": 0,
    "likes_count": 0
  }
}
```

---

#### 7.6 Get My Listings

```http
GET /listings/my?status=active&page=1&limit=10
```

**Query Parameters:**
- `status` (optional): active, draft, paused, rented, expired
- `page`, `limit`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "listings": [
      {
        "listing_id": "uuid",
        "title": "Spacious 2BHK in Bandra West",
        "rent_monthly": 35000,
        "locality": "Bandra West",
        "configuration": "2bhk",
        "status": "active",
        "views_count": 250,
        "likes_count": 35,
        "contact_requests_count": 12,
        "photos": [
          {
            "photo_url": "https://...",
            "is_primary": true
          }
        ],
        "created_at": "2024-01-15",
        "expires_at": "2024-02-15"
      }
    ],
    "pagination": { /* ... */ }
  }
}
```

---

#### 7.7 Get Listing by ID

```http
GET /listings/{listing_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "listing_id": "uuid",
    "host": {
      "user_id": "uuid",
      "full_name": "Jane Smith",
      "profile_photo_url": "https://...",
      "is_verified": true,
      "host_category": "owner",
      "avg_rating": 4.5,
      "total_ratings": 25,
      "response_time": "within_24_hours"
    },
    "title": "Spacious 2BHK in Bandra West",
    "description": "Beautiful apartment...",
    "location": {
      "locality": "Bandra West",
      "city": "Mumbai",
      "latitude": 19.0596,
      "longitude": 72.8295
    },
    "property_details": {
      "property_type": "apartment",
      "configuration": "2bhk",
      "total_area_sqft": 1000,
      "furnishing": "semi_furnished"
    },
    "amenities": { /* ... */ },
    "restrictions": { /* ... */ },
    "financial": {
      "rent_monthly": 35000,
      "deposit_amount": 70000,
      "total_move_in_cost": 140000  // rent + deposit + brokerage
    },
    "photos": [
      {
        "photo_id": "uuid",
        "photo_url": "https://...",
        "photo_type": "room",
        "sequence_order": 1,
        "is_primary": true
      }
    ],
    "status": "active",
    "views_count": 250,
    "likes_count": 35,
    "is_premium": false,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

#### 7.8 Update Listing

```http
PUT /listings/{listing_id}
```

**Request Body:** Same as create (partial updates allowed)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Listing updated successfully"
}
```

---

#### 7.9 Pause/Resume Listing

```http
PATCH /listings/{listing_id}/status
```

**Request Body:**
```json
{
  "status": "paused"  // or "active" to resume
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Listing status updated",
  "data": {
    "listing_id": "uuid",
    "status": "paused"
  }
}
```

---

#### 7.10 Mark as Rented

```http
POST /listings/{listing_id}/mark-rented
```

**Request Body:**
```json
{
  "rented_to_match_id": "uuid",  // Optional: if from platform
  "rent_amount": 35000,
  "notes": "Rented to John Doe"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Listing marked as rented"
}
```

---

#### 7.11 Delete Listing

```http
DELETE /listings/{listing_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Listing deleted successfully"
}
```

---

### 8. FEED & DISCOVERY MODULE

#### 8.1 Get Listings Feed (For Tenants)

```http
GET /feed/listings
```

**Query Parameters:**
```
budget_min: 10000
budget_max: 30000
localities: Bandra,Khar,Santacruz  // comma-separated
occupancy: single
property_type: flat,1bhk,2bhk  // comma-separated
furnishing: furnished,semi_furnished
possession_from: 2024-04-01
gender_preference: any
page: 1
limit: 20
sort: compatibility  // compatibility, newest, price_low, price_high, distance
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "listings": [
      {
        "listing_id": "uuid",
        "title": "Spacious 2BHK",
        "rent_monthly": 35000,
        "locality": "Bandra West",
        "configuration": "2bhk",
        "furnishing": "semi_furnished",
        "primary_photo": "https://...",
        "host": {
          "full_name": "Jane Smith",
          "is_verified": true,
          "avg_rating": 4.5
        },
        "compatibility_score": 87,  // 0-100
        "distance_km": 2.5,
        "badges": ["verified_host", "premium", "photos_verified"],
        "highlights": [
          "Near metro",
          "Pet friendly",
          "Non-smoker preferred"
        ],
        "created_at": "2024-01-15",
        "is_liked": false,
        "is_saved": false
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 10,
      "total_items": 195,
      "has_more": true
    }
  }
}
```

---

#### 8.2 Get Requirements Feed (For Hosts)

```http
GET /feed/requirements
```

**Query Parameters:**
```
budget_min: 10000
budget_max: 30000
localities: Bandra,Khar
occupancy: single
property_type: flat
gender_preference: any
page: 1
limit: 20
sort: compatibility
```

**Response:** Similar to listings feed

---

#### 8.3 Search Listings

```http
GET /search/listings?q=2bhk bandra furnished&page=1
```

**Query Parameters:**
- `q`: Search query (text search on title, description, locality)
- Filters same as feed endpoint

**Response:** Similar to feed

---

### 9. SWIPE & MATCHING MODULE

#### 9.1 Swipe Action

```http
POST /swipe
```

**Request Body:**
```json
{
  "swiper_type": "tenant",  // or "host"
  "action": "like",  // like, dislike, super_like, skip
  "swiped_listing_id": "uuid",  // if tenant swiping listing
  "swiped_requirement_id": null,  // if host swiping requirement
  "swiped_user_id": "uuid"
}
```

**Response (200 OK) - No Match:**
```json
{
  "success": true,
  "message": "Action recorded",
  "data": {
    "swipe_id": "uuid",
    "action": "like",
    "is_match": false
  }
}
```

**Response (200 OK) - Match Created:**
```json
{
  "success": true,
  "message": "It's a Match! 🎉",
  "data": {
    "swipe_id": "uuid",
    "action": "like",
    "is_match": true,
    "match": {
      "match_id": "uuid",
      "matched_with": {
        "user_id": "uuid",
        "full_name": "Jane Smith",
        "profile_photo_url": "https://...",
        "user_type": "host"
      },
      "listing": {
        "listing_id": "uuid",
        "title": "Spacious 2BHK",
        "rent_monthly": 35000,
        "primary_photo": "https://..."
      },
      "compatibility_score": 87,
      "contact_shared": true,
      "contact_details": {
        "phone": "+919876543211",
        "email": "jane@example.com"
      },
      "conversation_id": "uuid",
      "matched_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

---

#### 9.2 Get My Matches

```http
GET /matches?status=active&page=1&limit=20
```

**Query Parameters:**
- `status`: active, visit_scheduled, deal_closed, unmatched
- `page`, `limit`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "matches": [
      {
        "match_id": "uuid",
        "matched_user": {
          "user_id": "uuid",
          "full_name": "Jane Smith",
          "profile_photo_url": "https://...",
          "user_type": "host",
          "is_verified": true
        },
        "listing": {
          "listing_id": "uuid",
          "title": "Spacious 2BHK",
          "rent_monthly": 35000,
          "primary_photo": "https://..."
        },
        "compatibility_score": 87,
        "match_status": "active",
        "contact_shared": true,
        "chat_enabled": true,
        "conversation_id": "uuid",
        "last_message": {
          "text": "Hi, interested in visiting",
          "sent_at": "2024-01-15T11:00:00Z",
          "is_read": true
        },
        "unread_count": 0,
        "matched_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": { /* ... */ }
  }
}
```

---

#### 9.3 Get Match Details

```http
GET /matches/{match_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "match_id": "uuid",
    "tenant": { /* full user details */ },
    "host": { /* full user details */ },
    "requirement": { /* requirement details */ },
    "listing": { /* listing details */ },
    "compatibility_score": 87,
    "match_status": "active",
    "contact_shared": true,
    "contact_details": {
      "phone": "+919876543211",
      "email": "jane@example.com"
    },
    "visit_scheduled": false,
    "deal_closed": false,
    "conversation_id": "uuid",
    "matched_at": "2024-01-15T10:30:00Z"
  }
}
```

---

#### 9.4 Unmatch

```http
DELETE /matches/{match_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Unmatched successfully"
}
```

---

#### 9.5 Save/Bookmark Item

```http
POST /saved
```

**Request Body:**
```json
{
  "saved_listing_id": "uuid",  // either listing or requirement
  "saved_requirement_id": null,
  "notes": "Good location, need to visit"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Saved successfully",
  "data": {
    "saved_id": "uuid"
  }
}
```

---

#### 9.6 Get Saved Items

```http
GET /saved?page=1&limit=20
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "saved_items": [
      {
        "saved_id": "uuid",
        "listing": { /* listing details */ },
        "notes": "Good location",
        "created_at": "2024-01-15"
      }
    ],
    "pagination": { /* ... */ }
  }
}
```

---

#### 9.7 Remove from Saved

```http
DELETE /saved/{saved_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Removed from saved"
}
```

---

### 10. MESSAGING MODULE

#### 10.1 Get Conversations

```http
GET /conversations?page=1&limit=20
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "conversation_id": "uuid",
        "match_id": "uuid",
        "other_user": {
          "user_id": "uuid",
          "full_name": "Jane Smith",
          "profile_photo_url": "https://...",
          "is_online": true,
          "last_seen": "2024-01-15T11:30:00Z"
        },
        "last_message": {
          "message_id": "uuid",
          "sender_id": "uuid",
          "message_text": "Hi, interested in visiting",
          "sent_at": "2024-01-15T11:00:00Z",
          "is_read": true
        },
        "unread_count": 2,
        "is_active": true,
        "last_message_at": "2024-01-15T11:00:00Z"
      }
    ],
    "pagination": { /* ... */ }
  }
}
```

---

#### 10.2 Get Conversation Messages

```http
GET /conversations/{conversation_id}/messages?page=1&limit=50
```

**Query Parameters:**
- `before_message_id`: For pagination (cursor-based)
- `limit`: default 50

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "conversation_id": "uuid",
    "messages": [
      {
        "message_id": "uuid",
        "sender_id": "uuid",
        "sender": {
          "full_name": "John Doe",
          "profile_photo_url": "https://..."
        },
        "message_text": "Hi, I'm interested in this property",
        "message_type": "text",
        "is_read": true,
        "read_at": "2024-01-15T11:05:00Z",
        "sent_at": "2024-01-15T11:00:00Z"
      },
      {
        "message_id": "uuid2",
        "sender_id": "uuid2",
        "message_text": "Great! When would you like to visit?",
        "message_type": "text",
        "is_read": false,
        "sent_at": "2024-01-15T11:02:00Z"
      }
    ],
    "has_more": true
  }
}
```

---

#### 10.3 Send Message

```http
POST /conversations/{conversation_id}/messages
```

**Request Body:**
```json
{
  "message_text": "Hi, I'm interested in this property",
  "message_type": "text"  // text, image, document, visit_request
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Message sent",
  "data": {
    "message_id": "uuid",
    "message_text": "Hi, I'm interested in this property",
    "sent_at": "2024-01-15T11:00:00Z"
  }
}
```

---

#### 10.4 Send Image/Document

```http
POST /conversations/{conversation_id}/messages
```

**Content-Type:** `multipart/form-data`

**Form Data:**
```
file: <file>
message_type: "image"  // or "document"
caption: "Here's my ID proof"
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "message_id": "uuid",
    "message_type": "image",
    "attachment_url": "https://cdn.homigo.com/messages/img_123.jpg",
    "sent_at": "2024-01-15T11:00:00Z"
  }
}
```

---

#### 10.5 Mark Messages as Read

```http
PUT /conversations/{conversation_id}/read
```

**Request Body:**
```json
{
  "last_read_message_id": "uuid"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Messages marked as read"
}
```

---

#### 10.6 Schedule Visit

```http
POST /matches/{match_id}/schedule-visit
```

**Request Body:**
```json
{
  "visit_date": "2024-01-20T15:00:00Z",
  "notes": "Looking forward to seeing the property"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Visit scheduled successfully",
  "data": {
    "match_id": "uuid",
    "visit_date": "2024-01-20T15:00:00Z",
    "visit_status": "scheduled",
    "confirmation_sent": true
  }
}
```

---

Continuing in next file due to length...
