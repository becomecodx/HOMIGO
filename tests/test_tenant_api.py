"""
HOMIGO Tenant API Test Script

Tests all Tenant API endpoints:
1. Create/Update Tenant Profile (tenant_jay)
2. Get Tenant Profile
3. Set Tenant Priorities
4. Get Tenant Priorities
5. Create Tenant Requirement
6. Get My Requirements
7. Update Requirement
8. Activate Requirement
9. Get Requirement by ID
10. Delete Requirement

Logs stored in: tests/tenant_test_logs_<timestamp>.txt
"""

import requests
import json
import logging
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict
import sys
import os
import uuid

# ============ CONFIGURATION ============

BASE_URL = "http://localhost:8000/api/v1"

# Generate unique identifiers for this test run
TEST_RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
UNIQUE_ID = uuid.uuid4().hex[:8]

# ============ LOGGING SETUP ============

os.makedirs("tests", exist_ok=True)
log_file = f"tests/tenant_test_logs_{TEST_RUN_ID}.txt"

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

def create_mock_token(firebase_id: str) -> str:
    """Create a mock Firebase token for testing."""
    payload = base64.urlsafe_b64encode(json.dumps({
        "user_id": firebase_id,
        "sub": firebase_id,
        "email": f"{firebase_id}@test.com"
    }).encode()).decode().rstrip('=')
    return f"xxx.{payload}.xxx"


def log_separator(title: str):
    sep = "=" * 60
    logger.info(sep)
    logger.info(f"  {title}")
    logger.info(sep)


def api_call(method: str, endpoint: str, data: Optional[Dict] = None, 
             token: Optional[str] = None) -> Dict:
    """Make an API call and return the result."""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    logger.info(f"REQUEST: {method} {endpoint}")
    if data:
        logger.info(f"PAYLOAD: {json.dumps(data, indent=2, default=str)}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        result = response.json()
        logger.info(f"STATUS: {response.status_code}")
        logger.info(f"RESPONSE: {json.dumps(result, indent=2, default=str)[:1500]}")
        
        if response.status_code < 400:
            logger.info("✅ SUCCESS")
        else:
            logger.warning(f"❌ FAILED: {response.status_code}")
        
        return {"status": response.status_code, "body": result}
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"status": 500, "body": {"error": str(e)}}


# ============ TENANT API TESTER ============

