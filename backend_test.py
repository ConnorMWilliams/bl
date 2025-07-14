#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for QuickFlow Capital
Tests OpenAI GPT-4o Integration, Loan Application Submission, Lender Matching, and MongoDB Integration
"""

import requests
import json
import time
import os
from typing import Dict, Any

# Get backend URL from frontend environment
BACKEND_URL = "https://9a956868-ad08-497e-953d-efe2266b1d5e.preview.emergentagent.com/api"

# Sample business data for testing as specified in the review request
SAMPLE_APPLICATION = {
    "business_name": "Tech Startup Inc",
    "industry": "Technology",
    "years_in_business": 3,
    "annual_revenue": 750000.0,
    "credit_score": 680,
    "monthly_cash_flow": 15000.0,
    "existing_debt": 50000.0,
    "loan_amount_requested": 200000.0,
    "loan_purpose": "Business Expansion",
    "contact_email": "john@techstartup.com",
    "contact_phone": "(555) 123-4567"
}

class BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.application_id = None
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "passed": passed,
            "details": details
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, "API is healthy and responding")
                    return True
                else:
                    self.log_test("Health Check", False, f"Unexpected health status: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_loan_application_submission(self):
        """Test the main loan application submission endpoint"""
        try:
            print("Testing loan application submission with sample data...")
            print(f"Sample Application: {json.dumps(SAMPLE_APPLICATION, indent=2)}")
            
            response = requests.post(
                f"{self.base_url}/submit-application",
                json=SAMPLE_APPLICATION,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Store application ID for later tests
                self.application_id = data.get("application_id")
                
                # Validate response structure
                required_fields = [
                    "application_id", "qualification_score", "qualification_status",
                    "recommended_loan_amount", "interest_rate_range", "risk_assessment",
                    "ai_analysis", "matched_lenders", "next_steps"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("Loan Application Submission", False, 
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Validate data types and ranges
                if not isinstance(data["qualification_score"], int) or not (0 <= data["qualification_score"] <= 100):
                    self.log_test("Loan Application Submission", False, 
                                f"Invalid qualification_score: {data['qualification_score']}")
                    return False
                
                if data["qualification_status"] not in ["Approved", "Conditional", "Declined"]:
                    self.log_test("Loan Application Submission", False, 
                                f"Invalid qualification_status: {data['qualification_status']}")
                    return False
                
                if not isinstance(data["matched_lenders"], list):
                    self.log_test("Loan Application Submission", False, 
                                f"matched_lenders should be a list: {type(data['matched_lenders'])}")
                    return False
                
                if not isinstance(data["next_steps"], list):
                    self.log_test("Loan Application Submission", False, 
                                f"next_steps should be a list: {type(data['next_steps'])}")
                    return False
                
                details = f"Application ID: {data['application_id']}, Score: {data['qualification_score']}, Status: {data['qualification_status']}, Lenders: {len(data['matched_lenders'])}"
                self.log_test("Loan Application Submission", True, details)
                return True
                
            else:
                self.log_test("Loan Application Submission", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Loan Application Submission", False, f"Error: {str(e)}")
            return False

    def test_openai_integration(self):
        """Test OpenAI GPT-4o integration by analyzing the AI response quality"""
        try:
            response = requests.post(
                f"{self.base_url}/submit-application",
                json=SAMPLE_APPLICATION,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_analysis = data.get("ai_analysis", "")
                
                # Check if AI analysis is meaningful (not just fallback)
                fallback_indicators = [
                    "Unable to complete AI analysis",
                    "Manual review required",
                    "AI analysis unavailable"
                ]
                
                is_fallback = any(indicator in ai_analysis for indicator in fallback_indicators)
                
                if is_fallback:
                    self.log_test("OpenAI GPT-4o Integration", False, 
                                f"AI analysis appears to be fallback response: {ai_analysis}")
                    return False
                
                # Check for structured analysis components
                if len(ai_analysis) < 50:
                    self.log_test("OpenAI GPT-4o Integration", False, 
                                f"AI analysis too short, likely not from GPT-4o: {ai_analysis}")
                    return False
                
                # Check if we have additional AI fields
                ai_fields = ["key_strengths", "key_concerns", "improvement_suggestions"]
                ai_field_count = sum(1 for field in ai_fields if field in data and data[field])
                
                if ai_field_count >= 2:
                    self.log_test("OpenAI GPT-4o Integration", True, 
                                f"AI analysis appears comprehensive with {ai_field_count} additional fields")
                    return True
                else:
                    self.log_test("OpenAI GPT-4o Integration", False, 
                                f"AI analysis lacks comprehensive structure, only {ai_field_count} additional fields found")
                    return False
                    
            else:
                self.log_test("OpenAI GPT-4o Integration", False, 
                            f"Failed to get response for AI analysis test: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("OpenAI GPT-4o Integration", False, f"Error testing AI integration: {str(e)}")
            return False

    def test_lender_matching(self):
        """Test the mock lender database and matching algorithm"""
        try:
            response = requests.post(
                f"{self.base_url}/submit-application",
                json=SAMPLE_APPLICATION,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                matched_lenders = data.get("matched_lenders", [])
                
                if not matched_lenders:
                    self.log_test("Mock Lender Database", False, "No lenders matched")
                    return False
                
                # Validate lender structure
                for i, lender in enumerate(matched_lenders):
                    required_lender_fields = ["lender_name", "lender_type", "interest_rate_range", "match_score"]
                    missing_lender_fields = [field for field in required_lender_fields if field not in lender]
                    
                    if missing_lender_fields:
                        self.log_test("Mock Lender Database", False, 
                                    f"Lender {i} missing fields: {missing_lender_fields}")
                        return False
                
                # Check if lenders are appropriate for Technology industry and credit score 680
                tech_friendly_lenders = [
                    "Capital Growth Partners",  # Technology specialty
                    "Quick Capital Solutions"   # Technology specialty
                ]
                
                matched_names = [lender["lender_name"] for lender in matched_lenders]
                tech_matches = [name for name in matched_names if name in tech_friendly_lenders]
                
                if tech_matches:
                    details = f"Found {len(matched_lenders)} lenders, including tech-friendly: {tech_matches}"
                    self.log_test("Mock Lender Database", True, details)
                    return True
                else:
                    # Still pass if we have valid lenders, even if not tech-specific
                    details = f"Found {len(matched_lenders)} valid lenders: {matched_names}"
                    self.log_test("Mock Lender Database", True, details)
                    return True
                    
            else:
                self.log_test("Mock Lender Database", False, 
                            f"Failed to test lender matching: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Mock Lender Database", False, f"Error testing lender matching: {str(e)}")
            return False

    def test_mongodb_integration(self):
        """Test MongoDB integration by retrieving stored application"""
        if not self.application_id:
            self.log_test("MongoDB Integration", False, "No application ID available for testing")
            return False
            
        try:
            # Test retrieval of stored application
            response = requests.get(
                f"{self.base_url}/application/{self.application_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate stored data structure
                required_fields = ["application_id", "business_details", "loan_result", "created_at"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("MongoDB Integration", False, 
                                f"Stored data missing fields: {missing_fields}")
                    return False
                
                # Validate business details match original application
                business_details = data["business_details"]
                if business_details["business_name"] != SAMPLE_APPLICATION["business_name"]:
                    self.log_test("MongoDB Integration", False, 
                                f"Business name mismatch: stored={business_details['business_name']}, original={SAMPLE_APPLICATION['business_name']}")
                    return False
                
                if business_details["credit_score"] != SAMPLE_APPLICATION["credit_score"]:
                    self.log_test("MongoDB Integration", False, 
                                f"Credit score mismatch: stored={business_details['credit_score']}, original={SAMPLE_APPLICATION['credit_score']}")
                    return False
                
                self.log_test("MongoDB Integration", True, 
                            f"Successfully stored and retrieved application {self.application_id}")
                return True
                
            elif response.status_code == 404:
                self.log_test("MongoDB Integration", False, 
                            f"Application {self.application_id} not found in database")
                return False
            else:
                self.log_test("MongoDB Integration", False, 
                            f"Error retrieving application: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("MongoDB Integration", False, f"Error testing MongoDB: {str(e)}")
            return False

    def test_input_validation(self):
        """Test input validation and error handling"""
        test_cases = [
            {
                "name": "Missing Required Field",
                "data": {k: v for k, v in SAMPLE_APPLICATION.items() if k != "business_name"},
                "expected_status": 422
            },
            {
                "name": "Invalid Credit Score",
                "data": {**SAMPLE_APPLICATION, "credit_score": 1000},
                "expected_status": [200, 422]  # May pass validation but should handle gracefully
            },
            {
                "name": "Negative Revenue",
                "data": {**SAMPLE_APPLICATION, "annual_revenue": -100000},
                "expected_status": [200, 422]
            },
            {
                "name": "Invalid Email",
                "data": {**SAMPLE_APPLICATION, "contact_email": "invalid-email"},
                "expected_status": [200, 422]
            }
        ]
        
        validation_passed = True
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/submit-application",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                
                expected_statuses = test_case["expected_status"] if isinstance(test_case["expected_status"], list) else [test_case["expected_status"]]
                
                if response.status_code in expected_statuses:
                    print(f"✅ {test_case['name']}: HTTP {response.status_code} (expected)")
                else:
                    print(f"❌ {test_case['name']}: HTTP {response.status_code} (expected {expected_statuses})")
                    validation_passed = False
                    
            except Exception as e:
                print(f"❌ {test_case['name']}: Error - {str(e)}")
                validation_passed = False
        
        self.log_test("Input Validation & Error Handling", validation_passed, 
                    "Tested various invalid input scenarios")
        return validation_passed

    def test_nonexistent_application(self):
        """Test retrieval of non-existent application"""
        try:
            fake_id = "00000000-0000-0000-0000-000000000000"
            response = requests.get(
                f"{self.base_url}/application/{fake_id}",
                timeout=10
            )
            
            if response.status_code == 404:
                self.log_test("Non-existent Application Handling", True, 
                            "Correctly returns 404 for non-existent application")
                return True
            else:
                self.log_test("Non-existent Application Handling", False, 
                            f"Expected 404, got HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Non-existent Application Handling", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 80)
        print("QUICKFLOW CAPITAL BACKEND API TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Sample Application: {SAMPLE_APPLICATION['business_name']} ({SAMPLE_APPLICATION['industry']})")
        print("=" * 80)
        print()
        
        # Run tests in logical order
        tests = [
            self.test_health_check,
            self.test_loan_application_submission,
            self.test_openai_integration,
            self.test_lender_matching,
            self.test_mongodb_integration,
            self.test_input_validation,
            self.test_nonexistent_application
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            if test():
                passed_tests += 1
            time.sleep(1)  # Brief pause between tests
        
        # Print summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print()
        print(f"OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Backend API is working correctly.")
        else:
            print(f"⚠️  {total_tests - passed_tests} test(s) failed. Review issues above.")
        
        print("=" * 80)
        
        return passed_tests, total_tests, self.test_results

if __name__ == "__main__":
    tester = BackendTester()
    passed, total, results = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if passed == total else 1)