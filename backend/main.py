from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import asyncio

# Import our new modules
from database import get_db, ResearchAnalysis, SessionLocal
from patent_service import PatentSearchService

app = FastAPI(
    title="FTO Navigator API",
    description="Patent freedom-to-operate analysis for researchers",
    version="0.2.0",
)

# Initialize services
patent_service = PatentSearchService()

# Define what research input looks like
class ResearchInput(BaseModel):
    title: str = Field(..., description="Title of your research")
    description: str = Field(..., min_length=50, description="Detailed descripton (min 50 chars)")
    field_of_study: str = Field(..., description="e.g., 'Biotechnology', 'Software', 'Mechanical'")
    keywords: list[str] = Field(..., min_items=1, max_items=10, description="Key technical terms")
    researcher_name: Optional[str] = Field(None, description="Your name (optional)")

# Response model for analysis status
class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str
    created_at: datetime

# Response model for analysis results
class AnalysisResults(BaseModel):
    analysis_id: str
    title: str
    status: str
    patent_search_results: Optional[dict] = None
    risk_assessment: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

# Basic health check endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to FTO Navigator API",
        "status": "healthy",
        "version": "0.2.0",
        "timestamp": datetime.now().isoformat()
    }

# Our main analysis endpoint
@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_research(
    research: ResearchInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    #Create new analysis record
    analysis = ResearchAnalysis(
        title=research.title,
        description=research.description,
        field_of_study=research.field_of_study,
        keywords=research.keywords,
        researcher_name=research.researcher_name,
        status="pending"
    )

    # Save to database
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Start background analysis
    background_tasks.add_task(
        perform_analysis,
        analysis_id=analysis.id,
        keywords=research.keywords,
        field_of_study=research.field_of_study
    )

    return AnalysisResponse(
        analysis_id=analysis.id,
        status="pending",
        message="Analysis started. Check back in a few moments for results.",
        created_at=analysis.created_at
    )

# Get analysis results
@app.get("/api/results/{analysis_id}", response_model=AnalysisResults)
def get_analysis_results(analysis_id: str, db: Session = Depends(get_db)):
    # Find analysis in database
    analysis = db.query(ResearchAnalysis).filter(ResearchAnalysis.id == analysis_id).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Basic risk assessment if patents are found
    risk_assesssment = None
    if analysis.patent_search_results and analysis.status == "completed":
        risk_assessment = calculate_basic_risk(analysis.patent_search_results)
        analysis.risk_assessment = risk_assessment
        db.commit ()

    return AnalysisResults(
        analysis_id=analysis.id,
        title=analysis.title,
        status=analysis.status,
        patent_search_results=analysis.risk_assessment,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at
    )

# Get all analyses (useful for testing)
@app.get("/api/analyses")
def list_analyes(db: Session = Depends(get_db)):
    analyses = db.query(ResearchAnalysis).order_by(ResearchAnalysis.created_at.desc()).all()
    return {
        "total": len(analyses),
        "analyses": [
            {
                "id": a.id,
                "title": a.title,
                "status": a.status,
                "created_at": a.created_at.isoformat()
            }
            for a in analyses
        ]
    }

# Background task to perform analysis
async def perform_analysis(analysis_id: str, keywords: List[str], field_of_study: str):
    """Run patent search in background"""
    print(f"Starting background analysis for {analysis_id}") # Debug log
    db = SessionLocal()
    analysis = None # Initialize to None
    try:
        # Get analysis record
        analysis = db.query(ResearchAnalysis).filter(ResearchAnalysis.id == analysis_id).first()
        if not analysis:
            print(f"Analysis {analysis_id} not found in database") # Debug log
            return
        
        # Update status
        analysis.status = "analyzing"
        db.commit()
        print(f"Status updated to 'analyzing' for {analysis_id}") # Debug log

        # Perform patent search
        search_results = await patent_service.search_patents(keywords, field_of_study)
        print(f"Search completed with status: {search_results.get('status')}") # Debug log

        # Save results
        analysis.patent_search_results = search_results
        analysis.status = "completed" if search_results["status"] == "success" else "error"
        analysis.updated_at = datetime.now(timezone.utc)
        db.commit()
        print(f"Analysis {analysis_id} completed with status: {analysis.status}") # Debug log

    except Exception as e:
        print(f"Error in perform_analysis: {type(e).__name__}: {str(e)}") # Debug log
        # Handle errors
        if analysis:
            analysis.status = "error"
            analysis.patent_search_results = {"error": str(e)}
            db.commit()
    finally:
        db.close()

def calculate_basic_risk(patent_results: dict) -> dict:
    """Calculate basic FTO risk based on patent search results"""
    if not patent_results or not patent_results.get("patents"):
        return {
            "risk_level": "low",
            "score": 20,
            "factors": ["No directly relevant patents found"],
            "recommendations": ["Proceed with standard IP precautions"]
        }
    
    patent_count = len(patent_results.get("patents", []))
    max_relevance = max([p.get("relevance_score", 0) for p in patent_results["patents"]], default=0)

    # Simple risk calculation
    if patent_count >= 5 and max_relevance >= 3:
        risk_level = "high"
        score = 80
        recommendations = [
            "Consult with a patent attorney before proceeding",
            "Consider freedom-to-operate search by professional",
            "Review identified patents carefully"
        ]
    elif patent_count >= 3 or max_relevance >= 2:
        risk_level = "medium"
        score = 50
        recommendations = [
            "Review identified patents for potential conflicts",
            "Consider design modifications to avoid patent claims",
            "Document your novel contributions clearly"
        ]
    else:
        risk_level = "low"
        score = 30
        recommendations = [
            "Continue with standard IP documentation"
            "Monitor for new patents in this space"
            "Consider filing your own patent if novel"
        ]
    
    return {
        "risk_level": risk_level,
        "score": score,
        "factors": [
            f"Found {patent_count} potentially relevant patents",
            f"Highest relevance score: {max_relevance:1.f}",
            f"Search date: {patent_results.get('search_timestamp', 'Unknown')}"
        ],
        "recommendations": recommendations,
        "disclaimer": "This is a basic automated assessment. Consult an IP attorney for professional advice."
    }