class TenantAPITester:
    """Tenant API Test Runner."""
    
    def __init__(self):
        self.firebase_id = f"tenant_{UNIQUE_ID}"
        self.token = create_mock_token(self.firebase_id)
        self.user_id = None
        self.tenant_profile_id = None
        self.requirement_id = None
        
    def run_all_tests(self):
        """Run all tenant API tests."""
        logger.info("\n" + "=" * 70)
        logger.info("  HOMIGO TENANT API TEST")
        logger.info(f"  Test Run ID: {TEST_RUN_ID}")
        logger.info(f"  Firebase ID: {self.firebase_id}")
        logger.info(f"  Log File: {log_file}")
        logger.info("=" * 70 + "\n")
        
        tests = [
            ("1. Signup User (type: tenant)", self.test_signup),
            ("2. Login", self.test_login),
            ("3. Create Tenant Profile (tenant_jay)", self.test_create_tenant_profile),
            ("4. Get Tenant Profile", self.test_get_tenant_profile),
            ("5. Update Tenant Profile", self.test_update_tenant_profile),
            ("6. Set Tenant Priorities", self.test_set_priorities),
            ("7. Get Tenant Priorities", self.test_get_priorities),
            ("8. Create Tenant Requirement", self.test_create_requirement),
            ("9. Get My Requirements", self.test_get_my_requirements),
            ("10. Get Requirement by ID", self.test_get_requirement_by_id),
            ("11. Update Requirement", self.test_update_requirement),
            ("12. Activate Requirement", self.test_activate_requirement),
            ("13. Delete Requirement", self.test_delete_requirement),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            log_separator(test_name)
            try:
                success = test_func()
                results.append((test_name, "✅ PASSED" if success else "❌ FAILED"))
            except Exception as e:
                logger.error(f"Exception: {e}")
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
    
    def test_signup(self) -> bool:
        """Signup a new tenant user."""
        result = api_call("POST", "/auth/signup", {
            "firebase_id": self.firebase_id,
            "full_name": f"Tenant Jay {UNIQUE_ID}",
            "email": f"tenant_{UNIQUE_ID}@test.com",
            "phone": f"+9198765{UNIQUE_ID[:5]}",
            "user_type": "tenant"  # Tenant only
        })
        
        if result["status"] == 201:
            self.user_id = result["body"].get("user", {}).get("user_id")
            logger.info(f"Created user: {self.user_id}")
            return True
        return False
    
    def test_login(self) -> bool:
        """Login and verify user."""
        result = api_call("POST", "/auth/login", {"firebase_token": self.token})
        
        if result["status"] == 200:
            user = result["body"].get("user", {})
            self.user_id = user.get("user_id")
            logger.info(f"Logged in as: {user.get('full_name')} (type: {user.get('user_type')})")
            return True
        return False
    
    def test_create_tenant_profile(self) -> bool:
        """Create tenant profile (tenant_jay)."""
        # Using correct values that fit VARCHAR constraints
        result = api_call("PUT", "/tenant/profile", {
            "occupation_type": "working_professional",  # Valid enum
            "job_title": "Software Engineer",
            "company_name": "Tech Corp",
            "smoking": "no",           # <= 10 chars ✓
            "drinking": "no",          # <= 10 chars ✓ (not "occasionally" which is 12 chars!)
            "food_preference": "veg",  # Valid enum
            "bio": "Looking for a peaceful place - tenant_jay",
            "hobbies": "Reading, Gaming, Music",
            "languages_spoken": "English, Hindi"
        }, token=self.token)
        
        if result["status"] == 200:
            self.tenant_profile_id = result["body"].get("data", {}).get("tenant_profile_id")
            logger.info(f"Created tenant profile: {self.tenant_profile_id}")
            return True
        return False
    
    def test_get_tenant_profile(self) -> bool:
        """Get tenant profile."""
        result = api_call("GET", "/tenant/profile", token=self.token)
        
        if result["status"] == 200:
            bio = result["body"].get("data", {}).get("bio", "")
            logger.info(f"Profile bio: {bio}")
            return "tenant_jay" in bio
        return False
    
    def test_update_tenant_profile(self) -> bool:
        """Update tenant profile."""
        result = api_call("PUT", "/tenant/profile", {
            "bio": "Updated bio - tenant_jay - professional looking for great place",
            "hobbies": "Reading, Gaming, Music, Movies"
        }, token=self.token)
        
        if result["status"] == 200:
            logger.info("Profile updated successfully")
            return True
        return False
    
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
        
        return result["status"] == 200
    
    def test_get_priorities(self) -> bool:
        """Get tenant search priorities."""
        result = api_call("GET", "/tenant/priorities", token=self.token)
        
        if result["status"] == 200:
            priority = result["body"].get("data", {})
            logger.info(f"Budget priority: {priority.get('budget_priority')}")
            return priority.get("budget_priority") == 1
        return False
    
    def test_create_requirement(self) -> bool:
        """Create a tenant requirement."""
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
        
        if result["status"] == 201:
            self.requirement_id = result["body"].get("data", {}).get("requirement_id")
            logger.info(f"Created requirement: {self.requirement_id}")
            return True
        return False
    
    def test_get_my_requirements(self) -> bool:
        """Get all my requirements."""
        result = api_call("GET", "/tenant/requirements/my", token=self.token)
        
        if result["status"] == 200:
            requirements = result["body"].get("data", {}).get("requirements", [])
            logger.info(f"Found {len(requirements)} requirements")
            return len(requirements) > 0
        return False
    
    def test_get_requirement_by_id(self) -> bool:
        """Get requirement by ID."""
        if not self.requirement_id:
            logger.warning("No requirement_id to get")
            return False
        
        result = api_call("GET", f"/tenant/requirements/{self.requirement_id}", token=self.token)
        
        if result["status"] == 200:
            title = result["body"].get("data", {}).get("title", "")
            logger.info(f"Requirement title: {title}")
            return UNIQUE_ID in title
        return False
    
    def test_update_requirement(self) -> bool:
        """Update requirement."""
        if not self.requirement_id:
            logger.warning("No requirement_id to update")
            return False
        
        result = api_call("PUT", f"/tenant/requirements/{self.requirement_id}", {
            "description": "Updated - Need a peaceful 2BHK flat with good connectivity",
            "budget_max": 45000
        }, token=self.token)
        
        return result["status"] == 200
    
    def test_activate_requirement(self) -> bool:
        """Activate requirement (simulates payment)."""
        if not self.requirement_id:
            logger.warning("No requirement_id to activate")
            return False
        
        result = api_call("POST", f"/tenant/requirements/{self.requirement_id}/activate", token=self.token)
        
        if result["status"] == 200:
            status = result["body"].get("data", {}).get("status")
            logger.info(f"Requirement status: {status}")
            return status == "active"
        return False
    
    def test_delete_requirement(self) -> bool:
        """Delete requirement."""
        if not self.requirement_id:
            logger.warning("No requirement_id to delete")
            return False
        
        result = api_call("DELETE", f"/tenant/requirements/{self.requirement_id}", token=self.token)
        
        return result["status"] == 200


# ============ MAIN ============

if __name__ == "__main__":
    print("\n" + "🚀 Starting HOMIGO Tenant API Tests...\n")
    
    tester = TenantAPITester()
    passed, failed = tester.run_all_tests()
    
    print("\n" + "=" * 70)
    if failed == 0:
        print("🎉 ALL TENANT TESTS PASSED!")
    else:
        print(f"⚠️  {failed} test(s) failed. Check logs for details.")
    print("=" * 70 + "\n")
    
    sys.exit(0 if failed == 0 else 1)
