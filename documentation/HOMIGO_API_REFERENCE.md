# HOMIGO API Documentation

> Complete API Reference for the HOMIGO Rental Platform

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000/api/v1`  
**Last Updated:** December 18, 2025

---

## Table of Contents

1. [Authentication](#1-authentication)
2. [Tenant APIs](#2-tenant-apis)
3. [Host APIs](#3-host-apis)
4. [Listings APIs](#4-listings-apis)
5. [Feed & Discovery APIs](#5-feed--discovery-apis)
6. [Matching APIs](#6-matching-apis)
7. [User Flows](#7-user-flows)
8. [Data Types & Enums](#8-data-types--enums)
9. [Error Handling](#9-error-handling)

---

## 1. Authentication

All authenticated endpoints require a Firebase Bearer Token in the header:
```
Authorization: Bearer <firebase_token>
```

### 1.1 Health Check

```
GET /auth/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "auth-api",
  "version": "1.0.0"
}
```

---

### 1.2 User Signup

```
POST /auth/signup
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| firebase_id | string | Yes | Firebase UID from Firebase Auth |
| full_name | string | Yes | User's full name |
| email | string | Yes | Valid email address |
| phone | string | Yes | Phone number (E.164 format: +919876543210) |
| user_type | enum | Yes | `"tenant"`, `"host"`, or `"both"` |
| date_of_birth | date | No | YYYY-MM-DD format |
| gender | string | No | `"male"`, `"female"`, `"other"` |

**Example Request:**
```json
{
  "firebase_id": "abc123xyz789",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+919876543210",
  "user_type": "both"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "user_id": "uuid-here",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+919876543210",
    "user_type": "both",
    "profile_photo_url": null,
    "account_status": "active",
    "created_at": "2025-12-18T12:00:00.000000",
    "last_login_at": "2025-12-18T12:00:00.000000"
  }
}
```

---

### 1.3 User Login

