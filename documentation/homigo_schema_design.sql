-- =====================================================
-- HOMIGO DATABASE SCHEMA DESIGN
-- Rental & Flatmate Marketplace with Tinder-Style Matching
-- =====================================================

-- =====================================================
-- CORE USER TABLES
-- =====================================================

-- Main Users table (base for both tenants and hosts)
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    date_of_birth DATE,
    age INT GENERATED ALWAYS AS (EXTRACT(YEAR FROM AGE(date_of_birth))) STORED,
    gender VARCHAR(20) CHECK (gender IN ('Male', 'Female', 'Other', 'Prefer not to say')),
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('tenant', 'host', 'both')),
    profile_photo_url TEXT,
    account_status VARCHAR(20) DEFAULT 'active' CHECK (account_status IN ('active', 'suspended', 'deleted', 'pending')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    device_token TEXT, -- For push notifications
    fcm_token TEXT -- Firebase Cloud Messaging token
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_user_type ON users(user_type);
CREATE INDEX idx_users_account_status ON users(account_status);

-- =====================================================
-- VERIFICATION TABLES
-- =====================================================

CREATE TABLE user_verifications (
    verification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Verification flags
    phone_verified BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    aadhaar_verified BOOLEAN DEFAULT FALSE,
    face_id_verified BOOLEAN DEFAULT FALSE,
    
    -- Verification timestamps
    phone_verified_at TIMESTAMP,
    email_verified_at TIMESTAMP,
    aadhaar_verified_at TIMESTAMP,
    face_id_verified_at TIMESTAMP,
    
    -- Aadhaar details (encrypted/hashed)
    aadhaar_last_4_digits VARCHAR(4),
    aadhaar_verification_reference VARCHAR(100),
    
    -- Face ID details
    face_id_reference VARCHAR(100),
    face_verification_score DECIMAL(5,2),
    
    -- Overall verification status
    is_fully_verified BOOLEAN GENERATED ALWAYS AS (
        phone_verified AND email_verified AND aadhaar_verified AND face_id_verified
    ) STORED,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_verifications_user_id ON user_verifications(user_id);
CREATE INDEX idx_verifications_status ON user_verifications(is_fully_verified);

-- OTP verification logs
CREATE TABLE otp_logs (
    otp_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    contact_method VARCHAR(20) CHECK (contact_method IN ('phone', 'email', 'aadhaar')),
    contact_value VARCHAR(255) NOT NULL,
    otp_code VARCHAR(10) NOT NULL,
    otp_hash VARCHAR(255) NOT NULL, -- Store hashed OTP for security
    purpose VARCHAR(50) NOT NULL, -- 'signup', 'login', 'verification', 'reset_password'
    is_verified BOOLEAN DEFAULT FALSE,
    attempts INT DEFAULT 0,
    expires_at TIMESTAMP NOT NULL,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_otp_user_id ON otp_logs(user_id);
CREATE INDEX idx_otp_contact ON otp_logs(contact_method, contact_value);

-- =====================================================
-- TENANT PROFILE & REQUIREMENTS
-- =====================================================

CREATE TABLE tenant_profiles (
    tenant_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Occupation details
    occupation_type VARCHAR(50) CHECK (occupation_type IN ('working_professional', 'student', 'self_employed', 'actor', 'actress', 'freelancer', 'other')),
    job_title VARCHAR(255),
    company_name VARCHAR(255),
    educational_institution VARCHAR(255),
    
    -- Lifestyle preferences
    smoking VARCHAR(10) CHECK (smoking IN ('yes', 'no', 'occasionally')),
    drinking VARCHAR(10) CHECK (drinking IN ('yes', 'no', 'occasionally')),
    food_preference VARCHAR(20) CHECK (food_preference IN ('veg', 'non_veg', 'both', 'vegan', 'eggetarian')),
    lifestyle_notes TEXT,
    
    -- Bio and additional info
    bio TEXT,
    hobbies TEXT,
    languages_spoken TEXT,
    
    -- Profile completeness
    profile_completeness INT DEFAULT 0, -- Percentage 0-100
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id)
);

CREATE INDEX idx_tenant_profile_user_id ON tenant_profiles(user_id);

-- Tenant requirement postings
CREATE TABLE tenant_requirements (
    requirement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Basic details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Budget
    budget_min DECIMAL(10,2) NOT NULL,
    budget_max DECIMAL(10,2) NOT NULL,
    
    -- Location preferences
    preferred_localities JSONB, -- Array of locality names
    preferred_coordinates GEOGRAPHY(POINT), -- For geo-based search
    
    -- Property requirements
    occupancy VARCHAR(20) CHECK (occupancy IN ('single', 'double', 'triple', 'any')),
    property_type VARCHAR(50) CHECK (property_type IN ('flat', 'pg', 'shared_room', 'whole_flat', '1rk', '1bhk', '2bhk', '3bhk', 'studio')),
    furnishing VARCHAR(20) CHECK (furnishing IN ('furnished', 'semi_furnished', 'non_furnished', 'any')),
    
    -- Move-in details
    possession_date DATE NOT NULL,
    lease_duration_months INT, -- Preferred lease duration
    
    -- Preferences
    gender_preference VARCHAR(20) CHECK (gender_preference IN ('male', 'female', 'any')),
    flatmate_occupation_preference TEXT, -- Comma separated: 'working_professional,student'
    
    -- Lifestyle requirements for flatmate
    want_non_smoker BOOLEAN DEFAULT FALSE,
    want_non_drinker BOOLEAN DEFAULT FALSE,
    want_vegetarian BOOLEAN DEFAULT FALSE,
    want_non_party BOOLEAN DEFAULT FALSE,
    other_preferences TEXT,
    
    -- Privacy and contact settings
    contact_visibility VARCHAR(50) DEFAULT 'verified_hosts_only' CHECK (
        contact_visibility IN ('verified_hosts_only', 'after_mutual_match', 'all_hosts')
    ),
    
    -- Status and validity
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('draft', 'active', 'paused', 'expired', 'fulfilled', 'deleted')),
    expires_at DATE NOT NULL,
    views_count INT DEFAULT 0,
    likes_count INT DEFAULT 0,
    
    -- Monetization
    is_premium BOOLEAN DEFAULT FALSE,
    premium_expires_at DATE,
    payment_amount DECIMAL(10,2) DEFAULT 250.00,
    payment_status VARCHAR(20) CHECK (payment_status IN ('pending', 'paid', 'refunded')),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tenant_req_user_id ON tenant_requirements(user_id);
CREATE INDEX idx_tenant_req_status ON tenant_requirements(status);
CREATE INDEX idx_tenant_req_budget ON tenant_requirements(budget_min, budget_max);
CREATE INDEX idx_tenant_req_location ON tenant_requirements USING GIST(preferred_coordinates);
CREATE INDEX idx_tenant_req_possession ON tenant_requirements(possession_date);
CREATE INDEX idx_tenant_req_premium ON tenant_requirements(is_premium, expires_at);

-- Tenant priority settings
CREATE TABLE tenant_priorities (
    priority_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Priority rankings (1-8, where 1 is highest)
    budget_priority INT,
    occupancy_priority INT,
    location_priority INT,
    possession_priority INT,
    gender_priority INT,
    property_type_priority INT,
    lifestyle_priority INT,
    furnishing_priority INT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id)
);

-- =====================================================
-- HOST PROFILE & PROPERTY LISTINGS
-- =====================================================

CREATE TABLE host_profiles (
    host_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Host category
    host_category VARCHAR(50) NOT NULL CHECK (host_category IN (
        'owner', 'broker', 'company', 'future_room_partner', 
        'flatmate', 'known_of_flatmate', 'known_of_owner'
    )),
    
    -- Business details (if company)
    company_name VARCHAR(255),
    company_registration_number VARCHAR(100),
    gst_number VARCHAR(20),
    
    -- Professional info
    bio TEXT,
    response_time_expectation VARCHAR(50), -- 'within_1_hour', 'within_24_hours', etc.
    preferred_tenant_types TEXT, -- Comma separated
    
    -- Ratings and performance
    avg_rating DECIMAL(3,2) DEFAULT 0.00,
    total_ratings INT DEFAULT 0,
    total_properties_listed INT DEFAULT 0,
    successful_matches INT DEFAULT 0,
    
    -- Subscription status
    is_premium BOOLEAN DEFAULT FALSE,
    premium_expires_at DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id)
);

