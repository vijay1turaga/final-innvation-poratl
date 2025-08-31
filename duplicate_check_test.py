import requests
import sys
import json
from collections import Counter

class DuplicateCheckTester:
    def __init__(self, base_url="https://ip-dashboard-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0

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

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}

            return success, response.status_code, response_data

        except Exception as e:
            return False, 0, {"error": str(e)}

    def test_admin_login_specific(self):
        """Test admin login with specific credentials from request"""
        data = {
            "email": "admin@university.edu",
            "password": "admin123"
        }
        
        success, status, response = self.make_request('POST', 'auth/login', data, expected_status=200)
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            self.log_test("Admin Login (Specific Credentials)", True, f"Login successful for {data['email']}")
        else:
            self.log_test("Admin Login (Specific Credentials)", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_duplicate_dr_john_smith(self):
        """Test for duplicate Dr. John Smith entries"""
        if not self.admin_token:
            self.log_test("Duplicate Dr. John Smith Check", False, "No admin token available")
            return False

        success, status, response = self.make_request('GET', 'admin/faculty', token=self.admin_token)
        
        if not success:
            self.log_test("Duplicate Dr. John Smith Check", False, f"Failed to get faculty list - Status: {status}")
            return False

        if not isinstance(response, list):
            self.log_test("Duplicate Dr. John Smith Check", False, "Invalid response format")
            return False

        # Count occurrences of "Dr. John Smith"
        faculty_names = [faculty.get('full_name', '') for faculty in response]
        dr_john_smith_count = faculty_names.count('Dr. John Smith')
        
        # Count all faculty with similar names (case insensitive)
        similar_names = []
        for name in faculty_names:
            if 'john' in name.lower() and 'smith' in name.lower():
                similar_names.append(name)
        
        # Count duplicates by email as well
        faculty_emails = [faculty.get('email', '') for faculty in response]
        email_counts = Counter(faculty_emails)
        duplicate_emails = {email: count for email, count in email_counts.items() if count > 1}
        
        # Count duplicates by name
        name_counts = Counter(faculty_names)
        duplicate_names = {name: count for name, count in name_counts.items() if count > 1}
        
        print(f"\n📊 DUPLICATE CHECK RESULTS:")
        print(f"   Total Faculty Members: {len(response)}")
        print(f"   'Dr. John Smith' entries: {dr_john_smith_count}")
        print(f"   Similar names (John Smith variants): {similar_names}")
        print(f"   Duplicate names found: {duplicate_names}")
        print(f"   Duplicate emails found: {duplicate_emails}")
        
        # Print all faculty for verification
        print(f"\n👥 ALL FACULTY MEMBERS:")
        for i, faculty in enumerate(response, 1):
            print(f"   {i}. {faculty.get('full_name', 'N/A')} ({faculty.get('email', 'N/A')})")
        
        # Test passes if exactly 1 Dr. John Smith and no duplicates
        test_passed = (
            dr_john_smith_count == 1 and 
            len(duplicate_names) == 0 and 
            len(duplicate_emails) == 0
        )
        
        if test_passed:
            self.log_test("Duplicate Dr. John Smith Check", True, 
                         f"Exactly 1 'Dr. John Smith' found, no duplicates detected")
        else:
            failure_reasons = []
            if dr_john_smith_count != 1:
                failure_reasons.append(f"Expected 1 'Dr. John Smith', found {dr_john_smith_count}")
            if duplicate_names:
                failure_reasons.append(f"Duplicate names: {duplicate_names}")
            if duplicate_emails:
                failure_reasons.append(f"Duplicate emails: {duplicate_emails}")
            
            self.log_test("Duplicate Dr. John Smith Check", False, "; ".join(failure_reasons))
        
        return test_passed

    def test_faculty_uniqueness(self):
        """Test overall faculty uniqueness"""
        if not self.admin_token:
            self.log_test("Faculty Uniqueness Check", False, "No admin token available")
            return False

        success, status, response = self.make_request('GET', 'admin/faculty', token=self.admin_token)
        
        if not success:
            self.log_test("Faculty Uniqueness Check", False, f"Failed to get faculty list - Status: {status}")
            return False

        # Check for unique IDs
        faculty_ids = [faculty.get('id', '') for faculty in response]
        unique_ids = len(set(faculty_ids))
        total_faculty = len(response)
        
        # Check for unique emails
        faculty_emails = [faculty.get('email', '') for faculty in response]
        unique_emails = len(set(faculty_emails))
        
        ids_unique = unique_ids == total_faculty
        emails_unique = unique_emails == total_faculty
        
        if ids_unique and emails_unique:
            self.log_test("Faculty Uniqueness Check", True, 
                         f"All {total_faculty} faculty have unique IDs and emails")
        else:
            failure_details = []
            if not ids_unique:
                failure_details.append(f"IDs not unique: {unique_ids}/{total_faculty}")
            if not emails_unique:
                failure_details.append(f"Emails not unique: {unique_emails}/{total_faculty}")
            
            self.log_test("Faculty Uniqueness Check", False, "; ".join(failure_details))
        
        return ids_unique and emails_unique

    def run_duplicate_tests(self):
        """Run all duplicate-related tests"""
        print("🔍 Starting Duplicate Dr. John Smith Verification Tests")
        print("=" * 60)

        # Test admin login with specific credentials
        print("\n🔐 Admin Authentication Test")
        if not self.test_admin_login_specific():
            print("❌ Cannot proceed without admin access")
            return 1

        # Test for duplicate Dr. John Smith entries
        print("\n🎯 Duplicate Detection Tests")
        self.test_duplicate_dr_john_smith()
        self.test_faculty_uniqueness()

        # Final Results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All duplicate tests passed! No duplicate Dr. John Smith entries found.")
            return 0
        else:
            print(f"⚠️ {self.tests_run - self.tests_passed} tests failed. Duplicates may still exist.")
            return 1

def main():
    tester = DuplicateCheckTester()
    return tester.run_duplicate_tests()

if __name__ == "__main__":
    sys.exit(main())