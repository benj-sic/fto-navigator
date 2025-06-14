import httpx
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

class PatentSearchService:
    def __init__(self):
        self.api_key = os.getenv("USPTO_API_KEY")
        self.api_url = os.getenv("USPTO_API_URL")
        
        if not self.api_key:
            raise ValueError("USPTO_API_KEY not found in environment variables")
    
    async def search_patents(self, keywords: List[str], limit: int = 10) -> Dict:
        """
        Search USPTO for patents based on keywords
        Returns simplified patent data for FTO analysis
        """
        # Build search query from keywords
        search_query = " OR ".join(keywords)
        
        # USPTO API parameters
        params = {
            "titleText": search_query,  # Search in patent titles
            "statusCodeBag": "150",  # Only granted patents
            "rowCount": str(limit),
            "sortBy": "grantDate",
            "sortOrder": "desc"
        }
        
        headers = {
            "X-API-Key": self.api_key,
            "Accept": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.api_url,
                    params=params,
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Extract relevant patent information
                simplified_results = self._simplify_patent_data(data)
                
                return {
                    "success": True,
                    "count": data.get("count", 0),
                    "patents": simplified_results,
                    "search_query": search_query
                }
                
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"USPTO API error: {str(e)}",
                "patents": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "patents": []
            }
    
    def _simplify_patent_data(self, raw_data: Dict) -> List[Dict]:
        """Extract key information from USPTO response"""
        simplified_patents = []
        
        patents = raw_data.get("patentFileWrapperDataBag", [])
        
        for patent in patents[:10]:  # Limit to 10 results
            meta = patent.get("applicationMetaData", {})
            
            # Extract key fields for FTO analysis
            simplified = {
                "patent_number": meta.get("patentNumber", "N/A"),
                "application_number": patent.get("applicationNumberText", "N/A"),
                "title": meta.get("inventionTitle", "No title"),
                "grant_date": meta.get("grantDate", "N/A"),
                "status": meta.get("applicationStatusDescriptionText", "Unknown"),
                "applicants": self._extract_applicants(meta),
                "inventors": self._extract_inventors(meta),
                "classifications": meta.get("cpcClassificationBag", [])[:5],  # Top 5 classifications
                "filing_date": meta.get("filingDate", "N/A"),
                "field": meta.get("class", "N/A")
            }
            
            simplified_patents.append(simplified)
        
        return simplified_patents
    
    def _extract_applicants(self, meta: Dict) -> List[str]:
        """Extract applicant names"""
        applicants = []
        for applicant in meta.get("applicantBag", []):
            name = applicant.get("applicantNameText", "Unknown")
            applicants.append(name)
        return applicants[:3]  # Limit to 3 applicants
    
    def _extract_inventors(self, meta: Dict) -> List[str]:
        """Extract inventor names"""
        inventors = []
        for inventor in meta.get("inventorBag", []):
            name = inventor.get("inventorNameText", "Unknown")
            inventors.append(name)
        return inventors[:3]  # Limit to 3 inventors