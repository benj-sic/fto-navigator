import httpx
import json

# Very simple test of PatentsView API
url = "https://api.patentsview.org/patents/query"

# Simplest possible query - just get any 2 patents
query = {
    "q": {"patent_number": "1"},  # Patents starting with 1
    "f": ["patent_number", "patent_title"],
    "o": {"per_page": 2}
}

print("Testing PatentsView API directly...")
print(f"Query: {json.dumps(query, indent=2)}")

response = httpx.post(url, json=query, timeout=10.0)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")