import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("USPTO_API_KEY")
base_url = "https://api.uspto.gov/api/v1/patent/applications"

headers = {
    "X-API-Key": api_key,
    "Accept": "application/json"
}

print(f"API Key: {api_key[:10]}... (truncated)")
print(f"Testing USPTO Patent File Wrapper API\n")

# Test 1: Try to get ANY results with very broad searches
test_queries = [
    # Try without field specifiers
    "gene",
    "software",
    "method",
    # Try with wildcards
    "*gene*",
    "gene*",
    # Try specific patent numbers if we know any
    "10000000",
    # Try boolean operators
    "gene AND editing",
    "gene OR therapy",
    # Try other field names that might work
    "abstract:gene",
    "claims:gene",
    "description:gene",
    # Try searching everything
    "all:gene",
    "*:gene"
]

for query in test_queries:
    print(f"{'='*60}")
    print(f"Testing query: {query}")
    
    params = {
        "searchText": query,
        "start": "0",
        "rows": "2"
    }
    
    try:
        response = httpx.get(
            f"{base_url}/search",
            params=params,
            headers=headers,
            timeout=15.0
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            print(f"Found: {data.get('numFound', 0)} results")
            
            results = data.get('results', [])
            if results:
                print(f"First result keys: {list(results[0].keys())}")
                print(f"Application number: {results[0].get('applicationNumber', 'N/A')}")
            else:
                # Print part of response to debug
                print(f"Raw response (first 300 chars): {json.dumps(data)[:300]}")
        else:
            print(f"Error response: {response.text[:200]}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

# Test 2: Try getting a specific patent directly
print(f"\n{'='*60}")
print("Testing direct patent retrieval...")
test_app_number = "16000000"  # A likely valid application number

try:
    response = httpx.get(
        f"{base_url}/{test_app_number}",
        headers=headers,
        timeout=15.0
    )
    
    print(f"Direct fetch status: {response.status_code}")
    if response.status_code == 200:
        print("Success! Can retrieve individual patents")
    else:
        print(f"Error: {response.text[:200]}")
        
except Exception as e:
    print(f"Error: {str(e)}")