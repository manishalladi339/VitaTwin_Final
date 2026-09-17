from contextlib import asynccontextmanager
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import close_database, ensure_indexes, ping_database
from routers import auth, checkins, twin, users

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s :: %(message)s")
logger = logging.getLogger("vitatwin")


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.validate()
    ensure_indexes()
    yield
    close_database()


app = FastAPI(title="VitaTwin API", version="2.0.0", description="Transparent wellness digital-twin API.", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def request_timing(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time-Ms"] = f"{(time.perf_counter() - started) * 1000:.1f}"
    logger.info("%s %s %s", request.method, request.url.path, response.status_code)
    return response


@app.get("/")
def root():
    return {"name": "VitaTwin API", "version": "2.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    ping_database()
    return {"status": "ready"}


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/profile", tags=["profile"])
app.include_router(checkins.router, prefix="/api/v1/checkins", tags=["check-ins"])
app.include_router(twin.router, prefix="/api/v1/twin", tags=["digital twin"])
