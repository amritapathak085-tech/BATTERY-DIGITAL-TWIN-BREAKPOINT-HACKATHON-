import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.batteries import router as batteries_router

app = FastAPI(title="Battery Digital Twin API", version="1.0.0")

allowed_origins = ["http://localhost:3000"]
vercel_url = os.getenv("VERCEL_FRONTEND_URL")
if vercel_url:
    allowed_origins.append(vercel_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(batteries_router)


@app.get("/health")
def health():
    return {"status": "ok"}
