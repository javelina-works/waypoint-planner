# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routers import waypoints, tiles, uploads
from app.db import engine, Base
from titiler.core.factory import TilerFactory
from titiler.core.errors import DEFAULT_STATUS_CODES, add_exception_handlers

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow only your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Register routers
app.include_router(waypoints.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1", tags=["uploads"])
# app.include_router(tiles.router, prefix="/api/v1", tags=["tiles"])
cog = TilerFactory(router_prefix="/api/v1")
app.include_router(cog.router, prefix="/api/v1", tags=["tiles"])
add_exception_handlers(app, DEFAULT_STATUS_CODES)


# Serve static files from the Vue build directory
app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")