CREATE INDEX idx_host_profile_user_id ON host_profiles(user_id);
CREATE INDEX idx_host_profile_category ON host_profiles(host_category);

-- Property listings
CREATE TABLE property_listings (
    listing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    host_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Basic property info
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Location details
    locality VARCHAR(255) NOT NULL,
    tower_building_name VARCHAR(255),
    full_address TEXT,
    coordinates GEOGRAPHY(POINT),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10),
    
    -- Property configuration
    property_type VARCHAR(50) CHECK (property_type IN ('apartment', 'house', 'pg', 'villa', 'independent_floor')),
    configuration VARCHAR(20) CHECK (configuration IN ('1rk', '1bhk', '2bhk', '3bhk', '4bhk', '5bhk', 'studio')),
    floor_number INT,
    total_floors INT,
    
    -- Area details
    total_area_sqft INT,
    rentable_area_type VARCHAR(50) CHECK (rentable_area_type IN ('single_room', 'double_room', 'triple_room', 'whole_flat')),
    
    -- Furnishing and amenities
    furnishing VARCHAR(20) CHECK (furnishing IN ('furnished', 'semi_furnished', 'non_furnished')),
    has_wifi BOOLEAN DEFAULT FALSE,
    has_fridge BOOLEAN DEFAULT FALSE,
    has_ac BOOLEAN DEFAULT FALSE,
    has_fans BOOLEAN DEFAULT TRUE,
    has_washing_machine BOOLEAN DEFAULT FALSE,
    has_tv BOOLEAN DEFAULT FALSE,
    has_gas_connection BOOLEAN DEFAULT FALSE,
    
    -- Parking
    parking_type VARCHAR(20) CHECK (parking_type IN ('car', 'bike', 'both', 'none')),
    
    -- Bathrooms
    wc_type VARCHAR(20) CHECK (wc_type IN ('separate', 'shared', 'attached')),
    total_bathrooms INT,
    
    -- Water supply
    water_supply_type VARCHAR(50),
    water_supply_hours VARCHAR(100),
    
    -- Property age
    property_age_years INT,
    
    -- Restrictions and rules
    pets_allowed BOOLEAN DEFAULT FALSE,
    non_veg_allowed BOOLEAN DEFAULT TRUE,
    drinking_allowed BOOLEAN DEFAULT TRUE,
    partying_allowed BOOLEAN DEFAULT TRUE,
    guests_allowed BOOLEAN DEFAULT TRUE,
    
    -- Suitable for
    suitable_for TEXT, -- 'bachelors,couples,married,family'
    open_for_gender VARCHAR(20) CHECK (open_for_gender IN ('male', 'female', 'any')),
    open_for_occupation TEXT, -- 'working_professionals,students,actors,actresses'
    
    -- Services
    cook_available BOOLEAN DEFAULT FALSE,
    maid_available BOOLEAN DEFAULT FALSE,
    
    -- Distance to amenities (in meters)
    distance_to_metro INT,
    distance_to_train INT,
    distance_to_bus_stop INT,
    distance_to_airport INT,
    distance_to_gym INT,
    distance_to_hospital INT,
    distance_to_grocery INT,
    distance_to_mall INT,
    distance_to_movie_theatre INT,
    
    -- Current occupants info
    current_flatmates_count INT DEFAULT 0,
    flatmates_info TEXT, -- Brief description or JSON
    
    -- Financial details
    rent_monthly DECIMAL(10,2) NOT NULL,
    deposit_amount DECIMAL(10,2) NOT NULL,
    brokerage_amount DECIMAL(10,2) DEFAULT 0,
    maintenance_monthly DECIMAL(10,2) DEFAULT 0,
    electricity_charges VARCHAR(100), -- 'included', 'actual', 'fixed_500'
    water_charges VARCHAR(100),
    wifi_charges DECIMAL(10,2) DEFAULT 0,
    other_charges_onetime DECIMAL(10,2) DEFAULT 0,
    other_charges_monthly DECIMAL(10,2) DEFAULT 0,
    charges_notes TEXT,
    
    -- Availability
    possession_date DATE NOT NULL,
    minimum_lease_months INT DEFAULT 11,
    
    -- Additional highlights
    other_highlights TEXT,
    
    -- Status and visibility
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'rented', 'paused', 'expired', 'deleted')),
    views_count INT DEFAULT 0,
    likes_count INT DEFAULT 0,
    contact_requests_count INT DEFAULT 0,
    
    -- Photo verification
    photos_verified BOOLEAN DEFAULT FALSE,
    photos_verified_at TIMESTAMP,
    photos_verified_by UUID REFERENCES users(user_id),
    
    -- Monetization
    is_premium BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    premium_expires_at DATE,
    payment_amount DECIMAL(10,2) DEFAULT 499.00,
    payment_status VARCHAR(20) CHECK (payment_status IN ('pending', 'paid', 'refunded')),
    
    -- Timestamps and validity
    expires_at DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP
);

