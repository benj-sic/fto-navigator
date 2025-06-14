from sqlalchemy import create_engine, Column, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./fto_navigator.db"

# Create database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
Base = declarative_base()

# Define our database models
class ResearchAnalysis(Base):
    __tablename__ = "research_analyses"
    
    analysis_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    field_of_study = Column(String, nullable=False)
    keywords = Column(Text, nullable=False)  # Store as JSON string
    researcher_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Patent search results
    patent_search_status = Column(String, default="pending")
    patent_results = Column(Text, nullable=True)  # Store as JSON string
    patent_count = Column(String, nullable=True)
    
    def get_keywords(self):
        """Convert keywords JSON string back to list"""
        return json.loads(self.keywords) if self.keywords else []
    
    def get_patent_results(self):
        """Convert patent results JSON string back to dict"""
        return json.loads(self.patent_results) if self.patent_results else None

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()