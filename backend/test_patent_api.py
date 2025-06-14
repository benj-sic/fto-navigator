import asyncio
from patent_service import PatentSearchService

async def test_patent_search():
    service = PatentSearchService()
    keywords = ["CRISPR", "gene editing"]
    field = "Biotechnology"

    print("Testing patent search...")
    result = await service.search_patents(keywords, field)

    print(f"\nSuccess: {result.get('success', False)}")
    print(f"Total found: {result.get('total_found', 0)}")
    print(f"Patents returned: {len(result.get('patents', []))}")

    if not result.get('success'):
        print(f"Error: {result.get('error', 'Unknown error')}")
    else:
        for i, patent in enumerate(result.get('patents', [])[:3]):
            print(f"\nPatent {i+1}:")
            print(f"  Number: {patent['patent_number']}")
            print(f"  Title: {patent['title'][:60]}...")
            print(f"  Applicants: {', '.join(patent['applicants'][:2])}")

# Run the test
asyncio.run(test_patent_search())