CREATE INDEX idx_listing_host_id ON property_listings(host_id);
CREATE INDEX idx_listing_status ON property_listings(status);
CREATE INDEX idx_listing_location ON property_listings USING GIST(coordinates);
CREATE INDEX idx_listing_city ON property_listings(city);
CREATE INDEX idx_listing_rent ON property_listings(rent_monthly);
CREATE INDEX idx_listing_premium ON property_listings(is_premium, is_featured);
CREATE INDEX idx_listing_possession ON property_listings(possession_date);

-- Property photos
CREATE TABLE property_photos (
    photo_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL REFERENCES property_listings(listing_id) ON DELETE CASCADE,
    
    photo_url TEXT NOT NULL,
    photo_type VARCHAR(50) CHECK (photo_type IN (
        'room', 'kitchen', 'bathroom', 'hall', 'balcony', 
        'building_exterior', 'street_view', 'other'
    )),
    sequence_order INT NOT NULL, -- Enforces photo order
    is_primary BOOLEAN DEFAULT FALSE,
    
    -- Verification
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    
    caption TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_property_photos_listing ON property_photos(listing_id, sequence_order);

-- Property host preferences
CREATE TABLE host_preferences (
    preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    host_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Preferred tenant attributes (matching criteria)
    prefer_non_drinker BOOLEAN DEFAULT FALSE,
    prefer_non_smoker BOOLEAN DEFAULT FALSE,
    prefer_vegetarian BOOLEAN DEFAULT FALSE,
    prefer_working_professional BOOLEAN DEFAULT FALSE,
    prefer_student BOOLEAN DEFAULT FALSE,
    preferred_gender VARCHAR(20),
    preferred_age_min INT,
    preferred_age_max INT,
    other_preferences TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(host_id)
);

-- =====================================================
-- MATCHING & INTERACTIONS
-- =====================================================

-- Swipe actions (Tinder-style)
CREATE TABLE swipe_actions (
    swipe_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    swiper_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    swiper_type VARCHAR(10) CHECK (swiper_type IN ('tenant', 'host')),
    
    -- What they swiped on
    swiped_listing_id UUID REFERENCES property_listings(listing_id) ON DELETE CASCADE,
    swiped_requirement_id UUID REFERENCES tenant_requirements(requirement_id) ON DELETE CASCADE,
    swiped_user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Action taken
    action VARCHAR(20) NOT NULL CHECK (action IN ('like', 'dislike', 'super_like', 'skip')),
    
    -- Compatibility score at time of swipe
    compatibility_score DECIMAL(5,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure one swipe per combination
    UNIQUE(swiper_id, swiped_listing_id),
    UNIQUE(swiper_id, swiped_requirement_id),
    
    -- Check constraint: either listing or requirement, not both
    CHECK (
        (swiped_listing_id IS NOT NULL AND swiped_requirement_id IS NULL) OR
        (swiped_listing_id IS NULL AND swiped_requirement_id IS NOT NULL)
    )
);

CREATE INDEX idx_swipe_swiper ON swipe_actions(swiper_id);
CREATE INDEX idx_swipe_listing ON swipe_actions(swiped_listing_id);
CREATE INDEX idx_swipe_requirement ON swipe_actions(swiped_requirement_id);

-- Matches (mutual likes)
CREATE TABLE matches (
    match_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    tenant_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    host_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    requirement_id UUID REFERENCES tenant_requirements(requirement_id) ON DELETE SET NULL,
    listing_id UUID REFERENCES property_listings(listing_id) ON DELETE SET NULL,
    
    -- Match details
    compatibility_score DECIMAL(5,2),
    match_status VARCHAR(20) DEFAULT 'active' CHECK (match_status IN (
        'active', 'tenant_unmatched', 'host_unmatched', 'both_unmatched', 
        'visit_scheduled', 'deal_closed', 'deal_failed'
    )),
    
    -- Contact sharing
    contact_shared BOOLEAN DEFAULT FALSE,
    contact_shared_at TIMESTAMP,
    
    -- Chat enabled
    chat_enabled BOOLEAN DEFAULT TRUE,
    
    -- Visit scheduling
    visit_scheduled BOOLEAN DEFAULT FALSE,
    visit_date TIMESTAMP,
    visit_status VARCHAR(20) CHECK (visit_status IN ('scheduled', 'completed', 'cancelled', 'rescheduled')),
    
    -- Deal closure
    deal_closed BOOLEAN DEFAULT FALSE,
    deal_closed_at TIMESTAMP,
    deal_amount DECIMAL(10,2),
    
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unmatched_at TIMESTAMP,
    
    UNIQUE(tenant_id, host_id, listing_id)
);

CREATE INDEX idx_match_tenant ON matches(tenant_id);
CREATE INDEX idx_match_host ON matches(host_id);
CREATE INDEX idx_match_status ON matches(match_status);
CREATE INDEX idx_match_listing ON matches(listing_id);
CREATE INDEX idx_match_requirement ON matches(requirement_id);

-- Saved/Shortlisted items
CREATE TABLE saved_items (
    saved_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    saved_listing_id UUID REFERENCES property_listings(listing_id) ON DELETE CASCADE,
    saved_requirement_id UUID REFERENCES tenant_requirements(requirement_id) ON DELETE CASCADE,
    
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, saved_listing_id),
    UNIQUE(user_id, saved_requirement_id),
    
    CHECK (
        (saved_listing_id IS NOT NULL AND saved_requirement_id IS NULL) OR
        (saved_listing_id IS NULL AND saved_requirement_id IS NOT NULL)
    )
);

CREATE INDEX idx_saved_user ON saved_items(user_id);

-- =====================================================
-- MESSAGING & COMMUNICATION
-- =====================================================

CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
    
    tenant_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    host_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(match_id)
);

