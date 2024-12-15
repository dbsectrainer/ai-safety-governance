"""
Database initialization module for AI Safety Governance Platform.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create SQLAlchemy base class for models
Base = declarative_base()

def get_database_url():
    """Get database URL from environment or use default"""
    # PostgreSQL connection URL
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "db")  # service name from docker-compose
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "ai_safety_governance")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

# Initialize database engine
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,  # Connection pool size
    max_overflow=10  # Max number of connections to create beyond pool_size
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database dependency
def get_db():
    """
    Get database session.
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
