import asyncio
from patent_service import PatentSearchService

async def test_patent_search():
    service = PatentSearchService()
    keywords = ["CRISPR", "gene editing"]
    field = "Biotechnology"

    print("Testing patent search...")
    result = await service.search_patents(keywords, field)

    print(f"\nStatus: {result['status']}")
    print(f"Total found: {result.get('total_found', 0)}")
    print(f"Patents returned: {len(result.get('patents', []))}")

    if result['status'] == 'error':
        print(f"Error: {result.get('message')}")
    else:
        for i, patent in enumerate(result.get('patnets', [])[:3]):
            print(f"\nPatent {i+1}")
            print(f" Number: {patent['patent_number']}")
            print(f" Title: {patent['title'][:60]}...")
            print(f" Relevance: {patent['relevance_score']}")

# Run the test
asyncio.run(test_patent_search())