CREATE INDEX idx_conv_tenant ON conversations(tenant_id);
CREATE INDEX idx_conv_host ON conversations(host_id);

CREATE TABLE messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    message_text TEXT,
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN (
        'text', 'image', 'document', 'system', 'visit_request', 'visit_confirmation'
    )),
    
    -- For non-text messages
    attachment_url TEXT,
    attachment_type VARCHAR(50),
    
    -- Message status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_msg_conversation ON messages(conversation_id, sent_at DESC);
CREATE INDEX idx_msg_sender ON messages(sender_id);

-- =====================================================
-- NOTIFICATIONS
-- =====================================================

CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    notification_type VARCHAR(50) NOT NULL CHECK (notification_type IN (
        'like_received', 'match_made', 'message_received', 'visit_scheduled',
        'visit_reminder', 'listing_expiring', 'requirement_expiring',
        'payment_reminder', 'verification_pending', 'new_matching_listing',
        'new_matching_requirement', 'system_announcement'
    )),
    
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    
    -- Related entities
    related_user_id UUID REFERENCES users(user_id),
    related_listing_id UUID REFERENCES property_listings(listing_id),
    related_requirement_id UUID REFERENCES tenant_requirements(requirement_id),
    related_match_id UUID REFERENCES matches(match_id),
    
    -- Notification channels
    sent_via_app BOOLEAN DEFAULT TRUE,
    sent_via_email BOOLEAN DEFAULT FALSE,
    sent_via_whatsapp BOOLEAN DEFAULT FALSE,
    sent_via_sms BOOLEAN DEFAULT FALSE,
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    -- Action URL/Deep link
    action_url TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP
);

