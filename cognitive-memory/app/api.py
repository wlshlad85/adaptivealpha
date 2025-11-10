"""
FastAPI Interface - REST API for Cognitive Memory System
Provides HTTP endpoints for intelligence operations
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
from memory_engine import engine
from database import db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class InteractionRequest(BaseModel):
    """Request model for processing interactions"""
    context: str = Field(..., description="Context or problem description", min_length=1)
    decision: Optional[str] = Field(None, description="Decision being considered")
    complexity: Optional[str] = Field(None, description="Expected complexity (e.g., O(n), O(log n))")
    expected_outcomes: Optional[List[Dict[str, Any]]] = Field(None, description="Expected future outcomes")
    related_decisions: Optional[List[str]] = Field(None, description="Related past decisions")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "context": "optimize database queries with slow performance",
                "decision": "add database indexes",
                "complexity": "O(log n)",
                "expected_outcomes": [
                    {"outcome": "faster queries", "probability": 0.9}
                ]
            }
        }


class ProcessingConfig(BaseModel):
    """Configuration for intelligence processing"""
    predict_future: bool = Field(True, description="Generate future predictions")
    cascade_depth: int = Field(5, ge=1, le=10, description="Depth of cascade prediction")
    similarity_threshold: float = Field(0.6, ge=0.0, le=1.0, description="Pattern similarity threshold")


class IntelligenceResponse(BaseModel):
    """Response model for intelligence operations"""
    direct_solution: Dict[str, Any]
    future_implications: Dict[str, Any]
    risk_matrix: Dict[str, Any]
    optimization_path: List[Dict[str, str]]
    pattern_insights: Dict[str, Any]
    intelligence_metrics: Dict[str, Any]
    brutal_honesty: Dict[str, Any]


class PatternQuery(BaseModel):
    """Query model for pattern search"""
    context: Dict[str, Any] = Field(..., description="Context to search patterns for")
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0)
    limit: int = Field(10, ge=1, le=50)


class DecisionRequest(BaseModel):
    """Request model for decision analysis"""
    decision: str = Field(..., min_length=1)
    immediate_impact: Dict[str, Any]
    confidence_score: float = Field(0.5, ge=0.0, le=1.0)
    cascade_depth: int = Field(5, ge=1, le=10)


class ErrorLogRequest(BaseModel):
    """Request model for error logging"""
    error_context: Dict[str, Any]
    solution: Optional[Dict[str, Any]] = None
    resolution_time_seconds: Optional[int] = None


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management"""
    # Startup
    logger.info("🚀 Starting Cognitive Memory System...")
    await engine.initialize()
    logger.info("✓ System ready for intelligent operations")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Cognitive Memory System...")
    await engine.shutdown()
    logger.info("✓ Shutdown complete")


