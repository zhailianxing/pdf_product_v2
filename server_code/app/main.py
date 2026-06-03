from contextlib import asynccontextmanager

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routers import audit_logs, auth, dashboard, records, users
from app.seed import run_seed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_seed()
    logger.info("Database initialized, AI provider=%s", settings.ai_provider)
    yield


app = FastAPI(
    title="材质报告 AI 自动审核系统 API",
    description="后台管理系统服务端接口",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"code": 500, "message": str(exc), "data": None})


@app.get("/api/health")
def health():
    return {"status": "ok", "ai_provider": settings.ai_provider}


api_prefix = "/api/v1"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(records.router, prefix=api_prefix)
app.include_router(audit_logs.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
