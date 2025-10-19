from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes.mood_routes import router as mood_router
from routes.summary_routes import router as summary_router
from routes.auth_routes import router as auth_router
from routes.user_routes import router as user_router
from fastapi.responses import JSONResponse
from fastapi import Request
import os, time

load_dotenv()

app = FastAPI(title="VitaTwin API", version="1.0")

CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
origins = [o.strip() for o in CORS_ORIGINS.split(',') if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"message": "VitaTwin API is running 🚀"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    dur = round((time.time() - start) * 1000, 2)
    print(f"{request.method} {request.url.path} -> {response.status_code} [{dur}ms]")
    return response

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Not Found", "path": request.url.path})

# Routers
app.include_router(mood_router, prefix="/api/mood")
app.include_router(summary_router, prefix="/api/summary")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(user_router, prefix="/api/user")
