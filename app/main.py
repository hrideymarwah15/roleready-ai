"""
FastAPI application entry point.
AI-Adaptive Onboarding Engine backend.
"""

import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import roadmap

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI-Adaptive Onboarding Engine",
    description="Generate personalized learning roadmaps based on resume and job description",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(roadmap.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "AI-Adaptive Onboarding Engine",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/generate-roadmap": "Generate learning roadmap",
            "GET /api/health": "Health check",
            "GET /docs": "Interactive API documentation",
        },
    }


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("🚀 AI-Adaptive Onboarding Engine starting...")
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        logger.info("✅ OpenAI API key configured")
    else:
        logger.warning("⚠️  No OpenAI API key - using keyword extraction fallback")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
