import sys
import os
import logging
from contextlib import asynccontextmanager

# Add backend directory to sys.path automatically
backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router
from app.core.scheduler import start_scheduler, stop_scheduler

logger = logging.getLogger("uvicorn.error")

# Create database tables automatically
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Démarrage : lance le moteur d'arrière-plan (télémétrie, TTF, santé)
    start_scheduler()
    logger.info("Scheduler Sentinelle AIOps démarré (télémétrie=10s, TTF=30s, santé=60s).")
    yield
    # Arrêt propre du scheduler à l'extinction du serveur
    stop_scheduler()
    logger.info("Scheduler Sentinelle AIOps arrêté.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)