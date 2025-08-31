import requests
import sys
import json
from datetime import datetime

class FacultyIPSystemTester:
    def __init__(self, base_url="https://ip-dashboard-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.faculty_token = None
        self.admin_token = None
        self.faculty_user_id = None
        self.admin_user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_patent_id = None
        self.faculty_list = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        if details:
            print(f"   Details: {details}")

    def make_request(self, method, endpoint, data=None, token=None, expected_status=200):
        """Make HTTP request with proper headers"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}

            return success, response.status_code, response_data

        except Exception as e:
            return False, 0, {"error": str(e)}

    def test_faculty_registration(self):
        """Test faculty user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        data = {
            "email": f"john.faculty{timestamp}@university.edu",
            "password": "faculty123",
            "full_name": "Dr. John Smith",
            "user_type": "faculty"
        }
        
        success, status, response = self.make_request('POST', 'auth/register', data, expected_status=200)
        
        if success and 'access_token' in response:
            self.faculty_token = response['access_token']
            self.faculty_user_id = response['user_info']['id']
            self.log_test("Faculty Registration", True, f"Token received, User ID: {self.faculty_user_id}")
        else:
            self.log_test("Faculty Registration", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_admin_registration_blocked(self):
        """Test that admin registration should be blocked"""
        timestamp = datetime.now().strftime('%H%M%S')
        data = {
            "email": f"admin{timestamp}@university.edu",
            "password": "admin123",
            "full_name": "Admin User",
            "user_type": "admin"
        }
        
        success, status, response = self.make_request('POST', 'auth/register', data, expected_status=400)
        
        # Admin registration should fail - this is expected behavior
        if not success and status in [400, 403, 422]:
            self.log_test("Admin Registration Blocked", True, f"Admin registration correctly blocked (Status: {status})")
            return True
        elif success:
            self.log_test("Admin Registration Blocked", False, f"Admin registration should be blocked but succeeded")
            return False
        else:
            self.log_test("Admin Registration Blocked", False, f"Unexpected status: {status}, Response: {response}")
            return False

    def test_faculty_login(self):
        """Test faculty login with existing credentials"""
        data = {
            "email": "john.faculty@university.edu",
            "password": "faculty123"
        }
        
        success, status, response = self.make_request('POST', 'auth/login', data, expected_status=200)
        
        if success and 'access_token' in response:
            # Use this token if registration failed
            if not self.faculty_token:
                self.faculty_token = response['access_token']
                self.faculty_user_id = response['user_info']['id']
            self.log_test("Faculty Login", True, "Login successful")
        else:
            self.log_test("Faculty Login", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_fixed_admin_login(self):
        """Test fixed admin login with specific credentials"""
        data = {
            "email": "nit.official@gmail.com",
            "password": "12345123"
        }
        
        success, status, response = self.make_request('POST', 'auth/login', data, expected_status=200)
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            self.admin_user_id = response['user_info']['id']
            user_type = response.get('user_type')
            if user_type == 'admin':
                self.log_test("Fixed Admin Login", True, f"Admin login successful with correct credentials")
            else:
                self.log_test("Fixed Admin Login", False, f"Wrong user type returned: {user_type}")
                return False
        else:
            self.log_test("Fixed Admin Login", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_existing_faculty_login(self):
        """Test existing faculty login"""
        data = {
            "email": "john.faculty173336@university.edu",
            "password": "faculty123"
        }
        
        success, status, response = self.make_request('POST', 'auth/login', data, expected_status=200)
        
        if success and 'access_token' in response:
            self.faculty_token = response['access_token']
            self.faculty_user_id = response['user_info']['id']
            user_type = response.get('user_type')
            if user_type == 'faculty':
                self.log_test("Existing Faculty Login", True, f"Faculty login successful")
            else:
                self.log_test("Existing Faculty Login", False, f"Wrong user type returned: {user_type}")
                return False
        else:
            self.log_test("Existing Faculty Login", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_faculty_profile(self):
        """Test getting faculty profile"""
        if not self.faculty_token:
            self.log_test("Faculty Profile", False, "No faculty token available")
            return False

        success, status, response = self.make_request('GET', 'faculty/profile', token=self.faculty_token)
        
        if success and 'email' in response:
            self.log_test("Faculty Profile", True, f"Profile retrieved for {response.get('full_name')}")
        else:
            self.log_test("Faculty Profile", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_google_scholar_update(self):
        """Test Google Scholar profile update"""
        if not self.faculty_token:
            self.log_test("Google Scholar Update", False, "No faculty token available")
            return False

        data = {
            "google_scholar_url": "https://scholar.google.com/citations?user=JicYPdAAAAAJ"
        }
        
        success, status, response = self.make_request('PUT', 'faculty/scholar', data, token=self.faculty_token)
        
        if success and 'data' in response:
            scholar_data = response['data']
            if 'name' in scholar_data:
                self.log_test("Google Scholar Update", True, f"Scholar data retrieved for {scholar_data.get('name')}")
            else:
                self.log_test("Google Scholar Update", False, f"Scholar data incomplete: {scholar_data}")
        else:
            self.log_test("Google Scholar Update", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_create_patent(self):
        """Test creating a patent"""
        if not self.faculty_token:
            self.log_test("Create Patent", False, "No faculty token available")
            return False

        data = {
            "title": "Advanced AI Algorithm for Data Processing",
            "date_issued": "2024-01-15",
            "patent_number": "US12345678",
            "commercialized": True,
            "commercialization_amount": 150000.50
        }
        
        success, status, response = self.make_request('POST', 'faculty/patents', data, token=self.faculty_token, expected_status=200)
        
        if success and 'id' in response:
            self.test_patent_id = response['id']
            self.log_test("Create Patent", True, f"Patent created with ID: {self.test_patent_id}")
        else:
            self.log_test("Create Patent", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_get_faculty_patents(self):
        """Test getting faculty patents"""
        if not self.faculty_token:
            self.log_test("Get Faculty Patents", False, "No faculty token available")
            return False

        success, status, response = self.make_request('GET', 'faculty/patents', token=self.faculty_token)
        
        if success and isinstance(response, list):
            self.log_test("Get Faculty Patents", True, f"Retrieved {len(response)} patents")
        else:
            self.log_test("Get Faculty Patents", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_admin_get_faculty(self):
        """Test admin getting all faculty and check for duplicates"""
        if not self.admin_token:
            self.log_test("Admin Get Faculty", False, "No admin token available")
            return False

        success, status, response = self.make_request('GET', 'admin/faculty', token=self.admin_token)
        
        if success and isinstance(response, list):
            self.faculty_list = response
            faculty_count = len(response)
            
            # Check for duplicate names
            names = [faculty.get('full_name', '') for faculty in response]
            unique_names = set(names)
            
            # Check for Dr. John Smith duplicates specifically
            dr_john_count = names.count('Dr. John Smith')
            
            print(f"   Faculty found: {faculty_count}")
            print(f"   Unique names: {len(unique_names)}")
            print(f"   Dr. John Smith entries: {dr_john_count}")
            
            # Print all faculty for verification
            for i, faculty in enumerate(response, 1):
                print(f"   {i}. {faculty.get('full_name', 'Unknown')} ({faculty.get('email', 'No email')})")
            
            # Verify requirements
            if faculty_count == 2 and len(unique_names) == 2 and dr_john_count <= 1:
                self.log_test("Admin Get Faculty - Duplicate Check", True, f"No duplicates found, {faculty_count} unique faculty")
            else:
                self.log_test("Admin Get Faculty - Duplicate Check", False, f"Duplicates found or wrong count: {faculty_count} faculty, {dr_john_count} Dr. John Smith entries")
                return False
                
            self.log_test("Admin Get Faculty", True, f"Retrieved {faculty_count} faculty members")
        else:
            self.log_test("Admin Get Faculty", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_admin_get_faculty_patents(self):
        """Test admin getting faculty patents"""
        if not self.admin_token or not self.faculty_user_id:
            self.log_test("Admin Get Faculty Patents", False, "Missing admin token or faculty ID")
            return False

        success, status, response = self.make_request('GET', f'admin/faculty/{self.faculty_user_id}/patents', token=self.admin_token)
        
        if success and isinstance(response, list):
            self.log_test("Admin Get Faculty Patents", True, f"Retrieved {len(response)} patents for faculty")
        else:
            self.log_test("Admin Get Faculty Patents", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_admin_export_faculty_data(self):
        """Test admin exporting faculty data"""
        if not self.admin_token or not self.faculty_user_id:
            self.log_test("Admin Export Faculty Data", False, "Missing admin token or faculty ID")
            return False

        success, status, response = self.make_request('GET', f'admin/faculty/{self.faculty_user_id}/export', token=self.admin_token)
        
        if success and 'faculty_info' in response and 'patents' in response:
            self.log_test("Admin Export Faculty Data", True, "Export data retrieved successfully")
        else:
            self.log_test("Admin Export Faculty Data", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_role_based_access(self):
        """Test role-based access control"""
        tests_passed = 0
        total_tests = 2

        # Test faculty trying to access admin endpoints
        if self.faculty_token:
            success, status, response = self.make_request('GET', 'admin/faculty', token=self.faculty_token, expected_status=403)
            if success:
                tests_passed += 1
                print("✅ Faculty blocked from admin endpoints")
            else:
                print(f"❌ Faculty access control failed - Status: {status}")

        # Test admin trying to access faculty profile (should fail)
        if self.admin_token:
            success, status, response = self.make_request('GET', 'faculty/profile', token=self.admin_token, expected_status=403)
            if success:
                tests_passed += 1
                print("✅ Admin blocked from faculty endpoints")
            else:
                print(f"❌ Admin access control failed - Status: {status}")

        self.log_test("Role-Based Access Control", tests_passed == total_tests, f"{tests_passed}/{total_tests} access control tests passed")
        return tests_passed == total_tests

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Faculty IP Management System Final Verification Tests")
        print("=" * 70)

        # CRITICAL: Test fixed admin login first
        print("\n🔑 FIXED ADMIN LOGIN TESTING")
        admin_login_success = self.test_fixed_admin_login()
        
        # Test admin registration should be blocked
        print("\n🚫 ADMIN REGISTRATION BLOCKING TEST")
        self.test_admin_registration_blocked()

        # Test existing faculty login
        print("\n👨‍🎓 EXISTING FACULTY LOGIN TEST")
        faculty_login_success = self.test_existing_faculty_login()

        # CRITICAL: Test duplicate removal verification
        print("\n🔍 DUPLICATE REMOVAL VERIFICATION")
        if admin_login_success:
            duplicate_check_success = self.test_admin_get_faculty()
        else:
            print("❌ Cannot verify duplicates - admin login failed")
            duplicate_check_success = False

        # Test faculty functionality if faculty login worked
        if faculty_login_success:
            print("\n👨‍🎓 Faculty Feature Tests")
            self.test_faculty_profile()
            self.test_google_scholar_update()
            self.test_create_patent()
            self.test_get_faculty_patents()

        # Test admin functionality if admin login worked
        if admin_login_success:
            print("\n🛡️ Admin Feature Tests")
            self.test_admin_get_faculty_patents()
            self.test_admin_export_faculty_data()

        # Security Tests
        if admin_login_success and faculty_login_success:
            print("\n🔒 Security Tests")
            self.test_role_based_access()

        # Test new faculty registration still works
        print("\n📝 NEW FACULTY REGISTRATION TEST")
        self.test_faculty_registration()

        # Final Results
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        # Critical requirements check
        critical_tests = {
            "Fixed Admin Login": admin_login_success,
            "Duplicate Removal": duplicate_check_success,
            "Existing Faculty Login": faculty_login_success
        }
        
        print("\n🎯 CRITICAL REQUIREMENTS STATUS:")
        all_critical_passed = True
        for test_name, passed in critical_tests.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"   {test_name}: {status}")
            if not passed:
                all_critical_passed = False
        
        if all_critical_passed:
            print("\n🎉 All critical requirements verified! System is ready.")
            return 0
        else:
            print("\n⚠️ Critical requirements failed. System needs fixes.")
            return 1

def main():
    tester = FacultyIPSystemTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())