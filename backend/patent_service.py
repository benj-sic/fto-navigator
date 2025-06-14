import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import asyncio
from google.cloud import bigquery

# Load environment variables from .env file
load_dotenv()

# Initialize BigQuery client. It will automatically use GOOGLE_APPLICATION_CREDENTIALS.
client = bigquery.Client()

class PatentSearchService:
    def __init__(self):
        self.client = bigquery.Client()
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.dataset_id = "patents-public-data.patents"

    async def search_patents(self, keywords: List[str], field_of_study: str = None, limit: int = 10) -> Dict:
        """
        Search Google Patents Public Dataset on BigQuery.
        """
        try:
            search_terms_lower = [k.lower() for k in keywords]
            keyword_conditions_list = []
            for term in search_terms_lower:
                keyword_conditions_list.append(f"""
                    EXISTS(SELECT 1 FROM UNNEST(title_localized) AS tl WHERE LOWER(tl.text) LIKE '%{term}%') OR
                    EXISTS(SELECT 1 FROM UNNEST(abstract_localized) AS al WHERE LOWER(al.text) LIKE '%{term}%') OR
                    EXISTS(SELECT 1 FROM UNNEST(claims_localized) AS cl WHERE LOWER(cl.text) LIKE '%{term}%')
                """)
            keyword_conditions = "(" + " OR ".join(keyword_conditions_list) + ")"

            field_condition = ""
            if field_of_study:
                field_of_study_lower = field_of_study.lower()
                field_condition = f"""
                    AND (
                        EXISTS(SELECT 1 FROM UNNEST(title_localized) AS tl WHERE LOWER(tl.text) LIKE '%{field_of_study_lower}%') OR
                        EXISTS(SELECT 1 FROM UNNEST(abstract_localized) AS al WHERE LOWER(al.text) LIKE '%{field_of_study_lower}%')
                    )
                """

            query = f"""
                SELECT
                    publication_number,
                    ANY_VALUE(tl.text) AS title,
                    ANY_VALUE(al.text) AS abstract,
                    publication_date,
                    assignee_harmonized,
                    inventor_harmonized,
                    -- CHANGED: Use 'citation' instead of 'prior_art_citations'
                    citation,
                    cpc,
                    claims_localized
                FROM
                    `{self.dataset_id}.publications`
                LEFT JOIN
                    UNNEST(title_localized) AS tl ON tl.language = 'en'
                LEFT JOIN
                    UNNEST(abstract_localized) AS al ON al.language = 'en'
                LEFT JOIN
                    UNNEST(claims_localized) AS cl ON cl.language = 'en'
                WHERE
                    {keyword_conditions}
                    {field_condition}
                GROUP BY
                    publication_number, publication_date, assignee_harmonized, inventor_harmonized, citation, cpc, claims_localized
                LIMIT {limit}
            """

            print(f"Executing BigQuery search with SQL:\n{query}")

            query_job = self.client.query(query)
            results_iterator = query_job.result()

            patents_data = []
            for row in results_iterator:
                claims_text = ""
                if row.get('claims_localized'):
                    english_claims = [c['text'] for c in row['claims_localized'] if c.get('language') == 'en']
                    if english_claims:
                        claims_text = english_claims[0]

                # Extract citation details (patent numbers from the citations list)
                cited_patent_numbers = []
                if row.get('citation'):
                    for cited_patent in row['citation']:
                        # The 'citation' field is a RECORD REPEATED, containing 'publication_number' inside.
                        if isinstance(cited_patent, dict) and 'publication_number' in cited_patent:
                            cited_patent_numbers.append(cited_patent['publication_number'])

                patent_info = {
                    "patent_number": row.get("publication_number"),
                    "application_number": row.get("publication_number"),
                    "title": row.get("title"),
                    "abstract": row.get("abstract"),
                    "claims": claims_text,
                    "grant_date": str(row.get("publication_date")) if row.get("publication_date") else "N/A",
                    "status": "Published" if row.get("publication_date") else "Unknown",
                    "applicants": [
                        assignee['assignee_name']
                        for assignee in row.get("assignee_harmonized", [])
                        if isinstance(assignee, dict) and 'assignee_name' in assignee
                    ] if row.get("assignee_harmonized") else [],
                    "inventors": [
                        inventor['inventor_name']
                        for inventor in row.get("inventor_harmonized", [])
                        if isinstance(inventor, dict) and 'inventor_name' in inventor
                    ] if row.get("inventor_harmonized") else [],
                    "classifications": [
                        cpc_data['code']
                        for cpc_data in row.get("cpc", [])
                        if isinstance(cpc_data, dict) and 'code' in cpc_data
                    ] if row.get("cpc") else [],
                    "filing_date": "N/A",
                    "field": field_of_study,
                    "cited_patents": cited_patent_numbers # Add the extracted cited patent numbers
                }
                patents_data.append(patent_info)

            print(f"BigQuery search found {len(patents_data)} patents within the limit.")

            total_matching_count = await self._get_total_matching_count(
                keyword_conditions,
                field_condition
            )

            return {
                "success": True,
                "count": len(patents_data),
                "patents": patents_data,
                "search_query": query,
                "total_found": total_matching_count
            }

        except Exception as e:
            print(f"Error searching BigQuery patents: {str(e)}")
            return {
                "success": False,
                "error": f"BigQuery search error: {str(e)}",
                "patents": [],
                "count": 0,
                "total_found": 0
            }

    async def _get_total_matching_count(self, keyword_conditions: str, field_condition: str) -> int:
        """Helper to get the total count of matching results without a LIMIT clause."""
        count_query = f"""
            SELECT
                COUNT(DISTINCT publication_number)
            FROM
                `{self.dataset_id}.publications`
            LEFT JOIN
                UNNEST(title_localized) AS tl ON tl.language = 'en'
            LEFT JOIN
                UNNEST(abstract_localized) AS al ON al.language = 'en'
            LEFT JOIN
                UNNEST(claims_localized) AS cl ON cl.language = 'en'
            WHERE
                {keyword_conditions}
                {field_condition}
        """
        try:
            count_job = self.client.query(count_query)
            count_result = count_job.result()
            for row in count_result:
                return row[0]
            return 0
        except Exception as e:
            print(f"Error getting total count from BigQuery: {e}")
            return 0