```
POST /auth/login
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| firebase_token | string | Yes | JWT token from Firebase Auth |

**Example Request:**
```json
{
  "firebase_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "user_id": "uuid-here",
    "full_name": "John Doe",
    "email": "john@example.com",
    "user_type": "both",
    "last_login_at": "2025-12-18T12:30:00.000000"
  },
  "access_token": null
}
```

---

### 1.4 Get Current User

```
GET /auth/me
```

**Headers:** `Authorization: Bearer <token>`

**Success Response (200 OK):**
```json
{
  "user_id": "uuid-here",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+919876543210",
  "user_type": "both",
  "profile_photo_url": null,
  "account_status": "active",
  "created_at": "2025-12-18T12:00:00.000000",
  "last_login_at": "2025-12-18T12:30:00.000000"
}
```

---

### 1.5 Update User Profile

```
PUT /auth/me
```

**Headers:** `Authorization: Bearer <token>`

**Request Body (all fields optional):**
| Field | Type | Description |
|-------|------|-------------|
| full_name | string | Updated name |
| phone | string | Updated phone |
| date_of_birth | date | YYYY-MM-DD |
| gender | string | `"male"`, `"female"`, `"other"` |
| profile_photo_url | string | URL to profile photo |

**Example Request:**
```json
{
  "full_name": "John D. Smith",
  "phone": "+919876543211"
}
```

---

## 2. Tenant APIs

> Requires user_type: `"tenant"` or `"both"`

### 2.1 Create/Update Tenant Profile

```
PUT /tenant/profile
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| occupation_type | enum | No | See [Enums](#occupation-types) | Type of occupation |
| job_title | string | No | max 255 chars | Current job title |
| company_name | string | No | max 255 chars | Current employer |
| educational_institution | string | No | max 255 chars | For students |
| smoking | enum | No | max 10 chars | `"yes"`, `"no"` |
| drinking | enum | No | max 10 chars | `"yes"`, `"no"` |
| food_preference | enum | No | See [Enums](#food-preferences) | Dietary preference |
| lifestyle_notes | text | No | - | Additional notes |
| bio | text | No | - | Self introduction |
| hobbies | text | No | - | Comma-separated hobbies |
| languages_spoken | text | No | - | Languages known |

**Example Request:**
```json
{
  "occupation_type": "working_professional",
  "job_title": "Software Engineer",
  "company_name": "Tech Corp",
  "smoking": "no",
  "drinking": "no",
  "food_preference": "veg",
  "bio": "Looking for a peaceful place near my office",
  "hobbies": "Reading, Gaming",
  "languages_spoken": "English, Hindi"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Tenant profile updated",
  "data": {
    "tenant_profile_id": "uuid-here",
    "user_id": "uuid-here",
    "occupation_type": "working_professional",
    "job_title": "Software Engineer",
    "company_name": "Tech Corp",
    "smoking": "no",
    "drinking": "no",
    "food_preference": "veg",
    "bio": "Looking for a peaceful place near my office",
    "hobbies": "Reading, Gaming",
    "languages_spoken": "English, Hindi",
    "profile_completeness": 100,
    "created_at": "2025-12-18T12:00:00.000000",
    "updated_at": "2025-12-18T12:00:00.000000"
  }
}
```

---

### 2.2 Get Tenant Profile

```
GET /tenant/profile
```

**Headers:** `Authorization: Bearer <token>`

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Profile retrieved",
  "data": {
    "tenant_profile_id": "uuid-here",
    "user_id": "uuid-here",
    "occupation_type": "working_professional",
    "job_title": "Software Engineer",
    "profile_completeness": 100,
    ...
  }
}
```

---

### 2.3 Set Tenant Priorities

```
PUT /tenant/priorities
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
| Field | Type | Description |
|-------|------|-------------|
| budget_priority | integer (1-8) | Priority rank for budget |
| location_priority | integer (1-8) | Priority rank for location |
| property_type_priority | integer (1-8) | Priority rank for property type |
| furnishing_priority | integer (1-8) | Priority rank for furnishing |
| occupancy_priority | integer (1-8) | Priority rank for occupancy |
| possession_priority | integer (1-8) | Priority rank for possession date |
| gender_priority | integer (1-8) | Priority rank for gender preference |
| lifestyle_priority | integer (1-8) | Priority rank for lifestyle match |

> Note: 1 = Highest Priority, 8 = Lowest Priority

**Example Request:**
```json
{
  "budget_priority": 1,
  "location_priority": 2,
  "property_type_priority": 3,
  "furnishing_priority": 4,
  "occupancy_priority": 5,
  "possession_priority": 6,
  "gender_priority": 7,
  "lifestyle_priority": 8
}
```

---

### 2.4 Get Tenant Priorities

```
GET /tenant/priorities
```

**Headers:** `Authorization: Bearer <token>`

---

### 2.5 Create Tenant Requirement

```
POST /tenant/requirements
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Requirement title (max 255 chars) |
| description | text | No | Detailed description |
| budget_min | number | Yes | Minimum budget in INR |
| budget_max | number | Yes | Maximum budget in INR |
| preferred_localities | array[string] | No | List of preferred areas |
| occupancy | enum | No | `"single"`, `"couple"`, `"family"`, `"sharing"` |
| property_type | enum | No | `"apartment"`, `"house"`, `"pg"`, `"villa"` |
| furnishing | enum | No | `"unfurnished"`, `"semi_furnished"`, `"fully_furnished"` |
| possession_date | date | Yes | YYYY-MM-DD |
| lease_duration_months | integer | No | Default: 11 |
| gender_preference | enum | No | `"male"`, `"female"`, `"any"` |
| want_non_smoker | boolean | No | Default: false |
| want_non_drinker | boolean | No | Default: false |
| want_vegetarian | boolean | No | Default: false |
| want_non_party | boolean | No | Default: false |

**Example Request:**
```json
{
  "title": "Looking for 2BHK in Bandra",
  "description": "Need a peaceful 2BHK near Bandra station",
  "budget_min": 25000,
  "budget_max": 40000,
  "preferred_localities": ["Bandra West", "Khar", "Santacruz"],
  "occupancy": "single",
  "property_type": "apartment",
  "furnishing": "semi_furnished",
  "possession_date": "2025-02-01",
  "lease_duration_months": 11,
  "gender_preference": "any",
  "want_non_smoker": true,
  "want_vegetarian": true
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Requirement created successfully",
  "data": {
    "requirement_id": "uuid-here",
    "user_id": "uuid-here",
    "title": "Looking for 2BHK in Bandra",
    "status": "draft",
    "expires_at": "2025-02-18",
    ...
  }
}
```

---

### 2.6 Get My Requirements

```
GET /tenant/requirements/my
```

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| status | string | Filter by status: `"draft"`, `"active"`, `"expired"` |
| page | integer | Page number (default: 1) |
| limit | integer | Items per page (default: 10, max: 50) |

---

### 2.7 Get Requirement by ID

```
GET /tenant/requirements/{requirement_id}
```

---

### 2.8 Update Requirement

```
PUT /tenant/requirements/{requirement_id}
```

---

### 2.9 Activate Requirement

```
POST /tenant/requirements/{requirement_id}/activate
```

> Simulates payment completion. In production, called after payment webhook.

**Success Response:**
```json
{
  "success": true,
  "message": "Requirement activated successfully",
  "data": {
    "requirement_id": "uuid-here",
    "status": "active",
    "payment_status": "paid"
  }
}
```

---

### 2.10 Delete Requirement

```
DELETE /tenant/requirements/{requirement_id}
```

---

## 3. Host APIs

> Requires user_type: `"host"` or `"both"`

### 3.1 Create/Update Host Profile

```
PUT /host/profile
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| host_category | enum | No | See [Host Categories](#host-categories) |
| company_name | string | No | For company hosts |
| company_registration_number | string | No | Registration number |
| gst_number | string | No | GST number |
| bio | text | No | Host bio/description |
| response_time_expectation | enum | No | `"within_1_hour"`, `"within_24_hours"`, `"within_48_hours"` |
| preferred_tenant_types | string | No | Comma-separated: `"working_professionals,students"` |

**Example Request:**
```json
{
  "host_category": "owner",
  "bio": "Professional property owner with 5 years experience",
  "response_time_expectation": "within_24_hours",
  "preferred_tenant_types": "working_professionals,students"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Host profile updated",
  "data": {
    "host_profile_id": "uuid-here",
    "user_id": "uuid-here",
    "host_category": "owner",
    "bio": "Professional property owner...",
    "avg_rating": 0.0,
    "total_ratings": 0,
    "total_properties_listed": 0,
    "successful_matches": 0,
    "is_premium": false,
    "created_at": "2025-12-18T12:00:00.000000"
  }
}
```

---

### 3.2 Get Host Profile

```
GET /host/profile
```

---

### 3.3 Set Host Preferences

```
PUT /host/preferences
```

---

### 3.4 Get Host Preferences

```
GET /host/preferences
```

---

## 4. Listings APIs

> Requires user_type: `"host"` or `"both"`

### 4.1 Create Property Listing

```
POST /listings
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Property title (max 255 chars) |
| description | text | No | Property description |
| locality | string | Yes | Area/locality name |
| city | string | Yes | City name |
| state | string | Yes | State name |
| pincode | string | No | 6-digit pincode |
| property_type | enum | No | `"apartment"`, `"house"`, `"pg"`, `"villa"`, `"independent_floor"` |
| configuration | string | No | `"1rk"`, `"1bhk"`, `"2bhk"`, `"3bhk"`, `"4bhk+"` |
| floor_number | integer | No | Floor number |
| total_floors | integer | No | Total floors in building |
| total_area_sqft | integer | No | Area in sqft |
| furnishing | enum | No | `"unfurnished"`, `"semi_furnished"`, `"fully_furnished"` |
| possession_date | date | Yes | YYYY-MM-DD |
| minimum_lease_months | integer | No | Default: 11 |
| financial | object | Yes | Financial details (see below) |
| amenities | object | No | Amenity flags (see below) |
| restrictions | object | No | Restriction flags (see below) |

**Financial Object:**
| Field | Type | Required |
|-------|------|----------|
| rent_monthly | number | Yes |
| deposit_amount | number | Yes |
| brokerage_amount | number | No |
| maintenance_monthly | number | No |

**Amenities Object (all boolean):**
| Field | Default |
|-------|---------|
| has_wifi | false |
| has_fridge | false |
| has_ac | false |
| has_washing_machine | false |
| has_tv | false |
| has_gas_connection | false |

**Restrictions Object (all boolean):**
| Field | Default |
|-------|---------|
| pets_allowed | false |
| non_veg_allowed | true |
| drinking_allowed | true |
| partying_allowed | true |
| guests_allowed | true |

**Example Request:**
```json
{
  "title": "Beautiful 3BHK Apartment in Andheri",
  "description": "Spacious apartment with modern amenities",
  "locality": "Andheri West",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400053",
  "property_type": "apartment",
  "configuration": "3bhk",
  "floor_number": 8,
  "total_floors": 15,
  "total_area_sqft": 1200,
  "furnishing": "fully_furnished",
  "possession_date": "2025-02-01",
  "minimum_lease_months": 11,
  "financial": {
    "rent_monthly": 45000,
    "deposit_amount": 90000,
    "brokerage_amount": 45000,
    "maintenance_monthly": 3000
  },
  "amenities": {
    "has_wifi": true,
    "has_ac": true,
    "has_fridge": true
  },
  "restrictions": {
    "pets_allowed": false,
    "non_veg_allowed": true
  }
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Listing created successfully",
  "data": {
    "listing_id": "uuid-here",
    "status": "draft",
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

### 4.2 Get My Listings

```
GET /listings/my
```

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| status | string | Filter: `"draft"`, `"active"`, `"paused"`, `"rented"`, `"expired"` |
| page | integer | Page number |
| limit | integer | Items per page (max: 50) |

---

### 4.3 Get Listing by ID

```
GET /listings/{listing_id}
```

---

### 4.4 Update Listing

```
PUT /listings/{listing_id}
```

---

### 4.5 Publish Listing

```
POST /listings/{listing_id}/publish
```

> Activates the listing after payment

---

### 4.6 Update Listing Status

```
PATCH /listings/{listing_id}/status
```

**Request Body:**
```json
{
  "status": "paused"  // or "active"
}
```

---

### 4.7 Mark as Rented

```
POST /listings/{listing_id}/mark-rented
```

**Request Body:**
```json
{
  "rent_amount": 45000,
  "notes": "Rented to verified tenant"
}
```

---

### 4.8 Delete Listing

```
DELETE /listings/{listing_id}
```

---

## 5. Feed & Discovery APIs

### 5.1 Get Listings Feed (For Tenants)

```
GET /feed/listings
```

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| budget_min | number | Minimum rent |
| budget_max | number | Maximum rent |
| city | string | City name |
| localities | string | Comma-separated localities |
| property_type | string | Comma-separated types |
| furnishing | string | Comma-separated furnishing types |
| gender_preference | string | `"male"`, `"female"`, `"any"` |
| sort | string | `"newest"`, `"price_low"`, `"price_high"` |
| page | integer | Page number |
| limit | integer | Items per page (max: 50) |

**Success Response:**
```json
{
  "success": true,
  "data": {
    "listings": [
      {
        "listing_id": "uuid",
        "title": "Beautiful 3BHK",
        "rent_monthly": 45000,
        "deposit_amount": 90000,
        "locality": "Andheri West",
        "city": "Mumbai",
        "configuration": "3bhk",
        "furnishing": "fully_furnished",
        "property_type": "apartment",
        "primary_photo": "https://...",
        "photos_count": 5,
        "host": {
          "user_id": "uuid",
          "full_name": "Host Name",
          "profile_photo_url": null
        },
        "is_premium": false,
        "is_featured": false,
        "views_count": 120,
        "likes_count": 25,
        "possession_date": "2025-02-01",
        "created_at": "2025-12-18T12:00:00"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_items": 50,
      "items_per_page": 10,
      "has_more": true
    }
  }
}
```

---

### 5.2 Get Requirements Feed (For Hosts)

```
GET /feed/requirements
```

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| budget_min | number | Minimum budget |
| budget_max | number | Maximum budget |
| occupancy | string | Occupancy type |
| property_type | string | Property type |
| gender_preference | string | Gender preference |
| sort | string | `"newest"`, `"budget_low"`, `"budget_high"` |
| page | integer | Page number |
| limit | integer | Items per page |

---

### 5.3 Search Listings

```
GET /feed/search/listings
```

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| q | string | Yes | Search query (min 2 chars) |
| page | integer | No | Page number |
| limit | integer | No | Items per page |

---

## 6. Matching APIs

### 6.1 Swipe Action

```
POST /matching/swipe
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| swiper_type | enum | Yes | `"tenant"` or `"host"` |
| action | enum | Yes | `"like"`, `"dislike"`, `"super_like"`, `"skip"` |
| swiped_listing_id | uuid | Conditional | UUID of the listing (if tenant swiping) |
| swiped_requirement_id | uuid | Conditional | UUID of the requirement (if host swiping) |
| swiped_user_id | uuid | Yes | UUID of the other user |

> Note: Provide either `swiped_listing_id` OR `swiped_requirement_id`, not both.

**Example Request (Tenant liking a listing):**
```json
{
  "swiper_type": "tenant",
  "action": "like",
  "swiped_listing_id": "listing-uuid-here",
  "swiped_user_id": "host-user-uuid-here"
}
```

**Success Response (Match Created):**
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
      "matched_at": "2025-12-18T12:30:00",
      "contact_shared": true
    }
  }
}
```

---

### 6.2 Get Matches

```
GET /matching/matches
```

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| status | string | `"active"`, `"deal_closed"`, `"unmatched"` |
| page | integer | Page number |
| limit | integer | Items per page |

**Success Response:**
```json
{
  "success": true,
  "data": {
    "matches": [
      {
        "match_id": "uuid",
        "my_role": "tenant",
        "matched_user": {
          "user_id": "uuid",
          "full_name": "Host Name",
          "profile_photo_url": null,
          "user_type": "host"
        },
        "listing": {
          "listing_id": "uuid",
          "title": "Beautiful 3BHK",
          "rent_monthly": 45000,
          "locality": "Andheri West"
        },
        "requirement": null,
        "compatibility_score": 85.5,
        "match_status": "active",
        "contact_shared": true,
        "chat_enabled": true,
        "visit_scheduled": false,
        "deal_closed": false,
        "matched_at": "2025-12-18T12:30:00"
      }
    ],
    "pagination": {...}
  }
}
```

---

### 6.3 Get Match Details

```
GET /matching/matches/{match_id}
```

---

### 6.4 Schedule Visit

```
POST /matching/matches/{match_id}/schedule-visit
```

**Request Body:**
```json
{
  "visit_date": "2025-12-25T14:00:00",
  "notes": "Please keep documents ready"
}
```

---

### 6.5 Close Deal

```
POST /matching/matches/{match_id}/close-deal
```

**Request Body:**
```json
{
  "deal_amount": 45000,
  "notes": "Deal finalized at listed rent"
}
```

---

### 6.6 Unmatch

```
POST /matching/matches/{match_id}/unmatch
```

---

### 6.7 Save Item

```
POST /matching/save
```

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| listing_id | uuid | UUID of listing to save |
| requirement_id | uuid | UUID of requirement to save |

> Provide either `listing_id` OR `requirement_id`

---

### 6.8 Get Saved Items

```
GET /matching/saved
```

---

### 6.9 Unsave Item

```
DELETE /matching/saved/{saved_id}
```

---

## 7. User Flows

### 7.1 Tenant Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                      TENANT USER FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. REGISTRATION                                                 │
│     POST /auth/signup (user_type: "tenant" or "both")           │
│                           ↓                                      │
│  2. CREATE TENANT PROFILE                                        │
│     PUT /tenant/profile                                          │
│     (occupation, lifestyle, bio, etc.)                          │
│                           ↓                                      │
│  3. SET SEARCH PRIORITIES                                        │
│     PUT /tenant/priorities                                       │
│     (budget, location, property type rankings)                  │
│                           ↓                                      │
│  4. CREATE REQUIREMENT POST (Optional)                           │
│     POST /tenant/requirements                                    │
│     (what you're looking for)                                   │
│                           ↓                                      │
│  5. ACTIVATE REQUIREMENT                                         │
│     POST /tenant/requirements/{id}/activate                      │
│     (simulates payment)                                         │
│                           ↓                                      │
│  6. BROWSE LISTINGS FEED                                         │
│     GET /feed/listings                                           │
│     (filter by budget, location, etc.)                          │
│                           ↓                                      │
│  7. SWIPE ON LISTINGS                                            │
│     POST /matching/swipe                                         │
│     (action: like/dislike/super_like)                           │
│                           ↓                                      │
│  8. VIEW MATCHES                                                 │
│     GET /matching/matches                                        │
│     (see mutual matches with hosts)                             │
│                           ↓                                      │
│  9. SCHEDULE VISIT                                               │
│     POST /matching/matches/{id}/schedule-visit                   │
│                           ↓                                      │
│ 10. CLOSE DEAL                                                   │
│     POST /matching/matches/{id}/close-deal                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Host Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                       HOST USER FLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. REGISTRATION                                                 │
│     POST /auth/signup (user_type: "host" or "both")             │
│                           ↓                                      │
│  2. CREATE HOST PROFILE                                          │
│     PUT /host/profile                                            │
│     (category, bio, response time)                              │
│                           ↓                                      │
│  3. SET HOST PREFERENCES                                         │
│     PUT /host/preferences                                        │
│     (preferred tenant types)                                    │
│                           ↓                                      │
│  4. CREATE PROPERTY LISTING                                      │
│     POST /listings                                               │
│     (title, location, rent, amenities)                          │
│                           ↓                                      │
│  5. UPLOAD PHOTOS (Future)                                       │
│     POST /listings/{id}/photos                                   │
│                           ↓                                      │
│  6. PUBLISH LISTING                                              │
│     POST /listings/{id}/publish                                  │
│     (activates after payment)                                   │
│                           ↓                                      │
│  7. BROWSE REQUIREMENTS FEED                                     │
│     GET /feed/requirements                                       │
│     (see what tenants are looking for)                          │
│                           ↓                                      │
│  8. SWIPE ON REQUIREMENTS                                        │
│     POST /matching/swipe                                         │
│     (accept/reject tenant requirements)                         │
│                           ↓                                      │
│  9. VIEW MATCHES                                                 │
│     GET /matching/matches                                        │
│     (see interested tenants)                                    │
│                           ↓                                      │
│ 10. SCHEDULE VISIT & CLOSE DEAL                                  │
│     POST /matching/matches/{id}/schedule-visit                   │
│     POST /matching/matches/{id}/close-deal                       │
│                           ↓                                      │
│ 11. MARK AS RENTED                                               │
│     POST /listings/{id}/mark-rented                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3 Matching Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      MATCHING FLOW                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TENANT                              HOST                        │
│     │                                  │                         │
│     ├──── Views Listing Feed ────────→│                         │
│     │                                  │                         │
│     │←──── Host Posts Listing ────────┤                         │
│     │                                  │                         │
│     ├─── LIKE Listing ─────────────── │ (Swipe recorded)        │
│     │                                  │                         │
│     │                                  ├─── Views Tenant Req     │
│     │                                  │                         │
│     │ (If Host also LIKES) ←──────────┤─── LIKE Requirement     │
│     │                                  │                         │
│     │         🎉 MATCH CREATED! 🎉     │                         │
│     │                                  │                         │
│     ├──── Contact Shared ─────────────┤                         │
│     │                                  │                         │
│     ├──── Chat Enabled ───────────────┤                         │
│     │                                  │                         │
│     ├──── Schedule Visit ─────────────┤                         │
│     │                                  │                         │
│     └──── Close Deal ─────────────────┘                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Data Types & Enums

### User Types
| Value | Description |
|-------|-------------|
| `tenant` | Can only browse listings, create requirements |
| `host` | Can only create listings, browse requirements |
| `both` | Can do both tenant and host actions |

### Occupation Types
| Value | Description |
|-------|-------------|
| `working_professional` | Employed person |
| `student` | Full-time student |
| `self_employed` | Self-employed/business owner |
| `freelancer` | Freelance worker |
| `actor` | Actor/actress |
| `actress` | Actress |
| `other` | Other occupation |

### Food Preferences
| Value | Description |
|-------|-------------|
| `veg` | Vegetarian |
| `non_veg` | Non-vegetarian |
| `both` | Eats both |
| `vegan` | Vegan |
| `eggetarian` | Vegetarian + eggs |

### Host Categories
| Value | Description |
|-------|-------------|
| `owner` | Property owner |
| `broker` | Real estate broker |
| `company` | Company/property management |
| `future_room_partner` | Looking for flatmate |
| `flatmate` | Current flatmate |
| `known_of_flatmate` | Posting for a friend |
| `known_of_owner` | Posting on behalf of owner |

### Property Types
| Value | Description |
|-------|-------------|
| `apartment` | Flat in a building |
| `house` | Independent house |
| `pg` | Paying guest |
| `villa` | Villa |
| `independent_floor` | Independent floor |

### Furnishing Types
| Value | Description |
|-------|-------------|
| `unfurnished` | No furniture |
| `semi_furnished` | Basic furniture |
| `fully_furnished` | Complete furniture |

### Listing Status
| Value | Description |
|-------|-------------|
| `draft` | Not yet published |
| `active` | Live and visible |
| `paused` | Temporarily hidden |
| `rented` | Successfully rented |
| `expired` | Listing expired |

### Match Status
| Value | Description |
|-------|-------------|
| `active` | Active match |
| `deal_closed` | Rental finalized |
| `unmatched` | Match ended |

---

## 9. Error Handling

### Standard Error Response

```json
{
  "success": false,
  "message": "Error description here",
  "error_code": "ERROR_CODE"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid/missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 422 | Validation Error |
| 500 | Internal Server Error |

### Common Error Codes

| Error Code | Description |
|------------|-------------|
| `INVALID_TOKEN` | Firebase token is invalid or expired |
| `USER_NOT_FOUND` | User doesn't exist in database |
| `UNAUTHORIZED` | Action not permitted for user |
| `PROFILE_NOT_FOUND` | Tenant/Host profile not created |
| `LISTING_NOT_FOUND` | Listing doesn't exist |
| `ALREADY_EXISTS` | Resource already saved/exists |
| `INTERNAL_ERROR` | Server-side error |

---

## Appendix: Sample API Calls

### Using cURL

```bash
# Signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"firebase_id": "abc123", "full_name": "John Doe", "email": "john@test.com", "phone": "+919876543210", "user_type": "both"}'

# Create Tenant Profile
curl -X PUT http://localhost:8000/api/v1/tenant/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"occupation_type": "working_professional", "job_title": "Engineer"}'

# Create Listing
curl -X POST http://localhost:8000/api/v1/listings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"title": "2BHK Apartment", "locality": "Bandra", "city": "Mumbai", "state": "Maharashtra", "financial": {"rent_monthly": 35000, "deposit_amount": 70000}, "possession_date": "2025-02-01"}'

# Get Listings Feed
curl -X GET "http://localhost:8000/api/v1/feed/listings?city=Mumbai&budget_max=50000" \
  -H "Authorization: Bearer <token>"
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your-firebase-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Create tenant profile
response = requests.put(
    f"{BASE_URL}/tenant/profile",
    headers=headers,
    json={
        "occupation_type": "working_professional",
        "job_title": "Software Engineer",
        "bio": "Looking for a nice place"
    }
)
print(response.json())
```

---

**© 2025 HOMIGO. All rights reserved.**
