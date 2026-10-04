from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_async_session

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", summary="Get system health and database connectivity status")
async def get_health(db: AsyncSession = Depends(get_async_session)):
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "degraded"

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "version": "1.0.0",
    }


@router.get("/liveness", summary="Simple liveness probe")
async def get_liveness():
    return {"status": "healthy"}
