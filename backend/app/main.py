from datetime import datetime
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.api.v1.api import api_router
from app.api.v1.websocket import router as ws_router
from sqlalchemy import text
import redis.asyncio as aioredis

app = FastAPI(
    title=settings.APP_NAME,
    description="High-performance asynchronous RESTful API & CBT Engine for E-Learning LMS built with FastAPI, SQLAlchemy 2.0, and WebSockets.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handlers for uniform ApiResponse envelope
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err["loc"] if loc != "body")
        errors.append(f"{field}: {err['msg']}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error: " + "; ".join(errors),
            "data": exc.errors(),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": f"Internal server error: {str(exc)}",
            "data": None,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# Health check with active PostgreSQL & Redis ping
@app.get("/health", tags=["Health"])
async def health_check():
    db_status = "connected"
    redis_status = "connected"
    is_healthy = True

    # 1. Active PostgreSQL Ping
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        is_healthy = False

    # 2. Active Redis Ping
    try:
        r = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        await r.ping()
        await r.aclose()
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"

    overall_status = "healthy" if is_healthy and redis_status == "connected" else ("degraded" if is_healthy else "unhealthy")

    payload = {
        "status": overall_status,
        "database": db_status,
        "redis": redis_status,
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if not is_healthy:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=payload)
    return payload


# Include Routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_router)
