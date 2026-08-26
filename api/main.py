from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import (
    farmer,
    harvest,
    market,
    recommendation
)

from api.routes.dashboard import router as dashboard_router


app = FastAPI(
    title="VilaiNilai API",
    description="AI-Powered Dynamic Farm-to-Market Optimization for Tamil Nadu",
    version="0.1.0"
)


# -----------------------------
# CORS
# -----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Routers
# -----------------------------

app.include_router(farmer.router)
app.include_router(harvest.router)
app.include_router(market.router)
app.include_router(recommendation.router)
app.include_router(dashboard_router)


# -----------------------------
# Root
# -----------------------------

@app.get("/")
def root():
    return {
        "project": "VilaiNilai",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }