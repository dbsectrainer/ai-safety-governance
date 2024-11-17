"""
Main application entry point for AI Safety Governance Platform.
"""
from fastapi import FastAPI
from src.api import create_app
from src.database import init_db, Base

# Create FastAPI application
app = create_app()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize components on application startup."""
    engine, SessionLocal = init_db()
    
    # Create database tables if they don't exist
    # Note: In production, use Alembic migrations instead
    Base.metadata.create_all(bind=engine)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        workers=1     # Number of worker processes
    )
