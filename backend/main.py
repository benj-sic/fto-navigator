from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
import uuid
import json

# Import our new modules
from database import get_db, ResearchAnalysis
from patent_service import PatentSearchService

# Add these imports after the existing ones
from risk_assessment import RiskAssessmentService
from report_generator import ReportGenerator

# Initialize services after patent_service
risk_service = RiskAssessmentService()
report_generator = ReportGenerator()

# Create our FastAPI application
app = FastAPI(
    title="FTO Navigator API",
    description="Patent freedom-to-operate analysis for researchers",
    version="0.2.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize patent search service
patent_service = PatentSearchService()

# Define what research input looks like
class ResearchInput(BaseModel):
    title: str = Field(..., description="Title of your research")
    description: str = Field(..., min_length=50, description="Detailed description (min 50 chars)")
    field_of_study: str = Field(..., description="e.g., 'Biotechnology', 'Software', 'Mechanical'")
    keywords: list[str] = Field(..., min_items=1, max_items=10, description="Key technical terms")
    researcher_name: Optional[str] = Field(None, description="Your name (optional)")

# Response model for analysis results
class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str
    patent_count: Optional[int] = None
    top_patents: Optional[List[Dict]] = None

# Basic health check endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to FTO Navigator API v0.2",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "features": ["Patent search", "Database storage", "Analysis tracking"]
    }

# Our enhanced analysis endpoint
@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_research(research: ResearchInput, db: Session = Depends(get_db)):
    """
    Analyze research for potential patent conflicts
    Now includes real USPTO patent search!
    """
    # Generate unique ID for this analysis
    analysis_id = str(uuid.uuid4())
    
    # Save to database
    db_analysis = ResearchAnalysis(
        analysis_id=analysis_id,
        title=research.title,
        description=research.description,
        field_of_study=research.field_of_study,
        keywords=json.dumps(research.keywords),
        researcher_name=research.researcher_name,
        patent_search_status="searching"
    )
    db.add(db_analysis)
    db.commit()
    
    # Search for relevant patents
    patent_results = await patent_service.search_patents(research.keywords)
    
    # Update database with results
    if patent_results["success"]:
        db_analysis.patent_search_status = "completed"
        db_analysis.patent_results = json.dumps(patent_results["patents"])
        db_analysis.patent_count = str(patent_results["count"])
    else:
        db_analysis.patent_search_status = "error"
        db_analysis.patent_results = json.dumps({"error": patent_results["error"]})
    
    db.commit()
    
    # Prepare response
    if patent_results["success"]:
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            message=f"Found {patent_results['count']} potentially relevant patents",
            patent_count=patent_results["count"],
            top_patents=patent_results["patents"][:5]  # Return top 5 patents
        )
    else:
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="error",
            message=f"Patent search failed: {patent_results['error']}"
        )

# New endpoint to retrieve analysis results
@app.get("/api/analyses/{analysis_id}")
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieve a previous analysis by ID"""
    analysis = db.query(ResearchAnalysis).filter(
        ResearchAnalysis.analysis_id == analysis_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    patents = analysis.get_patent_results()
    
    return {
        "analysis_id": analysis.analysis_id,
        "title": analysis.title,
        "field_of_study": analysis.field_of_study,
        "keywords": analysis.get_keywords(),
        "created_at": analysis.created_at.isoformat(),
        "patent_search_status": analysis.patent_search_status,
        "patent_count": analysis.patent_count,
        "patents": patents
    }

# Add this endpoint after the get_analysis endpoint

@app.get("/api/analyses/{analysis_id}/report")
def generate_report(analysis_id: str, db: Session = Depends(get_db)):
    """Generate a comprehensive FTO report for an analysis"""
    analysis = db.query(ResearchAnalysis).filter(
        ResearchAnalysis.analysis_id == analysis_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Get patent results - handle None case
    patents = analysis.get_patent_results()
    
    # Don't raise error if no patents - just use empty list
    if patents is None:
        patents = []
    
    # Prepare research data
    research_data = {
        "analysis_id": analysis.analysis_id,
        "title": analysis.title,
        "field_of_study": analysis.field_of_study,
        "keywords": analysis.get_keywords(),
        "researcher_name": analysis.researcher_name
    }
    
    # Run risk assessment (will handle empty patents)
    risk_assessment = risk_service.assess_patents(research_data, patents)
    
    # Generate report
    report = report_generator.generate_report(research_data, risk_assessment)
    
    return report

@app.get("/api/analyses/{analysis_id}/risk")
def get_risk_assessment(analysis_id: str, db: Session = Depends(get_db)):
    """Get just the risk assessment for an analysis"""
    analysis = db.query(ResearchAnalysis).filter(
        ResearchAnalysis.analysis_id == analysis_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    patents = analysis.get_patent_results()
    
    research_data = {
        "title": analysis.title,
        "field_of_study": analysis.field_of_study,
        "keywords": analysis.get_keywords()
    }
    
    risk_assessment = risk_service.assess_patents(research_data, patents or [])
    
    return risk_assessment

# List all analyses (useful for testing)
@app.get("/api/analyses")
def list_analyses(db: Session = Depends(get_db)):
    """List all analyses in the database"""
    analyses = db.query(ResearchAnalysis).order_by(
        ResearchAnalysis.created_at.desc()
    ).limit(10).all()
    
    return {
        "count": len(analyses),
        "analyses": [
            {
                "analysis_id": a.analysis_id,
                "title": a.title,
                "created_at": a.created_at.isoformat(),
                "status": a.patent_search_status
            }
            for a in analyses
        ]
    }