# Test code (if you have a separate test file, update that instead)
async def test_bigquery_patent_search():
    print("Testing BigQuery patent search...")
    service = PatentSearchService()

    # Example search
    keywords = ["CRISPR", "gene editing"]
    field_of_study = "Biotechnology"

    results = await service.search_patents(keywords, field_of_study, limit=5)

    print("\n--- Search Results ---")
    print(f"Success: {results['success']}")
    print(f"Error: {results.get('error')}")
    print(f"Total patents found by query: {results.get('total_found', 'N/A')}")
    print(f"Number of patents returned (limited): {results['count']}")
    print("Patents:")
    for patent in results['patents']:
        print(f"  Title: {patent.get('title')}")
        print(f"  Abstract: {patent.get('abstract')[:100] if patent.get('abstract') else 'N/A'}...") # Handle None or empty string
        print(f"  Claims: {patent.get('claims')[:100] if patent.get('claims') else 'N/A'}...")
        print(f"  Patent Number: {patent.get('patent_number')}")
        print(f"  Applicants: {', '.join(patent.get('applicants', []))}")
        print(f"  Grant Date: {patent.get('grant_date')}")
        print(f"  Classifications: {', '.join(patent.get('classifications', []))}")
        print(f"  Cited Patents (first 5): {', '.join(patent.get('cited_patents', [])[:5])}") # New field
        print("-" * 20)

if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    load_dotenv() # Load your .env file
    asyncio.run(test_bigquery_patent_search())