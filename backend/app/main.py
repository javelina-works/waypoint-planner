# app/main.py
from fastapi import FastAPI
from app.routers import waypoints, tiles, uploads
from app.db import engine, Base
from titiler.core.factory import TilerFactory
from titiler.core.errors import DEFAULT_STATUS_CODES, add_exception_handlers

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Register routers
app.include_router(waypoints.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1", tags=["uploads"])
# app.include_router(tiles.router, prefix="/api/v1", tags=["tiles"])
cog = TilerFactory(router_prefix="/api/v1")
app.include_router(cog.router, prefix="/api/v1", tags=["tiles"])
add_exception_handlers(app, DEFAULT_STATUS_CODES)