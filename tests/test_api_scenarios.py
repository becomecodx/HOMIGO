"""
HOMIGO API Test Script - Comprehensive Scenario Testing

Tests all API endpoints in sequence with FRESH data:
1. Signup new user (type: 'both')
2. Create Tenant Profile (tenant_jay)
3. Create Host Profile (host_jay)
4. Post tenant requirement
5. Create property listing
6. Publish listing
7. Get listings feed
8. Get requirements feed
9. Swipe/Match actions
10. Mark as rented

Logs stored in: tests/api_test_logs_<timestamp>.txt
"""

import requests
import json
import logging
import base64
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
import sys
import os
import uuid

# ============ CONFIGURATION ============

BASE_URL = "http://localhost:8000/api/v1"

# Generate unique identifiers for this test run
TEST_RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
UNIQUE_ID = uuid.uuid4().hex[:8]

# ============ LOGGING SETUP ============

# Create logs directory if not exists
os.makedirs("tests", exist_ok=True)

# Setup logging to file and console
log_file = f"tests/api_test_logs_{TEST_RUN_ID}.txt"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ============ HELPER FUNCTIONS ============

def create_mock_firebase_token(firebase_id: str) -> str:
    """
    Create a mock Firebase-like token for testing.
    Since we're using simplified JWT decoding, we just need the payload.
    """
    header = base64.urlsafe_b64encode(json.dumps({
        "alg": "RS256",
        "typ": "JWT"
    }).encode()).decode().rstrip('=')
    
    payload = base64.urlsafe_b64encode(json.dumps({
        "user_id": firebase_id,
        "sub": firebase_id,
        "email": f"test_{firebase_id[:8]}@test.com",
        "iat": int(datetime.utcnow().timestamp()),
        "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())
    }).encode()).decode().rstrip('=')
    
    # Fake signature (our simplified decoder doesn't verify it)
    signature = base64.urlsafe_b64encode(b"fake_signature").decode().rstrip('=')
    
    return f"{header}.{payload}.{signature}"


def log_separator(title: str):
    """Log a visual separator."""
    sep = "=" * 60
    logger.info(sep)
    logger.info(f"  {title}")
    logger.info(sep)


def log_request(method: str, endpoint: str, data: Optional[Dict] = None):
    """Log request details."""
    logger.info(f"REQUEST: {method} {endpoint}")
    if data:
        # Truncate token for cleaner logs
        log_data = data.copy()
        if 'firebase_token' in log_data:
            log_data['firebase_token'] = log_data['firebase_token'][:50] + "..."
        logger.info(f"PAYLOAD: {json.dumps(log_data, indent=2, default=str)}")


def log_response(response: requests.Response):
    """Log response details."""
    try:
        body = response.json()
        logger.info(f"STATUS: {response.status_code}")
        # Truncate long responses
        body_str = json.dumps(body, indent=2, default=str)
        if len(body_str) > 2000:
            body_str = body_str[:2000] + "\n... (truncated)"
        logger.info(f"RESPONSE: {body_str}")
        return body
    except:
        logger.info(f"STATUS: {response.status_code}")
        logger.info(f"RESPONSE: {response.text[:500]}")
        return None


def api_call(method: str, endpoint: str, data: Optional[Dict] = None, 
             token: Optional[str] = None, expect_success: bool = True) -> Dict:
    """Make an API call and log it."""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    log_request(method, endpoint, data)
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        result = log_response(response)
        
        if expect_success and response.status_code >= 400:
            logger.warning(f"⚠️  Expected success but got {response.status_code}")
        elif not expect_success and response.status_code < 400:
            logger.warning(f"⚠️  Expected failure but got {response.status_code}")
        else:
            if response.status_code < 400:
                logger.info("✅ SUCCESS")
            else:
                logger.info("❌ FAILED (as expected)")
        
        return result or {}
    
    except requests.exceptions.ConnectionError:
        logger.error("❌ Connection Error - Is the server running?")
        return {"error": "Connection failed"}
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"error": str(e)}


# ============ TEST SCENARIOS ============

