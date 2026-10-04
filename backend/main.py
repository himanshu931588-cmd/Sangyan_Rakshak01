import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.database.session import init_db
from backend.database.seeds import seed_database
from backend.routers import verify_router, grievance_router, health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SangyanMain")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler. Runs table initialization and benchmark database seeding on startup.
    """
    logger.info("Starting Sangyan Rakshak FastAPI backend service...")
    try:
        await init_db()
        await seed_database()
        logger.info("Database initialized and benchmark seeds applied successfully.")
    except Exception as e:
        logger.error(f"Startup database error: {e}", exc_info=True)
    yield
    logger.info("Shutting down Sangyan Rakshak backend service.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Multimodal Investor Scam-Shield and SEBI Verification Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred.",
            "error_type": type(exc).__name__,
        },
    )


# Include API Routers under /api/v1
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(verify_router, prefix=settings.API_V1_STR)
app.include_router(grievance_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "documentation": "/docs",
        "health_check": f"{settings.API_V1_STR}/health",
    }
