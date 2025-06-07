from sqlalchemy import create_engine, Column, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import uuid

# Create database enginge (SQLite for simplicity)
SQLALCHEMY_DATABASE_URL = "sqlite:///./fto_navigator.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Define research model
class ResearchAnalysis(Base):
    __tablename__ = "research_analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Research details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    field_of_study = Column(String, nullable=False)
    keywords = Column(JSON, nullable=False) # Store list as JSON
    researcher_name = Column(String, nullable=True)

    # Analysis status
    status = Column(String, nullable=False, default="pending") # pending, analyzing, completed, error

    # Timestamps 
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

# Create tables
Base.metadata.create_all(bind=engine)

# Create a dependency for getting a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    
    