class APITester:
    """API Test Runner with fresh data for each run."""
    
    def __init__(self):
        # Generate unique firebase_id for this test run
        self.firebase_id = f"test_user_{UNIQUE_ID}"
        self.token = create_mock_firebase_token(self.firebase_id)
        
        # Will be populated during tests
        self.user_id = None
        self.tenant_profile_id = None
        self.host_profile_id = None
        self.requirement_id = None
        self.listing_id = None
        self.match_id = None
        self.saved_id = None
        
        # Test user data
        self.user_email = f"both_user_{UNIQUE_ID}@test.com"
        self.user_name = f"Test User {UNIQUE_ID}"
        
    def run_all_tests(self):
        """Run all test scenarios in sequence."""
        logger.info("\n" + "=" * 70)
        logger.info("  HOMIGO API COMPREHENSIVE TEST - FRESH DATA")
        logger.info(f"  Test Run ID: {TEST_RUN_ID}")
        logger.info(f"  Unique ID: {UNIQUE_ID}")
        logger.info(f"  Firebase ID: {self.firebase_id}")
        logger.info(f"  Log File: {log_file}")
        logger.info("=" * 70 + "\n")
        
        tests = [
            ("1. Health Check", self.test_health_check),
            ("2. Signup New User (type: both)", self.test_signup),
            ("3. Login User", self.test_login),
            ("4. Create Tenant Profile (tenant_jay)", self.test_create_tenant_profile),
            ("5. Create Host Profile (host_jay)", self.test_create_host_profile),
            ("6. Update User to 'both_up_jay'", self.test_update_user),
            ("7. Set Tenant Priorities", self.test_set_priorities),
            ("8. Post Tenant Requirement", self.test_post_requirement),
            ("9. Activate Requirement", self.test_activate_requirement),
            ("10. Create Property Listing", self.test_create_listing),
            ("11. Publish Listing", self.test_publish_listing),
            ("12. Get My Listings", self.test_get_my_listings),
            ("13. Get Listings Feed", self.test_listings_feed),
            ("14. Get Requirements Feed", self.test_requirements_feed),
            ("15. Search Listings", self.test_search_listings),
            ("16. Save a Listing", self.test_save_listing),
            ("17. Get Saved Items", self.test_get_saved_items),
            ("18. Swipe/Like Action", self.test_swipe_action),
            ("19. Get Matches", self.test_get_matches),
            ("20. Mark as Rented", self.test_mark_rented),
            ("21. Get Host Profile (host_jay)", self.test_get_host_profile),
            ("22. Get Tenant Profile (tenant_jay)", self.test_get_tenant_profile),
            ("23. Get User Profile", self.test_get_user_profile),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            log_separator(test_name)
            try:
                success = test_func()
                results.append((test_name, "✅ PASSED" if success else "❌ FAILED"))
            except Exception as e:
                logger.error(f"Exception: {e}")
                import traceback
                traceback.print_exc()
                results.append((test_name, f"💥 EXCEPTION: {e}"))
            logger.info("")
        
        # Summary
        log_separator("TEST SUMMARY")
        for test_name, status in results:
            logger.info(f"{status} - {test_name}")
        
        passed = sum(1 for _, s in results if "PASSED" in s)
        failed = sum(1 for _, s in results if "FAILED" in s or "EXCEPTION" in s)
        logger.info(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")
        logger.info(f"\n📄 Full logs saved to: {log_file}")
        
        return passed, failed
    
    # ============ INDIVIDUAL TESTS ============
    
    def test_health_check(self) -> bool:
        """Test API health check."""
        result = api_call("GET", "/auth/health")
        return result.get("status") == "healthy"
    
    def test_signup(self) -> bool:
        """Signup a new user with type 'both'."""
        result = api_call("POST", "/auth/signup", {
            "firebase_id": self.firebase_id,
            "full_name": self.user_name,
            "email": self.user_email,
            "phone": f"+91987654{UNIQUE_ID[:4]}",
            "user_type": "both"  # Important: enables both tenant and host features
        })
        
        if result.get("success"):
            self.user_id = result.get("user", {}).get("user_id")
            logger.info(f"Created user: {self.user_id}")
            return True
        return False
    
    def test_login(self) -> bool:
        """Test login with Firebase token."""
        result = api_call("POST", "/auth/login", 
                         {"firebase_token": self.token})
        
        if result.get("success"):
            user = result.get("user", {})
            self.user_id = user.get("user_id")
            logger.info(f"Logged in as: {user.get('full_name')} (type: {user.get('user_type')})")
            return True
        return False
    
    def test_create_tenant_profile(self) -> bool:
        """Create tenant profile (tenant_jay)."""
        result = api_call("PUT", "/tenant/profile", {
            "occupation_type": "working_professional",
            "job_title": "Software Engineer",
            "company_name": "Tech Corp",
            "smoking": "no",
            "drinking": "occasionally",
            "food_preference": "veg",
            "bio": "Looking for a peaceful place - tenant_jay",
            "hobbies": "Reading, Gaming, Music",
            "languages_spoken": "English, Hindi"
        }, token=self.token)
        
        if result.get("success"):
            self.tenant_profile_id = result.get("data", {}).get("tenant_profile_id")
            logger.info(f"Created tenant profile: {self.tenant_profile_id}")
            return True
        return False
    
    def test_create_host_profile(self) -> bool:
        """Create host profile (host_jay)."""
        result = api_call("PUT", "/host/profile", {
            "host_category": "owner",
            "bio": "Professional property owner - host_jay",
            "response_time_expectation": "within_24_hours",
            "preferred_tenant_types": "working_professionals,students"
        }, token=self.token)
        
        if result.get("success"):
            self.host_profile_id = result.get("data", {}).get("host_profile_id")
            logger.info(f"Created host profile: {self.host_profile_id}")
            return True
        return False
    
    def test_update_user(self) -> bool:
        """Update user name to 'both_up_jay'."""
        result = api_call("PUT", "/auth/me", {
            "full_name": f"both_up_jay_{UNIQUE_ID}"
        }, token=self.token)
        
        if result.get("success"):
            logger.info(f"Updated user name to: both_up_jay_{UNIQUE_ID}")
            return True
        return result.get("full_name") is not None
    
    def test_set_priorities(self) -> bool:
        """Set tenant search priorities."""
        result = api_call("PUT", "/tenant/priorities", {
            "budget_priority": 1,
            "location_priority": 2,
            "property_type_priority": 3,
            "furnishing_priority": 4,
            "occupancy_priority": 5,
            "possession_priority": 6,
            "gender_priority": 7,
            "lifestyle_priority": 8
        }, token=self.token)
        
        return result.get("success", False)
    
    def test_post_requirement(self) -> bool:
        """Post a tenant requirement."""
        possession_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        result = api_call("POST", "/tenant/requirements", {
            "title": f"Looking for 2BHK in Bandra - {UNIQUE_ID}",
            "description": "Need a peaceful 2BHK flat near Bandra station for working professional",
            "budget_min": 25000,
            "budget_max": 40000,
            "preferred_localities": ["Bandra West", "Khar", "Santacruz"],
            "occupancy": "single",
            "property_type": "apartment",
            "furnishing": "semi_furnished",
            "possession_date": possession_date,
            "lease_duration_months": 11,
            "gender_preference": "any",
            "want_non_smoker": True,
            "want_vegetarian": True
        }, token=self.token)
        
        if result.get("success"):
            self.requirement_id = result.get("data", {}).get("requirement_id")
            logger.info(f"Created requirement: {self.requirement_id}")
            return True
        return False
    
    def test_activate_requirement(self) -> bool:
        """Activate a requirement (simulate payment)."""
        if not self.requirement_id:
            logger.warning("No requirement_id to activate - skipping")
            return False
        
        result = api_call("POST", f"/tenant/requirements/{self.requirement_id}/activate",
                         token=self.token)
        return result.get("success", False)
    
    def test_create_listing(self) -> bool:
        """Create a property listing."""
        possession_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
        
        result = api_call("POST", "/listings", {
            "title": f"Beautiful 3BHK Apartment - {UNIQUE_ID}",
            "description": "Spacious 3BHK with modern amenities and great connectivity",
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
            "amenities": {
                "has_wifi": True,
                "has_ac": True,
                "has_fridge": True,
                "has_washing_machine": True,
                "has_tv": True
            },
            "restrictions": {
                "pets_allowed": False,
                "non_veg_allowed": True,
                "drinking_allowed": True
            },
            "financial": {
                "rent_monthly": 45000,
                "deposit_amount": 90000,
                "brokerage_amount": 45000,
                "maintenance_monthly": 3000
            },
            "possession_date": possession_date,
            "minimum_lease_months": 11,
            "other_highlights": "Sea view, Gym, Swimming Pool, Covered parking"
        }, token=self.token)
        
        if result.get("success"):
            self.listing_id = result.get("data", {}).get("listing_id")
            logger.info(f"Created listing: {self.listing_id}")
            return True
        return False
    
    def test_publish_listing(self) -> bool:
        """Publish the created listing."""
        if not self.listing_id:
            logger.warning("No listing_id to publish - skipping")
            return False
        
        result = api_call("POST", f"/listings/{self.listing_id}/publish",
                         token=self.token)
        return result.get("success", False)
    
    def test_get_my_listings(self) -> bool:
        """Get all listings by current user."""
        result = api_call("GET", "/listings/my", token=self.token)
        
        if result.get("success"):
            listings = result.get("data", {}).get("listings", [])
            logger.info(f"Found {len(listings)} listings")
            return True
        return False
    
    def test_listings_feed(self) -> bool:
        """Get listings feed for tenants."""
        result = api_call("GET", "/feed/listings", {
            "city": "Mumbai",
            "budget_max": 100000,
            "limit": 10
        }, token=self.token)
        
        if result.get("success"):
            listings = result.get("data", {}).get("listings", [])
            logger.info(f"Feed returned {len(listings)} listings")
            return True
        return False
    
    def test_requirements_feed(self) -> bool:
        """Get requirements feed for hosts."""
        result = api_call("GET", "/feed/requirements", {
            "budget_min": 10000,
            "budget_max": 100000,
            "limit": 10
        }, token=self.token)
        
        if result.get("success"):
            requirements = result.get("data", {}).get("requirements", [])
            logger.info(f"Feed returned {len(requirements)} requirements")
            return True
        return False
    
    def test_search_listings(self) -> bool:
        """Search listings by text."""
        result = api_call("GET", "/feed/search/listings", {
            "q": "apartment"
        }, token=self.token)
        
        if result.get("success"):
            listings = result.get("data", {}).get("listings", [])
            logger.info(f"Search returned {len(listings)} listings")
            return True
        return False
    
    def test_save_listing(self) -> bool:
        """Save a listing."""
        if not self.listing_id:
            logger.warning("No listing_id to save - skipping")
            return False
        
        result = api_call("POST", f"/matching/save?listing_id={self.listing_id}",
                         token=self.token)
        
        if result.get("success"):
            self.saved_id = result.get("data", {}).get("saved_id")
            return True
        return False
    
    def test_get_saved_items(self) -> bool:
        """Get saved items."""
        result = api_call("GET", "/matching/saved", token=self.token)
        
        if result.get("success"):
            items = result.get("data", {}).get("saved_items", [])
            logger.info(f"Found {len(items)} saved items")
            return True
        return False
    
    def test_swipe_action(self) -> bool:
        """Test swipe/like action."""
        if not self.listing_id or not self.user_id:
            logger.warning("Missing listing_id or user_id for swipe - skipping")
            return True  # Skip gracefully
        
        result = api_call("POST", "/matching/swipe", {
            "swiper_type": "tenant",
            "action": "like",
            "swiped_listing_id": self.listing_id,
            "swiped_user_id": self.user_id  # Self-swipe for testing
        }, token=self.token)
        
        if result.get("success"):
            is_match = result.get("data", {}).get("is_match", False)
            if is_match:
                self.match_id = result.get("data", {}).get("match", {}).get("match_id")
                logger.info(f"Match created! ID: {self.match_id}")
            return True
        return False
    
    def test_get_matches(self) -> bool:
        """Get all matches."""
        result = api_call("GET", "/matching/matches", token=self.token)
        
        if result.get("success"):
            matches = result.get("data", {}).get("matches", [])
            logger.info(f"Found {len(matches)} matches")
            return True
        return False
    
    def test_mark_rented(self) -> bool:
        """Mark listing as rented."""
        if not self.listing_id:
            logger.warning("No listing_id to mark as rented - skipping")
            return False
        
        result = api_call("POST", f"/listings/{self.listing_id}/mark-rented", {
            "rent_amount": 45000,
            "notes": "Test rental completed"
        }, token=self.token)
        
        return result.get("success", False)
    
    def test_get_host_profile(self) -> bool:
        """Get host profile (host_jay)."""
        result = api_call("GET", "/host/profile", token=self.token)
        
        if result.get("success"):
            bio = result.get("data", {}).get("bio", "")
            logger.info(f"Host bio: {bio}")
            return "host_jay" in bio
        return False
    
    def test_get_tenant_profile(self) -> bool:
        """Get tenant profile (tenant_jay)."""
        result = api_call("GET", "/tenant/profile", token=self.token)
        
        if result.get("success"):
            bio = result.get("data", {}).get("bio", "")
            logger.info(f"Tenant bio: {bio}")
            return "tenant_jay" in bio
        return False
    
    def test_get_user_profile(self) -> bool:
        """Get current user profile."""
        result = api_call("GET", "/auth/me", token=self.token)
        
        if result.get("user_id") or result.get("full_name"):
            logger.info(f"User: {result.get('full_name')} (type: {result.get('user_type')})")
            return True
        return False


# ============ MAIN ============

if __name__ == "__main__":
    print("\n" + "🚀 Starting HOMIGO API Test Suite with FRESH DATA...\n")
    
    tester = APITester()
    passed, failed = tester.run_all_tests()
    
    print("\n" + "=" * 70)
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {failed} test(s) failed. Check logs for details.")
    print("=" * 70 + "\n")
    
    sys.exit(0 if failed == 0 else 1)
