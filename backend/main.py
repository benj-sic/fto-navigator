from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

app = FastAPI(
    title="FTO Navigator API",
    description="Patent freedom-to-operate analysis for researchers",
    version="0.1.0",
)

# Define what research input looks like
class ResearchInput(BaseModel):
    title: str = Field(..., description="Title of your research")
    description: str = Field(..., min_length=50, description="Detailed descripton (min 50 chars)")
    field_of_study: str = Field(..., description="e.g., 'Biotechnology', 'Software', 'Mechanical'")
    keywords: list[str] = Field(..., min_items=1, max_items=10, description="Key technical terms")
    reseracher_name: Optional[str] = Field(None, description="Your name (optional)")

# Basic health check endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to FTO Navigator API",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# Our main analysis endpoint
@app.post("/api/analyze")
def analyze_research(research: ResearchInput):
    # For now, just echo back what we recevied
    # We'll add patent searching in the next section

    return {
        "status": "received",
        "analysis_id": "demo-123", # We'll generate real IDs later
        "research_title": research.title,
        "keywords_count": len(research.keywords),
        "message": "Research description received. Patent analysis will be added next session!",
        "next_steps": [
            "Patent search integration",
            "Risk assessment algorithm",
            "Report generation"
        ]
    }