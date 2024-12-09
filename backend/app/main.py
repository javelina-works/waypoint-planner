# app/main.py
from fastapi import FastAPI
from app.routers import waypoints, tiles, uploads
from app.db import engine, Base

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Register routers
app.include_router(waypoints.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1", tags=["uploads"])
app.include_router(tiles.router, prefix="/api/v1", tags=["tiles"])