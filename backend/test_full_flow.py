import httpx
import json
import asyncio

async def test_fto_navigator():
    """Test the complete FTO analysis flow"""
    base_url = "http://127.0.0.1:8000"
    
    # Test research data
    research = {
        "title": "AI-Powered Drug Discovery Platform",
        "description": "Using machine learning algorithms to predict drug-protein interactions and accelerate the drug discovery process for neurodegenerative diseases",
        "field_of_study": "Biotechnology",
        "keywords": ["machine learning", "drug discovery", "AI", "protein interaction"],
        "researcher_name": "Dr. Alex Chen"
    }
    
    async with httpx.AsyncClient() as client:
        # 1. Submit research for analysis
        print("1. Submitting research for analysis...")
        response = await client.post(f"{base_url}/api/analyze", json=research)
        result = response.json()
        print(f"   Analysis ID: {result['analysis_id']}")
        print(f"   Status: {result['status']}")
        print(f"   Patents found: {result.get('patent_count', 0)}")
        
        analysis_id = result['analysis_id']
        
        # 2. Get risk assessment
        print("\n2. Getting risk assessment...")
        response = await client.get(f"{base_url}/api/analyses/{analysis_id}/risk")
        risk = response.json()
        print(f"   Overall risk: {risk['overall_risk_level']}")
        print(f"   Risk score: {risk['overall_risk_score']}")
        print(f"   High-risk patents: {risk['high_risk_patents']}")
        
        # 3. Generate full report
        print("\n3. Generating full report...")
        response = await client.get(f"{base_url}/api/analyses/{analysis_id}/report")
        report = response.json()
        print(f"   Executive Summary: {report['executive_summary'][:100]}...")
        print(f"   Recommendations: {len(report['recommendations']['general_recommendations'])}")
        
        # Save report to file
        with open('sample_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print("\n✅ Full report saved to sample_report.json")

# Run the test
asyncio.run(test_fto_navigator())