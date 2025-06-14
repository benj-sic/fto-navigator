import httpx
import json

# USPTO Public Search API (different from Patent File Wrapper)
base_url = "https://developer.uspto.gov/ibd-api/v1/application/publications"

print("Testing USPTO Public Search API (no key required)...\n")

# This API uses different query syntax
test_queries = [
    {"searchText": "CRISPR", "rows": 5},
    {"inventionTitle": "CRISPR", "rows": 5},
    {"abstract": "gene editing", "rows": 5}
]

for params in test_queries:
    print(f"{'='*60}")
    print(f"Testing with params: {params}")
    
    try:
        response = httpx.get(
            base_url,
            params=params,
            timeout=15.0
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if "response" in data:
                resp = data["response"]
                print(f"Found: {resp.get('numFound', 0)} results")
                
                docs = resp.get("docs", [])
                if docs:
                    print(f"\nFirst result:")
                    print(f"  Title: {docs[0].get('inventionTitle', 'N/A')}")
                    print(f"  App Number: {docs[0].get('applicationNumber', 'N/A')}")
                    print(f"  Date: {docs[0].get('publicationDate', 'N/A')}")
            else:
                print(f"Response structure: {list(data.keys())}")
        else:
            print(f"Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"Error: {str(e)}")