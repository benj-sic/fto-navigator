import requests
import json
import os

# Base URL of the running FastAPI application
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/analyze"

# Path to the test data file, located in the same directory as this script
TEST_DATA_FILE = os.path.join(os.path.dirname(__file__), 'test_data.json')

def load_test_data():
    """Loads test cases from the JSON file."""
    try:
        with open(TEST_DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Test data file not found at {TEST_DATA_FILE}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {TEST_DATA_FILE}")
        return []

def run_test(test_case_data, test_name):
    """Runs a single analysis test case."""
    print("-" * 50)
    print(f"🚀 Running test case: '{test_name}'")
    print(f"   Jurisdiction: {test_case_data.get('jurisdiction')}")
    print("-" * 50)
    
    try:
        response = requests.post(API_URL, json=test_case_data)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        print(f"Status Code: {response.status_code}")
        
        response_data = response.json()
        print("API Response:")
        # Pretty print the JSON response
        print(json.dumps(response_data, indent=2))
        
        # Basic assertions to verify the test outcome
        assert response.status_code == 200
        assert response_data["status"] in ["completed", "error"]
        if response_data["status"] == "completed":
            assert "analysis_id" in response_data
            assert "patent_count" in response_data
            assert isinstance(response_data["top_patents"], list)
            print(f"\n✅ Test '{test_name}' PASSED")
        else:
            # This handles cases where the API itself reports a failure (e.g., search error)
            print(f"\n⚠️ Test '{test_name}' COMPLETED WITH API-LEVEL ERROR: {response_data.get('message')}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Test '{test_name}' FAILED: Could not connect to the API.")
        print(f"Error: {e}")
        print("Please ensure the backend server is running (`uvicorn main:app --reload`).")

if __name__ == "__main__":
    test_cases = load_test_data()
    if not test_cases:
        print("\nNo test cases found. Exiting.")
    else:
        print(f"Found {len(test_cases)} test cases to run.")
        for test_case in test_cases:
            run_test(test_case['data'], test_case['test_case_name'])