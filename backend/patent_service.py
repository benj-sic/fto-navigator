import httpx
from typing import List, Dict
import asyncio
from datetime import datetime, timezone
import json

class PatentSearchService:
    """Handles patetn searches using free APIs"""

    def __init__(self):
        # We'll use USPTO's PatentsView API (free, no key required)
        self.base_url = "https://api.patentsview.org/patents/query"
        self.timeout = 30.0

    async def search_patents(self, keywords: List[str], field_of_study: str) -> Dict:
        """
        Search for patents based on keywords
        Return simplified patent data
        """
        print(f"Starting patent search for keywords: {keywords}") # Debug log
        # Build query - search in title and abstract
        query_terms = " OR ".join([f'"{keyword}"' for keyword in keywords])

        # PatentsView API query format
        query = {
            "q": {
                " or": [
                    {"_text_any": {"patent_title": query_terms}},
                    {"_text_any": {"patent_abstract": query_terms}}
                ]
            },
             "f": [
                "patent_number",
                "patent_title",
                "patent_date",
                "patent_abstract",
                "inventor_last_name",
                "assignee_organization"
            ],
            "o": {
                "per_page": 10 # Limit results for MVP
            }
        }

        print(f"Query being sent: {json.dumps(query, indent=2)}") # Debug log

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    json=query,
                    headers={"Content-Type": "application/json"}
                )    

                print(f"Response status: {response.status_code}") # Debug log

                if response.status_code == 200:
                    data = response.json()
                    print(f"Response data keys: {data.keys()}") # Debug log

                    # Transform the results into our format
                    patents = []
                    if "patents" in data:
                        print(f"Found {len(data['patents'])} patents") # Debug log
                        for patent in data["patents"]:
                            patents.append({
                                "patent_number": patent.get("patent_number", "Unknown"),
                                "title": patent.get("patent_title", "No title"),
                                "date": patent.get("patent_date", "Unknown date"),
                                "abstract": patent.get("patent_abstract", "No abstract available"),
                                "relevance_score": self._calculate_relevance(patent, keywords),
                                "assignee": patent.get("assignee_organization", ["Unknown"])[0] if patent.get("assignee_organization") else "Unknown"
                            })

                    # Sort by relevance
                    patents.sort(key=lambda x: x["relevance_score"], reverse=True)

                    return {
                        "status": "success",
                        "total_found": data.get("total_patent_count", 0),
                        "patents": patents[:5], # Top 5 most relevant
                        "search_timestamp": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Patent search failed with status {response.status_code}",
                        "patents": []
                    }
                
        except httpx.TimeoutException:
            print("Patent search timed out") # Debug log
            return {
                "status": "error",
                "message": "Patent search timed out - try fewer keywords",
                "patents": []
            }
        except Exception as e:
            print(f"Patent search error: {type(e).__name__}: {str(e)}") # Debug log
            return {
                "status": "error",
                "message": f"Patent search error: {str(e)}",
                "patents": []
            }
    
    def _calculate_relevance(self, patent: Dict, keywords: List[str]) -> float:
        """Simple relevance scoring based on keyword matches"""
        score = 0.0
        title = patent.get("patent_title", "").lower()
        abstract = patent.get("patent_abstract", "").lower()

        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Title matches are worth more
            if keyword_lower in title:
                score += 2.0
            if keyword_lower in abstract:
                score += 1.0
        
        return score