CREATE INDEX idx_notif_user ON notifications(user_id, created_at DESC);
CREATE INDEX idx_notif_type ON notifications(notification_type);
CREATE INDEX idx_notif_read ON notifications(is_read);

-- WhatsApp notification log
CREATE TABLE whatsapp_notifications (
    whatsapp_notif_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_id UUID REFERENCES notifications(notification_id),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    phone_number VARCHAR(20) NOT NULL,
    message_template VARCHAR(100),
    message_body TEXT NOT NULL,
    
    status VARCHAR(20) CHECK (status IN ('pending', 'sent', 'delivered', 'read', 'failed')),
    whatsapp_message_id VARCHAR(255),
    
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    failed_reason TEXT
);

CREATE INDEX idx_whatsapp_user ON whatsapp_notifications(user_id);
CREATE INDEX idx_whatsapp_status ON whatsapp_notifications(status);

-- =====================================================
-- PAYMENTS & SUBSCRIPTIONS
-- =====================================================

CREATE TABLE payments (
    payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- What the payment is for
    payment_for VARCHAR(50) CHECK (payment_for IN (
        'tenant_listing', 'host_listing', 'premium_listing', 
        'tenant_subscription', 'host_subscription', 'verification_badge',
        'featured_listing', 'boost'
    )),
    
    -- Related entity
    related_listing_id UUID REFERENCES property_listings(listing_id),
    related_requirement_id UUID REFERENCES tenant_requirements(requirement_id),
    
    -- Payment details
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    
    payment_method VARCHAR(50), -- 'upi', 'card', 'netbanking', 'wallet'
    payment_gateway VARCHAR(50), -- 'razorpay', 'paytm', 'stripe'
    gateway_transaction_id VARCHAR(255),
    gateway_order_id VARCHAR(255),
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'processing', 'completed', 'failed', 'refunded', 'cancelled'
    )),
    
    -- Timestamps
    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    refunded_at TIMESTAMP,
    
    -- Receipt
    receipt_url TEXT,
    invoice_number VARCHAR(100),
    
    -- Metadata
    metadata JSONB
);

