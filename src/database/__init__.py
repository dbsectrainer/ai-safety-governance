"""
Database initialization module for AI Safety Governance Platform.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create SQLAlchemy base class for models
Base = declarative_base()

# Initialize database engine with environment-aware configuration
def init_db(db_url=None):
    """
    Initialize database connection.
    
    Args:
        db_url (str, optional): Database URL. Defaults to None, which uses environment variable.
    
    Returns:
        tuple: (engine, SessionLocal)
    """
    if db_url is None:
        db_url = "sqlite:///./ai_safety_governance.db"  # Default to SQLite for development
        
    engine = create_engine(
        db_url,
        pool_pre_ping=True,  # Enable connection health checks
        pool_size=5,  # Connection pool size
        max_overflow=10  # Max number of connections to create beyond pool_size
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return engine, SessionLocal

# Database dependency
def get_db():
    """
    Get database session.
    
    Yields:
        Session: Database session
    """
    engine, SessionLocal = init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
