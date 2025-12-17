# HOMIGO API DOCUMENTATION (CONTINUED)
**Part 2: Payments, Notifications, Ratings, Admin**

---

### 11. NOTIFICATIONS MODULE

#### 11.1 Get Notifications

```http
GET /notifications?page=1&limit=20&unread_only=false
```

**Query Parameters:**
- `unread_only`: boolean (default false)
- `type`: Filter by notification type
- `page`, `limit`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "notification_id": "uuid",
        "notification_type": "match_made",
        "title": "It's a Match! 🎉",
        "body": "You and Jane Smith matched! Start chatting now.",
        "is_read": false,
        "action_url": "/matches/uuid",
        "related_user": {
          "user_id": "uuid",
          "full_name": "Jane Smith",
          "profile_photo_url": "https://..."
        },
        "related_listing": {
          "listing_id": "uuid",
          "title": "Spacious 2BHK"
        },
        "created_at": "2024-01-15T10:30:00Z"
      },
      {
        "notification_id": "uuid2",
        "notification_type": "like_received",
        "title": "Someone liked your requirement!",
        "body": "A verified host is interested in your requirement",
        "is_read": true,
        "read_at": "2024-01-15T10:35:00Z",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "unread_count": 5,
    "pagination": { /* ... */ }
  }
}
```

---

#### 11.2 Mark Notification as Read

```http
PUT /notifications/{notification_id}/read
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

---

#### 11.3 Mark All as Read

```http
PUT /notifications/read-all
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "All notifications marked as read"
}
```

---

#### 11.4 Get Notification Settings

```http
GET /notifications/settings
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "app_notifications": true,
    "email_notifications": true,
    "whatsapp_notifications": true,
    "sms_notifications": false,
    "notification_preferences": {
      "match_made": {
        "app": true,
        "email": true,
        "whatsapp": true
      },
      "message_received": {
        "app": true,
        "email": false,
        "whatsapp": false
      },
      "visit_scheduled": {
        "app": true,
        "email": true,
        "whatsapp": true
      },
      "listing_expiring": {
        "app": true,
        "email": true,
        "whatsapp": false
      }
    }
  }
}
```

---

#### 11.5 Update Notification Settings

```http
PUT /notifications/settings
```

**Request Body:**
```json
{
  "app_notifications": true,
  "email_notifications": true,
  "whatsapp_notifications": true,
  "notification_preferences": {
    "match_made": {
      "app": true,
      "email": true,
      "whatsapp": true
    }
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Settings updated successfully"
}
```

---

### 12. PAYMENTS MODULE

#### 12.1 Initiate Payment

```http
POST /payments/initiate
```

**Request Body:**
```json
{
  "payment_for": "tenant_listing",  // tenant_listing, host_listing, premium_listing, subscription
  "related_listing_id": "uuid",  // if for listing
  "related_requirement_id": "uuid",  // if for requirement
  "subscription_type": null,  // if for subscription
  "amount": 250.00,
  "currency": "INR",
  "payment_method": "upi"  // upi, card, netbanking, wallet
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Payment initiated",
  "data": {
    "payment_id": "uuid",
    "order_id": "order_123456",
    "amount": 250.00,
    "currency": "INR",
    "payment_gateway": "razorpay",
    "gateway_order_id": "rzp_order_abc123",
    "checkout_url": "https://razorpay.com/checkout/...",
    "razorpay_key": "rzp_test_key",
    "expires_at": "2024-01-15T11:00:00Z"
  }
}
```

---

#### 12.2 Verify Payment (Callback)

```http
POST /payments/callback
```

**Request Body (from Payment Gateway):**
```json
{
  "payment_id": "uuid",
  "gateway_transaction_id": "pay_abc123",
  "gateway_order_id": "rzp_order_abc123",
  "signature": "signature_here",  // For verification
  "status": "captured"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Payment verified successfully",
  "data": {
    "payment_id": "uuid",
    "status": "completed",
    "invoice_url": "https://api.homigo.com/invoices/inv_123.pdf",
    "listing_activated": true,  // or requirement activated
    "new_status": "active",
    "expires_at": "2024-02-15"
  }
}
```

---

#### 12.3 Get Payment History

```http
GET /payments/history?page=1&limit=20
```