CREATE INDEX idx_payment_user ON payments(user_id);
CREATE INDEX idx_payment_status ON payments(status);
CREATE INDEX idx_payment_gateway_txn ON payments(gateway_transaction_id);

CREATE TABLE subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    subscription_type VARCHAR(50) CHECK (subscription_type IN (
        'tenant_basic', 'tenant_premium', 'host_basic', 'host_premium'
    )),
    
    -- Duration
    duration_months INT NOT NULL,
    
    -- Pricing
    amount DECIMAL(10,2) NOT NULL,
    discount_applied DECIMAL(10,2) DEFAULT 0,
    final_amount DECIMAL(10,2) NOT NULL,
    
    -- Status and validity
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN (
        'active', 'expired', 'cancelled', 'paused'
    )),
    
    starts_at DATE NOT NULL,
    expires_at DATE NOT NULL,
    
    -- Auto-renewal
    auto_renew BOOLEAN DEFAULT FALSE,
    
    -- Payment reference
    payment_id UUID REFERENCES payments(payment_id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP
);

CREATE INDEX idx_subscription_user ON subscriptions(user_id);
CREATE INDEX idx_subscription_status ON subscriptions(status, expires_at);

-- =====================================================
-- RATINGS & REVIEWS
-- =====================================================

CREATE TABLE ratings (
    rating_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Who is rating whom
    rater_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    rated_user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Related match
    match_id UUID REFERENCES matches(match_id) ON DELETE SET NULL,
    listing_id UUID REFERENCES property_listings(listing_id) ON DELETE SET NULL,
    
    -- Rating
    rating_value DECIMAL(2,1) CHECK (rating_value >= 1.0 AND rating_value <= 5.0),
    
    -- Review
    review_title VARCHAR(255),
    review_text TEXT,
    
    -- Specific ratings
    communication_rating DECIMAL(2,1),
    accuracy_rating DECIMAL(2,1), -- How accurate was listing/requirement
    responsiveness_rating DECIMAL(2,1),
    
    -- Status
    is_verified BOOLEAN DEFAULT FALSE, -- Verified that actual deal happened
    is_visible BOOLEAN DEFAULT TRUE,
    is_reported BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(rater_id, rated_user_id, match_id)
);

CREATE INDEX idx_rating_rated_user ON ratings(rated_user_id);
CREATE INDEX idx_rating_match ON ratings(match_id);

-- =====================================================
-- REPORTS & MODERATION
-- =====================================================

CREATE TABLE reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- What is being reported
    reported_user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    reported_listing_id UUID REFERENCES property_listings(listing_id) ON DELETE CASCADE,
    reported_requirement_id UUID REFERENCES tenant_requirements(requirement_id) ON DELETE CASCADE,
    reported_message_id UUID REFERENCES messages(message_id) ON DELETE CASCADE,
    
    -- Report details
    report_type VARCHAR(50) CHECK (report_type IN (
        'fake_profile', 'fake_listing', 'inappropriate_content', 'harassment',
        'scam', 'spam', 'misleading_info', 'safety_concern', 'other'
    )),
    
    report_reason TEXT NOT NULL,
    evidence_urls TEXT[], -- Array of screenshot URLs
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'under_review', 'resolved', 'dismissed', 'action_taken'
    )),
    
    -- Moderation
    assigned_to_moderator UUID REFERENCES users(user_id),
    moderator_notes TEXT,
    action_taken VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE INDEX idx_report_reporter ON reports(reporter_id);
CREATE INDEX idx_report_reported_user ON reports(reported_user_id);
CREATE INDEX idx_report_status ON reports(status);