app = FastAPI(
    title="Cognitive Memory System",
    description="Database-backed intelligence amplification engine with persistent memory",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# CORE ENDPOINTS
# ============================================================================

@app.post("/process", response_model=IntelligenceResponse, tags=["Intelligence"])
async def process_interaction(
    request: InteractionRequest,
    config: ProcessingConfig = Depends()
):
    """
    Process an interaction through the intelligence engine

    Returns:
    - Direct solution based on learned patterns
    - Future implications analysis
    - Risk assessment matrix
    - Optimization suggestions
    - Pattern insights
    - Brutal honesty assessment
    """
    try:
        result = await engine.process_input(
            input_data=request.dict(exclude_none=True),
            predict_future=config.predict_future,
            cascade_depth=config.cascade_depth
        )

        return IntelligenceResponse(**result)

    except Exception as e:
        logger.error(f"Error processing interaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/patterns/search", tags=["Patterns"])
async def search_patterns(query: PatternQuery):
    """
    Search for similar patterns in historical data
    Uses Jaccard similarity for pattern matching
    """
    try:
        patterns = await db.find_patterns(
            context=query.context,
            similarity_threshold=query.similarity_threshold
        )

        return {
            "patterns": patterns[:query.limit],
            "total_found": len(patterns)
        }

    except Exception as e:
        logger.error(f"Error searching patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/patterns/top", tags=["Patterns"])
async def get_top_patterns(
    limit: int = Query(10, ge=1, le=50),
    min_accuracy: float = Query(0.5, ge=0.0, le=1.0)
):
    """Get most effective patterns"""
    try:
        patterns = await db.get_top_patterns(
            limit=limit,
            min_accuracy=min_accuracy
        )

        return {
            "patterns": patterns,
            "count": len(patterns)
        }

    except Exception as e:
        logger.error(f"Error retrieving top patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DECISION ANALYSIS ENDPOINTS
# ============================================================================

@app.post("/decisions/analyze", tags=["Decisions"])
async def analyze_decision(request: DecisionRequest):
    """
    Analyze a decision and predict cascade effects
    """
    try:
        # Store decision
        decision_id = await db.store_decision(
            decision=request.decision,
            immediate_impact=request.immediate_impact,
            confidence_score=request.confidence_score
        )

        # Predict cascades
        cascades = await db.predict_cascade_effects(
            decision=request.decision,
            depth=request.cascade_depth
        )

        return {
            "decision_id": decision_id,
            "cascade_effects": cascades,
            "total_levels": len(cascades),
            "confidence": request.confidence_score
        }

    except Exception as e:
        logger.error(f"Error analyzing decision: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/decisions/cascades/{decision}", tags=["Decisions"])
async def get_decision_cascades(
    decision: str,
    depth: int = Query(5, ge=1, le=10)
):
    """Get predicted cascade effects for a decision"""
    try:
        cascades = await db.predict_cascade_effects(
            decision=decision,
            depth=depth
        )

        return {
            "decision": decision,
            "cascades": cascades,
            "depth": len(cascades)
        }

    except Exception as e:
        logger.error(f"Error retrieving cascades: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MEMORY AND HISTORY ENDPOINTS
# ============================================================================

@app.get("/memory/history", tags=["Memory"])
async def get_memory_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Retrieve conversation history"""
    try:
        history = await db.retrieve_context(
            limit=limit,
            offset=offset
        )

        return {
            "history": history,
            "count": len(history),
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/intelligence-score", tags=["Memory"])
async def get_intelligence_score(hours: int = Query(1, ge=1, le=168)):
    """Get average intelligence score over specified time period"""
    try:
        score = await db.get_intelligence_score(hours=hours)

        return {
            "intelligence_score": round(score, 3),
            "time_period_hours": hours,
            "interpretation": "Higher scores indicate more pattern matches and learning"
        }

    except Exception as e:
        logger.error(f"Error retrieving intelligence score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ERROR HANDLING ENDPOINTS
# ============================================================================

@app.post("/errors/log", tags=["Errors"])
async def log_error(request: ErrorLogRequest):
    """Log an error with optional solution"""
    try:
        error_id = await db.log_error(
            error_context=request.error_context,
            solution=request.solution,
            resolution_time=request.resolution_time_seconds
        )

        return {
            "error_id": error_id,
            "status": "logged"
        }

    except Exception as e:
        logger.error(f"Error logging error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/errors/solution", tags=["Errors"])
async def get_error_solution(error_context: Dict[str, Any]):
    """Get known solution for similar error"""
    try:
        solution = await db.get_error_solution(error_context)

        if not solution:
            return {
                "found": False,
                "message": "No known solution for this error"
            }

        return {
            "found": True,
            "solution": solution
        }

    except Exception as e:
        logger.error(f"Error retrieving solution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/analytics/intelligence", tags=["Analytics"])
async def get_intelligence_analytics(hours: int = Query(24, ge=1, le=720)):
    """Get comprehensive intelligence metrics"""
    try:
        system_intelligence = await engine.get_system_intelligence()
        db_metrics = await db.get_intelligence_metrics(hours=hours)

        return {
            "system": system_intelligence,
            "database": db_metrics,
            "time_period_hours": hours
        }

    except Exception as e:
        logger.error(f"Error retrieving analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/patterns/effectiveness", tags=["Analytics"])
async def get_pattern_effectiveness(limit: int = Query(20, ge=1, le=100)):
    """Get pattern effectiveness analytics"""
    try:
        effectiveness = await db.get_pattern_effectiveness(limit=limit)

        return {
            "patterns": effectiveness,
            "count": len(effectiveness)
        }

    except Exception as e:
        logger.error(f"Error retrieving pattern effectiveness: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    """System health check"""
    try:
        db_health = await db.health_check()

        return {
            "status": "intelligent" if db_health['status'] == 'healthy' else "degraded",
            "memory": "persistent",
            "database": db_health,
            "learning": "active"
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/", tags=["System"])
async def root():
    """API root information"""
    return {
        "name": "Cognitive Memory System",
        "version": "1.0.0",
        "description": "Database-backed intelligence amplification with persistent memory",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "process": "/process",
            "patterns": "/patterns/*",
            "decisions": "/decisions/*",
            "memory": "/memory/*",
            "analytics": "/analytics/*"
        },
        "philosophy": "Code > Analysis > Alternatives. No fluff, pure intelligence."
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint not found",
        "suggestion": "Check /docs for available endpoints",
        "status": 404
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal error: {str(exc)}")
    return {
        "error": "Internal server error",
        "details": str(exc),
        "status": 500
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
