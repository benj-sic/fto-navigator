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

# Get just one result to examine structure
params = {
    "searchText": "gene",
    "start": "0",
    "rows": "1"
}

print("Fetching one patent to examine structure...\n")

response = httpx.get(
    f"{base_url}/search",
    params=params,
    headers=headers,
    timeout=15.0
)

if response.status_code == 200:
    data = response.json()
    
    print(f"Total count: {data.get('count')}")
    print(f"Number of patents returned: {len(data.get('patentFileWrapperDataBag', []))}")
    
    patents = data.get('patentFileWrapperDataBag', [])
    if patents:
        first_patent = patents[0]
        
        # Print the structure
        print("\nFirst patent structure:")
        print(f"Keys: {list(first_patent.keys())}")
        
        # Check for applicationMetaData
        if 'applicationMetaData' in first_patent:
            meta = first_patent['applicationMetaData']
            print(f"\napplicationMetaData keys: {list(meta.keys())[:10]}...")  # First 10 keys
            
            # Print some key fields if they exist
            print(f"\nKey fields:")
            print(f"  inventionTitle: {meta.get('inventionTitle', 'Not found')[:60]}...")
            print(f"  patentNumber: {meta.get('patentNumber', 'Not found')}")
            print(f"  applicationStatusDescriptionText: {meta.get('applicationStatusDescriptionText', 'Not found')}")
            
        # Print the full first patent (limited chars) to see structure
        print(f"\nFull first patent (first 1000 chars):")
        print(json.dumps(first_patent, indent=2)[:1000] + "...")