import requests
import sys
import json
from datetime import datetime

class DeptAIHubAPITester:
    def __init__(self, base_url="https://ai-dept-portal.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user_data = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health check endpoint"""
        return self.run_test("Health Check", "GET", "api/health", 200)

    def test_login_valid(self, roll_no="2473A31139"):
        """Test login with valid credentials"""
        success, response = self.run_test(
            "Valid Login",
            "POST",
            "api/auth/login",
            200,
            data={"roll_no": roll_no, "password": roll_no}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_data = response.get('user', {})
            print(f"   Token obtained: {self.token[:20]}...")
            print(f"   User data: {self.user_data}")
            return True
        return False

    def test_login_invalid_roll_no(self):
        """Test login with invalid roll number"""
        return self.run_test(
            "Invalid Roll Number",
            "POST",
            "api/auth/login",
            401,
            data={"roll_no": "invalid123", "password": "invalid123"}
        )

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        return self.run_test(
            "Wrong Password",
            "POST",
            "api/auth/login",
            401,
            data={"roll_no": "2473A31139", "password": "wrongpassword"}
        )

    def test_get_current_user(self):
        """Test getting current user info"""
        if not self.token:
            print("❌ No token available for user info test")
            return False
        
        return self.run_test("Get Current User", "GET", "api/auth/me", 200)

    def test_get_notices(self):
        """Test getting notices"""
        if not self.token:
            print("❌ No token available for notices test")
            return False
        
        return self.run_test("Get Notices", "GET", "api/notices", 200)

    def test_get_events(self):
        """Test getting events"""
        if not self.token:
            print("❌ No token available for events test")
            return False
        
        return self.run_test("Get Events", "GET", "api/events", 200)

    def test_get_timetable(self):
        """Test getting timetable"""
        if not self.token:
            print("❌ No token available for timetable test")
            return False
        
        return self.run_test("Get Timetable", "GET", "api/timetable", 200)

    def test_get_faculty(self):
        """Test getting faculty"""
        if not self.token:
            print("❌ No token available for faculty test")
            return False
        
        return self.run_test("Get Faculty", "GET", "api/faculty", 200)

    def test_get_resources(self):
        """Test getting resources"""
        if not self.token:
            print("❌ No token available for resources test")
            return False
        
        return self.run_test("Get Resources", "GET", "api/resources", 200)

    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        # Temporarily remove token
        temp_token = self.token
        self.token = None
        
        success, _ = self.run_test("Unauthorized Access", "GET", "api/auth/me", 401)
        
        # Restore token
        self.token = temp_token
        return success

    def test_admin_login(self):
        """Test admin login"""
        # Save current token
        temp_token = self.token
        temp_user = self.user_data
        
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={"roll_no": "admin", "password": "admin"}
        )
        
        if success and 'access_token' in response:
            admin_token = response['access_token']
            admin_user = response.get('user', {})
            print(f"   Admin user: {admin_user}")
            
            # Test admin can access all timetables
            self.token = admin_token
            admin_timetable_success, admin_timetable_data = self.run_test(
                "Admin Timetable Access", "GET", "api/timetable", 200
            )
            
            # Restore original token
            self.token = temp_token
            self.user_data = temp_user
            
            return admin_timetable_success
        
        # Restore original token
        self.token = temp_token
        self.user_data = temp_user
        return False

def main():
    print("🚀 Starting Dept-AI Hub API Testing...")
    print("=" * 50)
    
    # Initialize tester
    tester = DeptAIHubAPITester()
    
    # Test sequence
    tests = [
        ("Health Check", tester.test_health_check),
        ("Valid Login", lambda: tester.test_login_valid()),
        ("Invalid Roll Number", tester.test_login_invalid_roll_no),
        ("Wrong Password", tester.test_login_wrong_password),
        ("Get Current User", tester.test_get_current_user),
        ("Unauthorized Access", tester.test_unauthorized_access),
        ("Get Notices", tester.test_get_notices),
        ("Get Events", tester.test_get_events),
        ("Get Timetable", tester.test_get_timetable),
        ("Get Faculty", tester.test_get_faculty),
        ("Get Resources", tester.test_get_resources),
        ("Admin Login & Access", tester.test_admin_login),
    ]
    
    # Run all tests
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS:")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())