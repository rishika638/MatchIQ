from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from sqlalchemy import text
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import limiter

from app.core.config import settings
from app.core.database import engine, Base
from app.models import *
from app.api.v1 import (
    auth, candidates, opportunities, search, agent,
    feedback, saved, evaluation, ingestion, analytics
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("matchiq")

settings.validate_production()

# Create tables if not existing
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Opportunity Intelligence Engine — Semantic Discovery, Explainable Matching, and AI Career Copilot.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENVIRONMENT.lower() != "production" else None,
    docs_url=f"{settings.API_V1_STR}/docs" if settings.ENVIRONMENT.lower() != "production" else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.ENVIRONMENT.lower() != "production" else None
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in settings.cors_origins() if origin != "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000.0
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response

# Root and health checks
@app.get("/")
def root():
    return {
        "product": "MatchIQ",
        "description": "Opportunity Intelligence Engine",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }

@app.get("/health")
@app.get(f"{settings.API_V1_STR}/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception:
        database_status = "unavailable"
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": database_status}
        )
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "database": database_status,
        "embedding_model": settings.EMBEDDING_MODEL_NAME
    }

# Register API v1 Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(candidates.router, prefix=f"{settings.API_V1_STR}/candidates", tags=["Candidate Intelligence"])
app.include_router(opportunities.router, prefix=f"{settings.API_V1_STR}/opportunities", tags=["Opportunities"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["Hybrid Search"])
app.include_router(agent.router, prefix=f"{settings.API_V1_STR}/agent", tags=["AI Career Agent"])
app.include_router(feedback.router, prefix=f"{settings.API_V1_STR}/feedback", tags=["Recommendation Feedback"])
app.include_router(saved.router, prefix=f"{settings.API_V1_STR}/saved", tags=["Saved Opportunities"])
app.include_router(evaluation.router, prefix=f"{settings.API_V1_STR}/evaluation", tags=["Evaluation & Benchmarks"])
app.include_router(ingestion.router, prefix=f"{settings.API_V1_STR}/ingestion", tags=["Opportunity Ingestion"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Intelligence Analytics"])
