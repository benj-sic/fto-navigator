import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import asyncio
from google.cloud import bigquery
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Initialize BigQuery client
client = bigquery.Client()

class PatentSearchService:
    def __init__(self):
        self.client = bigquery.Client()
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.dataset_id = "patents-public-data.patents"

    async def search_patents(self, keywords: List[str], field_of_study: str = None, jurisdiction: str = 'US', limit: int = 25) -> Dict:
        """
        Search Google Patents Public Dataset on BigQuery, filtering for active patents by jurisdiction.
        """
        try:
            # Construct keyword search conditions for title and abstract
            search_terms_lower = [k.lower() for k in keywords]
            keyword_conditions_list = []
            for term in search_terms_lower:
                keyword_conditions_list.append(f"""
                    EXISTS(SELECT 1 FROM UNNEST(p.title_localized) AS tl WHERE tl.language = 'en' AND LOWER(tl.text) LIKE '%{term}%') OR
                    EXISTS(SELECT 1 FROM UNNEST(p.abstract_localized) AS al WHERE al.language = 'en' AND LOWER(al.text) LIKE '%{term}%')
                """)
            keyword_conditions = "(" + " OR ".join(keyword_conditions_list) + ")"

            # Calculate the date 20 years ago from today for the activity filter
            twenty_years_ago = datetime.now() - timedelta(days=20 * 365.25)
            filing_date_threshold = int(twenty_years_ago.strftime('%Y%m%d'))

            # CORRECTED QUERY: Aliases added to UNNEST operations in subqueries
            query = f"""
                SELECT
                    p.publication_number,
                    (SELECT text FROM UNNEST(p.title_localized) WHERE language = 'en' LIMIT 1) AS title,
                    (SELECT text FROM UNNEST(p.abstract_localized) WHERE language = 'en' LIMIT 1) AS abstract,
                    p.publication_date,
                    p.filing_date,
                    p.grant_date,
                    p.country_code,
                    (SELECT ARRAY_AGG(c.code) FROM UNNEST(p.cpc) AS c) as cpc_codes,
                    (SELECT ARRAY_AGG(a.name) FROM UNNEST(p.assignee_harmonized) as a) as assignees,
                    (SELECT ARRAY_AGG(i.name) FROM UNNEST(p.inventor_harmonized) as i) as inventors
                FROM
                    `{self.dataset_id}.publications` AS p
                WHERE
                    {keyword_conditions}
                    AND p.country_code = @jurisdiction
                    AND p.grant_date > 0 -- It must be a granted patent
                    AND p.filing_date >= @filing_date_threshold -- Filed in the last 20 years
                ORDER BY
                    p.publication_date DESC
                LIMIT @limit
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("jurisdiction", "STRING", jurisdiction.upper()),
                    bigquery.ScalarQueryParameter("filing_date_threshold", "INT64", filing_date_threshold),
                    bigquery.ScalarQueryParameter("limit", "INT64", limit),
                ]
            )

            # For debugging, you can uncomment the next line
            # print(f"Executing BigQuery search with SQL:\n{query}")

            query_job = self.client.query(query, job_config=job_config)
            results_iterator = query_job.result()

            patents_data = []
            for row in results_iterator:
                patent_info = {
                    "patent_number": row.get("publication_number"),
                    "title": row.get("title"),
                    "abstract": row.get("abstract"),
                    "grant_date": str(row.get("grant_date")) if row.get("grant_date") else "N/A",
                    "filing_date": str(row.get("filing_date")) if row.get("filing_date") else "N/A",
                    "applicants": row.get("assignees", []),
                    "inventors": row.get("inventors", []),
                    "classifications": row.get("cpc_codes", []),
                    "jurisdiction": row.get("country_code"),
                    "status": "Active"  # Based on our query logic
                }
                patents_data.append(patent_info)

            # print(f"BigQuery search found {len(patents_data)} patents within the limit.")

            return {
                "success": True,
                "count": len(patents_data),
                "patents": patents_data,
                "search_query": query,
            }

        except Exception as e:
            print(f"Error searching BigQuery patents: {str(e)}")
            return {
                "success": False,
                "error": f"BigQuery search error: {str(e)}",
                "patents": [],
                "count": 0,
            }

# Test code (if you have a separate test file, update that instead)
async def test_bigquery_patent_search():
    print("Testing BigQuery patent search...")
    service = PatentSearchService()

    # Example search
    keywords = ["CRISPR", "gene editing"]
    jurisdiction = "US"

    results = await service.search_patents(keywords=keywords, jurisdiction=jurisdiction, limit=5)

    print("\n--- Search Results ---")
    print(f"Success: {results['success']}")
    print(f"Error: {results.get('error')}")
    print(f"Number of patents returned (limited): {results['count']}")
    print("Patents:")
    for patent in results['patents']:
        print(f"  Title: {patent.get('title')}")
        print(f"  Abstract: {patent.get('abstract')[:100] if patent.get('abstract') else 'N/A'}...")
        print(f"  Patent Number: {patent.get('patent_number')}")
        print(f"  Jurisdiction: {patent.get('jurisdiction')}")
        print(f"  Grant Date: {patent.get('grant_date')}")
        print(f"  Filing Date: {patent.get('filing_date')}")
        print("-" * 20)

if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    load_dotenv() # Load your .env file
    asyncio.run(test_bigquery_patent_search())