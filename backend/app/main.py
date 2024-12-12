# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import waypoints, uploads
from app.db import engine, Base
from titiler.core.factory import TilerFactory
from titiler.core.errors import DEFAULT_STATUS_CODES, add_exception_handlers, TileOutsideBounds
from PIL import Image
from io import BytesIO
from contextlib import asynccontextmanager

# Initialize database
Base.metadata.create_all(bind=engine)

TRANSPARENT_TILE = None

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """
    Setup tasks for the FastAPI application.
    """
    global TRANSPARENT_TILE

    # Generate the transparent tile during startup
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))  # Transparent RGBA image
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    TRANSPARENT_TILE = buffer.getvalue()
    # Lifespan enter (app startup)
    yield
    # Lifespan exit (app shutdown)
    TRANSPARENT_TILE = None  # Clean up the cached tile if needed

app = FastAPI(lifespan=app_lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # Allow only your frontend origin
    allow_methods=["GET", "POST"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
    allow_credentials=True,
)


# Register routers
app.include_router(waypoints.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1", tags=["uploads"])
# app.include_router(tiles.router, prefix="/api/v1", tags=["tiles"])
cog = TilerFactory(router_prefix="/api/v1")
app.include_router(cog.router, prefix="/api/v1", tags=["tiles"])
add_exception_handlers(app, DEFAULT_STATUS_CODES)



@app.exception_handler(TileOutsideBounds)
async def handle_tile_out_of_bounds(request, exc):
    return StreamingResponse(BytesIO(TRANSPARENT_TILE), media_type="image/png")


# Serve static files from the Vue build directory
app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")


# # Define the directory where images are uploaded
# UPLOAD_DIR = Path("./uploaded_images")
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
# #  Mount the directory to serve static files
# app.mount("/uploaded_images", StaticFiles(directory=UPLOAD_DIR), name="uploaded_images")


# @app.get("/debug-file/{path}")
# async def debug_file(path: str):
#     # filepath = UPLOAD_DIR / filename
#     if os.path.exists(path):
#         return {"status": "File exists", "path": str(path)}
#     else:
#         return {"status": "File not found", "path": str(path)}

# @app.get("/debug-resolve/")
# async def debug_resolve(file_path: str):
#     """
#     Debug endpoint to resolve and check file paths.
#     Example: /debug-resolve/?file_path=file://uploaded_images\\output_cog.tif
#     """
#     # Remove "file://" prefix if present
#     if file_path.startswith("file://"):
#         file_path = file_path[7:]  # Strip "file://"

#     # Convert to Path object and resolve
#     resolved_path = Path(file_path).resolve()

#     # Check if the file exists
#     file_exists = os.path.exists(resolved_path)

#     # Return debugging information
#     return {
#         "input_path": file_path,
#         "resolved_path": str(resolved_path),
#         "file_exists": file_exists,
#         "is_absolute": resolved_path.is_absolute(),
#     }
