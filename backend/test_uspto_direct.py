import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("USPTO_API_KEY")
base_url = "https://api.uspto.gov/api/v1/patent/applications"

print(f"API Key: {api_key[:10]}... (truncated)")

# Test 1: Try searching with different query formats
test_queries = [
    'CRISPR',
    'inventionTitle:CRISPR',
    'inventionTitle:"CRISPR"',
    'titleText:CRISPR',
    'titleText:"CRISPR"',
    'inventionTitle:(CRISPR gene editing)'
]

headers = {
    "X-API-Key": api_key,
    "Accept": "application/json"
}

for query in test_queries:
    print(f"\n{'='*60}")
    print(f"Testing query: {query}")
    
    params = {
        "searchText": query,
        "start": 0,
        "rows": 2
    }
    
    try:
        response = httpx.get(
            f"{base_url}/search",
            params=params,
            headers=headers,
            timeout=10.0
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found: {data.get('numFound', 0)} results")
            results = data.get('results', [])
            if results:
                print(f"First result: {results[0].get('applicationNumber', 'N/A')}")
        else:
            print(f"Error response: {response.text[:200]}")
            
    except Exception as e:
        print(f"Error: {str(e)}")