**Query Parameters:**
- `status`: pending, completed, failed, refunded
- `payment_for`: Filter by type
- `page`, `limit`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "payments": [
      {
        "payment_id": "uuid",
        "payment_for": "tenant_listing",
        "amount": 250.00,
        "currency": "INR",
        "payment_method": "upi",
        "status": "completed",
        "related_item": {
          "type": "requirement",
          "id": "uuid",
          "title": "Looking for 1BHK"
        },
        "invoice_url": "https://...",
        "initiated_at": "2024-01-15T10:00:00Z",
        "completed_at": "2024-01-15T10:01:30Z"
      }
    ],
    "total_spent": 1248.00,
    "pagination": { /* ... */ }
  }
}
```

---

#### 12.4 Get Payment Details

```http
GET /payments/{payment_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "payment_id": "uuid",
    "payment_for": "tenant_listing",
    "amount": 250.00,
    "status": "completed",
    "gateway_transaction_id": "pay_abc123",
    "invoice_url": "https://...",
    "invoice_number": "INV-2024-001",
    "completed_at": "2024-01-15T10:01:30Z"
  }
}
```

---

#### 12.5 Download Invoice

```http
GET /payments/{payment_id}/invoice
```

**Response:** PDF file download

---

#### 12.6 Request Refund

```http
POST /payments/{payment_id}/refund
```

**Request Body:**
```json
{
  "reason": "Listing not activated within time",
  "description": "Payment was made but listing shows draft"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Refund request submitted",
  "data": {
    "refund_request_id": "uuid",
    "status": "pending",
    "estimated_time": "3-5 business days"
  }
}
```

---

### 13. SUBSCRIPTIONS MODULE

#### 13.1 Get Subscription Plans

```http
GET /subscriptions/plans
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "tenant_plans": [
      {
        "plan_id": "tenant_basic_monthly",
        "name": "Tenant Basic",
        "price": 999,
        "duration_months": 1,
        "features": [
          "Unlimited requirement postings",
          "Priority in host feeds",
          "Advanced filters",
          "Visit scheduling priority"
        ]
      },
      {
        "plan_id": "tenant_premium_quarterly",
        "name": "Tenant Premium",
        "price": 2499,
        "duration_months": 3,
        "discount_percent": 15,
        "features": [
          "All Basic features",
          "Dedicated support",
          "Property verification service",
          "Move-in assistance"
        ]
      }
    ],
    "host_plans": [
      {
        "plan_id": "host_basic_monthly",
        "name": "Host Basic",
        "price": 1499,
        "duration_months": 1,
        "features": [
          "Unlimited property listings",
          "Top placement in search",
          "Verified badge",
          "Analytics dashboard"
        ]
      }
    ]
  }
}
```

---

#### 13.2 Purchase Subscription

```http
POST /subscriptions/purchase
```

**Request Body:**
```json
{
  "plan_id": "tenant_basic_monthly",
  "auto_renew": true,
  "payment_method": "upi"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Subscription purchase initiated",
  "data": {
    "subscription_id": "uuid",
    "payment_id": "uuid",
    "checkout_url": "https://razorpay.com/checkout/...",
    "amount": 999
  }
}
```

---

#### 13.3 Get My Subscriptions

```http
GET /subscriptions/my
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "active_subscriptions": [
      {
        "subscription_id": "uuid",
        "subscription_type": "tenant_basic",
        "status": "active",
        "amount": 999,
        "starts_at": "2024-01-15",
        "expires_at": "2024-02-15",
        "auto_renew": true,
        "days_remaining": 30
      }
    ],
    "expired_subscriptions": []
  }
}
```

---

#### 13.4 Cancel Subscription

```http
POST /subscriptions/{subscription_id}/cancel
```

**Request Body:**
```json
{
  "reason": "No longer needed",
  "cancel_immediately": false  // If false, continues till expiry
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Subscription will be cancelled at the end of current period",
  "data": {
    "subscription_id": "uuid",
    "status": "cancelled",
    "active_until": "2024-02-15"
  }
}
```

---

#### 13.5 Renew Subscription

```http
POST /subscriptions/{subscription_id}/renew
```

**Request Body:**
```json
{
  "duration_months": 1,
  "auto_renew": true
}
```

**Response:** Similar to purchase

---

### 14. RATINGS & REVIEWS MODULE

#### 14.1 Rate User

```http
POST /ratings
```

**Request Body:**
```json
{
  "rated_user_id": "uuid",
  "match_id": "uuid",
  "listing_id": "uuid",  // If rating about a listing
  "rating_value": 4.5,  // 1.0 to 5.0
  "review_title": "Great landlord, smooth process",
  "review_text": "Jane was very professional and responsive. The property matched the listing perfectly.",
  "communication_rating": 5.0,
  "accuracy_rating": 4.5,
  "responsiveness_rating": 4.5
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Rating submitted successfully",
  "data": {
    "rating_id": "uuid",
    "rating_value": 4.5,
    "is_verified": false,  // Verified after deal completion
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

#### 14.2 Get User Ratings

```http
GET /users/{user_id}/ratings?page=1&limit=10
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "user_id": "uuid",
      "full_name": "Jane Smith",
      "avg_rating": 4.5,
      "total_ratings": 25
    },
    "ratings_breakdown": {
      "5_star": 15,
      "4_star": 8,
      "3_star": 2,
      "2_star": 0,
      "1_star": 0
    },
    "average_scores": {
      "communication": 4.7,
      "accuracy": 4.5,
      "responsiveness": 4.6
    },
    "reviews": [
      {
        "rating_id": "uuid",
        "rater": {
          "user_id": "uuid",
          "full_name": "John Doe",
          "profile_photo_url": "https://..."
        },
        "rating_value": 5.0,
        "review_title": "Excellent experience",
        "review_text": "Very professional...",
        "is_verified": true,
        "created_at": "2024-01-10T10:00:00Z"
      }
    ],
    "pagination": { /* ... */ }
  }
}
```

---

#### 14.3 Update Rating

```http
PUT /ratings/{rating_id}
```

**Request Body:**
```json
{
  "rating_value": 5.0,
  "review_text": "Updated review text"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Rating updated successfully"
}
```

---

#### 14.4 Delete Rating

```http
DELETE /ratings/{rating_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Rating deleted successfully"
}
```

---

### 15. REPORTS & MODERATION MODULE

#### 15.1 Report User/Content

```http
POST /reports
```

**Request Body:**
```json
{
  "reported_user_id": "uuid",  // Who to report
  "reported_listing_id": null,  // Optional: if reporting a listing
  "reported_requirement_id": null,  // Optional
  "reported_message_id": null,  // Optional
  "report_type": "fake_profile",  // fake_profile, fake_listing, harassment, scam, spam, etc.
  "report_reason": "This person used fake photos and information",
  "evidence_urls": [
    "https://cdn.homigo.com/evidence/screenshot1.jpg",
    "https://cdn.homigo.com/evidence/screenshot2.jpg"
  ]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Report submitted successfully",
  "data": {
    "report_id": "uuid",
    "status": "pending",
    "reference_number": "RPT-2024-001",
    "message": "We'll review this report within 24 hours"
  }
}
```

---

#### 15.2 Get My Reports

```http
GET /reports/my?status=pending&page=1
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "reports": [
      {
        "report_id": "uuid",
        "report_type": "fake_profile",
        "reported_user": {
          "user_id": "uuid",
          "full_name": "Reported User"
        },
        "status": "under_review",
        "created_at": "2024-01-15T10:00:00Z"
      }
    ],
    "pagination": { /* ... */ }
  }
}
```

---

#### 15.3 Block User

```http
POST /users/{user_id}/block
```

**Request Body:**
```json
{
  "reason": "Inappropriate behavior"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User blocked successfully",
  "data": {
    "blocked_user_id": "uuid",
    "blocked_at": "2024-01-15T10:30:00Z"
  }
}
```

---

#### 15.4 Unblock User

```http
DELETE /users/{user_id}/block
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User unblocked successfully"
}
```

---

#### 15.5 Get Blocked Users

```http
GET /users/blocked
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "blocked_users": [
      {
        "block_id": "uuid",
        "blocked_user": {
          "user_id": "uuid",
          "full_name": "Blocked User"
        },
        "reason": "Inappropriate behavior",
        "blocked_at": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

---

### 16. PARTNER SERVICES MODULE

#### 16.1 Get Available Services

```http
GET /services?city=Mumbai&service_type=packers_movers
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "services": [
      {
        "service_id": "uuid",
        "service_type": "packers_movers",
        "partner_name": "ABC Packers & Movers",
        "service_description": "Professional packing and moving services",
        "pricing_model": "per_service",
        "estimated_cost": "Starting from ₹5,000",
        "rating": 4.5,
        "reviews_count": 120,
        "cities_available": ["Mumbai", "Pune", "Bangalore"]
      }
    ]
  }
}
```

---

#### 16.2 Request Service

```http
POST /services/request
```

**Request Body:**
```json
{
  "service_id": "uuid",
  "match_id": "uuid",  // Optional: if related to a match
  "listing_id": "uuid",  // Optional
  "service_details": {
    "move_from": "Bandra, Mumbai",
    "move_to": "Andheri, Mumbai",
    "move_date": "2024-02-01",
    "items": "1BHK furniture, 2 beds, sofa, etc.",
    "additional_notes": "Need packing materials"
  }
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Service request submitted",
  "data": {
    "request_id": "uuid",
    "status": "requested",
    "partner_will_contact": true,
    "estimated_response_time": "within 24 hours"
  }
}
```

---

#### 16.3 Get My Service Requests

```http
GET /services/requests/my
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "requests": [
      {
        "request_id": "uuid",
        "service": {
          "service_type": "packers_movers",
          "partner_name": "ABC Packers"
        },
        "status": "assigned",  // requested, assigned, in_progress, completed
        "quoted_amount": 8500,
        "requested_at": "2024-01-15",
        "scheduled_date": "2024-02-01"
      }
    ]
  }
}
```

---

### 17. ANALYTICS MODULE (User-Facing)

#### 17.1 Get My Stats

```http
GET /analytics/my-stats
```

**Response (200 OK) - Tenant:**
```json
{
  "success": true,
  "data": {
    "user_type": "tenant",
    "stats": {
      "total_requirements": 3,
      "active_requirements": 1,
      "profile_views": 125,
      "likes_received": 45,
      "matches_made": 12,
      "messages_sent": 67,
      "visits_scheduled": 3,
      "properties_viewed": 234
    },
    "recent_activity": {
      "swipes_today": 15,
      "messages_today": 5
    }
  }
}
```

**Response (200 OK) - Host:**
```json
{
  "success": true,
  "data": {
    "user_type": "host",
    "stats": {
      "total_listings": 5,
      "active_listings": 3,
      "total_views": 1250,
      "total_likes": 180,
      "contact_requests": 45,
      "matches_made": 25,
      "successful_rentals": 8,
      "avg_response_time": "2 hours"
    },
    "listing_performance": [
      {
        "listing_id": "uuid",
        "title": "2BHK in Bandra",
        "views": 450,
        "likes": 65,
        "match_rate": 14.4
      }
    ]
  }
}
```

---

#### 17.2 Get Listing Performance

```http
GET /analytics/listings/{listing_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "listing_id": "uuid",
    "title": "2BHK in Bandra",
    "performance": {
      "views": 450,
      "likes": 65,
      "contact_requests": 18,
      "matches": 5,
      "avg_view_duration": 45,  // seconds
      "photos_viewed": 3.2  // average
    },
    "demographics": {
      "viewer_age_groups": {
        "21-25": 25,
        "26-30": 40,
        "31-35": 20,
        "36-40": 15
      },
      "viewer_occupations": {
        "working_professional": 60,
        "student": 25,
        "self_employed": 15
      }
    },
    "time_series": [
      {
        "date": "2024-01-15",
        "views": 45,
        "likes": 6
      }
    ]
  }
}
```

---

### 18. SETTINGS MODULE

#### 18.1 Get Settings

```http
GET /settings
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "profile_visibility": "public",  // public, verified_only, matches_only
    "show_phone_to": "matches_only",  // all, verified, matches_only
    "show_email_to": "matches_only",
    "allow_messages_from": "all",  // all, verified, matches_only
    "notification_settings": { /* ... */ },
    "privacy": {
      "show_last_seen": true,
      "show_online_status": true,
      "read_receipts": true
    },
    "preferences": {
      "language": "en",
      "currency": "INR",
      "distance_unit": "km"
    }
  }
}
```

---

#### 18.2 Update Settings

```http
PUT /settings
```

**Request Body:**
```json
{
  "profile_visibility": "verified_only",
  "privacy": {
    "show_last_seen": false,
    "read_receipts": false
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Settings updated successfully"
}
```

---

#### 18.3 Delete Account

```http
DELETE /account
```

**Request Body:**
```json
{
  "reason": "No longer needed",
  "password": "user_password",  // For verification
  "confirmation": "DELETE"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Account deletion scheduled",
  "data": {
    "deletion_date": "2024-01-30",  // 15 days grace period
    "can_cancel_until": "2024-01-29"
  }
}
```

---

### 19. ADMIN APIs (Internal Use)

#### 19.1 Get Dashboard Stats

```http
GET /admin/dashboard
```

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "overview": {
      "total_users": 25000,
      "active_users": 15000,
      "total_listings": 5000,
      "active_listings": 3500,
      "total_matches": 8000,
      "total_revenue": 1250000
    },
    "today": {
      "new_users": 120,
      "new_listings": 45,
      "matches_made": 180,
      "revenue": 45000
    }
  }
}
```

---

#### 19.2 Review Reports

```http
GET /admin/reports?status=pending
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "reports": [
      {
        "report_id": "uuid",
        "reporter": { /* user info */ },
        "reported_user": { /* user info */ },
        "report_type": "fake_profile",
        "status": "pending",
        "evidence_urls": ["..."],
        "created_at": "2024-01-15"
      }
    ]
  }
}
```

---

#### 19.3 Take Action on Report

```http
POST /admin/reports/{report_id}/action
```

**Request Body:**
```json
{
  "action": "suspend_user",  // warn, suspend_user, ban_user, remove_content, dismiss
  "moderator_notes": "Profile photos are fake, verified through reverse image search",
  "suspend_duration_days": 7
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Action taken successfully"
}
```

---

### 20. WEBHOOKS

Homigo sends webhooks for important events to registered URLs.

#### Webhook Events

```
user.verified
match.created
payment.completed
payment.failed
subscription.renewed
subscription.cancelled
visit.scheduled
deal.closed
```

#### Webhook Payload Format

```json
{
  "event": "match.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "match_id": "uuid",
    "tenant_id": "uuid",
    "host_id": "uuid",
    "listing_id": "uuid",
    "compatibility_score": 87
  },
  "signature": "webhook_signature_for_verification"
}
```

---

## Common Request/Response Formats

### Success Response Format

```json
{
  "success": true,
  "message": "Operation successful",
  "data": { /* ... */ }
}
```

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

---

## Error Codes

| HTTP Status | Error Code | Description |
|-------------|-----------|-------------|
| 400 | VALIDATION_ERROR | Invalid input data |
| 401 | UNAUTHORIZED | Missing or invalid token |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource conflict (duplicate) |
| 422 | UNPROCESSABLE | Valid but unprocessable request |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |
| 503 | SERVICE_UNAVAILABLE | Service temporarily down |

---

## Rate Limiting

### Limits by Endpoint Type

| Endpoint Type | Limit |
|--------------|-------|
| Authentication | 5 requests/minute |
| Search/Feed | 100 requests/minute |
| CRUD Operations | 60 requests/minute |
| File Uploads | 10 requests/minute |
| Swipe Actions | 100 requests/minute |

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1642234567
```

### Rate Limit Error Response

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again in 60 seconds.",
    "retry_after": 60
  }
}
```

---

## Pagination

### Standard Pagination

```
GET /listings?page=1&limit=20
```

**Response:**
```json
{
  "data": { /* ... */ },
  "pagination": {
    "current_page": 1,
    "total_pages": 50,
    "total_items": 1000,
    "items_per_page": 20,
    "has_next": true,
    "has_previous": false
  }
}
```

### Cursor-based Pagination (for real-time data)

```
GET /messages?limit=50&before=message_uuid_123
```

---

## File Uploads

### Upload Constraints

- **Image files:** JPG, PNG, WebP (max 5MB each)
- **Documents:** PDF (max 10MB)
- **Profile photos:** Square aspect ratio preferred (min 400x400px)
- **Property photos:** Landscape preferred (min 1200x800px)

### Upload Response

```json
{
  "success": true,
  "data": {
    "file_id": "uuid",
    "file_url": "https://cdn.homigo.com/uploads/file_123.jpg",
    "file_type": "image/jpeg",
    "file_size": 2458624,
    "uploaded_at": "2024-01-15T10:30:00Z"
  }
}
```

---

## Security Best Practices

### API Key Management
- Never expose API keys in client code
- Rotate keys regularly
- Use environment variables

### Token Security
- Store JWT securely (secure httpOnly cookies or secure storage)
- Implement token refresh mechanism
- Set appropriate expiration times

### Data Validation
- Validate all inputs on client and server
- Sanitize user inputs
- Use parameterized queries

### HTTPS Only
- All API calls must use HTTPS
- Reject HTTP requests

---

This completes the comprehensive API documentation for Homigo!
