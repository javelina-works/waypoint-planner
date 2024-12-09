# app/main.py
from fastapi import FastAPI
from app.routers import waypoints
from app.db import engine, Base

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Register routers
app.include_router(waypoints.router, prefix="/api/v1")
