"""
API initialization module for AI Safety Governance Platform.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app():
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    app = FastAPI(
        title="AI Safety Governance Platform",
        description="API for managing AI safety and governance",
        version="1.0.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Import and include routers
    from .routers import users, auth, models, compliance
    
    # Add routers
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(models.router, prefix="/api/v1/models", tags=["Models"])
    app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["Compliance"])
    
    return app