CREATE TABLE blocked_users (
    block_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blocker_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    blocked_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(blocker_id, blocked_id)
);

CREATE INDEX idx_blocked_blocker ON blocked_users(blocker_id);
CREATE INDEX idx_blocked_blocked ON blocked_users(blocked_id);

-- =====================================================
-- ANALYTICS & TRACKING
-- =====================================================

CREATE TABLE user_activity_logs (
    activity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    
    activity_type VARCHAR(50) NOT NULL,
    activity_details JSONB,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    device_type VARCHAR(50),
    app_version VARCHAR(20),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_user ON user_activity_logs(user_id, created_at DESC);
CREATE INDEX idx_activity_type ON user_activity_logs(activity_type);

-- View tracking
CREATE TABLE listing_views (
    view_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL REFERENCES property_listings(listing_id) ON DELETE CASCADE,
    viewer_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    
    view_duration_seconds INT,
    photos_viewed INT,
    
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_listing_views ON listing_views(listing_id);

CREATE TABLE requirement_views (
    view_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES tenant_requirements(requirement_id) ON DELETE CASCADE,
    viewer_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    
    view_duration_seconds INT,
    
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_requirement_views ON requirement_views(requirement_id);

-- =====================================================
-- PARTNER SERVICES
-- =====================================================

CREATE TABLE partner_services (
    service_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    service_type VARCHAR(50) CHECK (service_type IN (
        'packers_movers', 'furniture_rental', 'cleaning', 'internet',
        'verification_service', 'legal_assistance', 'painting', 'plumbing'
    )),
    
    partner_name VARCHAR(255) NOT NULL,
    partner_contact VARCHAR(20),
    partner_email VARCHAR(255),
    
    service_description TEXT,
    pricing_model TEXT, -- 'per_service', 'subscription', 'commission'
    
    commission_percentage DECIMAL(5,2), -- Homigo's commission
    
    is_active BOOLEAN DEFAULT TRUE,
    cities_available TEXT[], -- Array of city names
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE service_requests (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES partner_services(service_id),
    
    match_id UUID REFERENCES matches(match_id),
    listing_id UUID REFERENCES property_listings(listing_id),
    
    request_details JSONB,
    
    status VARCHAR(20) DEFAULT 'requested' CHECK (status IN (
        'requested', 'assigned', 'in_progress', 'completed', 'cancelled'
    )),
    
    -- Pricing
    quoted_amount DECIMAL(10,2),
    final_amount DECIMAL(10,2),
    commission_earned DECIMAL(10,2),
    
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_service_request_user ON service_requests(user_id);
CREATE INDEX idx_service_request_service ON service_requests(service_id);

-- =====================================================
-- ADMIN & SYSTEM TABLES
-- =====================================================

CREATE TABLE admin_users (
    admin_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE UNIQUE,
    
    role VARCHAR(50) CHECK (role IN ('super_admin', 'moderator', 'support', 'finance')),
    permissions JSONB, -- Array of permission strings
    
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE system_settings (
    setting_key VARCHAR(100) PRIMARY KEY,
    setting_value TEXT NOT NULL,
    setting_type VARCHAR(50), -- 'string', 'number', 'boolean', 'json'
    description TEXT,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES admin_users(admin_id)
);

-- =====================================================
-- UTILITY VIEWS
-- =====================================================

-- View for fully verified users
CREATE VIEW verified_users AS
SELECT 
    u.*,
    v.is_fully_verified,
    v.phone_verified,
    v.email_verified,
    v.aadhaar_verified,
    v.face_id_verified
FROM users u
JOIN user_verifications v ON u.user_id = v.user_id
WHERE v.is_fully_verified = TRUE;

-- View for active listings with host info
CREATE VIEW active_listings_with_hosts AS
SELECT 
    pl.*,
    u.full_name as host_name,
    u.phone as host_phone,
    u.email as host_email,
    hp.host_category,
    hp.avg_rating as host_rating,
    v.is_fully_verified as host_verified
FROM property_listings pl
JOIN users u ON pl.host_id = u.user_id
JOIN host_profiles hp ON u.user_id = hp.user_id
JOIN user_verifications v ON u.user_id = v.user_id
WHERE pl.status = 'active';

-- View for active requirements with tenant info
CREATE VIEW active_requirements_with_tenants AS
SELECT 
    tr.*,
    u.full_name as tenant_name,
    tp.occupation_type,
    tp.smoking,
    tp.drinking,
    tp.food_preference,
    v.is_fully_verified as tenant_verified
FROM tenant_requirements tr
JOIN users u ON tr.user_id = u.user_id
JOIN tenant_profiles tp ON u.user_id = tp.user_id
JOIN user_verifications v ON u.user_id = v.user_id
WHERE tr.status = 'active';

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tenant_profiles_updated_at BEFORE UPDATE ON tenant_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tenant_requirements_updated_at BEFORE UPDATE ON tenant_requirements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_host_profiles_updated_at BEFORE UPDATE ON host_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_property_listings_updated_at BEFORE UPDATE ON property_listings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Update views count
CREATE OR REPLACE FUNCTION increment_listing_views()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE property_listings 
    SET views_count = views_count + 1 
    WHERE listing_id = NEW.listing_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER increment_listing_views_trigger AFTER INSERT ON listing_views
    FOR EACH ROW EXECUTE FUNCTION increment_listing_views();

-- Similar trigger for requirements
CREATE OR REPLACE FUNCTION increment_requirement_views()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE tenant_requirements 
    SET views_count = views_count + 1 
    WHERE requirement_id = NEW.requirement_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER increment_requirement_views_trigger AFTER INSERT ON requirement_views
    FOR EACH ROW EXECUTE FUNCTION increment_requirement_views();

-- Update likes count
CREATE OR REPLACE FUNCTION update_likes_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.action = 'like' OR NEW.action = 'super_like' THEN
        IF NEW.swiped_listing_id IS NOT NULL THEN
            UPDATE property_listings 
            SET likes_count = likes_count + 1 
            WHERE listing_id = NEW.swiped_listing_id;
        END IF;
        
        IF NEW.swiped_requirement_id IS NOT NULL THEN
            UPDATE tenant_requirements 
            SET likes_count = likes_count + 1 
            WHERE requirement_id = NEW.swiped_requirement_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_likes_count_trigger AFTER INSERT ON swipe_actions
    FOR EACH ROW EXECUTE FUNCTION update_likes_count();

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Text search indexes (for search functionality)
CREATE INDEX idx_listings_text_search ON property_listings 
    USING GIN(to_tsvector('english', title || ' ' || description || ' ' || locality));

CREATE INDEX idx_requirements_text_search ON tenant_requirements 
    USING GIN(to_tsvector('english', title || ' ' || description));

-- Composite indexes for common queries
CREATE INDEX idx_listings_active_premium ON property_listings(status, is_premium, created_at DESC)
    WHERE status = 'active';

CREATE INDEX idx_requirements_active_premium ON tenant_requirements(status, is_premium, created_at DESC)
    WHERE status = 'active';

-- =====================================================
-- SAMPLE DATA INSERT (OPTIONAL - FOR TESTING)
-- =====================================================

-- This section would include sample INSERT statements for testing
-- Commented out for production use

/*
INSERT INTO users (full_name, email, phone, user_type, gender) VALUES
('John Doe', 'john@example.com', '9876543210', 'tenant', 'Male'),
('Jane Smith', 'jane@example.com', '9876543211', 'host', 'Female');
*/

-- =====================================================
-- NOTES & RECOMMENDATIONS
-- =====================================================

/*
1. SECURITY:
   - All passwords should be hashed using bcrypt or argon2
   - Aadhaar numbers should be encrypted at rest
   - PII data should have restricted access
   - Implement row-level security (RLS) for multi-tenancy if needed

2. SCALABILITY:
   - Consider partitioning large tables (messages, activity_logs) by date
   - Implement read replicas for analytics queries
   - Use connection pooling (PgBouncer)
   - Consider caching layer (Redis) for frequently accessed data

3. BACKUPS:
   - Automated daily backups with point-in-time recovery
   - Geo-redundant backup storage
   - Regular backup restoration testing

4. MONITORING:
   - Set up query performance monitoring
   - Monitor slow queries and optimize
   - Track table growth and plan for archival

5. COMPLIANCE:
   - GDPR compliance: implement data deletion endpoints
   - Data retention policies
   - Audit logs for sensitive operations
   - Privacy policy compliance for data collection

6. FUTURE ENHANCEMENTS:
   - Implement full-text search using PostgreSQL or ElasticSearch
   - Add geospatial clustering for location-based recommendations
   - Implement ML-based compatibility scoring
   - Add chat message encryption
   - Implement real-time notifications using WebSockets
*/
